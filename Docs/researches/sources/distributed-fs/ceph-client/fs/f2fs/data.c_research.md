# sources/distributed-fs/ceph-client/fs/f2fs/data.c

## Purpose

`data.c` is the central F2FS data path implementation. It binds the Linux address-space operations for regular data to F2FS block mapping, page-cache reads, writeback, direct-I/O iomap setup, swapfile activation, encryption, fs-verity, compression, multi-device routing, zoned-device serialization, and in-place versus out-of-place update policy.

The file is responsible for turning logical file offsets into physical block addresses, assembling and submitting bios, completing read and write bios, updating dirty/writeback/read counters, and keeping read extent cache state synchronized with dnode block-address changes. It also implements the `f2fs_dblock_aops` table used by the VFS page cache.

## Important APIs, Types, And Functions

Important local state includes `struct bio_post_read_ctx`, which tracks post-read steps (`STEP_DECRYPT`, `STEP_DECOMPRESS`, `STEP_VERITY`), the target `bio`, owning `sbi`, optional fs-verity info, and the starting filesystem block address. `struct f2fs_folio_state` is attached to large folios to count pending subpage reads before completing the folio.

Initialization and teardown APIs include `f2fs_init_bioset()`, `f2fs_destroy_bioset()`, `f2fs_init_post_read_processing()`, `f2fs_destroy_post_read_processing()`, `f2fs_init_post_read_wq()`, `f2fs_destroy_post_read_wq()`, `f2fs_init_bio_entry_cache()`, and `f2fs_destroy_bio_entry_cache()`. These create the bioset, post-read mempool, post-read workqueue, and slab caches for bio entries and large-folio state.

Bio submission and completion are handled by `__bio_alloc()`, `f2fs_submit_read_bio()`, `f2fs_submit_write_bio()`, `f2fs_read_end_io()`, `f2fs_write_end_io()`, and `f2fs_zone_write_end_io()`. Merge helpers include `page_is_mergeable()`, `io_type_is_mergeable()`, `io_is_mergeable()`, `__submit_merged_bio()`, `f2fs_submit_merged_write()`, `f2fs_submit_merged_write_cond()`, `f2fs_submit_merged_write_folio()`, `f2fs_flush_merged_writes()`, `f2fs_merge_page_bio()`, and `f2fs_submit_merged_ipu_write()`.

Read-path entry points include `f2fs_read_data_folio()`, `f2fs_readahead()`, `f2fs_mpage_readpages()`, `f2fs_read_single_page()`, `f2fs_read_multi_pages()` under compression, `f2fs_read_data_large_folio()`, `f2fs_get_read_data_folio()`, `f2fs_find_data_folio()`, `f2fs_get_lock_data_folio()`, and `f2fs_get_new_data_folio()`.

Block mapping and allocation are centered on `f2fs_map_blocks()`, `f2fs_map_blocks_cached()`, `map_is_mergeable()`, `f2fs_reserve_new_blocks()`, `f2fs_reserve_block()`, `f2fs_get_block_locked()`, `__allocate_data_block()`, `f2fs_set_data_blkaddr()`, and `f2fs_update_data_blkaddr()`. `f2fs_iomap_begin()` exposes this logic to iomap direct I/O through `f2fs_iomap_ops`.

Writeback entry points include `f2fs_write_single_data_page()`, `f2fs_do_write_data_page()`, `f2fs_submit_page_write()`, `f2fs_write_cache_pages()`, `__f2fs_write_data_pages()`, `f2fs_write_data_pages()`, `f2fs_write_begin()`, `f2fs_write_end()`, and `f2fs_write_failed()`.

Placement policy is controlled by `check_inplace_update_policy()`, `f2fs_should_update_inplace()`, `f2fs_should_update_outplace()`, and `need_inplace_update()`. Bmap, fiemap, swap, and page lifecycle hooks are provided by `f2fs_bmap()`, `f2fs_fiemap()`, `f2fs_swap_activate()`, `f2fs_swap_deactivate()`, `f2fs_invalidate_folio()`, `f2fs_release_folio()`, and `f2fs_dirty_data_folio()`.

