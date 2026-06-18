# sources/distributed-fs/ceph-client/fs/btrfs/extent_io.c

## Purpose

`extent_io.c` is the main Btrfs bridge between VFS folio writeback/read paths, Btrfs extent state, extent maps, ordered extents, BIO submission, and metadata extent-buffer lifetime. It handles data folio reads and writes, readahead, delalloc locking and cleanup, metadata tree block read/writeback, extent-buffer allocation/freeing, subpage metadata/data state, and extent-buffer memory access helpers used by tree code.

## Important APIs, Types, And Functions

- `struct btrfs_bio_ctrl` batches read/write state while building `struct btrfs_bio` objects. It tracks the current bio, next logical file offset, compression type, ordered-extent boundary, op flags, max extent generation for checksum lookup optimization, writeback control, subpage submit bitmap, readahead control, and last extent-map start for compressed read correctness.
- Cache lifecycle: `extent_buffer_init_cachep()` and `extent_buffer_free_cachep()` create/destroy the `btrfs_extent_buffer` slab cache. Debug builds also maintain `fs_info->allocated_ebs` via leak debug helpers.
- Data reads: `btrfs_read_folio()`, `btrfs_readahead()`, `lock_extents_for_read()`, `btrfs_do_readpage()`, `submit_extent_folio()`, `end_bbio_data_read()`, and `end_folio_read()` coordinate locked folios, ordered extents, extent-map lookup, holes/inline/compressed extents, fsverity verification, zeroing past EOF, and BIO completion.
- Data writes: `btrfs_writepages()`, `extent_write_cache_pages()`, `extent_writepage()`, `writepage_delalloc()`, `extent_writepage_io()`, `submit_one_sector()`, `extent_write_locked_range()`, and `end_bbio_data_write()` run delayed allocation, create/finish ordered extents, submit normal writeback, and complete folio writeback state.
- Metadata writeback: `btree_writepages()`, `lock_extent_buffer_for_io()`, `prepare_eb_write()`, `write_one_eb()`, `end_bbio_meta_write()`, `btrfs_btree_wait_writeback_range()`, and xarray tag helpers drive dirty/writeback metadata extent buffers.
- Extent buffer lifetime: `alloc_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, `try_release_extent_buffer()`, and `try_release_subpage_extent_buffer()` manage buffer-tree xarray entries, folios, references, stale/tree refs, and subpage sharing.
- Extent buffer I/O and access: `read_extent_buffer_pages_nowait()`, `read_extent_buffer_pages()`, `end_bbio_meta_read()`, `set_extent_buffer_dirty()`, `btrfs_clear_buffer_dirty()`, `set_extent_buffer_uptodate()`, `clear_extent_buffer_uptodate()`, `read_extent_buffer()`, `write_extent_buffer()`, `memcmp_extent_buffer()`, `copy_extent_buffer*()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, and bitmap helpers abstract tree-block memory that may span folios or sit inside a subpage folio.
- Readahead helpers: `btrfs_readahead_tree_block()` and `btrfs_readahead_node_child()` create/find metadata blocks and submit nonblocking metadata reads with parent checks.

## Control Flow

Data read starts by locking the inode extent range with `lock_extents_for_read()`. That helper waits for ordered extents unless the locked folio state proves the ordered range can be skipped. `btrfs_do_readpage()` then walks the folio by sectorsize, sets/uses Btrfs folio private state, resolves an extent map, and handles each sector as EOF zeroing, already-uptodate, hole zeroing, inline data already copied by `btrfs_get_extent()`, or BIO-backed read. BIOs are split when compression type changes, when logical/disk contiguity breaks, or when adjacent compressed file extents point at the same compressed extent through different extent maps. Completion updates subpage/folio uptodate bits, runs fsverity where relevant, zeroes EOF tails, and unlocks the correct range.

Data writeback flows from `btrfs_writepages()` into `extent_write_cache_pages()`, which iterates dirty folios by writeback tags, handles cyclic scans, waits on writeback for sync/subpage cases, clears dirty-for-IO, and calls `extent_writepage()`. `extent_writepage()` validates the folio, maps it into Btrfs folio state, calls `writepage_delalloc()` to lock and run delalloc ranges, then `extent_writepage_io()` submits sectors indicated by `bio_ctrl->submit_bitmap`. `submit_one_sector()` obtains the final extent map, rejects holes/inline/compressed cases that should not reach normal writeback, updates dirty/ordered/writeback bits, and appends the sector to a BIO. `end_bbio_data_write()` clears ordered/writeback state and finishes the ordered extent.

