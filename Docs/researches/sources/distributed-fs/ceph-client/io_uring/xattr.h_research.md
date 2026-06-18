# sources/distributed-fs/ceph-client/io_uring/xattr.h

Purpose: declares xattr prep, issue, and cleanup hooks for io_uring opcode dispatch.

Important APIs/types/functions: `io_xattr_cleanup()`, prep/issue pairs for `fsetxattr`, `setxattr`, `fgetxattr`, and `getxattr`.

Control flow: none.

State and persistence: no state defined; cleanup declaration indicates requests may own imported names/values and delayed paths.

Dependencies/integration: consumed by opdef dispatch and cleanup paths.

Risks/test signals: compile coverage and xattr cancellation/fault tests validate the API.
