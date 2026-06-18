# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/upath

Minimal shell helper for reporting the resolved underlying vdev path.

Behavior:
- `-h` prints help.
- Prints `upath="$VDEV_UPATH"` exactly as supplied by the zpool custom-column environment.

Role:
- Exposes the underlying path selected by ZFS for a vdev.
