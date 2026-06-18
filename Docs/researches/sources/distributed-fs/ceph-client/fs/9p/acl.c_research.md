<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.c -->
# sources/distributed-fs/ceph-client/fs/9p/acl.c

## Purpose
`acl.c` implements POSIX ACL support for 9p, translating Linux ACL operations to 9P2000.L extended attributes and maintaining cached ACLs when client-side access checks are enabled.

## Important APIs, types, and functions
Important functions are `v9fs_get_acl`, `v9fs_iop_get_inode_acl`, `v9fs_iop_get_acl`, `v9fs_iop_set_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_acl_mode`, and `v9fs_put_acl`. Helpers include `v9fs_fid_get_acl`, `v9fs_acl_get`, `__v9fs_get_acl`, and `v9fs_set_acl`.

## Control flow
ACL reads fetch `system.posix_acl_*` xattrs via a fid, decode them with `posix_acl_from_xattr`, and cache results on inode creation. ACL sets validate and encode ACLs, possibly update mode bits, issue xattr writes, and update cached ACL state. Creation helpers derive inherited ACLs from the parent and apply them after remote object creation.

## State and persistence
Kernel state is the inode ACL cache. Persistent ACL values live on the 9p server as xattrs.

## Dependencies and integration points
It depends on xattr helpers, fid lookup, POSIX ACL library, `v9fs_vfs_setattr_dotl`, and 9P2000.L access mode semantics.

## Risks and test signals
Risks include stale cached ACLs, server-side xattr failures, access=client behavior differences, mode/ACL update ordering, and symlink/default ACL edge cases. Test signals include get/set ACL, chmod with ACLs, inherited default ACLs, access modes, and servers without ACL xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/acl.c -->
