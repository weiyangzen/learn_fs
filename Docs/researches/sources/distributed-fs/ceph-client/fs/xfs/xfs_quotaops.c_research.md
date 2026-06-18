# sources/distributed-fs/ceph-client/fs/xfs/xfs_quotaops.c

Purpose: Bridges Linux VFS `quotactl_ops` to XFS quota syscall helpers and maps generic quota ids, flags, state, limits, and timers into XFS quota types and flags.

Important APIs and functions: Exports `const struct quotactl_ops xfs_quotactl_operations`. `xfs_fs_get_quota_state` fills `qc_state`, per-type flags, quota inode numbers, quota file sizes/extents, default timers, and in-core dquot counts. `xfs_fs_set_info` updates default timers through id-zero setqlim. `xfs_quota_enable` and `xfs_quota_disable` translate generic FS quota flags to XFS flags. `xfs_fs_rm_xquota` truncates inactive quota files. `xfs_fs_get_dqblk`, `xfs_fs_get_nextdqblk`, and `xfs_fs_set_dqblk` wrap dquot report/update operations.

Control flow: VFS quotactl calls enter this table. Each mutating operation rejects read-only superblocks and requires active quota state where appropriate. Type conversion maps `USRQUOTA`, `GRPQUOTA`, and default/project to `XFS_DQTYPE_*`. State queries call `xfs_qm_fill_state` for all three types; absent quota inodes are reported as `NULLFSINO`, while errors other than `-ENOENT` propagate.

State and persistence: This file does not directly persist data; it reports state from `m_quotainfo`, quota inodes, and `m_qflags`, and delegates persistence to `xfs_qm_scall_*`. It converts ids through kernel quota namespace helpers and converts returned ids from get-next back into the current user namespace.

Dependencies and integration: Depends on VFS quota infrastructure, user namespace id conversion, quota manager syscall helpers, quota inode loading, and read-only checks. It is the user-visible quotactl integration point for XFS.

Risks and invariants: `xfs_quota_type` maps any non-user/non-group type to project quota, so callers must validate generic types before reaching unexpected values. `rm_xquota` requires quota to be off, while enable/disable require quota to be on. State reporting loads quota inodes each time and can surface metadata errors.

Test signals: Run generic quota ioctl/quotactl tests for state, set_info timer changes, enable/disable enforcement, get/set dqblk, get-next id conversion, read-only rejection, and rm_xquota behavior when quotas are active versus inactive.
