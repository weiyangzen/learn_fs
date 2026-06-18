# sources/distributed-fs/ceph-client/fs/xfs/scrub/refcount_repair.c

## Purpose
`refcount_repair.c` rebuilds an AG refcount btree from rmapbt records. It derives shared extent records by sweeping overlapping file data rmaps, preserves CoW staging extents, stages a replacement refcountbt, commits it into the AGF, and reaps the obsolete tree blocks.

## Important APIs, types, and functions
`xrep_setup_ag_refcountbt` allocates an xfile-backed workspace. `struct xrep_refc` owns the xfarray of new `xfs_refcount_irec` records, a `xrep_newbt`, an `xagb_bitmap` of old refcountbt blocks, counters, and cursor position for bulk loading. Key helpers are `xrep_refc_walk_rmaps`, `xrep_refc_find_refcounts`, `xrep_refc_stash`, `xrep_refc_sort_records`, `xrep_refc_build_new_tree`, `xrep_refc_reset_counters`, `xrep_refc_remove_old_tree`, and the exported `xrep_refcountbt`.

## Control flow
Repair requires rmapbt support. It creates storage sized for one refcount record per AG block, initializes the old-tree bitmap, and scans rmaps. Shareable written data fork rmaps are fed into an `rcbag` sweep-line algorithm that emits refcount records whenever overlap depth changes above one. CoW owner records are stashed as CoW refcount records with count one, and old refcountbt owner records are remembered for later reaping. Records are sorted in on-disk domain/start order, geometry is computed with a staged fake root, blocks are reserved, `xfs_btree_bload` bulk-loads records, and `xfs_refcountbt_commit_staged_btree` installs the root.

## State and persistence
Persistent changes are the new refcountbt root and AGF counters. The code temporarily sets `pagf_repair_refcount_level` so verifiers tolerate old and new heights during AIL checkpoint/reap races, then clears it after old blocks are reaped and requests per-AG reservation reset.

## Dependencies and integration points
It depends on rmapbt as the source of truth, `xfarray`, `rcbag`, `xrep_newbt`, AG reservation accounting, staged btree bulk load, and `xrep_reap_agblocks`. The scrub setup in `refcount.c` calls its setup path before AG btree setup.

## Risks and test signals
Important risks are incorrect shareability filtering, overlap sweep off-by-one errors, refcount clamping, stale old-tree block reaping, verifier races when tree height shrinks, and insufficient AG reservation. Tests should rebuild from fragmented rmap sets, CoW staging extents, maximal refcounts, sorted shared/CoW domains, full and empty refcount trees, allocation pressure, forced termination before commit, and post-repair scrub revalidation.
