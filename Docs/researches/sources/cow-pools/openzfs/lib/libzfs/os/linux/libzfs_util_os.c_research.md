# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_util_os.c

Linux libzfs utility glue. It provides initialization diagnostics, module autoload/wait logic, `.zfs/shares` inode discovery for diffs, kernel version reading, and user-namespace attach/detach support.

Key interfaces:
- `libzfs_error_init()` maps initialization errno values to actionable Linux messages.
- `libzfs_load_module()` tries `modprobe zfs`, checks sysfs, and waits for `/dev/zfs` via inotify and timerfd. `ZFS_MODULE_TIMEOUT` controls the wait, and containers default to zero wait.
- `find_shares_object()` stats `<mountpoint>/.zfs/shares/` and records its inode for `zfs diff`.
- `zfs_version_kernel()` reads `ZFS_SYSFS_DIR/version`.
- `zfs_userns()` validates the handle is a filesystem, opens a namespace path, and sends `ZFS_IOC_USERNS_ATTACH` or `ZFS_IOC_USERNS_DETACH`.

Snapshot-destroy OS hook is a no-op on Linux.
