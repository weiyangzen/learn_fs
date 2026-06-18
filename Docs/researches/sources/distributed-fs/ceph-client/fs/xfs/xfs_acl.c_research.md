<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c

Purpose: Implements XFS POSIX ACL get/set support by translating between Linux `struct posix_acl` and XFS root-namespace extended attributes (`SGI_ACL_FILE` and `SGI_ACL_DEFAULT`).

Important APIs and functions: `xfs_get_acl` loads an ACL xattr and converts it with `xfs_acl_from_disk`. `__xfs_set_acl` directly upserts or removes the ACL xattr and updates the inode ACL cache. `xfs_set_acl` is the VFS-facing setter that validates ACL size and updates file mode for access ACLs. `xfs_acl_set_mode` logs an inode core mode/ctime update. `xfs_forget_acl` invalidates cached ACLs when raw xattr paths bypass the ACL interface. Internal converters are `xfs_acl_from_disk` and `xfs_acl_to_disk`.

Control flow: Reads select the correct xattr name based on ACL type, call `xfs_attr_get`, convert big-endian disk entries to core tags/perms/uids/gids, and return NULL on `-ENOATTR` so the VFS can negative-cache. Writes reject default ACLs on nondirectories, serialize through the xattr change path, and only update cached ACLs after success. The public setter updates mode only after the ACL xattr succeeds to avoid changing mode when ENOSPC prevents ACL persistence.

State and persistence: ACLs persist as root namespace xattrs. Access ACL updates can also persist inode mode and ctime through a separate transaction. Cached ACL state in the VFS inode is synchronized after successful changes or explicitly forgotten after raw xattr mutation.

Dependencies and integration: Uses XFS attr APIs, transaction logging, inode locking expected by caller `i_mutex`, POSIX ACL helpers, idmapped mount mode update logic, XFS corruption reporting, and namespace constants from xattr headers.

Risks: Disk ACL corruption is detected through length/count/tag validation, but invalid uid/gid mappings are represented through init_user_ns conversions. Mode update happens after xattr update, so failure of the second transaction can leave an ACL change without the intended mode change. Raw xattr writers must call `xfs_forget_acl`.

Test signals: ACL round-trip tests, invalid disk ACL fuzzing, access ACL mode recalculation with idmapped mounts, default ACL rejection on nondirectories, ENOSPC during set, and cache invalidation through raw xattr paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.c -->