## Control Flow

For reads, page-cache callers enter through `f2fs_read_data_folio()` or `f2fs_readahead()`. Inline data is attempted first, then `f2fs_mpage_readpages()` chooses the normal page-sized path or the large-folio path. The normal path maps logical blocks with `f2fs_map_blocks()`, zero-fills holes or beyond-EOF regions, validates block addresses, waits for any conflicting writeback, merges contiguous blocks into a read bio, increments read counters, and submits the final bio. Compressed files collect cluster pages in `compress_ctx` and use `f2fs_read_multi_pages()` to read compressed cluster blocks and attach decompression contexts to post-read processing.

Read bio completion runs in `f2fs_read_end_io()`. It handles injected read faults, then either finishes immediately or dispatches post-read work. The post-read pipeline decrypts with fscrypt, decompresses compressed clusters, and schedules fs-verity verification on the verity workqueue when needed. `f2fs_finish_read_bio()` marks non-compressed folios uptodate only on success, decrements read accounting, validates node-page footers, updates large-folio pending counters, completes folio reads, releases decompression references, frees the post-read context, and drops the bio.

For buffered writes, `f2fs_write_begin()` prepares the target folio and reserves or finds a data block. It handles inline-data conversion, compressed overwrite preparation, COW inode reservation for atomic files, free-space balancing, and partial-page read-before-write. `f2fs_write_end()` marks the folio uptodate/dirty, updates atomic flags, advances `i_size`, and updates request time. Later, writeback enters `f2fs_write_data_pages()` and `f2fs_write_cache_pages()`, which scan tagged dirty folios, respect sync-priority serialization, group compressed clusters, and call `f2fs_write_single_data_page()`.

`f2fs_write_single_data_page()` rejects or redirties pages during checkpoint errors or power-on recovery, trims beyond-EOF partial pages, chooses directory/quota checkpoint handling, handles inline data, and delegates placement to `f2fs_do_write_data_page()`. That function resolves the dnode, detects truncation, validates the old block, optionally encrypts the page, then chooses in-place update (`f2fs_inplace_write_data()`) or log-structured out-of-place update (`f2fs_outplace_write_data()`). Submitted writes are merged through `f2fs_submit_page_write()` or the IPU merge path. Write completion updates mapping errors, checkpoint-failure state, warm-node fsync lists, page counters, checkpoint waiters, GC flags, and folio writeback state.

`f2fs_map_blocks()` is the shared mapping engine. It first checks the read extent cache for non-creating lookups, then walks dnodes. Depending on the caller flag, it may reserve delayed-allocation blocks for buffered AIO, allocate real data blocks for direct I/O, return holes for fiemap or direct reads, pre-cache extents, or return bmap-compatible physical blocks. The function keeps multi-device direct-I/O boundaries, waits for block writeback on direct I/O, marks newly allocated mappings, and updates read extent cache ranges when pre-caching.

## State And Persistence Behavior

Persistent block mapping changes are made by writing block addresses into dnode pages through `__set_data_blkaddr()` and marking node folios dirty. New block reservations convert `NULL_ADDR` slots to `NEW_ADDR`; real allocation replaces `NULL_ADDR`, `NEW_ADDR`, or an old physical block with a freshly allocated block and updates summaries and extent cache state.

The read extent cache is not authoritative persistence, but `f2fs_update_data_blkaddr()` and `f2fs_map_blocks()` keep it aligned with dnode mappings. Fiemap and bmap expose logical-to-physical persistence state, including compressed clusters, inline data, xattrs, delayed allocation, unwritten blocks, and encrypted extents.

