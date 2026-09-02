"""Generate stable metadata for the images in this repository."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "image-manifest.json"
IMAGE_EXTENSIONS = {".avif", ".gif", ".ico", ".jpeg", ".jpg", ".png", ".webp"}


def collect_images() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path != OUTPUT
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def describe(path: Path) -> dict[str, int | str]:
    try:
        with Image.open(path) as image:
            width, height = image.size
            image_format = (image.format or path.suffix.lstrip(".")).lower()
    except Exception as error:  # Pillow uses several exception types by format.
        raise RuntimeError(f"cannot read image dimensions: {path}") from error

    return {
        "path": path.relative_to(ROOT).as_posix(),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "format": image_format,
    }


def main() -> None:
    images = [describe(path) for path in collect_images()]
    document = {"schemaVersion": 1, "images": images}
    OUTPUT.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(images)} image records in {OUTPUT.name}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error
