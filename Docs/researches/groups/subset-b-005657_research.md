# Research: subset-b-005657

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/data.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/debug.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/debug.c

## Purpose

`debug.c` implements F2FS runtime statistics collection and debugfs presentation. It builds per-superblock `f2fs_stat_info`, maintains all mounted instances on a global stats list, calculates segment distribution and memory footprint, and exposes a consolidated `/sys/kernel/debug/f2fs/status` view when `CONFIG_DEBUG_FS` is enabled.

The file does not implement filesystem behavior directly. Its job is observability: surfacing allocation, checkpoint, GC, extent-cache, dirty-page, IO, discard, compression, swapfile, atomic-write, multi-device, and memory statistics in a single status report.

## Important APIs, Types, And Functions

Global state includes `f2fs_stat_list`, protected by `f2fs_stat_lock`, plus `f2fs_debugfs_root` under `CONFIG_DEBUG_FS`.

`f2fs_build_stats()` allocates and initializes `struct f2fs_stat_info` and per-device stats, resets related counters in `sbi`, stores `sbi->stat_info`, and links the instance into the global list. `f2fs_destroy_stats()` removes the instance and frees its stats.

`f2fs_create_root_stats()` creates the `f2fs` debugfs directory and `status` file. `f2fs_destroy_root_stats()` removes the tree. `DEFINE_SHOW_ATTRIBUTE(stat)` binds `stat_show()` to the debugfs file operations.

`f2fs_update_sit_info()` calculates a bimodal distribution factor and average valid blocks among dirty sections. `update_multidevice_stats()` summarizes per-device segment and section states. `update_general_status()` snapshots most live counters from `sbi`, node manager, segment manager, SIT, NAT, checkpoint merge state, discard/flush queues, extent caches, dirty pages, and curseg positions. `update_mem_info()` estimates static, cache, extent-cache, and page-cache memory footprint.

`stat_show()` is the main renderer. It takes the global spinlock, walks all mounted stat objects, refreshes status, and prints a human-readable report with policy, utilization, segment layout, checkpoint and GC counts, extent cache hit ratios, async IO counters, dirty pages, NAT/SIT stats, user-block distribution, IPU/SSR/LFS counts, segment BDF, and memory usage.

## Control Flow

Stats are built at mount-time through `f2fs_build_stats()`, then debugfs root creation is handled once through `f2fs_create_root_stats()`. When a user reads the debugfs `status` file, `stat_show()` iterates over `f2fs_stat_list`. For each `sbi`, it calls `update_general_status()`, then prints partition identity and checkpoint state, superblock layout, policy, utilization, current segment positions, multi-device summaries, checkpoint merge statistics, GC movement counts, extent-cache metrics, dirty/writeback/read counters, metadata cache counts, user-block distribution, IPU/SSR/LFS counters, SIT distribution statistics, and memory footprint.

`update_general_status()` is a broad snapshot. It reads raw superblock fields that may change during online resize, pulls extent-cache hit counters and tree/node counts, reads dirty and IO page counters, snapshots flush/discard queues when present, copies checkpoint merge timing under its own lock, calculates segment/free/dirty/prefree counts, reads page-cache sizes for node/meta/compress inodes, collects NAT/SIT/free-nid counts, records current segment offsets and locations, and scans all main segments by type to aggregate dirty/full segment counts and valid blocks.

`update_mem_info()` lazily computes static/base allocations only once, then recomputes dynamic cache and page-cache memory on each status read.

## State And Persistence Behavior

The state in this file is in-memory diagnostic state. It does not persist to disk and does not change filesystem metadata except for initializing and resetting counters in `sbi` during stats setup.

The global list determines what mounted filesystems appear in the debugfs report. Per-mount `f2fs_stat_info` stores cached snapshots and memory estimates, but most values are refreshed from authoritative runtime structures when the debugfs file is read.

Counter initialization in `f2fs_build_stats()` is important because many counters live in `sbi` rather than only in `f2fs_stat_info`. Reset fields include extent-cache hit counters, inline/compressed/swapfile inode counters, atomic-file counts, inplace counts, metadata write counters, checkpoint call counters, and maximum atomic-write count.

## Dependencies And Integration Points

