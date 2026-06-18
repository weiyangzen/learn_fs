# sources/distributed-fs/ceph-client/fs/stat.c

## Purpose

`stat.c` implements VFS attribute retrieval and the user-facing stat/readlink/statx syscall family, including old/new/64-bit/compat ABI conversions and inode block-byte accounting helpers.

## Important APIs, Types, and Functions

Important exported helpers are `fill_mg_cmtime()`, `generic_fillattr()`, `generic_fill_statx_attr()`, `generic_fill_statx_atomic_writes()`, `vfs_getattr_nosec()`, `vfs_getattr()`, `vfs_fstat()`, inode byte accounting helpers, and syscall entry points for stat variants and `statx`. Internal helpers include `statx_lookup_flags()`, `vfs_statx_path()`, `vfs_statx_fd()`, `vfs_statx()`, ABI copy helpers (`cp_old_stat`, `cp_new_stat`, `cp_new_stat64`, `cp_statx`, compat copies), and `do_readlinkat()`.

## Control Flow

Attribute queries resolve a path or fd, call security hooks when appropriate, then dispatch to filesystem `getattr` or `generic_fillattr()`. `vfs_statx_path()` augments results with mount id and mount-root attribute. Syscalls convert `struct kstat` into the requested user ABI while checking overflow. `readlinkat` resolves the path without following symlinks, checks security, touches atime, and calls `vfs_readlink()`. Inode byte helpers update `i_blocks`/`i_bytes` with or without caller-held locks.

## State and Persistence Behavior

Most functions return snapshots of inode/mount state. `fill_mg_cmtime()` can set the queried bit in multigrain ctime state. `touch_atime()` may update atime. Inode byte accounting functions mutate inode block accounting. No file-private persistent state is owned by this module.

## Dependencies and Integration Points

This file is central VFS infrastructure and integrates with path lookup, mount id handling, security hooks, idmapped mounts, block device statx, filesystem `getattr`, user copy APIs, compat syscall wiring, and timestamp tracing.

## Risks and Edge Cases

ABI overflow checks are critical for old and 32-bit layouts. `AT_EMPTY_PATH`, automount/no-follow flags, statx reserved masks, sync flag validation, idmapped uid/gid conversion, multigrain timestamp queried bits, and stale NFS retry behavior are all sensitive. User copy errors must return `-EFAULT`.

## Test Signals

LTP stat/readlink/statx suites, compat syscall tests, idmapped mount stat tests, automount/symlink/no-follow cases, large inode/file/device number overflow tests, multigrain timestamp tracing, and inode byte accounting tests under concurrent updates.
