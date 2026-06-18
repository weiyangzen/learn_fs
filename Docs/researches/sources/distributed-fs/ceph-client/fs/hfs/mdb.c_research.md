# sources/distributed-fs/ceph-client/fs/hfs/mdb.c

Purpose: reads, validates, updates, and releases the classic HFS Master Directory Block (MDB), alternate MDB, volume bitmap, catalog tree, and extents tree.

Important APIs and control flow: `hfs_get_last_session()` chooses a CD-ROM/session starting sector or whole-device default. `is_hfs_cnid_counts_valid()` checks `next_id`, file count, and folder count against `U32_MAX`. `hfs_mdb_get()` sets block size, locates the HFS MDB directly or via partition map, validates allocation block size, loads geometry/counters/root counts, optionally loads alternate MDB, reads the volume bitmap into memory, opens extents and catalog btrees, and marks writable mounts as unclean/inconsistent. `hfs_mdb_commit()` writes dirty MDB counters/times, writes alternate MDB after special btree fork growth, and flushes dirty bitmap bytes back to disk. `hfs_mdb_close()` marks the volume clean on unmount, and `hfs_mdb_put()` closes btrees, releases buffers, unloads NLS tables, and frees the bitmap.

State and persistence: owns primary and alternate MDB buffer_heads, `hfs_sb_info` geometry/counters/free blocks, in-memory volume bitmap, unmount/lock/inconsistent attributes, write count, and btree handles. Dirty flags control which portions are copied back.

Dependencies and integration: depends on block-device helpers, CD-ROM multisession APIs, partition parsing in `part_tbl.c`, btree open/close, and fork write helpers. `super.c` calls these from mount, sync, delayed work, and unmount paths.

Risks and test signals: mount can continue read-only after suspicious counters or unclean/locked attributes. Bitmap allocation is fixed-size 8192 bytes, matching classic HFS limits. Tests should use images with partition maps, alternate MDB missing, unclean flags, corrupt counters, unusual block sizes, dirty bitmap writes, and read-only remounts.
