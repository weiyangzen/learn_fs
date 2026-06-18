# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/dm-deps

Shell helper for device-mapper dependency reporting.

Behavior:
- `-h` prints help.
- Reads `VDEV_PATH`.
- If the vdev path is a symlink, resolves it with `readlink`.
- Uses the basename as a block device name.
- If `/sys/class/block/<dev>/slaves` exists, lists slave devices in one space-normalized line.
- Always prints `dm-deps=<value>`.

Role:
- Maps a dm/multipath vdev back to underlying block devices for `zpool status -c dm-deps`.
