# File Research: sources/cow-pools/openzfs/lib/libzfs/os/freebsd/libzfs_zmount.c

FreeBSD implementation of Solaris-compatible mount helpers for libzfs. It uses FreeBSD `nmount(2)` and `unmount(2)`.

Key behavior:
- `build_iovec()` appends name/value pairs for `nmount()`.
- `do_mount()` builds iovecs for update/remount, readonly, `fstype=zfs`, `fspath`, `from`, and each parsed mount option, then calls `nmount()`.
- `do_unmount()` calls `unmount()` and converts failure to `errno`.
- `zfs_mount_setattr()` falls back to full remount because FreeBSD lacks Linux `mount_setattr(2)`.
- Delegation and pool/volume disable hooks are no-ops on this platform.

Option parsing is simple and platform-specific; mount options are split using `strsep(&optstr, ",/")`.
