# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_compat.c

FreeBSD-specific libzfs compatibility glue. It supplies an `execvpe()` fallback for older FreeBSD, module initialization/error text, jail/unjail ioctl plumbing, next-boot bootloader command support, and kernel version retrieval.

Key interfaces:
- `libzfs_error_init()` builds FreeBSD-aware initialization errors, including module-load context.
- `libzfs_load_module()` checks `modfind("zfs")` and tries `kldload(ZFS_KMOD)`, where `ZFS_KMOD` is `zfs` in-base or `openzfs` out-of-base.
- `zfs_jail()` validates dataset type and sends `ZFS_IOC_JAIL` or `ZFS_IOC_UNJAIL`.
- `zpool_nextboot()` packages pool/device GUIDs plus command into an nvlist for `ZFS_IOC_NEXTBOOT`.
- `zfs_version_kernel()` reads `vfs.zfs.version.module` via `sysctlbyname()`.

Several Linux-style hooks are intentionally no-ops on FreeBSD: disk relabel/label helpers, `find_shares_object()`, and `zfs_destroy_snaps_nvl_os()`.
