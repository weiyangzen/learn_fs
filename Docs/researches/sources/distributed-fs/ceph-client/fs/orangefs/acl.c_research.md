## sources/distributed-fs/ceph-client/fs/orangefs/acl.c

### Purpose
This file implements OrangeFS POSIX ACL support using extended attributes as the backing store.

### Important APIs, types, and functions
- `orangefs_get_acl()` maps ACL type to `system.posix_acl_access` or `system.posix_acl_default`, fetches the xattr, and converts it with `posix_acl_from_xattr()`.
- `__orangefs_set_acl()` serializes a `struct posix_acl` with `posix_acl_to_xattr()` and calls `orangefs_inode_setxattr()`.
- `orangefs_set_acl()` updates file mode through `posix_acl_update_mode()`, writes the ACL xattr, and applies mode changes through `__orangefs_setattr_mode()`.

### Control flow
Read rejects RCU mode with `-ECHILD`, allocates a maximum-size xattr buffer to avoid a probe round trip, fetches the ACL xattr, maps missing ACLs to `NULL`, and returns conversion errors as `ERR_PTR`. Write validates the ACL type, optionally converts the ACL to an xattr blob, stores or removes the xattr, updates the cached ACL, and for access ACLs applies any mode change calculated by the POSIX ACL helper.

### State and persistence behavior
ACLs persist as OrangeFS xattrs. The VFS ACL cache is updated with `set_cached_acl()` after successful writes. Mode changes are propagated to the server through OrangeFS setattr rather than being purely local.

### Dependencies and integration points
Depends on `orangefs_inode_getxattr()`, `orangefs_inode_setxattr()`, POSIX ACL helpers, `init_user_ns`, and the OrangeFS inode operations in `inode.c` and `namei.c` that expose `.get_inode_acl` and `.set_acl`.

### Risks
Allocating `ORANGEFS_MAX_XATTR_VALUELEN` for each get avoids one network call but can be expensive. ACL and mode updates are multi-step and can partially fail after xattr success or before mode propagation. RCU permission paths must fall back because ACL reads may block on network I/O.

### Test signals
Run ACL xfstests for getfacl/setfacl, default ACL inheritance on create and mkdir, chmod interactions, ACL removal, missing ACL behavior, and daemon unavailable errors.
