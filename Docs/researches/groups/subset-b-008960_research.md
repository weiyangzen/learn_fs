# subset-b-008960

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ext.c -->
# sources/storage-engines/wiredtiger/src/block/block_ext.c

## Purpose

`block_ext.c` owns WiredTiger block-manager extent-list mechanics: allocation, freeing, merging, overlap reconciliation, extent-list read/write, truncation eligibility, and diagnostic dumping. It is the allocator's in-memory model of file-space state, tracking live `alloc`, `avail`, `discard`, and checkpoint-derived lists as ordered skip lists.

## Important APIs, Types, and Functions

The central types are `WT_BLOCK`, `WT_EXTLIST`, `WT_EXT`, and `WT_SIZE`. `WT_EXTLIST` stores extents by offset and, when `track_size` is enabled, by size to support best-fit allocation. Important exported/internal-entry functions are `__wti_block_alloc`, `__wt_block_free`, `__wti_block_off_free`, `__wti_block_off_remove_overlap`, `__wti_block_extlist_overlap`, `__wti_block_extlist_merge`, `__wti_block_extlist_read_avail`, `__wti_block_extlist_read`, `__wti_block_extlist_write`, `__wt_block_extlist_can_truncate`, `__wti_block_extlist_truncate`, `__wti_block_extlist_init`, `__wti_block_extlist_free`, and `__wti_block_extlist_dump_all`.

Local helpers implement skip-list operations: `__block_off_srch`, `__block_size_srch`, `__block_off_srch_pair`, `__block_ext_insert`, `__block_off_remove`, `__block_append`, and `__block_merge`. `WT_BLOCK_RET` converts extent corruption into verify errors while panicking in normal operation.

## Control Flow

Allocation requires `block->live_lock`, validates allocation-size alignment, chooses first-fit by offset or best-fit by size, removes or shrinks an available extent, and records the allocation in `live.alloc`. If no suitable range exists, `__block_extend` advances `block->size` and appends to the allocation list.

Freeing unpacks an address cookie, ignores old tiered object IDs, and under `live_lock` routes the range through `__wti_block_off_free`. Ranges allocated in the current checkpoint are removed from `live.alloc` and immediately returned to `live.avail`; older ranges are merged into `live.discard` so checkpoint resolution can decide when they are reusable.

Extent-list persistence writes a block-manager page with packed offset/size pairs bracketed by `WT_BLOCK_EXTLIST_MAGIC` and `WT_BLOCK_INVALID_OFFSET`. Reads validate alignment and checkpoint file bounds before rebuilding skip lists. Available-list reads remove the block occupied by the extent-list page itself.

## State and Persistence Behavior

The file mutates in-memory file-space state (`block->size`, `WT_EXTLIST.entries`, `bytes`, `last`, offset/size skiplists) and persists checkpoint extent lists as pages in the same data file. `live.alloc`, `live.avail`, `live.discard`, `live.ckpt_avail`, and per-checkpoint extents encode the durable allocator history used across checkpoints. Truncation removes a terminal available extent and calls `__wti_block_truncate`, making free-at-end space disappear from both memory and the underlying file.

## Dependencies and Integration Points

The code integrates with address-cookie unpacking in `block_addr`, raw block I/O in `block_read.c`/`block_write.c`, checkpoint code in `block_ckpt.c`, compaction/truncation code, salvage and verify paths, session-local extent allocation caches from `block_session.c`, and WiredTiger stats/verbose logging. It relies on callers to hold `live_lock` for live list mutation except salvage.

## Risks and Edge Cases

Extent-list overlap is a correctness boundary: overlap in normal operation panics, while verify returns an error. Incorrect lock ownership can corrupt skip lists. Size-list and offset-list indexes must stay synchronized on every insert/remove. Old tiered objects currently cannot reclaim freed blocks, so free tracking for non-current object IDs is ignored. Large or fragmented available lists can make first-fit scans expensive, though the code records search walk time.

## Test Signals

Diagnostic builds exercise misplaced-block checks and list-overlap panics. Unit-test shims expose skip-list search, insert, remove, append, merge, and allocation helpers. Runtime signals include `block_alloc`, `block_free`, `block_extension`, `block_reuse_bytes`, extent-list verbose dumps, verify-layout output, and corruption paths that dump all extent lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_open.c -->
# sources/storage-engines/wiredtiger/src/block/block_open.c

## Purpose

`block_open.c` creates, opens, closes, drops, and sizes WiredTiger block files. It owns descriptor-block read/write validation, block-handle sharing through the connection block hash, open-time allocation configuration, file-system flags, live-restore metadata attachment, and basic block statistics.

## Important APIs, Types, and Functions

Public entry points include `__wt_block_manager_drop`, `__wt_block_manager_drop_object`, `__wt_block_manager_create`, `__wt_block_close`, `__wti_block_configure_first_fit`, `__wt_block_open`, `__wti_desc_write`, `__wt_block_stat`, `__wt_block_manager_size`, and `__wt_block_manager_named_size`. The private `__desc_read` validates the first allocation-sized descriptor block, and `__file_is_wt_internal` distinguishes metadata/history-store files for salvage-oriented errors.

