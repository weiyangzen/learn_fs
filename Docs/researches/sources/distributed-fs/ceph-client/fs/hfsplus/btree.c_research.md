# sources/distributed-fs/ceph-client/fs/hfsplus/btree.c

Purpose: opens, validates, writes, grows, allocates, and frees nodes for HFS+ extents, catalog, and attributes B-trees.

Important APIs and control flow: `hfsplus_calc_btree_clump_size()` derives clump sizes from volume size and tree type using Apple's table-derived heuristics. `hfs_btree_open()` loads the special file inode, reads header node 0, validates max key length/flags/node size/count, assigns the proper comparator, detects HFSX binary versus casefold catalog behavior, initializes geometry, and verifies bit 0 in the btree map, forcing read-only if corrupted. `hfs_btree_write()` persists mutable header fields. `hfs_bmap_reserve()` extends the btree file using `hfsplus_file_extend()`, optionally zeroing new nodes when required, and updates node counts. `hfs_bmap_alloc()` scans header/map-node map records for free node bits, sets one, writes the btree header, and creates a bnode. `hfs_bmap_free()` clears a map bit with validation and updates free counts/header.

State and persistence: owns in-memory `struct hfs_btree` state and persists header fields plus btree allocation bits. Growing btree special files updates their inode allocation/size state and dirties the special inode.

Dependencies and integration: depends on `hfsplus_iget()`, bnode helpers, extent-based file extension, volume flags, and comparators from `catalog.c`, `extents.c`, and `attributes.c`. Mount code opens these trees; btree mutators reserve/allocate/free nodes here.

Risks and test signals: map-record corruption causes read-only fallback, a critical safety behavior. Attribute tree has different key rules. Tests should cover malformed headers, map bit 0 clear, HFSX binary vs casefold comparator selection, btree growth ENOSPC, new map-node creation, and node free double-free detection.
