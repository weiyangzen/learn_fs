# sources/distributed-fs/ceph-client/fs/xfs/scrub/rmap_repair.c

## Purpose
`rmap_repair.c` rebuilds a per-AG rmapbt by deriving reverse mappings from primary metadata and file forks. It is the most complex AG btree repair because it must scan inodes while tracking live rmap updates, reserve space for the new rmapbt without recursive rmap changes, bulk-load the replacement tree, and reap the old tree blocks.

## Important APIs, types, and functions
`xrep_setup_ag_rmapbt` enables rmap filesystem gates, creates xfile storage, and allocates `struct xrep_rmap`. That context owns a `xrep_newbt`, mutex, in-memory `xfbtree`, rmap hook, inode scan cursor, record counts, and old AGF counters. Major helpers include `xrep_rmap_stash`, inode fork scanners, `xrep_rmap_find_inode_rmaps`, `xrep_rmap_find_refcount_rmaps`, `xrep_rmap_find_rmaps`, `xrep_rmap_reserve_space`, `xrep_rmap_build_new_tree`, `xrep_rmap_remove_old_tree`, live update hook `xrep_rmapbt_live_update`, and exported `xrep_rmapbt`.

## Control flow
The repair first records non-space metadata rmaps under AG locks, then drops AG buffers and uses an empty transaction while scanning every inode fork for mappings into the target AG. A live rmap hook updates the in-memory btree for already-scanned owners. After relocking the AG, collected records are validated and counted. Space reservation iteratively allocates new rmapbt blocks in no-rmap mode, recomputes `OWN_AG` records for bnobt/cntbt/AGFL/new rmapbt blocks, and repeats until geometry is stable. The new tree is bulk-loaded and committed to AGF, counters are reset, and old rmapbt blocks are inferred from gaps not present in bnobt free space.

## State and persistence
Persistent state includes the new rmapbt root and AGF `btreeblks`/rmap counters. Temporary state includes xfile-backed in-memory btree, inode scan cursor, live update hook, and reservation lists. `pagf_repair_rmap_level` tolerates tree height transitions until old blocks are reaped and reservations reset.

## Dependencies and integration points
It integrates inode scanning, bmap btree walking, inode btree/refcount metadata derivation, AG allocation, rmap hooks, staged btree bulk loading, and reaping. It also understands metadir realtime btree inodes because their blocks live on the data device and must have AG rmaps.

## Risks and test signals
Risks include stale in-memory records if live hooks miss updates, deadlocks during inode scan, recursive allocation/rmap updates, old-tree block misidentification, and incorrect bmbt/realtime fork filtering. Tests should cover concurrent file changes, attr/data forks, btree and extent forks, reflink CoW, empty inobt root, internal log, AGFL churn, low free space, hook failure aborts, and post-repair rmap/refcount scrub consistency.