## Control Flow

Creation opens a new durable exclusive file, renames unexpected leftovers aside with numeric suffixes, writes the descriptor, fsyncs, closes, and removes the file on error. Open first searches `conn->blockhash` under `conn->block_lock` for an existing `WT_BLOCK` matching filename and object ID. If absent, it allocates and configures a new handle, opens the file, attaches live-restore metadata to the file handle, records current file size, initializes `live_lock`, verifies the descriptor unless forced salvage is requested, then inserts the handle into the connection hash.

`__desc_read` reads the descriptor block, performs endian-aware checksum validation, checks magic and supported major/minor versions, handles rollback-to-stable by returning `ENOENT` for too-small/corrupt files, and marks connection data corruption for general corruption cases.

## State and Persistence Behavior

The descriptor block is the durable file identity record: magic, block major/minor versions, allocation-size-sized checksum, and endian-normalized layout. Open initializes `WT_BLOCK` fields such as `name`, `objectid`, `allocsize`, `allocfirst`, `os_cache_max`, `os_cache_dirty_max`, `extend_len`, `size`, `readonly`, and `created_during_backup`. Handles are reference-counted and shared until `__wt_block_close` destroys locks, checkpoint state, file handles, and memory.

## Dependencies and Integration Points

This file sits under the block-cache open path, tiered-object open path, live restore, the WiredTiger file-system API, config parsing, connection block-hash locking, incremental backup, rollback-to-stable, import repair, and data-source statistics. `__wti_desc_write` is also used by salvage to reset the file descriptor.

## Risks and Edge Cases

Open error handling must unlock `conn->block_lock` and close partially initialized handles. Descriptor validation intentionally behaves differently for rollback-to-stable, internal files, import repair, and forced salvage. Renaming unexpected files on create handles non-transactional schema leftovers but can surprise external users writing in WiredTiger's namespace. `allocfirst` is an atomic counter because multiple operations can request first-fit allocation concurrently.

## Test Signals

Signals include descriptor checksum/magic/version failures, create with leftover files, forced salvage skipping descriptor reads, rollback-to-stable corrupt-file paths, first-fit configuration races, and statistics populated by `__wt_block_stat` (`allocation_size`, `block_checkpoint_size`, `block_reuse_bytes`, and `block_size`).
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_read.c -->
# sources/storage-engines/wiredtiger/src/block/block_read.c

## Purpose

`block_read.c` implements physical block reads for file-backed block handles. It unpacks address cookies, reads aligned disk blocks, validates checksums, swaps headers to native endian order, reports corruption, optionally diagnoses single-bit flips, and dumps filesystem free-space and extent-list context on checksum failures.

## Important APIs, Types, and Functions

Key functions are `__wt_bm_read`, `__wt_bm_corrupt`, diagnostic `__wt_block_read_off_blind`, `__wti_block_read_off`, and private `__block_bitflip_detect` plus `__fs_free_space_dump`. It consumes `WT_BLOCK_HEADER`, `WT_PAGE_HEADER`, `WT_BM`, `WT_BLOCK`, and address-cookie fields `(objectid, offset, size, checksum)`.

## Control Flow

`__wt_bm_read` unpacks the address cookie, resolves a tiered/multi-handle object if needed, runs diagnostic misplaced-block checks, delegates to `__wti_block_read_off`, discards OS cache when configured, and releases tiered read handles. `__wti_block_read_off` validates minimum size, allocates the destination buffer, throttles read capacity, reads from the file handle, byte-swaps a copy of the block header, chooses full-data versus prefix checksum based on `WT_BLOCK_DATA_CKSUM`, clears the stored checksum before recomputation, and swaps the page header before returning.

On mismatch, it logs differentiated full-checksum or header-checksum messages, dumps the corrupt block, dumps free disk space, optionally searches for a single-bit flip, sets connection data-corruption state, returns `WT_ERROR` for verify/quiet-corrupt paths, or panics during normal reads.

## State and Persistence Behavior

Normal reads do not mutate durable state, but they update connection statistics, session buffers, read histograms, and OS cache-discard counters. Corruption paths set `WT_CONN_DATA_CORRUPTION` and may emit diagnostic data dumps. Multi-handle reads manipulate `block->read_count` through tiered handle acquisition/release and can trigger handle sweeping after the last release.

## Dependencies and Integration Points

This code is below `block_cache/block_io.c` and the `WT_BM.read` method table. It uses block address packing/unpacking, file-system reads, capacity throttling, checksum utilities, verbose logging, diagnostic extent-list dumping from `block_ext.c`, tiered handle management from `block_tier.c`, and log-manager paths for journal free-space diagnostics.

## Risks and Edge Cases

