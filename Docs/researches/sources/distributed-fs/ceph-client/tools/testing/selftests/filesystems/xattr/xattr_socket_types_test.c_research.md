<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c

## Purpose
This test verifies fd-based `user.*` xattrs on sockfs sockets across multiple address families and an abstract Unix socket.

## Important APIs, Types, And Functions
The `xattr_socket_types` fixture variants create `AF_INET`, `AF_INET6`, `AF_NETLINK`, and `AF_PACKET` sockets. The main test uses `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and `fremovexattr()`. The `xattr_abstract` fixture binds an abstract `AF_UNIX` socket and tests fd-based set/get.

## Control Flow
Setup creates the socket for each family and skips unsupported or permission-blocked socket types on `EAFNOSUPPORT`, `EPERM`, or `EACCES`. The test writes a `user.testattr`, verifies retrieval and list membership, removes it, and verifies `ENODATA`.

## State And Persistence
Xattrs are per sockfs inode and exist only while the socket fd and inode live. Abstract Unix sockets have no pathname, so all access is through the fd.

## Dependencies And Integration Points
It integrates with sockfs, networking socket families, Linux netlink headers, AF_PACKET permission behavior, VFS fd xattr syscalls, and kselftest fixture variants.

## Risks
AF_PACKET and netlink availability vary by kernel config and privileges. The test assumes sockfs supports `user.*` xattrs uniformly; regressions may show as set/list/remove failures on only some families.

## Test Signals
Pass signals are successful set/get/list/remove on each available socket family and `futex`-style skip reporting for unavailable families, with `ENODATA` after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_types_test.c -->
