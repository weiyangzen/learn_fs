<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h

Purpose: Declares the XFS POSIX ACL interface and provides no-op/null substitutes when POSIX ACL support is not compiled.

Important APIs: With `CONFIG_XFS_POSIX_ACL`, exports `xfs_get_acl`, `xfs_set_acl`, `__xfs_set_acl`, and `xfs_forget_acl`. Without it, `xfs_get_acl` and `xfs_set_acl` are `NULL`, `__xfs_set_acl` returns success, and `xfs_forget_acl` is empty.

Control flow and integration: VFS inode operation setup can assign these names directly while remaining configuration-neutral. Internal XFS code can call `__xfs_set_acl` without additional ifdefs.

State and persistence: The enabled implementation persists ACLs as xattrs; the disabled header path intentionally does not persist or cache ACL state.

Dependencies: Forward-declares inode and posix ACL types and relies on VFS ACL integration in the implementation.

Risks: Disabled builds silently succeed for internal `__xfs_set_acl` calls, so callers must rely on VFS feature gating to prevent unsupported user-visible ACL operations.

Test signals: Compile coverage for ACL enabled/disabled configurations and inode operation registration checks for NULL operation pointers when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_acl.h -->
