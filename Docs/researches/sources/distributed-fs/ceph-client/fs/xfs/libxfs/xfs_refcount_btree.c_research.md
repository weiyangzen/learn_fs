# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount_btree.c

## Purpose
`xfs_refcount_btree.c` implements the per-AG refcount btree geometry and generic btree operation table. It does not perform high-level refcount interval editing; instead, it tells the generic btree code how to allocate/free refcountbt blocks, compare keys, verify blocks, initialize cursors, compute tree height/size, and commit staged repair trees.

## Important APIs and functions
The main exported entry points are `xfs_refcountbt_init_cursor`, `xfs_refcountbt_commit_staged_btree`, `xfs_refcountbt_maxrecs`, `xfs_refcountbt_compute_maxlevels`, `xfs_refcountbt_calc_size`, `xfs_refcountbt_max_size`, `xfs_refcountbt_calc_reserves`, `xfs_refcountbt_maxlevels_ondisk`, and the cursor cache init/destroy functions.

The `xfs_refcountbt_ops` table provides callbacks for cursor duplication, root updates, block allocation/freeing, min/max record counts, key/record initialization, comparison, verifier operations, ordering, and key contiguity. `xfs_refcountbt_buf_ops` wires the CRC and structural verifiers into buffer I/O.

## Control flow
When btree shape changes need a new block, `xfs_refcountbt_alloc_block` allocates one metadata-reserved block near the refcount btree area, records ownership as `XFS_RMAP_OINFO_REFC`, increments `agf_refcount_blocks`, and logs the AGF field. Freeing decrements the block count and schedules the btree block for deferred freeing with refcount owner info. Root changes update `agf_refcount_root` and `agf_refcount_level`, mirror the level into `pagf_refcount_level`, and log root/level fields.

Cursor initialization allocates from `xfs_refcountbt_cur_cache`, holds the AG group, attaches the AGF buffer when available, and initializes `bc_refc.nr_ops` / `shape_changes`. Staged repair commits replace root, level, and block count from the fake root and then ask generic btree staging code to finish.

## State and persistence behavior
Persistent state is held in AGF fields: `agf_refcount_root`, `agf_refcount_level`, and `agf_refcount_blocks`, plus the btree blocks themselves. Block verification requires reflink support, valid v5 AG btree headers, sane level bounds, and generic btree block consistency with mount record geometry. Writes recalculate the AG btree CRC.

## Dependencies and integration points
This file integrates with `xfs_alloc`, `xfs_rmap`, `xfs_btree`, `xfs_btree_staging`, AG health, tracing, and mount geometry setup. `xfs_refcount.c` relies on this cursor implementation for all per-AG refcount mutations, while repair code uses staged commit support.

## Risks and test signals
Risks include mismatched AGF counters, root/level updates not logged, invalid maxlevel computation for extreme AG sizes, and verifier behavior during online repair. Tests should exercise btree block split/merge, reserve calculations with an internal log AG, online repair staged-tree commit, bad magic/CRC/level verifier failures, and disabled-reflink mounts.
