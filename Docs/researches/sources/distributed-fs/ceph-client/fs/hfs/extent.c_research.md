# sources/distributed-fs/ceph-client/fs/hfs/extent.c

Purpose: manages classic HFS file extent mapping, extent overflow tree records, allocation bitmap interactions, block mapping, file growth, fork freeing, and truncation.

Important APIs and control flow: `hfs_ext_keycmp()` orders extent records by file id, fork type, and allocation block. `hfs_ext_find_block()` maps a logical allocation-block offset through the three extents in a record. `hfs_ext_write_extent()` flushes cached dirty/new overflow extents to the extents tree. `hfs_ext_read_extent()` fills the inode's cached overflow extent record if a block is outside the first extents. `hfs_get_block()` maps VFS block numbers to disk sectors, optionally extending the file by one allocation clump. `hfs_extend_file()` chooses an allocation goal from the last extent, searches/marks the volume bitmap, appends to first or cached extents when possible, or creates a new overflow record. `hfs_free_fork()` and `hfs_file_truncate()` release allocation blocks and remove obsolete overflow records.

State and persistence: mutates `HFS_I(inode)` extent fields (`first_extents`, `cached_extents`, block counts, dirty/new flags), volume bitmap bits, free block counts, file physical/logical sizes, inode bytes, and MDB dirty flags. Btree overflow extent records are persisted through `brec.c`; bitmap and MDB fields flush through `mdb.c`.

Dependencies and integration: depends on `hfs_vbm_search_free()`/`hfs_clear_vbm_bits()`, btree find/record helpers, `hfs_write_begin()`, and inode writeback. It services all page cache and direct I/O block mapping via `hfs_aops`.

Risks and test signals: HFS uses 16-bit allocation-block indexes here, making overflow/corruption checks important. Truncate has comments noting limited error handling. Tests should force extents beyond the first three, noncontiguous allocation, ENOSPC during extension, partial truncate across first and overflow extents, and resource fork cleanup.