Read sizes smaller than allocation size are rejected. Partial checksums intentionally protect only the uncompressed/unencrypted prefix, so upper layers must correctly decompress/decrypt. `__block_bitflip_detect` mutates the buffer while testing and restores each bit; it is bounded by `WT_BITFLIP_MAX_SIZE` to avoid excessive CPU. Quiet corruption and verify modes must not panic. Multi-handle release must happen on all read paths to avoid preventing tiered-handle sweeping.

## Test Signals

Useful tests include checksum mismatch paths, compressed/encrypted checksum mode behavior, diagnostic blind reads, quiet-corrupt verify reads, single-bit-flip detection through the unit-test shim, free-space logging when the file-system hook succeeds or fails, and stats `block_read`, `block_byte_read`, `block_map_read`, and read latency histograms.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_session.c -->
# sources/storage-engines/wiredtiger/src/block/block_session.c

## Purpose

`block_session.c` provides session-local caches for block-manager extent structures. It reduces allocation churn for `WT_EXT` and `WT_SIZE` objects used by extent lists, with cleanup hooks tied to the session's block-manager state.

## Important APIs, Types, and Functions

The main exported helpers are `__wti_block_ext_alloc`, `__wti_block_ext_free`, `__wti_block_size_alloc`, `__wti_block_size_free`, `__wti_block_ext_prealloc`, and `__wti_block_ext_discard`. Private helpers include `__block_ext_alloc`, `__block_ext_prealloc`, `__block_ext_discard`, `__block_size_alloc`, `__block_size_prealloc`, `__block_size_discard`, and `__block_manager_session_cleanup`.

`WT_BLOCK_MGR_SESSION` holds `ext_cache`, `ext_cache_cnt`, `sz_cache`, and `sz_cache_cnt`. `WT_EXT` allocations include variable space for two pointer arrays per skip-list depth.

## Control Flow

Allocations first try the session cache. Reused `WT_EXT` nodes have both offset and size skip-list links cleared for their depth. If no cache exists, allocation falls back to heap allocation with a randomly chosen skip-list depth. Preallocation lazily creates `session->block_manager`, installs `session->block_manager_cleanup`, and fills both caches to a requested minimum. Freeing returns objects to the cache when available, or directly frees them if no block-manager session cache exists.

Discard trims caches to a maximum or fully drains them during cleanup. Cleanup drains both caches and frees the `WT_BLOCK_MGR_SESSION`.

## State and Persistence Behavior

This file is purely in-memory. It persists no file content, but it materially affects checkpoint/allocation performance by retaining extent/list nodes across operations in a session. Cache counts are advisory and checked for consistency only on full discard.

## Dependencies and Integration Points

The extent allocator in `block_ext.c` calls these helpers for every `WT_EXT`/`WT_SIZE` insert/remove. Checkpoint and free paths preallocate a small number of entries before acquiring or while holding allocator locks, reducing failure windows during list mutation. The session cleanup hook integrates with the broader session lifecycle.

## Risks and Edge Cases

Cache-count drift is tolerated during normal operation but reported on full cleanup. Reused `WT_SIZE` nodes are not explicitly cleared in this file beyond being removed from the free list, so callers must initialize fields before insertion. `__wti_block_ext_discard` assumes `session->block_manager` exists; callers should only use it after preallocation or initialization. Failure during preallocation can leave a partially filled but valid cache.

## Test Signals

Unit-test shims expose allocation, preallocation, discard, and cleanup helpers. Runtime validation comes from memory diagnostics, cache count consistency on cleanup, and extent-list correctness under allocation-heavy checkpoint/free workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_slvg.c -->
# sources/storage-engines/wiredtiger/src/block/block_slvg.c

## Purpose

`block_slvg.c` implements physical-file salvage iteration for file-backed block handles. It rewrites descriptor metadata, rebuilds a live checkpoint from pages that can still be read and validated, and frees skipped allocation-size fragments.

## Important APIs, Types, and Functions

Important functions are `__wt_block_salvage_start`, `__wt_block_salvage_end`, `__wti_block_offset_invalid`, `__wt_block_salvage_next`, and `__wt_block_salvage_valid`. It uses `WT_BLOCK.slvg_off`, `WT_BLOCK.live.alloc`, `WT_BLOCK.ckpt_state`, `WT_BLOCK_HEADER.disk_size`, address-cookie pack/unpack helpers, and raw read/free functions.

## Control Flow

Salvage start rewrites the descriptor block, initializes the live checkpoint, truncates the file to an allocation-size multiple, starts scanning after the descriptor block, places the rest of the file on `live.alloc`, and marks checkpoint state `WT_CKPT_SALVAGE`.

`__wt_block_salvage_next` reads one allocation-sized header at `slvg_off`, obtains the candidate disk size/checksum, rejects insane offsets with `__wti_block_offset_invalid`, and calls `__wti_block_read_off` to validate the full block. Invalid candidates free one allocation-size unit and advance. Valid candidates are returned as reconstructed address cookies. `__wt_block_salvage_valid` is the upper-layer feedback loop: accepted blocks advance past the full block, rejected candidates free one allocation-size unit and advance.

## State and Persistence Behavior

