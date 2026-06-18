# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_dquot.c

## Purpose
`xfs_trans_dquot.c` stages quota reservations and usage deltas inside transactions, applies them to in-core dquots at commit time, unwinds reservations on abort, and performs quota limit enforcement for user, group, and project quotas.

## Important APIs, types, and functions
Public functions include `xfs_trans_dqjoin`, `xfs_trans_log_dquot`, `xfs_trans_dup_dqinfo`, `xfs_trans_mod_dquot_byino`, `xfs_trans_mod_dquot`, `xfs_trans_apply_dquot_deltas`, `xfs_trans_unreserve_and_mod_dquots`, `xfs_trans_reserve_quota_bydquots`, `xfs_trans_reserve_quota_nblks`, `xfs_trans_reserve_quota_icreate`, `xfs_trans_free_dqinfo`, and `xfs_quota_reserve_blkres`. The central data structures are `struct xfs_dqtrx`, `struct xfs_dquot`, `struct xfs_trans`, and `struct xfs_quotainfo`.

## Control flow
Callers attach quota changes with `xfs_trans_mod_dquot` or the inode wrapper. Transaction commit locks affected dquots, joins their log items, applies block, realtime block, inode, and delayed-allocation deltas, adjusts default limits/timers, marks the dquot dirty, logs it, and releases any unused reservation. Transaction abort walks the same staged records and subtracts reservations without applying usage deltas. Reservation APIs enforce hard and soft limits, send quota netlink warnings, and unwind earlier user/group reservations if project quota reservation fails.

## State and persistence
`tp->t_dqinfo` is a transaction-scoped staging area. Dquot counters and reservation fields are in-core until the dquot log item is committed and written. Bigtime format can be enabled on non-root dquots at log time. Hook state exists only with `CONFIG_XFS_LIVE_HOOKS` and supports online fsck observation of quota updates.

## Dependencies and integration points
The file depends on quota core warning APIs, XFS dquot locking, quota defaults and timers, inode quota attachments, transaction item logging, health marking, and optional live hooks. It is used by allocation, inode creation, delayed allocation, chown, and realtime allocation paths.

## Risks and test signals
Risks include all-or-nothing reservation unwind, signed delta arithmetic, reservation-used math when allocations exceed reservation, lock ordering across multiple dquots, metadir/quota inode exclusions, soft-limit timer enforcement, and hook ordering. Test signals include user/group/project reservation failures at each stage, forced reservations, delayed allocation accounting, abort after partial reservation, live hook consumers, soft and hard limit warning delivery, and corruption detection when reserved drops below count.
