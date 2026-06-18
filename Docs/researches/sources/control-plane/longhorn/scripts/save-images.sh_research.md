# sources/control-plane/longhorn/scripts/save-images.sh

## Purpose
Pulls images listed in a Longhorn image list and optionally saves them into a gzip-compressed archive for offline transfer.

## Important APIs and Variables
`list` defaults to `longhorn-images.txt`; `CONTAINER_CLI` defaults to Docker. Flags are `--images`, `--image-list`, `--platform`, and `--help`.

## Control Flow
After flag parsing and help handling, `errexit` and `xtrace` are enabled. The script pulls each listed image, adding `--platform` when requested. If an archive path is provided, it runs container `save` for all listed images and pipes to `gzip -c`.

## State and Persistence
Mutates local container image cache by pulling images. Optionally writes a tar.gz archive at the requested path.

## Dependencies and Integration Points
Depends on Docker or Podman, network/registry access, image-list file, and gzip. Pairs with `load-images.sh` for air-gapped Longhorn installations.

## Risks
Unquoted variables can break paths with spaces. Saving all images in one command can be memory/disk intensive. There is no digest pinning or verification. Blank/comment lines in the list are not ignored.

## Test Signals
Use a small image list and confirm pulls succeed, archive is readable by `docker load`/`podman load`, and platform-specific pulls produce expected architecture images.
