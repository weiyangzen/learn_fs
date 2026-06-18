# sources/distributed-fs/glusterfs/libglusterfs/src/syscall.c

## Purpose

`syscall.c` wraps platform filesystem and socket syscalls behind Gluster-normalized `sys_*` helpers. It checks impossible return values, adapts OS differences for xattrs, openat-style operations, sync calls, fallocate, accept flags, and copy-file-range, and provides xattr namespace prefix helpers.

## Important APIs, Types, and Functions

The file exports wrappers for stat/lstat/fstat/fstatat, open/openat/opendir/readdir/closedir, mkdir/mknod/unlink/rmdir/symlink/rename/link/chmod/chown/truncate/utimes, read/write vector and positional I/O, lseek, statvfs, close, fsync/fdatasync, l/f xattr operations, access, fallocate, socket, accept, copy-file-range, and FreeBSD-only kill/sysctl. Internal macros `FS_RET_CHECK`, `FS_RET_CHECK0`, and `FS_RET_CHECK_ERRNO` normalize invalid syscall return values and set `errno = EIO`.

## Control Flow and Data Flow

Each wrapper delegates to the platform syscall or emulation path, then normalizes returns. Path operations on Darwin emulate `*at()` with `fchdir()` in the observed code. FreeBSD fixes `statvfs` block-size semantics and manually applies sticky bits after `openat(O_CREAT)`. `sys_readdir()` uses plain `readdir()` on glibc and `readdir_r()` elsewhere. Xattr wrappers select Linux/NetBSD, BSD `extattr`, Solaris compatibility, or Darwin signatures. `sys_accept()` prefers `accept4()` or `paccept()` with `SOCK_CLOEXEC`, otherwise sets flags and close-on-exec after accept and closes the accepted socket on setup failure.

`gf_add_prefix()` and `gf_remove_prefix()` allocate transformed xattr names when a namespace prefix must be added or stripped. `sys_copy_file_range()` tries libc `copy_file_range()`, a raw syscall fallback, or `ENOSYS`.

## State and Persistence Behavior

The wrapper layer does not own durable state, but the underlying operations mutate filesystem metadata, file contents, xattrs, sockets, and directory state. The main persistent behavior is controlled by callers. Return normalization logs critical messages for impossible values and makes callers see standard `-1` plus `errno`.

## Dependencies and Integration Points

The file depends on platform compatibility headers, Gluster syscall declarations, mem-pool allocation, logging, xattr namespace constants, Solaris/BSD/Darwin compatibility helpers, and libc/syscall facilities. It is a broad dependency for storage translators, management store code, statedump publishing, and any code that needs portable filesystem behavior.

## Risks and Edge Cases

Darwin `fchdir()` emulation does not restore the previous cwd in this file, which is dangerous in multithreaded contexts if compiled that way. Some platform-specific wrappers have no final fallback return outside known OS branches, so compile-time coverage matters. `gf_remove_prefix()` allocation uses arithmetic around namespace length and string length that needs boundary tests. `sys_close(-1)` normalizes to `-1`, so callers must avoid closing sentinel values when errors matter. `sys_copy_file_range()` raw syscall fallback bypasses `FS_RET_CHECK` in the observed code path.

## Test Signals

Tests should cover normal and failing syscalls, impossible-return fault injection, xattr namespace add/remove, close-on-exec socket/accept behavior, FreeBSD/Darwin/Solaris conditional builds, `statvfs` block-size adjustment, fallocate fallback semantics, copy-file-range `ENOSYS`, and fd cleanup after failed accept flag setup.