Salvage mutates the file descriptor, may truncate trailing garbage, rebuilds allocator state in memory, and frees skipped fragments into the live checkpoint's extent accounting. Salvage itself behaves like a checkpoint without the normal checkpoint start/resolve lifecycle; `__wt_block_salvage_end` resets state and unloads the checkpoint.

## Dependencies and Integration Points

The `WT_BM` method table in `block_mgr.c` exposes these routines to higher-level salvage. The file depends on descriptor write/open logic, checkpoint initialization/unload, extent insertion/freeing, block reads/checksums, and address-cookie packing. Tiered salvage is explicitly not implemented; object ID is forced to zero.

## Risks and Edge Cases

Salvage trusts only allocation-size stepping, so a valid page not aligned at the current scan boundary will be skipped. Rejected valid-size candidates only free one allocation-size unit rather than the candidate's full size. Because it rewrites descriptors and truncates files, it is not a read-only operation. It must avoid normal checkpoint state transitions while still leaving a coherent checkpoint for recovered pages.

## Test Signals

Signals include salvage over files with trailing garbage, checksum-corrupt blocks, valid pages after invalid fragments, upper-layer rejection through `salvage_valid(false)`, and final checkpoint unload. `WT_VERB_SALVAGE` logs skipped allocation-size chunks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_slvg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_vrfy.c -->
# sources/storage-engines/wiredtiger/src/block/block_vrfy.c

## Purpose

`block_vrfy.c` verifies physical block-file layout against checkpoint metadata and B-tree traversal. It tracks allocation-size fragments in bitmaps to detect duplicate references, missing references, references beyond checkpoint/file size, and corrupted extent lists.

## Important APIs, Types, and Functions

Entry points are `__wt_block_verify_start`, `__wt_block_verify_end`, `__wti_verify_ckpt_load`, `__wti_verify_ckpt_unload`, and `__wt_block_verify_addr`. Private helpers include `__verify_last_avail`, `__verify_set_file_size`, `__verify_filefrag_add`, `__verify_filefrag_chk`, `__verify_ckptfrag_add`, and `__verify_ckptfrag_chk`. Macros `WT_wt_off_TO_FRAG` and `WT_FRAG_TO_OFF` translate between file offsets and bitmap positions, excluding the descriptor block.

## Control Flow

Verify start parses `strict`, `dump_layout`, and `dump_tree_shape`, selects the last real checkpoint, sets `block->size` to that checkpoint's durable file size, validates allocation-size alignment, allocates the per-file fragment bitmap, marks the handle as verifying, initializes `verify_alloc`, and loads the last checkpoint's available list into the file-fragment bitmap.

For each checkpoint load, verification records root/extent-list blocks as seen, merges checkpoint allocation extents into accumulated `verify_alloc`, removes discard extents, reads available extents for corruption checking, removes the checkpoint root from accumulated allocation, then builds a per-checkpoint bitmap of expected blocks. During B-tree verification, `__wt_block_verify_addr` marks file fragments and clears checkpoint fragments. Checkpoint unload and verify end report any remaining expected or missing ranges.

## State and Persistence Behavior

Verification is read-only for disk content but mutates `WT_BLOCK` verification state: `verify`, `verify_strict`, `verify_layout`, `dump_tree_shape`, `verify_size`, `frags`, `fragfile`, `fragckpt`, and `verify_alloc`. It intentionally overrides `block->size` to the last checkpoint's file size so references beyond the checkpoint fail even if the physical file has grown.

## Dependencies and Integration Points

The file integrates with checkpoint unpacking/loading, extent-list reads and merges, B-tree verify traversal, block read corruption behavior, verbose layout dumping, and bitmap helpers. It depends on `block_ext.c` to avoid panics during verification via `block->verify`.

## Risks and Edge Cases

Bitmap size scales with file size divided by allocation size; very large files with small allocation units can consume significant memory. Missing trailing fragments are tolerated because files may have been extended or truncated after the checkpoint; missing interior fragments are errors or warnings depending on strict mode. Duplicate checks differ between per-file and per-checkpoint maps because blocks can appear in multiple checkpoints but not multiple times in one checkpoint.

## Test Signals

Tests should cover strict versus non-strict missing-fragment behavior, duplicate references within one checkpoint, last-checkpoint available-list validation, corrupted extent lists returning verify errors rather than panics, references beyond checkpoint/file size, and `dump_layout` verbose output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_vrfy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_write.c -->
# sources/storage-engines/wiredtiger/src/block/block_write.c

## Purpose

`block_write.c` implements physical writes to file-backed block handles. It aligns page images to allocation units, allocates file space, optionally extends/truncates OS-visible file size, computes block checksums, writes disk blocks, updates cache/fsync behavior, and returns address-cookie components.

## Important APIs, Types, and Functions

Important functions are `__wti_block_truncate`, `__wti_block_discard`, `__wt_block_write_size`, `__wt_block_write`, `__wti_block_write_off`, and private `__block_extend`/`__block_write_off`. It manipulates `WT_BLOCK_HEADER`, `WT_PAGE_HEADER`, `WT_BLOCK.size`, `extend_size`, `extend_len`, `os_cache`, and `WT_FH.written`.

