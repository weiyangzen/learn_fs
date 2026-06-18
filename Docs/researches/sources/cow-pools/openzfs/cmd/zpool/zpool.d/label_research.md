# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/label

Symlink to `lsblk`; behavior is selected by invoked basename `label`.

Behavior:
- Resolves block path from `VDEV_UPATH` or `VDEV_PATH`.
- Runs `lsblk -dl -n -o label <path>`.
- Trims leading/trailing whitespace.
- Prints `label=<filesystem label>`.

Role:
- Provides a filesystem label custom column for vdev block devices.
