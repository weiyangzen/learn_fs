# sources/distributed-fs/ceph-client/fs/hfsplus/extents.c

Purpose: maps, allocates, frees, writes, reads, and truncates HFS+ file/fork extents across catalog-inline extents and the extents overflow tree.

Important APIs and control flow: `hfsplus_ext_cmp_key()` orders extents by CNID, fork type, and start block. `hfsplus_ext_build_key()` builds fixed extents-tree keys. `hfsplus_ext_find_block()` maps logical allocation offsets across eight extents. `hfsplus_ext_write_extent()` flushes cached dirty/new overflow records with the inode extent lock. `hfsplus_ext_read_extent()` loads a cached overflow record when a block lies outside the first extents. `hfsplus_get_block()` maps VFS logical blocks to disk sectors, extends on create, reads overflow extents when needed, and marks dirty if extension or dirty-cache write occurred. `hfsplus_free_fork()` frees first and overflow extents, temporarily dropping the tree lock around bitmap frees. `hfsplus_file_extend()` allocates from the allocation bitmap near the last extent, falls back to the beginning, optionally zeroes new blocks, appends to existing extents or starts a new overflow record, and marks allocation/inode dirty. `hfsplus_file_truncate()` expands through zero-length write or frees trailing extents and removes obsolete overflow records.

State and persistence: mutates inode fork extent state, overflow extent btree records, allocation bitmap pages, free block count, physical/logical block counters, inode bytes, and dirty flags on allocation file, extents tree, and target inode.

Dependencies and integration: depends on `bitmap.c`, btree find/mutation helpers, inode writeback, page cache block mapping, and HFS+ superblock geometry (`fs_shift`, `blockoffset`, allocation block size).

Risks and test signals: lock ordering is delicate because bitmap frees occur outside the extents tree lock. The extents overflow file itself cannot use overflow lookups in `hfsplus_get_block()`. Tests should cover fragmented files with more than eight extents, ENOSPC and wraparound allocation, zeroout failure, truncate across overflow records, resource fork free, and dirty-cache read paths.