## Control Flow

`__wt_block_write_size` adds the block-manager header and rounds up to `block->allocsize`, rejecting sizes near 4 GiB. `__wt_block_write` calls `__wti_block_write_off`, then packs `(objectid, offset, size, checksum)` into an address cookie. `__wti_block_write_off` byte-swaps the page header around the internal write so callers keep native-order page images.

The internal write optionally adds final-checkpoint recovery data, aligns size, preallocates extent nodes, acquires `live_lock` if needed, allocates space through `__wti_block_alloc`, optionally extends the file outside the lock when supported, zeros alignment padding, initializes the block header, computes either full-data or prefix checksum, writes to the file handle, frees the allocation on write failure, optionally fsyncs dirty OS cache, discards from OS cache, updates statistics, and returns offset/size/checksum.

## State and Persistence Behavior

Successful writes persist an endian-normalized block header plus page image bytes to the data file and mutate allocator state by consuming/creating extents. `block->size` is advanced before the actual write, and failures free the allocated range back through allocator logic. `__wti_block_truncate` updates in-memory size even when physical truncate is unsupported or temporarily busy, because truncation is an optimization rather than a correctness requirement.

## Dependencies and Integration Points

This file depends on extent allocation/freeing, checkpoint-final metadata, address packing, capacity throttling, file-system write/extend/truncate/fsync/advise hooks, hot-backup locks, OS cache settings, and block-cache write wrappers that handle compression/encryption before physical writes.

## Risks and Edge Cases

File extension can release `live_lock`, so callers must honor the `caller_locked` contract. `block->size` can move ahead of durable writes, making failure cleanup essential. Prefix checksums rely on compression/encryption layers to detect payload corruption. Truncation and extension are skipped during hot backup and tolerate `EBUSY`/`ENOTSUP`. Incorrect buffer sizing before alignment is treated as a caller bug.

## Test Signals

Signals include allocation-size rounding, oversized write rejection, write-failure cleanup, full versus prefix checksum reads, hot-backup truncate/extend suppression, OS dirty-cache fsync scheduling, `block_write` and `block_byte_write_checkpoint` stats, and final checkpoint writes that patch file-size metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_cache.c -->
# sources/storage-engines/wiredtiger/src/block_cache/block_cache.c

## Purpose

`block_cache.c` implements the optional WiredTiger block cache and the block-manager open/setup entry point. It provides DRAM/NVRAM allocation, hash-bucket lookup/insert/remove, reference-safe eviction, cache bypass heuristics, cache destruction, configuration parsing, and `WT_BM` creation for file, tiered, or disaggregated objects.

## Important APIs, Types, and Functions

Important routines are `__wti_blkcache_get`, `__wti_blkcache_put`, `__wt_blkcache_remove`, `__wt_blkcache_destroy`, `__wt_blkcache_open`, and `__wt_blkcache_setup`. Private helpers include `__blkcache_alloc`, `__blkcache_free`, `__blkcache_should_evict`, `__blkcache_eviction_thread`, `__blkcache_estimate_filesize`, `__blkcache_init`, and `__blkcache_reconfig`. Core types are `WT_BLKCACHE`, `WT_BLKCACHE_ITEM`, `WT_BLKCACHE_DELTA`, `WT_BM`, and per-bucket spin locks.

## Control Flow

Lookup checks NVRAM bypass heuristics, hashes by address cookie plus btree file ID, locks the bucket, increments reference and frequency counters on hit, and tells callers whether subsequent put should be skipped. Put checks capacity and NVRAM overhead, copies page data and optional deltas outside the bucket lock, detects duplicate read inserts, inserts at the bucket head, and updates byte/block stats. Remove unlinks by address, waits for active references to drain, frees base/delta/meta buffers, and updates histograms/stats.

The eviction thread wakes once per second, scans buckets, decrements frequency/recency counters, avoids referenced blocks, avoids NVRAM eviction during high churn, and evicts least-reused stale blocks once the cache is above `full_target`.

`__wt_blkcache_open` delegates disaggregated URIs to the disaggregated manager, opens file URIs through `__wt_block_open`, or initializes a tiered multi-handle `WT_BM` with a handle array. `__wt_blkcache_setup` parses block-cache config, but currently logs a warning and returns without enabling when `block_cache.enabled` is true.

## State and Persistence Behavior

The cache is process-local and non-durable. It stores copied block images, optional delta arrays, page block metadata, file IDs, address bytes, reference counts, frequency counters, and global byte counters. NVRAM mode allocates from a memkind persistent-memory arena, but the cache contents are still managed as runtime cache state and destroyed on shutdown.

## Dependencies and Integration Points

This file is used by `block_io.c` read/write wrappers, `block_mgr.c` free paths, connection initialization/reconfiguration, tiered-object open, disaggregated object ownership, statistics, verbose logging, memkind when enabled, and the connection block-handle hash for file-size estimates.

## Risks and Edge Cases

