# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrefcount_repair.c

## Purpose
`rtrefcount_repair.c` rebuilds an rtgroup realtime refcount btree from realtime rmap records. It derives shared extents by sweeping rtrmap overlap depth, preserves CoW staging extents, stages a new metadata-inode btree, commits it to the rtrefcount inode, and reaps old btree blocks from the data device.

## Important APIs, types, and functions
`xrep_setup_rtrefcountbt` allocates xfile workspace. `struct xrep_rtrefc` owns the new refcount record xfarray, `xrep_newbt`, old-block `xfsb_bitmap`, scrub pointer, load cursor, and block count. Key helpers include `xrep_rtrefc_check_ext`, `xrep_rtrefc_stash`, `xrep_rtrefc_walk_rmaps`, `xrep_rtrefc_find_refcounts`, `xrep_rtrefc_scan_ag`, `xrep_rtrefc_sort_records`, `xrep_rtrefc_build_new_tree`, and exported `xrep_rtrefcountbt`.

## Control flow
Repair requires rtrmapbt support and first repairs metadata inode forks. It scans every data AG rmapbt to find old blocks owned by the rtrefcount inode data fork. It then initializes rtgroup btree cursors and sweeps the realtime rmapbt with an `rcbag`. Shareable written realtime file mappings produce shared refcount records when overlap depth changes above one; CoW owner records are preserved as CoW domain records. Records are sorted by encoded start/domain, geometry is computed for an inode-rooted staged btree, extra transaction reservation is taken against the rtrefcount inode, blocks are allocated, the tree is bulk-loaded, and the staged btree is committed.

## State and persistence
Persistent updates include the rtrefcount inode data fork, inode block count/quota accounting, and new metadata btree contents. Old btree blocks are tracked as fsblocks and reaped with `xrep_reap_metadir_fsblocks`. Temporary xfarray, rcbag, staged fake inode root, and xfile storage are destroyed on exit.

## Dependencies and integration points
It depends on rtrmap as the truth source, data-device rmapbt for locating metadir btree blocks, `xrep_newbt` metadir inode support, `rcbag`, metadata inode repair, and realtime in-use validation via `xrep_require_rtext_inuse`.

## Risks and test signals
Risks include deriving counts from corrupt rtrmap, allowing metadata or unwritten rmaps into shared calculations, missing old data-device btree blocks, transaction reservation underestimation, and root-format mistakes for metadir btrees. Tests should cover fragmented overlaps, CoW staging, misaligned realtime extents, no rtrmapbt support, large rtextent counts, old btree reaping, quota/block-count updates, and post-repair scrub.
