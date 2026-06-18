# sources/distributed-fs/ceph-client/fs/xfs/xfs_quota.h

Purpose: Declares kernel-only quota macros, transaction quota delta structures, quota operation prototypes, and no-op stubs for builds without `CONFIG_XFS_QUOTA`.

Important APIs and types: `XFS_NOT_DQATTACHED` determines whether an inode lacks any active quota dquot references. `XFS_QM_NEED_QUOTACHECK` derives mount-time quotacheck need from active quota types and checked superblock flags. `struct xfs_dqtrx` accumulates per-transaction reservations and deltas for data blocks, realtime blocks, delayed blocks, and inode counts. `struct xfs_apply_dqtrx_params` and `struct xfs_mod_ino_dqtrx_params` describe live-hook notification payloads. The header exposes transaction reservation/application functions and vnode quota helpers.

Control flow and integration: Transaction code reserves quota through `xfs_trans_reserve_quota_*`, accumulates changes with `xfs_trans_mod_dquot_byino` or live-hook-aware `xfs_trans_mod_ino_dquot`, and applies or unreserves changes during commit/cancel. Inode operations call dqalloc, create attach, rename attach, chown, attach/detach, and enforcement-near checks via this interface. Mount code uses newmount/resume/mount/unmount prototypes.

State and persistence: The header defines in-memory transaction accumulation; persistence occurs when dquot log items are joined/logged elsewhere. Deltas distinguish reserved versus used quota so delayed allocation and realtime reservations can be accounted correctly.

Dependencies and integration points: Integrates with `xfs_dquot`, `xfs_trans`, inode code, VFS quota operations, live hooks, and build configuration. Without quota support, most functions compile to no-ops or successful stubs while `xfs_rtmount_init`-style callers still get predictable behavior.

Risks and invariants: `XFS_NOT_DQATTACHED` is intentionally used without inode locks in some contexts and relies on inode references plus atomic ownership updates to be harmless. Stub behavior in nonquota builds must preserve call-site assumptions by nulling dquot outputs and returning success. The transaction dquot arrays assume no transaction affects more than `XFS_QM_TRANS_MAXDQS` dquots per type.

Test signals: Compile both quota and nonquota configurations, run delayed allocation quota reservation/rollback tests, verify quotacheck flag detection per quota type, exercise live hook enable/disable if configured, and check callers tolerate no-op stubs.
