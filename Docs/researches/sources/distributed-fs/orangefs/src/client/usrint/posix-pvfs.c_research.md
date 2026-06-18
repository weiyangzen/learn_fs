# sources/distributed-fs/orangefs/src/client/usrint/posix-pvfs.c

## Purpose
`posix-pvfs.c` implements the PVFS side of the `posix_ops` dispatch table. It translates POSIX-like operations into OrangeFS/PVFS client calls, mostly through `iocommon_*`, while preserving user-space descriptor state such as file offsets, duplicate semantics, umask, cwd, and fallback behavior when a symlink resolves out of PVFS.

## Important APIs, Types, and Functions
The file exports helper APIs `pvfs_valid_path`, `pvfs_valid_fd`, `pvfs_layout`, `pvfs_layout_fd`, `pvfs_layout_string`, and `pvfs_release_layout`. It implements open/create/delete/rename, I/O, seek/truncate/sync, stat and statfs families, time/owner/mode mutations, directory and symlink operations, xattrs and atomic xattrs, cwd and umask helpers, SELinux stubs, and the `posix_ops pvfs_ops` initializer.

`mask_val` stores the PVFS-layer umask. `PVFS_ATTR_DEFAULT_MASK` is duplicated locally. Layout helpers build `PVFS_sys_layout` structures from a path or fd and an ASCII server list, using `iocommon_parse_serverlist` and `BMI_addr_rev_lookup`.

## Control Flow
Path-based operations usually qualify or expand the path with `PVFS_qualify_path` or `PVFS_expand_path`, then call `iocommon_open` to obtain a descriptor or call an iocommon metadata function directly. If an opened object resolves to `glibc_ops`, several operations fall back to glibc f* calls on `pd->true_fd`. Relative `*at` operations validate the directory descriptor with `pvfs_find_descriptor` and pass `pd->s->pvfs_ref` as a parent reference.

I/O operations look up the descriptor, validate access mode against `O_ACCMODE`, wrap scalar buffers as an iovec when needed, and call `iocommon_readorwrite`. Sequential read/write and vector I/O update `pd->s->file_pointer`; append writes stat the file first and write at current size. `pvfs_lseek64` delegates pointer update to `iocommon_lseek`. `pvfs_dup`, `pvfs_dup2`, `pvfs_dup3`, and `pvfs_fcntl(F_DUPFD)` all use `pvfs_dup_descriptor`.

Metadata calls often open the target read-only, call `iocommon_stat`, `iocommon_chown`, `iocommon_chmod`, `iocommon_setattr`, `iocommon_statfs`, or xattr helpers, then close the temporary descriptor. `pvfs_close` frees descriptor state and optionally applies `clrflags` mode cleanup. `pvfs_sync` is a no-op; `pvfs_fsync` calls `iocommon_fsync` for PVFS descriptors and skips glibc fallback descriptors. SELinux label calls uniformly return `ENOTSUP`.

## State and Persistence Behavior
Per-open state is in `pvfs_descriptor_status`: file pointer, flags, mode, directory token, dpath, PVFS object reference, and optional cache entry. Persistent filesystem state changes are made through iocommon calls to PVFS servers: creates, unlinks, renames, truncates, setattr for times/ownership/mode, xattrs, directory creation, symlink creation, and fsync. The PVFS cwd is stored in the shared descriptor control area.

## Dependencies and Integration Points
The implementation depends on `posix-ops.h`, `posix-pvfs.h`, `openfile-util.h`, `iocommon.h`, `pvfs-path.h`, and BMI. It is called by `posix.c` through `pvfs_ops` and directly via `posix-pvfs.h`. It uses `glibc_ops` for fallback and server address helpers for layout construction.

## Risks and Edge Cases
Several operations return approximate semantics: `pvfs_fallocate` truncates to `offset + length`, `pvfs_fdatasync` is fsync, `pvfs_sync` does nothing, nanosecond timestamps are truncated, fadvise does nothing, hard links and flock are `ENOSYS`, and SELinux labels are `ENOTSUP`. `pvfs_mknodat` switches on `dev` rather than file-type bits in `mode`. `pvfs_futimes` closes the fd it was asked to update. The `pvfs_ops` table maps `statfs` and `statvfs` to interposed symbols instead of `pvfs_statfs`/`pvfs_statvfs`, which should be tested for recursion or dispatch surprises.

## Test Signals
Tests should cover PVFS open/openat, O_CREAT mode and hints, symlink-to-glibc fallback, sequential and positioned I/O offsets, O_APPEND, readv/writev updates, lseek, truncate/ftruncate/fallocate, close without unwanted fsync, stat/lstat/fstatat, futimes/futimens fd preservation, chmod/chown nofollow handling, mkdir/rmdir/unlinkat flags, readlink/symlink, unimplemented link/flock errors, xattrs, statfs/statvfs dispatch, cwd helpers, umask, and the `pvfs_ops` table.
