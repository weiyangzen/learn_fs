# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.c

## Purpose
`xfs_rmap_btree.c` defines the per-AG reverse mapping btree geometry, verifier, cursor allocation, block allocation/free policy, in-memory btree variant for repair, reserve calculations, and staged commit support. The rmapbt is an overlapping btree ordered by physical block, owner, and offset, allowing multiple file owners for shared reflink blocks.

## Important APIs and functions
Exports include `xfs_rmapbt_init_cursor`, `xfs_rmapbt_commit_staged_btree`, `xfs_rmapbt_maxrecs`, `xfs_rmapbt_compute_maxlevels`, `xfs_rmapbt_calc_size`, `xfs_rmapbt_max_size`, `xfs_rmapbt_calc_reserves`, `xfs_rmapbt_maxlevels_ondisk`, cursor cache lifecycle, and when `CONFIG_XFS_BTREE_IN_MEM` is enabled, `xfs_rmapbt_mem_cursor` and `xfs_rmapbt_mem_init`.

The `xfs_rmapbt_ops` table sets `XFS_BTGEO_OVERLAPPING`, uses two keys per pointer, and supplies root/block/key/verify/ordering callbacks. The in-memory ops mirror the same key behavior but use long pointers and `xfbtree` allocation callbacks.

## Control flow
New rmapbt blocks are allocated from the AGFL via `xfs_alloc_get_freelist`, reused through the busy extent mechanism, counted in `agf_rmap_blocks`, and charged against the `XFS_AG_RESV_RMAPBT` reservation. Freed blocks return to the AGFL, are marked busy with skip-discard, and decrement the rmapbt reservation. Root changes update `agf_rmap_root` and `agf_rmap_level`; staged-tree commit replaces root/level/block count from a fake root and logs all relevant AGF fields.

Key initialization masks unwritten from key comparisons because unwritten is a record attribute, while attr fork and bmbt flags remain key-significant. High keys extend both startblock and, for normal file mappings, logical offset to the final block covered by the record.

## State and persistence behavior
Persistent AGF fields are `agf_rmap_root`, `agf_rmap_level`, and `agf_rmap_blocks`. The btree stores `xfs_rmap_rec` records and internal nodes with low/high key pairs for overlapping range support. Verifiers require rmapbt feature support, valid v5 AG btree headers, correct CRC, valid level bounds, and generic block layout consistency. In-memory rmap btrees use CRC-less verification and fsblock-style headers for repair staging.

## Dependencies and integration points
The implementation integrates with allocation freelists, AG reservations, busy extents, generic and in-memory btree frameworks, online repair staging, AG health, tracepoints, and mount geometry initialization. `xfs_rmap.c` uses these cursors for all normal rmapbt edits; repair uses the in-memory and staged variants.

## Risks and test signals
Risks include incorrect overlapping-key high key construction, treating unwritten as key-significant, AGFL/reservation imbalance, and maxlevel underestimation on highly shared reflink filesystems. Tests should cover maxlevel calculations with reflink on/off, verifier failures, AGFL exhaustion behavior, staged repair commit, in-memory btree creation, and ordering of records with identical startblock but different owners/offsets.
