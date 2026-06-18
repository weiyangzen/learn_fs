# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_file_os.c

POSIX file wrapper used by libzpool in place of kernel file/vnode APIs.

Key behavior:
- `zfs_file_open()` opens paths with `open64()`, adds `O_DIRECT` for block devices, supports creation with temporary `umask(0)`, and optionally opens a dump file under `vn_dumpdir`.
- `zfs_file_pwrite()` intentionally splits writes randomly on sector boundaries to let ztest simulate interrupted disk writes.
- `zfs_file_pread()` optionally mirrors reads into the dump fd.
- `zfs_file_getattr()` returns size and mode via `fstat64_blk()`.
- `zfs_file_deallocate()` punches holes with Linux `fallocate()` or FreeBSD `fspacectl()` when available.
- `zfs_file_get()` and `zfs_file_put()` abort because direct fd reference ownership is unsupported in userland.

On Linux, `EINVAL` from O_DIRECT pread/pwrite causes abort to expose alignment bugs.