The cache is currently disabled by setup even when configured, so code may be less exercised. Duplicate insert handling assumes write collisions are impossible outside diagnostics. Removal busy-waits until `ref_count` drains. Some counters intentionally race for speed. NVRAM bypass depends on approximate file-size and overhead estimates. Reconfiguration only accepts identical settings and rejects meaningful changes.

## Test Signals

Test signals include cache hit/miss stats, duplicate read insert path, removal waiting for references, eviction above `full_target`, NVRAM unsupported builds returning configuration errors, setup's disabled warning, destroy-time nonzero ref-count errors, and reference histograms printed on destroy.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_io.c -->
# sources/storage-engines/wiredtiger/src/block_cache/block_io.c

## Purpose

`block_io.c` is the high-level block I/O adapter between B-tree pages and `WT_BM` physical managers. It performs mapped reads, block-cache reads, multi-read delta handling, compression, decompression, encryption, decryption, checksum policy selection, statistics, corruption escalation, and block-cache write allocation.

## Important APIs, Types, and Functions

Public functions are `__wt_blkcache_read`, `__wt_blkcache_read_multi`, `__wt_blkcache_compress`, and `__wt_blkcache_write`. Important private helpers are `__blkcache_read_corrupt`, `__blkcache_read_decrypt`, `__blkcache_cache_wants_encrypted_data`, and `__read_decompress`. It uses `WT_BM`, `WT_BTREE`, `WT_BLKCACHE_ITEM`, `WT_PAGE_BLOCK_META`, `WT_PAGE_HEADER`, `WT_BLOCK_DISAGG_HEADER`, compressors, encryptors, and delta arrays.

## Control Flow

Single-read first chooses a scratch buffer when conversion is expected, tries memory mapping, then block cache, then `bm->read` or `bm->read_multiple`. Disk reads update page-type and cache-read stats before conversion. It rejects unencrypted disk blocks when encryption is configured, optionally decrypts, inserts an encrypted or decrypted image into block cache depending on cache type, decompresses if needed, copies into the caller buffer, and physically verifies pages when the btree is in verify mode.

Multi-read returns base plus deltas. If the physical manager lacks `read_multiple`, it falls back to single-read with one result. Otherwise it can fetch cached base/deltas, or call the manager, decrypt/decompress the base image, then decrypt/decompress each delta using disaggregated block-header flags. Results are returned as an allocated `WT_ITEM` array.

Writes compress when configured and beneficial, encrypt when configured, derive data-checksum policy from the btree checksum mode, call either checkpoint or normal `WT_BM` write, update cache/write statistics, and optionally insert written page images into the block cache unless disabled, checkpoint-bypassed, no-write-allocate, final-checkpoint, or delta-bearing.

## State and Persistence Behavior

This layer persists data indirectly through `WT_BM.write`/`checkpoint`, and it mutates runtime caches, stats, scratch buffers, returned `WT_ITEM` ownership, and page flags (`WT_PAGE_COMPRESSED`, `WT_PAGE_ENCRYPTED`). It can store encrypted images in NVRAM cache and decrypted images in DRAM cache. It does not itself own file allocation state.

## Dependencies and Integration Points

The file integrates compressors, encryptors, block cache, block mapping, disaggregated multi-block reads, physical `WT_BM` methods, verification, WiredTiger cache/session stats, and corruption handling that calls `bm->corrupt` then panics outside verify/quiet-corrupt mode.

## Risks and Edge Cases

Buffer ownership in multi-read is subtle: cached data is borrowed until ref-count release, while disk-read results are freed or moved into the returned array. Compression ratio calculations divide by compressed lengths and assume meaningful sizes. Decompression passes `tmp->size` in the single-read path, so scratch-buffer state must match the source image. Deltas are cached but write-side block-cache insertion currently ignores delta-bearing writes. Encryption skip size depends on the block-manager method.

## Test Signals

Tests should cover compressed and encrypted read/write combinations, missing compressor/decryptor corruption, unencrypted disk data with configured encryption, mapped-read bypass, block-cache hit with conversion, multi-read base plus deltas, checksum policy modes, cache-on-checkpoint/cache-on-writes bypass stats, and verify-mode physical page validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_map.c -->
# sources/storage-engines/wiredtiger/src/block_cache/block_map.c

## Purpose

`block_map.c` provides memory-mapped read support for read-only block handles. It maps an underlying file when allowed, unmaps it, and services address-cookie reads directly from the mapped region with optional preload.

## Important APIs, Types, and Functions

The file exports `__wti_blkcache_map`, `__wti_blkcache_unmap`, and `__wti_blkcache_map_read`. It uses `WT_BM.map`, `maplen`, `mapped_cookie`, `WT_BLOCK.verify`, `WT_BLOCK.os_cache_max`, `WT_FILE_HANDLE.fh_map`, `fh_unmap`, and `fh_map_preload`.

## Control Flow

