# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_file_os.c

## Purpose

Provides the FreeBSD implementation of OpenZFS’s platform-neutral `zfs_file_*` abstraction. It adapts kernel `struct file`, vnode operations, `uio`, and FreeBSD file APIs to the interfaces used by common ZFS code.

## Open and Close

- `zfs_file_open(const char *path, int flags, int mode, zfs_file_t **fpp)`
  - Ensures process working directories are available via `pwd_ensure_dirs()`.
  - Rejects unsupported `O_EXEC` and `O_PATH`.
  - Converts POSIX-style flags to FreeBSD file flags with `FFLAGS()`.
  - Allocates a file with `falloc_noinstall()`.
  - Uses `NDINIT()` and `vn_open()` for kernel pathname open.
  - Initializes vnode file ops with `finit_vnode()` if needed.
  - Rejects non-regular files with `EACCES`.
  - Applies `O_TRUNC` via `fo_truncate()`.
- `zfs_file_close(zfs_file_t *fp)`
  - Drops the file reference with `fdrop()`.

## Read/Write

- `zfs_file_write_impl()`
  - Builds a single-segment kernel `uio` with `UIO_SYSSPACE`.
  - Requires `FWRITE`.
  - Calls `bwillwrite()` for vnode-backed files.
  - Writes through `fo_write(..., FOF_OFFSET, ...)`.
  - Updates the supplied offset by bytes actually written.
  - If no residual pointer is supplied, short writes become `EIO`.
- `zfs_file_write()`
  - Writes at `fp->f_offset` and advances `fp->f_offset` on success.
- `zfs_file_pwrite()`
  - Positional write; ignores `ashift` on FreeBSD.
- `zfs_file_read_impl()`
  - Builds a kernel `uio`, requires `FREAD`, reads through `fo_read()`, reports residual when requested, and advances the supplied offset.
- `zfs_file_read()`
  - Reads at and advances `fp->f_offset`.
- `zfs_file_pread()`
  - Positional read without changing `fp->f_offset`.

## Seek, Stat, Sync, Space Control

- `zfs_file_seek()`
  - Verifies the file ops are seekable via `DFLAG_SEEKABLE`.
  - Calls `fo_seek()` and copies the resulting offset from `td->td_uretoff.tdu_off`.
- `zfs_file_getattr()`
  - Calls `fo_stat()` with FreeBSD-version-specific signature.
  - Exposes size and mode through `zfs_file_attr_t`.
- `zfs_vop_fsync()`
  - Starts a write section, locks the vnode exclusively, calls `VOP_FSYNC(MNT_WAIT)`, unlocks, and finishes the write section.
- `zfs_file_fsync()`
  - Requires `DTYPE_VNODE`; then delegates to `zfs_vop_fsync()`.
- `zfs_file_deallocate()`
  - On newer FreeBSD, uses `fo_fspacectl(..., SPACECTL_DEALLOC, ...)`.
  - Returns `EOPNOTSUPP` on older FreeBSD.

## File Descriptor Helpers

- `zfs_file_get(int fd)`
  - Acquires a `struct file *` from a descriptor with `fget()` and `cap_no_rights`.
- `zfs_file_put(zfs_file_t *fp)`
  - Releases through `zfs_file_close()`.
- `zfs_file_off(zfs_file_t *fp)`
  - Returns `fp->f_offset`.
- `zfs_file_private(zfs_file_t *fp)`
  - Temporarily sets `curthread->td_fpop` to call `devfs_get_cdevpriv()`.
  - Restores the prior `td_fpop`.
- `zfs_file_unlink(const char *fnamep)`
  - Calls `kern_funlinkat()` with `AT_FDCWD`, `FD_NONE`, and `UIO_SYSSPACE`.

## Compatibility Notes

- Contains FreeBSD version conditionals for:
  - `NDINIT()` signature.
  - `fo_stat()` signature.
  - `vn_start_write()` flags.
  - `fo_fspacectl()` availability.
- All public functions return FreeBSD errno-style values wrapped with `SET_ERROR()` where applicable.

## Key Risks and Edge Cases

- `zfs_file_open()` closes the file if the target is not a regular vnode.
- Short write behavior depends on whether caller requests residual reporting.
- `zfs_file_private()` relies on temporarily mutating thread file-operation context; it restores it immediately after `devfs_get_cdevpriv()`.
