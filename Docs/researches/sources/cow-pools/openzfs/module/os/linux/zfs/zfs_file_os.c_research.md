# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_file_os.c

## Purpose

Linux kernel implementation of the portable `zfs_file_*` abstraction used by OpenZFS code that needs file operations from kernel context.

## File Lifecycle And References

- `zfs_file_open()` maps ZFS open requests to `filp_open()`. For non-create write-only opens it adds `O_EXCL`; for create it temporarily clears current umask so the requested mode is honored.
- `zfs_file_close()` calls `filp_close()`.
- `zfs_file_get()` obtains a `struct file *` from a file descriptor using `fget()`.
- `zfs_file_put()` releases it using `fput()`.
- `zfs_file_private()` returns `fp->private_data`.

## I/O Helpers

- `zfs_file_write()` and `zfs_file_read()` are stateful operations using and updating `fp->f_pos`.
- `zfs_file_pwrite()` and `zfs_file_pread()` perform positioned I/O without changing `fp->f_pos`.
- All read/write helpers return positive errno values, optionally report residual bytes, and treat short I/O without a residual pointer as `EIO`.
- `zfs_file_seek()` wraps `vfs_llseek()`, rejecting negative input offsets and returning `ESPIPE`-style errors from the kernel as positive errno.

## Attributes, Sync, And Allocation

- `zfs_file_getattr()` calls `vfs_getattr()` and returns size and mode in `zfs_file_attr_t`.
- `zfs_file_fsync()` maps `O_DSYNC` into the datasync flag for `vfs_fsync()`.
- `zfs_file_deallocate()` uses the file operation `fallocate()` with `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE` when available; otherwise it returns `EOPNOTSUPP`.
- `zfs_file_off()` returns the current file offset.
- `zfs_file_unlink()` is optional and intentionally unsupported on Linux, returning `EOPNOTSUPP`.
