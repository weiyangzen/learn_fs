# sources/distributed-fs/ceph-client/fs/fuse/acl.c

## Purpose
`acl.c` maps VFS POSIX ACL operations to FUSE xattr requests while preserving compatibility with older daemons that did not advertise `FUSE_POSIX_ACL`.

## Important APIs, Types, and Functions
- `__fuse_get_acl()` fetches ACL xattrs and converts them with `posix_acl_from_xattr()`.
- `fuse_no_acl()` rejects ACL interaction for unsupported daemons outside the initial user namespace.
- `fuse_get_acl()` is the dentry operation path.
- `fuse_get_inode_acl()` is the inode permission-check path and returns `NULL` when the daemon did not opt into kernel ACL checks.
- `fuse_set_acl()` serializes/removes ACL xattrs and invalidates cached ACLs/attributes when appropriate.

## Control Flow
ACL reads reject RCU mode, bad inodes, disabled getxattr, and unsupported ACL types. They allocate one page, issue `fuse_getxattr()`, and map empty, `-ENODATA`, and supported `-EOPNOTSUPP` cases to no ACL. Set operations validate support, convert ACLs to xattr bytes, apply `FUSE_SETXATTR_ACL_KILL_SGID` when the kernel ACL feature is active and the caller lacks group/capability privileges, then call `fuse_setxattr()` or `fuse_removexattr()`.

## State and Persistence
ACL data is persisted by the userspace daemon through xattrs. Kernel-side cached ACLs and inode attributes are invalidated after successful set/remove only for `fc->posix_acl` daemons.

## Dependencies and Integration Points
This file depends on `fuse_i.h`, POSIX ACL helpers, POSIX ACL xattr names, FUSE xattr operations, mount idmaps, and user namespace conversion through `fc->user_ns`.

## Risks
Backwards compatibility is subtle: daemons without `FUSE_POSIX_ACL` may still expose ACL xattrs but rely on userspace permission checks. The one-page read buffer means oversized ACL xattrs return `-E2BIG`. RCU ACL lookup is not supported and returns `-ECHILD`, so callers must retry in ref-walk context.

## Test Signals
Test ACL get/set/remove for daemons with and without `FUSE_POSIX_ACL`, user namespaces/idmapped mounts, large ACL xattrs, setgid stripping behavior, bad inode handling, and xattr-disabled fallback.
