# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syscall.h

Purpose: `syscall.h` declares GlusterFS wrapper functions around POSIX filesystem, xattr, I/O, socket, and platform-specific system calls.

Important APIs and types: wrappers include stat/open/read/write/dirent, mkdir/link/symlink/rename/unlink/chmod/chown/truncate/time, readv/writev/pread/pwrite, statvfs, close/fsync/fdatasync, xattr list/get/set/remove on path/fd, access, fallocate, socket/accept, copy_file_range, kill, and FreeBSD sysctl. It also normalizes xattr prefixes and flags such as `GF_XATTR_CREATE` and `GF_XATTR_REPLACE`.

Control flow and state: no inline logic. Implementations likely centralize portability, retry behavior, logging, or namespace handling. `gf_add_prefix`/`gf_remove_prefix` allocate transformed xattr names.

Dependencies and integration: graph code uses `sys_stat`, `sys_unlink`, `sys_close`, and `sys_ftruncate`. Store and translator implementations can use wrappers for consistent platform behavior.

Risks: wrappers must preserve errno semantics exactly enough to look like syscalls. Platform differences for xattrs, `off64_t`, `copy_file_range`, and Darwin/BSD behavior are high risk. Prefix helpers have allocation ownership contracts not documented here.

Test signals: syscall-wrapper parity tests, errno preservation, xattr namespace behavior on Linux/Darwin/BSD, large-offset copy_file_range, partial read/write behavior, and FreeBSD type compatibility should be covered.