Mapping returns no-op success unless connection mmap is enabled, verify is not active, OS cache limits are not configured, and the file handle supports `fh_map`. Unsupported or busy mapping failures are treated as cache-read fallback. Map reads check that the current `WT_BM` is mapped, assert it is not multi-handle or remote, unpack the address cookie, assert object ID matches the single block handle, and if the requested range lies within the map and preloading succeeds, point the caller buffer at mapped bytes.

## State and Persistence Behavior

This file does not change durable state. It stores mapped-region pointers and cookies in `WT_BM` and can return buffers that alias the mapped file instead of owned memory. It increments mapped-read statistics when successful.

## Dependencies and Integration Points

`block_mgr.c` invokes mapping when loading read-only checkpoints. `block_io.c` tries map reads before block-cache or disk reads. The file depends on file-system mapping hooks and address-cookie unpacking from the file-backed block manager.

## Risks and Edge Cases

Mapping is disabled during verify because mapped reads skip checksum validation. It is disabled when `os_cache_max` is configured because cache usage cannot be controlled. Multi-handle tiered and remote objects are unsupported. Callers must treat mapped buffers as borrowed memory tied to the mapped handle lifetime.

## Test Signals

Signals include successful checkpoint mapping, fallback when mmap is disabled or `fh_map` returns `ENOTSUP`/`EBUSY`, verify disabling mapped reads, object-ID assertions for non-tiered handles, and `block_map_read`/`block_byte_map_read` stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_mgr.c -->
# sources/storage-engines/wiredtiger/src/block_cache/block_mgr.c

## Purpose

`block_mgr.c` builds the `WT_BM` method table used by the B-tree layer and adapts generic block-manager operations to file-backed, read-only checkpoint, tiered multi-handle, block-cache, compaction, salvage, verify, and sync behavior.

## Important APIs, Types, and Functions

Externally visible functions are `__wti_bm_close_block`, `__wt_bm_sweep_handles`, `__wti_bm_method_set`, and `__wt_bm_set_readonly`. Private method implementations cover address validation/stringification, checkpoint lifecycle, close, compaction, encryption skip, free, mapped-state, read, salvage, stat, tiered object switching, sync, verify, write, write-size, and truncation checks. Important fields include `WT_BM.block`, `prev_block`, `next_block`, `handle_array`, `is_live`, `is_multi_handle`, `map`, and `max_flushed_objectid`.

## Control Flow

`__wti_bm_method_set` installs normal methods, then replaces mutating methods with read-only stubs for checkpoint handles. Normal reads and writes delegate to `__wt_bm_read` and `__wt_block_write`; free removes cached blocks then frees file space. Checkpoint load marks live versus checkpoint handles, loads block checkpoint metadata, optionally maps read-only single-file checkpoints, and switches the method table to read-only for checkpoint handles.

Tiered switching opens the requested object, loads its checkpoint, marks the current block for sync, and delays the active-handle swap until checkpoint write when eviction is disabled. Sync ensures pending switches have happened, fsyncs previous tiered handles as needed, and handles `prev_block`. Sweeping closes non-active tiered handles whose read count is zero and whose object ID is older than the maximum flushed object.

## State and Persistence Behavior

The file mutates `WT_BM` runtime method pointers and tiered handle arrays, reference counts in `WT_BLOCK`, `sync_on_checkpoint`, `prev_block`/`next_block`, mapped-region state, and `max_flushed_objectid`. Durable effects occur through delegated checkpoint, write, free, compact, salvage, fsync, and truncate operations.

## Dependencies and Integration Points

It integrates file-backed block APIs, block cache removal, mapping, tiered handle helpers, checkpoint code, compaction, salvage, verify, the B-tree `WT_BM` interface, connection block hash, checkpoint lock, capacity throttling, and filesystem fsync.

## Risks and Edge Cases

Read-only method replacement is a safety boundary for checkpoint handles. Tiered object switches are intentionally delayed; missing the checkpoint-time switch triggers an assertion in sync. Sweeping uses an array and `memmove`, noted as potentially slow with many handles. Closing a block during checkpoint is disallowed except panic-on-failure state. Cached block removal must happen before freeing disk space to avoid stale reads.

## Test Signals

Tests should exercise method-table read-only behavior, checkpoint load/unload mapping, tiered switch scheduling and completion, fsync of previous active tiered files, handle sweeping after last reader release, block-cache removal on free, compaction/salvage/verify readonly stubs, and `can_truncate` forwarding to available extents.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_tier.c -->
# sources/storage-engines/wiredtiger/src/block_cache/block_tier.c

## Purpose

`block_tier.c` opens and manages block handles for tiered storage objects. It resolves local versus shared-object names, opens remote bucket-backed objects when not present locally, manages the `WT_BM` tiered handle array, and tracks active readers so old object handles can be swept safely.

## Important APIs, Types, and Functions

Key functions are `__wti_blkcache_tiered_open`, `__wt_blkcache_get_handle`, `__wti_blkcache_get_read_handle`, and `__wt_blkcache_release_handle`. Private `__blkcache_find_open_handle` searches a `WT_BM` handle array and optionally increments `WT_BLOCK.read_count`.