`debug.c` depends on F2FS core headers plus `node.h`, `segment.h`, and `gc.h`. It reads from the segment manager (`SM_I`), node manager (`NM_I`), SIT (`SIT_I`), free segment maps (`FREE_I`), current segment arrays, checkpoint merge control, discard and flush command controls, extent cache structures, dirty inode counts, and compression mappings.

It integrates with Linux debugfs and seq_file APIs. It is conditional in two layers: the stats build/destroy routines are always present, while debugfs file creation and rendering helpers are compiled under `CONFIG_DEBUG_FS`.

## Risks And Edge Cases

The debugfs report reads many live fields. The code uses targeted locking for the global stats list and checkpoint timing, but many counters are read locklessly or through atomics. This is acceptable for observability but means output is a best-effort snapshot, not a transactionally consistent state.

Multi-device stats depend on correct device block ranges and segment conversion. Off-by-one mistakes would misclassify segments or sections in debug output. Online resize is handled by refreshing raw superblock main-area fields during status generation.

`f2fs_update_sit_info()` divides by a derived distribution denominator and then by `ndirty` only when `si->dirty_count` is nonzero. The code assumes dirty-count and `ndirty` remain coherent enough for diagnostic use.

Memory footprint reporting is approximate. `base_mem` is calculated once and may not reflect all dynamic structural changes after mount, while cache/page memory is refreshed.

## Test Signals

Validation should include mounting F2FS with `CONFIG_DEBUG_FS`, reading `/sys/kernel/debug/f2fs/status`, and confirming no lockdep splats or crashes across single-device, multi-device, compression-enabled, discard-enabled, and resize scenarios. Output should show sane segment totals, nonnegative dirty/free/prefree counts, extent-cache hit ratios matching workload behavior, and changing checkpoint/GC/IO counters under stress.

Unmount tests should confirm `f2fs_destroy_stats()` removes entries from the status output and frees per-device stats. Counter-reset tests should verify a newly mounted filesystem starts with zeroed debug counters where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/dir.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/dir.c

## Purpose

`dir.c` implements F2FS directory lookup, insertion, deletion, empty-directory checks, inode metadata initialization for directory entries, and readdir. It handles both inline dentries and regular dentry blocks, integrates fscrypt and Unicode casefolding, uses F2FS hash-directory layout, and updates parent/child metadata when links are created or removed.

The file provides the directory file operations table `f2fs_dir_operations`, with `iterate_shared` backed by `f2fs_readdir()` and fsync/ioctl delegated to shared F2FS handlers.

## Important APIs, Types, And Functions

Filename setup is handled by `f2fs_setup_filename()`, `f2fs_prepare_lookup()`, `__f2fs_setup_filename()`, `f2fs_init_casefolded_name()`, `f2fs_free_casefolded_name()`, and `f2fs_free_filename()`. These combine fscrypt name preparation, optional casefolded-name allocation, and F2FS dirhash calculation into `struct f2fs_filename`.

Hash-directory geometry helpers include `dir_blocks()`, `dir_buckets()`, `bucket_blocks()`, and `dir_block_index()`. Lookup helpers include `find_in_block()`, `f2fs_match_name()`, `f2fs_find_target_dentry()`, `find_in_level()`, `__f2fs_find_entry()`, `f2fs_find_entry()`, `f2fs_parent_dir()`, and `f2fs_inode_by_name()`.

Insertion and metadata setup are handled by `f2fs_do_make_empty_dir()`, `make_empty_dir()`, `f2fs_init_inode_metadata()`, `init_dent_inode()`, `f2fs_update_parent_metadata()`, `f2fs_room_for_filename()`, `f2fs_has_enough_room()`, `f2fs_update_dentry()`, `f2fs_add_regular_entry()`, `f2fs_add_dentry()`, `f2fs_do_add_link()`, and `f2fs_do_tmpfile()`.

Link removal and directory scanning are handled by `f2fs_drop_nlink()`, `f2fs_delete_entry()`, `f2fs_empty_dir()`, `f2fs_fill_dentries()`, and `f2fs_readdir()`.

## Control Flow

Lookup begins with `f2fs_find_entry()` or `f2fs_prepare_lookup()`. The name is prepared through fscrypt and optionally casefolded; encrypted no-key names can carry a predecoded hash. `__f2fs_find_entry()` searches inline dentries first when present. For regular directories, it walks hash levels up to `i_current_depth`, and `find_in_level()` selects the bucket from the hash, reads each dentry block with `f2fs_find_data_folio()`, and searches populated bitmap slots with `f2fs_find_target_dentry()`. If casefold compatibility fallback is enabled, a failed hash lookup in a casefolded directory retries with a linear scan.

