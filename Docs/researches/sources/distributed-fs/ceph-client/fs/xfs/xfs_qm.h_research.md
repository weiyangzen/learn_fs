# sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.h

Purpose: Defines the quota manager's in-core data structures, default limit containers, transaction dquot accounting layout, and function prototypes shared by quota manager implementation, syscall wrappers, and transaction code.

Important APIs and types: `struct xfs_quotainfo` is the central per-mount quota state, containing user/group/project dquot radix trees, quota inode pointers, optional quota directory inode, dquot LRU, quotaoff mutex, dquot chunk geometry, default quota limits, shrinker, expiry range, and live hook lists. `struct xfs_quota_limits` and `struct xfs_def_quota` model default hard/soft/time values for block, inode, and realtime block resources. `struct xfs_dquot_acct` stores transaction dquot deltas across user/group/project classes and up to `XFS_QM_TRANS_MAXDQS` entries each. Inline helpers `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` route by `xfs_dqtype_t`.

Control flow and integration: This header is included by quota manager, quota syscall, quotactl, and transaction accounting paths. The exported syscall prototypes (`xfs_qm_scall_*`) are implemented in `xfs_qm_syscalls.c` and surfaced through `xfs_quotaops.c`. The transaction prototypes connect to dquot log item handling and commit-time quota delta application. `xfs_qm_qino_load` gives other quota front ends a safe quota inode loader.

State and persistence: The header itself stores no state, but describes state whose persistent backing is quota inodes, dquot buffers, and superblock quota fields. `qi_dqchunklen` and `qi_dqperchunk` encode on-disk dquot clustering assumptions used during dquot iteration and quotacheck. Expiry bounds differ for bigtime versus legacy filesystems.

Dependencies and integration points: Depends on dquot and dquot log-item definitions. Consumers must hold the right locks around radix tree, dquot, inode, and quotaoff operations; the header's inline selectors do not synchronize. Live hook fields are used by online repair or hook users to observe quota transaction changes.

Risks and invariants: `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` assert on invalid quota types and return `NULL` only as an impossible fallback. `XFS_DQITER_MAP_SIZE` intentionally limits quotacheck bmap memory. `XFS_IS_DQUOT_UNINITIALIZED` defines when quota reporting treats a dquot as nonexistent, so changes to dquot resource fields can alter user-visible `ENOENT` behavior.

Test signals: Build coverage with and without quota/live-hook configuration, mount quota initialization checking `qi_dqperchunk`, quota report behavior for zeroed dquots, and transaction tests with more than one dquot of each class.
