<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c

## Purpose
This test validates `user.*` extended attributes on anonymous sockfs socket inodes and checks sockfs-specific per-inode limits.

## Important APIs, Types, And Functions
The `xattr_sockfs` fixture creates an unbound `AF_UNIX` stream socket. Tests use `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and `fremovexattr()`. Constants `SIMPLE_XATTR_MAX_NR` and `SIMPLE_XATTR_MAX_SIZE` model sockfs limits, with `XATTR_SIZE_MAX` fallback for older headers.

## Control Flow
Tests cover basic set/get/list/remove/update, create/replace flags, nonexistent names, empty values, size probes, small buffers, maximum xattr count, maximum total value size, freeing limit space after removal, and independence between two socket inodes.

## State And Persistence
All state is in-memory sockfs inode state tied to socket fd lifetimes. The per-inode tests prove values and limits are isolated between two sockets.

## Dependencies And Integration Points
The file depends on sockfs simple xattr support, VFS fd xattr syscalls, kernel xattr limit definitions, and `kselftest_harness.h`.

## Risks
The test encodes expected 128-name and 128 KiB total value limits; kernel changes to `simple_xattrs` accounting require test updates. Large allocations and limit tests can expose off-by-one or cleanup bugs.

## Test Signals
Expected results include `system.sockprotoname` in lists, `ENOSPC` at the 129th xattr and beyond 128 KiB total values, `ERANGE` on undersized reads, and independent values on separate sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_sockfs_test.c -->