Creation enters through `f2fs_do_add_link()`. It prepares the filename and, when the task differs from the last lookup task, rechecks the on-disk dentry to avoid lookup/create races from stackable filesystems. `f2fs_add_dentry()` tries inline insertion first under `i_xattr_sem`; if that returns `-EAGAIN`, `f2fs_add_regular_entry()` finds or allocates a regular dentry block at the appropriate hash level. It initializes child inode metadata if an inode is supplied, writes the dentry bitmap/name/inode/type fields, marks the dentry page dirty, records parent inode number in the child, updates the child inode page for new inodes, and updates parent depth/link/time metadata.

Directory inode initialization for new directories calls `make_empty_dir()`, which either uses inline dentry helpers or allocates the first data folio and writes `.` and `..` entries via `f2fs_do_make_empty_dir()`. `f2fs_init_inode_metadata()` also initializes ACLs, security xattrs, fscrypt context, directory-entry name information in the inode page, orphan handling for tmpfile link, and link counts.

Deletion through `f2fs_delete_entry()` updates request time, optionally records strict-fsync transition state, handles inline entries if needed, clears the dentry bitmap slots, marks the dentry folio dirty, and if the entire dentry block becomes empty, truncates the hole and clears page-cache dirty state. Parent times are updated and the victim inode link count is decremented through `f2fs_drop_nlink()`, which adds zero-link inodes to the orphan list.

`f2fs_readdir()` prepares fscrypt readdir state, handles inline directories through inline helpers, otherwise scans dentry blocks according to `ctx->pos`. It performs page-cache readahead for directory data pages, skips holes using `next_pgofs`, and delegates entry emission to `f2fs_fill_dentries()`. That function validates name lengths and bitmap slot boundaries, converts encrypted disk names to user names when needed, emits entries with `dir_emit()`, and optionally readaheads inode node pages for found entries.

## State And Persistence Behavior

Directory contents persist as inline dentry data inside inode pages or as regular dentry data blocks. Each dentry is represented by a bitmap slot range, `struct f2fs_dir_entry`, and name bytes. `f2fs_update_dentry()` sets the hash, name length, name bytes, target inode number, file type, and occupied slot bits; continuation slots have `name_len` cleared to avoid readdir garbage.

Directory hash growth is tracked by `F2FS_I(dir)->i_current_depth`, updated when insertion requires a deeper level. `chash` and `clevel` are transient hints that speed creation after lookup found room in a bucket.

Child inode metadata persists a copy of the disk name in `i_name`, parent inode number through `f2fs_i_pino_write()`, link counts, ACL/security/fscrypt context, and special encrypted-casefold hash suffix or `LOST_PINO` fallback for roll-forward recovery.

Deletion clears bitmap bits and may punch/truncate an empty dentry block. Link count updates, orphan list changes, and parent ctime/mtime changes persist through dirty inode/node pages and checkpoint/recovery mechanisms.

## Dependencies And Integration Points

`dir.c` depends on fscrypt, Unicode normalization/casefolding, generic VFS directory iteration, F2FS inline directory helpers, data folio helpers from `data.c`, inode/node metadata helpers, ACL and xattr initialization, orphan handling, tracepoints, and the page cache.

It integrates with mount options controlling lookup behavior (`LOOKUP_PERF`, `LOOKUP_COMPAT`, `LOOKUP_AUTO`), fsync behavior (`FSYNC_MODE_STRICT`), directory readahead (`sbi->readdir_ra`), and fault injection. It also interacts with checkpoint/recovery through orphan inodes, roll-forward name information, and transition-directory inode tracking.

## Risks And Edge Cases

Casefold plus encryption is the most complex name path. No-key encrypted names may provide only a decoded hash, strict Unicode encoding can reject invalid names, and encrypted casefolded filenames need special roll-forward recovery support because keys may be unavailable during recovery.

Hash-directory fallback behavior changes lookup coverage. In compatibility/auto modes, casefolded directories may perform a linear scan after hash lookup failure, which is slower but preserves compatibility with older hash behavior.

