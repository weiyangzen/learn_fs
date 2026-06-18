# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/locate_led

Symlink to `ses`; behavior is selected by invoked basename `locate_led`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Reads the slot `locate` sysfs file.
- Prints `locate_led=<value>` or an empty value when unavailable.

Role:
- Exposes enclosure locate LED state for a vdev.
