# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/media

Shell helper for classifying vdev media type.

Behavior:
- `-h` prints help.
- If `VDEV_UPATH` is a block device, extracts its basename and reads `/sys/block/<device>/queue/rotational`.
- Maps rotational `0` to `ssd`, `1` to `hdd`, anything else to `invalid`.
- Checks `/sys/block/<device>/device/vpd_pg83` for `iqn.` and overrides media to `iscsi` if found.
- If `VDEV_UPATH` is a regular file, reports `file`.
- Prints `media=<file|hdd|ssd|iscsi|invalid>`.

Role:
- Provides a coarse vdev media-class custom column.
