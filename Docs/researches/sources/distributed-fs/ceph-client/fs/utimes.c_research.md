<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/utimes.c -->
# sources/distributed-fs/ceph-client/fs/utimes.c

Purpose: Implements VFS timestamp update helpers and the `utimensat`, `futimesat`, `utimes`, `utime`, and compat time32 syscall front ends.

Important APIs, types, and functions: Exports `vfs_utimes()`. Internal helpers include `nsec_valid()`, `do_utimes_path()`, `do_utimes_fd()`, `do_utimes()`, `do_futimesat()`, and `do_compat_futimesat()`, plus syscall definitions for native and `CONFIG_COMPAT_32BIT_TIME` variants.

Control flow: Syscalls copy and normalize userspace time structures, reject invalid nanosecond/usec fields, and short-circuit the double-`UTIME_OMIT` no-op before path lookup. `do_utimes()` dispatches to fd or path mode. Path mode resolves with `LOOKUP_FOLLOW` unless `AT_SYMLINK_NOFOLLOW` is set, retries stale dentries with `LOOKUP_REVAL`, then calls `vfs_utimes()`. `vfs_utimes()` obtains mount write access, builds `iattr` flags for touch, explicit set, `UTIME_NOW`, and `UTIME_OMIT`, calls `notify_change()` under the inode lock, and breaks delegations before retrying.

State and persistence: The only persistent effect is filesystem inode atime/mtime/ctime mutation through `notify_change()`. The helper deliberately sets `ATTR_TIMES_SET` for explicit calls even when both individual timestamps are omitted, preserving permission semantics.

Dependencies and integration points: Depends on VFS path lookup, file descriptor lookup, mount write accounting, idmapped mount handling via `mnt_idmap()`, inode locking, delegation breaking, user copy helpers, and architecture config symbols that select legacy syscalls.

Risks and test signals: Risks include permission regressions for `times == NULL` versus explicit times, invalid time truncation in legacy timeval paths, symlink and `AT_EMPTY_PATH` behavior, stale path retry mistakes, and delegation retry loops. Test no-op omit/omit, fd mode, path mode with and without symlink following, read-only mounts, delegated files, invalid nanoseconds/useconds, compat 32-bit times, and idmapped mount ownership checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/utimes.c -->
