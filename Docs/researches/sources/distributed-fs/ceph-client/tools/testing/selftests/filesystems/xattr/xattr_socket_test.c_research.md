<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c

## Purpose
This kselftest verifies path-based extended attribute operations on filesystem-backed Unix domain socket nodes in `/tmp` for `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_SEQPACKET`.

## Important APIs, Types, And Functions
The `xattr_socket` fixture creates a bound `AF_UNIX` socket path per socket type. Tests cover `setxattr()`, `getxattr()`, `listxattr()`, `removexattr()`, `lsetxattr()`, `lgetxattr()`, `XATTR_CREATE`, `XATTR_REPLACE`, empty values, size probes, small buffers, nonexistent names, multiple names, and a 4096-byte value. A second `xattr_socket_trusted` fixture checks `trusted.*` behavior with `CAP_SYS_ADMIN` handling.

## Control Flow
Each fixture setup unlinks a unique `/tmp/xattr_socket_test_<type>.<pid>` path, creates the requested Unix socket, binds it, and tears it down by closing and unlinking. Tests then operate on the pathname rather than the socket fd, proving the socket inode's filesystem xattr hooks work.

## State And Persistence
The socket path and xattrs are temporary filesystem state. The persistence test closes the socket fd and confirms the xattr remains available through the path until the node is unlinked. Trusted xattrs may persist only when the caller has the required capability and filesystem support.

## Dependencies And Integration Points
The file depends on Unix domain sockets, the underlying `/tmp` filesystem's socket inode support, VFS xattr syscalls, and `kselftest_harness.h`.

## Risks
`/tmp` may be mounted on a filesystem without the expected socket xattr support, causing environment-specific failures. `trusted.*` results depend on privilege and are skipped/accepted carefully for `EPERM`. Path length and stale socket cleanup are handled but still depend on `/tmp` accessibility.

## Test Signals
Expected pass signals are correct byte counts and values, `ENODATA` after removal/nonexistent lookup, `EEXIST` for create-on-existing, `ERANGE` for too-small buffers, and trusted xattr skip when `CAP_SYS_ADMIN` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/xattr/xattr_socket_test.c -->