Dentry bitmap integrity is critical. `f2fs_fill_dentries()` detects zero name lengths after valid entries, slot overruns, and names longer than `F2FS_NAME_LEN`, then marks the filesystem needing fsck and reports corruption. Insert/delete paths must keep bitmap slots and continuation `name_len` fields coherent.

Creation has a deliberate race recheck when the creating task is not the task that performed lookup. Regressions there can allow duplicate dentries under stackable filesystem races.

Empty dentry block truncation in `f2fs_delete_entry()` changes both page-cache and block mapping state; it must correctly clear dirty accounting and private folio state after `f2fs_truncate_hole()`.

## Test Signals

Useful coverage includes lookup/create/unlink/rename workloads across inline and non-inline directories, encrypted directories with and without keys, casefolded directories under all lookup modes, strict Unicode rejection, tmpfile linking, directory fsync in strict mode, and recovery after fsync-created encrypted casefolded names.

Readdir tests should include holes in directory data, corrupted dentry name lengths, interrupted scans, encrypted name conversion, and readdir readahead. Consistency signals include correct link counts for `.`/`..`, parent times and depth updates, no duplicate dentries after racing create, and fsck-needed marking on detected corrupt dirents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/extent_cache.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/extent_cache.c

## Purpose

`extent_cache.c` implements F2FS in-memory extent caches. It supports read extents, which map contiguous logical file offsets to contiguous physical blocks, and block-age extents, which estimate update age for hot/warm/cold data placement. The implementation provides per-inode extent trees backed by rbtrees, global radix-tree ownership, LRU-style shrink lists, largest-read-extent persistence in the inode page, and debug counters.

The file accelerates mapping lookups in `data.c`, helps fiemap and read paths avoid repeated dnode traversal, records compressed read extents when supported, and feeds block-age policy without making the cache authoritative.

## Important APIs, Types, And Functions

Core structures are `struct extent_tree_info` per cache type in `sbi`, `struct extent_tree` per inode and type, `struct extent_node` per cached range, and `struct extent_info` for the range payload. Read extents use `fofs`, `len`, `blk`, and optional compressed length `c_len`; block-age extents use `fofs`, `len`, `age`, and `last_blocks`.

Initialization and teardown APIs include `f2fs_init_extent_cache_info()`, `f2fs_create_extent_cache()`, `f2fs_destroy_extent_cache()`, `f2fs_init_read_extent_tree()`, `f2fs_init_age_extent_tree()`, `f2fs_init_extent_tree()`, `f2fs_destroy_extent_node()`, `f2fs_drop_extent_tree()`, and `f2fs_destroy_extent_tree()`.

Lookup APIs include `f2fs_lookup_read_extent_cache()`, `f2fs_lookup_read_extent_cache_block()`, and `f2fs_lookup_age_extent_cache()`, all backed by `__lookup_extent_tree()` and rb helpers.

Update APIs include `f2fs_update_read_extent_cache()`, `f2fs_update_read_extent_cache_range()`, `f2fs_update_read_extent_tree_range_compressed()`, `f2fs_update_age_extent_cache()`, and `f2fs_update_age_extent_cache_range()`, all backed by `__update_extent_cache()` or `__update_extent_tree_range()`.

Memory-pressure APIs include `f2fs_shrink_read_extent_tree()` and `f2fs_shrink_age_extent_tree()`, both backed by `__shrink_extent_tree()`.

Internal helpers include `sanity_check_extent_cache()`, `__may_extent_tree()`, `__lookup_extent_node()`, `__lookup_extent_node_ret()`, `__attach_extent_node()`, `__detach_extent_node()`, `__release_extent_node()`, `__grab_extent_tree()`, `__free_extent_tree()`, `__try_merge_extent_node()`, `__insert_extent_tree()`, `__destroy_extent_node()`, `__drop_largest_extent()`, `__calculate_block_age()`, and `__get_new_block_age()`.

## Control Flow

Extent-cache setup starts with `f2fs_init_extent_cache_info()` for each superblock and `f2fs_create_extent_cache()` for global slab caches. Per-inode trees are created lazily through `__grab_extent_tree()` when mount options and inode type allow them. Read extent initialization can seed the tree from the on-disk largest extent stored in the inode page; if the inode is not eligible, the on-disk largest extent is cleared and `FI_NO_EXTENT` is set.

