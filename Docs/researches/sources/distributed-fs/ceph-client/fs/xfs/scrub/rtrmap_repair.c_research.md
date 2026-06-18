# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtrmap_repair.c

## Purpose
`rtrmap_repair.c` rebuilds an rtgroup realtime rmap btree. It scans realtime file data mappings and CoW staging extents into an in-memory btree, tracks live rtrmap updates during the inode scan, finds old rtrmapbt blocks through data-device rmaps, bulk-loads a new metadir btree into the realtime rmap inode, and reaps obsolete blocks.

## Important APIs, types, and functions
`xrep_setup_rtrmapbt` enables rmap gates, creates xfile storage, and stores `struct xrep_rtrmap` in `sc->buf`. That context owns `xrep_newbt`, a mutex, in-memory `xfbtree`, old-block `xfsb_bitmap`, live rmap hook, inode scan cursor, memory cursor, and record count. Major helpers are `xrep_rtrmap_stash`, `xrep_rtrmap_scan_dfork`, `xrep_rtrmap_scan_inode`, `xrep_rtrmap_find_refcount_rmaps`, `xrep_rtrmap_find_rmaps`, `xrep_rtrmap_build_new_tree`, `xrep_rtrmapbt_live_update`, setup/teardown helpers, and exported `xrep_rtrmapbt`.

## Control flow
Repair first fixes metadata inode forks. Scan setup initializes the in-memory rtrmapbt and installs a live rmap hook for the rtgroup. It records the realtime superblock range when present, records CoW staging extents from rtrefcount, unlocks realtime metadata, and scans all inodes. Only realtime data forks are accumulated; mappings are coalesced when physically and logically adjacent. After relocking realtime metadata, it scans all AG rmapbts for old rtrmap inode blocks, validates collected records against rtbitmap in-use state, computes staged btree geometry, reserves blocks on the rtrmap inode, bulk-loads from the in-memory tree, commits the staged btree, updates inode block counts, stops live updates, commits new blocks, and reaps old metadir fsblocks.

## State and persistence
Persistent state is the rebuilt rtrmap inode data fork and inode block accounting. Temporary state includes xfile-backed in-memory btree, old-block bitmap, inode scan cursor, live update hook, staged fake root, and temporary transactions used by hooks.

## Dependencies and integration points
It depends on inode cache scanning, realtime bmap conversion helpers, rtrefcount CoW records, rtbitmap in-use validation, data-device rmapbt for metadir block discovery, `xrep_newbt` metadir inode support, and rmap update notifier hooks.

## Risks and test signals
Risks include missed live updates, incorrect realtime fork filtering, old btree block leaks, stale CoW staging records, unit conversion between rtblock and rgbno, and lock ordering during long scans. Tests should cover concurrent realtime file changes, loaded and unloaded bmbt forks, unwritten mappings, rt superblock owner record, CoW staging, no realtime files, hook aborts, metadir old-block reaping, and post-repair rtrmap/rtbitmap/rtrefcount scrub.