Writeback mutates inode state by decrementing dirty page counts, setting `FI_APPEND_WRITE` or `FI_UPDATE_WRITE`, updating `last_disk_size`, maintaining atomic-write COW inode size, and adding/removing dirty inode tracking. Directory and quota data receive checkpoint-oriented handling; failures can stop checkpointing via `f2fs_stop_checkpoint()` for checkpoint-guaranteed data.

Swap activation persists policy state by marking the inode pinned (`FI_PIN_FILE`) after verifying or migrating extents to section-aligned, non-hole, non-zoned-compatible ranges. Swap deactivation clears that flag and decrements stats.

Large folio state is transient and attached as folio private data. It is freed on invalidate/release after all subpage reads complete.

## Dependencies And Integration Points

This file sits between VFS address-space operations, the block layer, and F2FS node/segment managers. It depends heavily on `f2fs.h`, `node.h`, `segment.h`, `iostat.h`, fscrypt, fsverity, compression helpers, tracepoints, iomap, writeback control, folio APIs, and block crypto.

Important internal integration points include extent cache lookups and updates in `extent_cache.c`, node lookup and node-info reads in the node manager, segment allocation via `f2fs_allocate_data_block()`, checkpoint and dirty-page accounting, GC metadata paths through `META_MAPPING`, compression read/write helpers, inline-data and inline-dentry helpers, atomic-write COW inode handling, and multi-device block translation through `f2fs_target_device()`.

Externally visible integration happens through `f2fs_dblock_aops` and `f2fs_iomap_ops`. The address-space ops table wires the file into generic page-cache read, readahead, writeback, buffered write, dirtying, invalidation, release, bmap, and swap activation flows.

## Risks And Edge Cases

Post-read ordering is delicate: decryption must happen before decompression when needed, and fs-verity verification is intentionally scheduled on a separate workqueue because verifying data may recursively read verity metadata that itself requires decrypt/decompress work. The mempool free-before-verify behavior prevents deadlocks but relies on verity remaining the last post-read step.

Compressed clusters are handled per cluster rather than per bio. Bios can span compressed and uncompressed pages, so completion must not mark compressed cache pages uptodate directly and must correctly balance decompression references even on I/O or decryption failure.

`f2fs_map_blocks()` has many caller-specific modes. Regressions in hole handling, `NEW_ADDR` handling, direct-I/O allocation, or multi-device boundary trimming can surface as corruption, stale data exposure, or incorrect fiemap/bmap output. LFS direct writes also carry `m_last_pblk` state through iomap private data to support out-of-place allocation semantics.

Lock ordering is a recurring risk. The file explicitly documents data-page to node-folio ordering for block-address changes, uses `f2fs_map_lock()` variants for AIO/direct paths, avoids `FGP_STABLE` in write-begin, and has retry paths for races with checkpoint, truncation, inline-data conversion, and writeback.

Fault-injection hooks (`FAULT_READ_IO`, `FAULT_WRITE_IO`, `FAULT_SKIP_WRITE`, `FAULT_DIR_DEPTH` in related directory paths) are expected to exercise error handling. Checkpoint errors, shutdown, power-on recovery, read-only errors mode, and fs-verity enablement all change normal writeback and truncate behavior.

## Test Signals

Useful test signals include xfstests coverage for buffered read/write, direct I/O, fsync, fiemap, bmap, fallocate, swapfile activation, compression, encryption, fs-verity, checkpoint error injection, and multi-device/zoned configurations. Kernel tracepoints such as `trace_f2fs_submit_read_bio`, `trace_f2fs_submit_write_bio`, `trace_f2fs_map_blocks`, `trace_f2fs_readpage`, `trace_f2fs_writepage`, and `trace_f2fs_fiemap` provide behavioral evidence.

Runtime counters from iostat and debugfs should show balanced read/write page counts, no leaked writeback, no stuck checkpoint waiters, and expected read extent cache hits after precache. Error-path tests should confirm mapping errors are set, checkpoint stops on checkpoint-data write failure, compressed read failures clear uptodate state, and large folios complete exactly after all pending subpage reads finish.