Lookup enters `__lookup_extent_tree()`. It first checks whether the inode may use the requested cache. For read extents, it checks the per-tree `largest` extent before the rbtree. It then checks the cached node and rbtree, copies the matching `extent_info`, updates hit counters, moves the node to the tail of the global LRU list, and updates `cached_en`.

Range updates enter `__update_extent_tree_range()`. The function locks the per-tree rwlock, drops overlapping largest-read extent state, finds the first overlapping or neighboring node, invalidates all overlapping nodes, possibly splitting existing nodes into left and right fragments, and then inserts or merges the new extent. For read extents, a nonzero `blk` inserts a logical-to-physical mapping; a zero `blk` invalidates a range. For block-age extents, invalid ranges can remove cache state, while valid age info is merged by age similarity rather than physical contiguity.

Compressed read extent updates use `f2fs_update_read_extent_tree_range_compressed()`, which inserts a read extent with a compressed length and avoids overwriting an existing node. Merge rules prevent unsafe merging when compressed logical length differs from compressed block length.

Shrinking first tries to free zombie extent trees from evicted inodes, then removes LRU extent nodes from active trees using trylocks. Destroy paths either move still-linked inode trees to the zombie list or free all nodes and remove the tree from the radix root.

## State And Persistence Behavior

Most extent-cache state is volatile. The rbtrees, cached node pointers, LRU lists, zombie lists, counters, and block-age extents are in-memory only and can be dropped under memory pressure or inode eviction.

The exception is the largest read extent stored in the inode page (`i_ext`). `f2fs_init_read_extent_tree()` reads it at inode setup, `__try_update_largest_extent()` updates in-memory largest state, and `__update_extent_tree_range()` marks the inode dirty when the largest extent changes or is dropped. `sanity_check_extent_cache()` validates this persisted largest extent against current block-device ranges.

`FI_NO_EXTENT` is used as a persistent/inode-state guard to disable extent caching for unsuitable or fragmented cases. Small split-heavy updates can cause read extent caching to be disabled for that inode.

Block-age state tracks `allocated_data_blocks`, `last_blocks`, and weighted age. It influences policy but is not persisted in inode metadata by this file.

## Dependencies And Integration Points

`extent_cache.c` depends on F2FS inode flags, mount options (`READ_EXTENT_CACHE`, `AGE_EXTENT_CACHE`), device layout, compression feature flags, rbtrees, radix trees, slab caches, atomic counters, rwlocks, mutexes, spinlocks, and tracepoints.

Its primary consumers are `data.c` block mapping and read/write paths: `f2fs_map_blocks()` uses read extents for fast non-creating lookups and precaching; `f2fs_get_read_data_folio()` and `f2fs_do_write_data_page()` use block lookup helpers; block-address updates call `f2fs_update_read_extent_cache()`. Segment allocation and hot/cold data policy can use block-age cache information.

Debugfs statistics in `debug.c` report extent tree, zombie tree, node counts, and hit ratios using counters maintained here.

## Risks And Edge Cases

Tree mutation is complex because a single update can split, delete, merge, and insert rb nodes. The code must keep the rbtree, cached node, largest extent, per-tree node count, global node count, and LRU list synchronized. The documented release flow is list removal, rbtree detach, then slab free.

Read extents must not represent invalid physical ranges. `sanity_check_extent_cache()` rejects invalid block addresses, meta-device aliases, zoned aliases, and device-alias extents that do not exactly match any device range.

Compressed extents have special merge constraints. If compressed length differs from logical length, naive adjacency merging could create incorrect mappings, so merge checks reject those cases.

`__may_extent_tree()` intentionally disables read extent caching for writable compressed files and block-age caching for compressed or cold files. Accidentally bypassing these checks could produce stale mappings or misleading age policy.

Shrinker paths use trylocks and may leave work for later. Tests should expect partial shrink progress, not complete reclamation in one call.

## Test Signals

Good tests include repeated sequential reads to confirm read extent hits, fragmented writes to verify invalidation and `FI_NO_EXTENT` behavior, fiemap/read paths after extent precaching, compressed readonly image reads, multi-device alias validation, and memory-pressure shrinker runs.

Instrumentation should show tracepoints for lookup, update, shrink, and destroy events; debugfs should report growing and shrinking tree/node counts and plausible L1/L2 hit ratios. Corruption tests should reject invalid persisted largest extents and mark/force repair through existing F2FS error handling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/extent_cache.c -->