Important types and fields are `WT_TIERED.current_id`, `WT_TIERED.tiers`, `WT_BUCKET_STORAGE`, `WT_BM.handle_array`, `handle_array_lock`, and `WT_BLOCK.remote`.

## Control Flow

Tiered open treats URI-based opens as the current local object and object-ID opens as historical objects. Current objects use the local `file:` tier and open read-write. Historical objects derive an `object:` URI, load metadata, check for a local copy, and otherwise compose `bucket_prefix + object_name`, switch into bucket storage, open read-only/fixed, and mark the block remote.

`__wt_blkcache_get_handle` first searches under a read lock. On miss it opens a new handle without holding the array write lock, then takes the write lock, checks for a racing insert, and appends the new handle or closes the duplicate. Read acquisitions increment `read_count`; release decrements and reports whether this was the last reader.

## State and Persistence Behavior

This file does not write data pages directly. It mutates runtime block-handle arrays, per-handle read counts, and remote/read-only flags. Opening remote objects may access bucket storage and local metadata. It relies on metadata configuration to locate objects and bucket prefixes.

## Dependencies and Integration Points

It is used by `block_cache.c` open for tiered trees, `block_read.c` for multi-handle reads, and `block_mgr.c` for tiered switching/sweeping. It depends on tiered metadata naming, bucket-storage file systems, `__wt_block_open`, read/write locks, and block close.

## Risks and Edge Cases

Current-object opens assert that racing `current_id` changes are impossible except under checkpoint-lock protection. The open-without-array-lock path avoids blocking but must close duplicate handles after races. Historical remote objects are read-only. Read-count correctness controls when old handles can be swept; leaks prevent cleanup and premature release risks closing a handle under readers.

## Test Signals

Tests should cover local current-object open, historical object open from local cache, remote bucket open with prefix, racing handle insertion, read-count last-release behavior, and sweeping eligibility after `max_flushed_objectid` advances.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_cache/block_tier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_addr.c -->
# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_addr.c

## Purpose

`block_disagg_addr.c` packs, unpacks, validates, formats, and checkpoint-wraps disaggregated-storage address cookies. It defines version compatibility behavior, optional debug upgrade/downgrade fields, supported flag masking, compact LSN/base-LSN encoding, and root checkpoint cookie serialization.

## Important APIs, Types, and Functions

Main functions are `__wti_block_disagg_addr_pack`, `__wt_block_disagg_addr_unpack`, `__wti_block_disagg_addr_invalid`, `__wti_block_disagg_addr_string`, `__wti_block_disagg_ckpt_pack`, and `__wti_block_disagg_ckpt_unpack`. Private helpers are `__block_disagg_addr_debug_upgrade`, `__block_disagg_addr_pack_version`, and `__block_disagg_addr_unpack_version`. The core type is `WT_BLOCK_DISAGG_ADDRESS_COOKIE` with `page_id`, `flags`, `lsn`, `base_lsn`, `size`, and `checksum`.

## Control Flow

Packing asserts a valid page ID and positive size, masks flags to `WT_BLOCK_DISAGG_ADDR_ALL_FLAGS`, optionally adds a debug optional flag, stores `base_lsn` as `lsn - base_lsn`, writes version/min-version, variable-length fields, fixed 32-bit checksum, and optional debug fields.

Unpacking computes the current readable version with debug settings, reads version/min-version, rejects cookies whose minimum version is newer than the reader, unpacks fields and checksum, validates debug fields when present, reconstructs `base_lsn`, rejects underflow, invalid page IDs, and zero size, returns only supported flags, and enforces exact cookie-size matching only for supported versions with no unsupported flags or optional debug field.

Checkpoint pack/unpack simply serialize or deserialize the root page's disaggregated address cookie into metadata checkpoint bytes.

## State and Persistence Behavior

Address cookies are durable metadata references to disaggregated page images and deltas. The format stores page identity, flags, LSN, base LSN delta, total size, and checksum. Debug knobs can intentionally write compatible or incompatible future-looking cookies to test upgrade behavior.

## Dependencies and Integration Points

This file is used by disaggregated read, write, checkpoint, and address-string methods. It depends on WiredTiger variable-length integer packing, fixed integer packing, connection debug settings, flag macros, and `WT_BM` address APIs. `block_cache/block_io.c` consumes disaggregated flags and sizes during multi-read delta handling.

## Risks and Edge Cases

Version compatibility is subtle: unsupported optional flags permit forward-compatible parsing only when size checks are relaxed. `lsn` must be greater than `base_lsn` during pack and not underflow during unpack. Returning only supported flags hides unknown flags from older readers by design. Debug optional fields alter size-check behavior and must not leak into production assumptions.

## Test Signals

Tests should cover normal pack/unpack round trips, compatible version bump, incompatible minimum-version rejection, optional-field parsing, unsupported flags with relaxed size checks, size mismatch errors, invalid page ID, zero size, LSN/base-LSN underflow, printable address strings, and checkpoint root cookie pack/unpack.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_addr.c -->
