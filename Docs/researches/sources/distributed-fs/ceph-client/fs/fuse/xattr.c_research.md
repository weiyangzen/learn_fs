# sources/distributed-fs/ceph-client/fs/fuse/xattr.c

## Purpose
Implements FUSE extended attribute get, set, list, and remove operations plus the generic xattr handler table used by VFS.

## Important APIs, Types, And Functions
`fuse_setxattr()` sends `FUSE_SETXATTR`, including extended `setxattr_flags` when negotiated. `fuse_getxattr()` sends `FUSE_GETXATTR`, supporting size-query and value-fetch modes. `fuse_listxattr()` sends `FUSE_LISTXATTR`, validates returned name lists, and enforces permission/bad-inode checks. `fuse_removexattr()` sends `FUSE_REMOVEXATTR`. `fuse_verify_xattr_list()` validates NUL-separated xattr names. `fuse_xattr_get()` and `fuse_xattr_set()` implement `struct xattr_handler`; `fuse_xattr_handlers` registers a catch-all empty-prefix handler.

## Control Flow
Each operation checks cached `fc->no_*` capability flags, builds a FUSE request with inode nodeid and name/value args, and maps `-ENOSYS` to `-EOPNOTSUPP` while caching the unsupported operation. Get/list with size zero request only the returned size structure; nonzero calls allow variable-length output. Set/remove update inode ctime after success.

## State And Persistence
Unsupported-operation booleans in `struct fuse_conn` are updated after `ENOSYS`. Successful set/remove persist xattr changes through the userspace server and update local ctime state. List validation does not persist state.

## Dependencies And Integration Points
Depends on FUSE request helpers, Linux xattr and POSIX ACL xattr headers, inode state helpers, and VFS xattr handler dispatch.

## Risks
Malformed xattr list responses are treated as `EIO`. Server `ENOSYS` disables future attempts for the connection. Size-query paths clamp to `XATTR_SIZE_MAX` and `XATTR_LIST_MAX`, which callers should observe. Permission checks exist for listxattr but get/set wrappers rely on VFS and bad-inode checks.

## Test Signals
Exercise set/get/remove/list success, unsupported server fallback, size-only get/list, malformed list without NUL terminator, ctime updates, bad inode behavior, and extended setxattr flag negotiation.
