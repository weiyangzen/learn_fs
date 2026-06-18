# sources/distributed-fs/ceph-client/fs/xfs/xfs_xattr.c

## Purpose
`xfs_xattr.c` adapts XFS attribute fork operations to the Linux VFS xattr API, including get/set/list handlers, namespace prefix translation, ACL name translation, quota attachment, and optional debug-only logged xattr assistance.

## Important APIs, types, and functions
The key exported symbols are `xfs_attr_change`, `xfs_xattr_handlers`, and `xfs_vn_listxattr`. Internal helpers include `xfs_attr_grab_log_assist`, `xfs_attr_want_log_assist`, `xfs_xattr_get`, `xfs_xattr_flags_to_op`, `xfs_xattr_set`, `xfs_xattr_put_listent`, and `__xfs_xattr_put_listent`. VFS handlers cover user, trusted/root, and security namespaces.

## Control flow
Get builds `xfs_da_args` from the VFS handler and calls `xfs_attr_get`. Set/remove attaches quota state, allows missing-name removal, optionally enables log-assisted xattrs in debug LARP mode, fills attr geometry/fork/owner/hash, and calls `xfs_attr_set` with reserve-pool permission for root/security attributes. List walks XFS attributes and emits VFS-prefixed names, hiding private namespaces and trusted names from callers without `CAP_SYS_ADMIN`, while translating legacy SGI ACL names to `system.posix_acl_*`.

## State and persistence
Persistent state lives in the inode attr fork and, when debug LARP is enabled, in the superblock log-incompat feature bit `XFS_SB_FEAT_INCOMPAT_LOG_XATTRS`. Runtime state is limited to list contexts, op flags, and quota attachments.

## Dependencies and integration points
It depends on XFS attr code, directory-attribute args, ACL handling, quota attachment, log feature updates, VFS xattr handlers, capabilities, and POSIX ACL xattr names.

## Risks and test signals
Risks include namespace filtering leaks, ACL name translation mistakes, using reserve blocks too broadly or too narrowly, attr fork zap handling, log-incompat enablement on unsupported filesystems, and list buffer sizing. Test signals include all xattr namespaces, ACL get/list behavior, unprivileged trusted listing, create/replace/remove flags, ENOSPC with security attrs, shutdown handling, and debug logged-xattr mode.