Metadata writeback is xarray-tag driven rather than page-cache-tag driven. `btree_writepages()` scans `fs_info->buffer_tree` for dirty/towrite extent buffers, checks zoned metadata write pointer constraints, locks each buffer, clears dirty tags, sets writeback state, zeroes stale tree-block areas with `prepare_eb_write()`, creates a metadata BIO in `write_one_eb()`, and completes in `end_bbio_meta_write()`. Write errors call `set_btree_ioerr()`, which records runtime buffer failure and persistent fs/log error flags needed by transaction commit and log sync paths.

Extent-buffer allocation first checks alignment and existing xarray entries, allocates an `extent_buffer`, preallocates subpage private state if needed, allocates folios, attaches/reuses page-cache folios under `i_private_lock`, inserts into `fs_info->buffer_tree` by xarray compare-exchange, sets the tree reference, then unlocks and drops allocation references. Release paths remove xarray entries with compare-exchange, detach folio private state only when safe, respect dirty/writeback guards, and use RCU freeing for mapped buffers.

## State And Persistence Behavior

The file maintains runtime state in `extent_buffer::bflags`, folio private/subpage bitmaps, inode `io_tree` extent states, inode extent maps, ordered extents, xarray marks on `fs_info->buffer_tree`, and writeback-control counters. Metadata dirty accounting updates `fs_info->dirty_metadata_bytes`; extent-buffer writeback errors set `BTRFS_FS_BTREE_ERR`, `BTRFS_FS_LOG1_ERR`, or `BTRFS_FS_LOG2_ERR`, which influences transaction/log error handling beyond the lifetime of a single buffer. Data write completion persists ordered-extent success/failure through `btrfs_finish_ordered_extent()` and mapping errors.

The actual persistent bytes are not formatted here, but this file decides when data and metadata reach block devices and when tree-block memory is sanitized before writeback. It also stores runtime read mirror choice in `eb->read_mirror`, sets header-written flags before metadata writeback, and enforces parent/generation checks on metadata reads through `btrfs_validate_extent_buffer()`.

## Dependencies And Integration Points

This file integrates Linux folios, page cache, readahead, writeback, BIO/block APIs, fsverity, xarray tags, RCU, slab caches, and Btrfs-specific modules: extent I/O tree locking, extent maps, ordered extents, compression, checksums, tree locking, backrefs, disk I/O, zoned block-group logic, transaction state, subpage state, file item accessors, and device replacement. It is called by Btrfs address-space operations for data and btree inodes, tree block lookup/read paths, transaction dirtying/cleaning paths, release/invalidate folio callbacks, and readahead callers.

## Risks And Edge Cases

- Reference lifetime is delicate: extent buffers have xarray tree refs, ordinary refs, stale refs, RCU freeing, and folio private attachments. Bugs can become use-after-free, leaks, or dirty buffers freed while still referenced.
- Subpage support is high risk because multiple logical sectors or metadata blocks share one folio; dirty, lock, writeback, uptodate, and eb-ref bitmaps must be range accurate.
- BIO merging must preserve both disk contiguity and file logical contiguity. Compressed extents add a correctness constraint around extent-map identity, not just disk bytenr.
- Ordered extent waiting/skip logic prevents read/write deadlocks and missing checksum insertion. Incorrect skip decisions could expose stale data or fail reads due to missing checksums.
- Metadata writeback errors must be recorded outside page state; otherwise transaction commit can succeed with invalid tree blocks.
- Zoned mode requires preserving metadata write order and zeroout semantics; bypassing dirty clear behavior could violate write pointer ordering.
- Range arithmetic is mostly inclusive and often converted to exclusive boundaries; off-by-one or overflow bugs are explicitly guarded in several helpers but remain a broad risk.

## Test Signals

Useful signals include xfstests for Btrfs generic read/write, fsync, compression, delalloc, subpage, zoned mode, fsverity, metadata writeback error injection, and fiemap interactions; Btrfs sanity tests for extent-buffer allocation and `find_lock_delalloc_range()`; fault injection for allocation/BIO errors; lockdep/KASAN/KCSAN for folio/private/refcount races; and debug assertions around extent buffer range access, dirty/writeback state, and extent-map assumptions.
