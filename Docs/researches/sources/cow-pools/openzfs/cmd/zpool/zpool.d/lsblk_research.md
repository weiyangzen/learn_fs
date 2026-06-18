# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/lsblk

Shell helper for common `lsblk`-derived vdev properties.

Behavior:
- `-h` prints basename-specific help.
- If invoked as `lsblk`, reports `size`, `vendor`, and `model`.
- If invoked via another lowercase symlink, uses the basename as an `lsblk --output` column.
- Uses `VDEV_UPATH` when it is a block device, otherwise `VDEV_PATH`.
- Special-cases file vdev size using `du -h --apparent-size`.
- Runs `lsblk -dl -n -o <column> <path>`, trims whitespace, and prints `<column>=<value>`.

Role:
- Provides simple block-device metadata columns for `zpool status -c`.
