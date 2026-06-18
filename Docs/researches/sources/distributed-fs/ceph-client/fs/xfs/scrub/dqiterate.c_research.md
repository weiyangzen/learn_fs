# sources/distributed-fs/ceph-client/fs/xfs/scrub/dqiterate.c

Purpose: Implements an iterator that walks both on-disk and in-core XFS dquots for a quota type, so scrub/repair code can inspect every relevant quota record even when quota file mappings are sparse or repairs have disturbed mappings.

Important APIs, types, and functions: Public APIs are `xchk_dqiter_init()` and `xchk_dquot_iter()`. Internal helpers are `xchk_dquot_iter_revalidate_bmap()`, `xchk_dquot_iter_advance_bmap()`, and `xchk_dquot_iter_advance_incore()`. State is stored in `struct xchk_dqiter` from the quota scrub headers, including current id, quota inode, cached bmap record, fork sequence, and quota type.

Control flow: Initialization records scrub context, quota type, quota inode, an invalid cached mapping, and id zero. Each `xchk_dquot_iter()` call locks the quota inode data map, revalidates the cached bmap against the quota fork sequence and current id, advances over holes to the next real quota-file extent, separately finds the next incore dquot id from the quota radix tree if the on-disk iterator jumped forward, chooses the lower id, obtains the dquot with `xfs_qm_dqget()`, advances the cursor, and returns 1/0/error.

State and persistence: The iterator does not persist metadata. It reads quota inode mappings and in-core dquot radix trees, and returns referenced dquots to callers. Cached bmap state is invalidated by fork sequence changes.

Dependencies and integration points: Used by quota scrub/repair code. It depends on XFS quota inode lookup, `m_quotainfo`, `qi_dqperchunk`, bmap read, data-map locking, dquot radix trees protected by `qi_tree_lock`, and `xfs_qm_dqget()`.

Risks and test signals: Risks include skipping incore dquots when the quota file has holes, stale bmap cache after quota file repair, id overflow around `XFS_DQ_ID_MAX`, sparse quota files with delayed mappings, and races with dquot allocation/removal. Test dense and sparse quota files, incore-only dquots, quota file extent changes during iteration, last-id boundary, user/group/project quota types, and injected bmap corruption or missing mapping records.
