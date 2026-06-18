# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/fault_led

Symlink to `ses`; behavior is selected by invoked basename `fault_led`.

Behavior:
- Reads `VDEV_ENC_SYSFS_PATH`.
- Checks slot `fault` first, then NVMe-style `attention`.
- Prints `fault_led=<value>` or an empty value if unsupported/unavailable.

Role:
- Exposes disk slot fault LED state as a custom column.
