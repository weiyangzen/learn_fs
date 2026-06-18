# Research: subset-b-004029

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.c

## Purpose

`block-map.c` implements VDO's logical-to-physical block map. It combines a per-logical-zone leaf-page cache with an in-memory forest of radix trees that point to allocated block-map pages. The file is responsible for finding or allocating the block-map slot for a logical block, loading and writing block-map pages, tracking dirty pages by recovery-journal era, traversing the forest for rebuild/growth work, draining/resuming zones, and reporting cache statistics.

## Important APIs, Types, And Functions

- `UNMAPPED_BLOCK_MAP_ENTRY`: canonical on-disk entry for an unmapped logical block.
- Page-cache helpers: `vdo_get_page`, `vdo_release_page_completion`, `vdo_request_page_write`, `vdo_get_cached_page`, `vdo_invalidate_page_cache`, and `vdo_get_block_map_statistics`.
- Tree lookup/allocation: `vdo_find_block_map_slot`, `vdo_find_block_map_page_pbn`, `load_block_map_page`, `allocate_block_map_page`, and `finish_block_map_allocation`.
- Mapping access: `vdo_get_mapped_block`, `vdo_put_mapped_block`, `vdo_update_block_map_page`, and `set_mapped_location`.
- Forest lifecycle: `vdo_decode_block_map`, `vdo_record_block_map`, `vdo_free_block_map`, `make_forest`, `replace_forest`, `vdo_prepare_to_grow_block_map`, `vdo_grow_block_map`, and `vdo_abandon_block_map_growth`.
- Persistence scheduling: `vdo_initialize_block_map_from_journal`, `vdo_advance_block_map_era`, `add_to_dirty_lists`, `write_expired_elements`, `enqueue_page`, and `write_page`.
- Admin operations: `vdo_drain_block_map`, `vdo_resume_block_map`, zone `admin_state`, and the block-map `action_manager`.

## Control Flow

The page-cache path starts in `vdo_get_page`. It initializes a `vdo_page_completion`, checks read-only restrictions for writable requests, and then either returns a valid cached page, waits behind an incoming/outgoing page, loads the page into a free slot, or requests eviction of an LRU page. Dirty evictions are written only after `save_pages` issues a flush so recovery-journal entries reach stable storage before the block-map pages that depend on them. Completion paths validate page headers with the map nonce and PBN, format invalid pages as empty pages when appropriate, distribute the page to waiters, and maintain busy counts until callers release the page.

The tree lookup path starts in `vdo_find_block_map_slot` after a `data_vio` owns its LBN lock. It computes the root index and leaf slot, walks already loaded in-memory tree pages from the root toward the leaf, validates tree entries, and either finishes with the leaf page PBN or loads/allocates the missing interior/leaf page. `loading_pages` serializes concurrent loads or allocations by a packed `page_descriptor`; waiters resume after the owner finishes.

Allocation of missing block-map pages uses normal VDO block allocation, recovery-journal insertion, reference-count update to `MAXIMUM_REFERENCES`, and a block-map tree update. `finish_block_map_allocation` records the new child PBN in the parent tree page, formats newly allocated interior pages in memory, releases the page lock, wakes waiters, and continues descending until the final leaf slot is known.

Mapping reads and writes are layered on top of slot lookup. `vdo_get_mapped_block` treats an unallocated leaf page as unmapped, otherwise fetches the leaf page read-only and decodes the slot. `vdo_put_mapped_block` fetches the page writable, packs `data_vio->new_mapped`, transfers the recovery-journal lock to the page, marks the page dirty, and places it on dirty-era lists.

Forest traversal creates one cursor per root, uses a pooled metadata VIO per cursor to load pages, calls a supplied callback for allocated non-leaf PBNs, removes invalid or out-of-bound entries, and finishes the parent completion after all roots drain. Growth prepares a new segmented forest, then replaces the active forest during a suspended admin operation.

## State And Persistence Behavior

Persistent state is the on-disk block-map tree and block-map page entries. Each dirty page records the earliest recovery-journal sequence that has uncommitted changes. The code acquires and releases recovery-journal block references so journal blocks needed to replay dirty map updates are not reaped before the corresponding map page reaches disk. Page writes use initialized-header handling for torn-write protection and use preflush when the page is the active flusher.

In-memory state includes per-zone `loading_pages`, `active_lookups`, dirty-era lists, dirty generation counters, a VIO pool for metadata reads/writes, and the leaf-page cache (`page_info` state, LRU, free, outgoing, wait queues, busy counters, and statistics). Cache statistics are updated on logical-zone threads with `WRITE_ONCE` and read cross-thread with `READ_ONCE`.

Read or write failures generally enter VDO read-only mode through `set_persistent_error`, `enter_zone_read_only_mode`, or completion error handlers. A read-only rebuild is special: page-read failure is treated as an uninitialized page so rebuild can continue.

## Dependencies And Integration Points

The file depends on VDO's completion and work-queue system, `data_vio` request state, recovery journal, physical-zone allocator and PBN locks, VIO metadata I/O submitters, `int_map`, wait queues, admin-state/action-manager scheduling, block-map encodings, and slab-depot validation. It is called by the data path to locate and update mappings, by recovery/rebuild to traverse tree pages, by growth/configuration code to resize logical capacity, and by admin suspend/resume paths to drain metadata I/O.

## Risks And Edge Cases

- The page cache relies on strict logical-zone thread affinity; cross-thread callers can corrupt wait queues, LRU state, or counters.
- Busy counts, waiter queues, and deferred writes must stay balanced. A missing `vdo_release_page_completion` can pin a page and cause cache pressure or drain hangs.
- Error paths often move the VDO to read-only mode. Tests need to distinguish expected `VDO_NO_SPACE` from fatal corruption or I/O errors.
- `data_vio->recovery_sequence_number` is transferred into page recovery locks by `vdo_update_block_map_page`; losing that transfer can permit journal reap before map persistence.
- Dirty generation accounting uses 8-bit cyclic generation values; underflow/overflow checks enter read-only mode.
- `vdo_find_block_map_page_pbn` is only valid after allocated tree pages are loaded, as documented.
- `vdo_invalidate_page_cache` reallocates the map only after asserting there are no dirty pages; callers must drain/write first.
- Traversal repairs invalid entries by clearing them and writing the affected tree page, so recovery tests should expect mutation.

## Test Signals

Useful signals include block-map cache statistics (`pages_loaded`, `pages_saved`, `discard_required`, `wait_for_page`, `failed_reads`, `failed_writes`, `flush_count`), read-only transitions, persistent page-cache error logs, bad page or bad mapping logs, drain completion behavior, and recovery-journal reference balance. Coverage should exercise cached hits, incoming/outgoing waiters, dirty eviction with flush, read-only rebuild read errors, missing tree-page allocation, concurrent waiters for the same tree page, map growth/abandon, forest traversal repair, and data-path get/put mapping updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.h

## Purpose

`block-map.h` declares the VDO block-map data structures and public API. It documents the design: a set of radix trees, distributed across logical zones, with a per-zone leaf-page cache and single-threaded zone ownership for normal lookup/update operations.

## Important APIs, Types, And Functions

- Constants and exports: `BLOCK_MAP_VIO_POOL_SIZE`, `vdo_page_generation`, and `UNMAPPED_BLOCK_MAP_ENTRY`.
- `struct vdo_page_cache`: per-zone cache for leaf block-map pages, including page arrays, PBN map, LRU/free/outgoing lists, I/O counters, waiters, and `block_map_statistics`.
- `enum vdo_page_buffer_state` and `enum vdo_page_write_status`: cache page lifecycle and write intent.
- `struct page_info`: one cache slot, including metadata VIO, PBN, busy count, waiters, list entries, and recovery-journal lock.
- `struct vdo_page_completion`: caller-owned request for a cache page, with readiness and writable state.
- `struct tree_page`, `struct dirty_lists`, `struct block_map_zone`, and `struct block_map`: interior tree page storage, dirty-era tracking, per-zone block-map state, and the top-level map.
- Public operations: page get/release/write/invalidate, slot lookup, map page PBN lookup, tree page write, forest traversal, decode/record/free, journal initialization, era advance, drain/resume, growth, mapping get/put, page update, and statistics.
- `vdo_convert_maximum_age`: converts old recovery-journal age tuning to the current journal entry density.

## Control Flow

The header splits responsibilities between cache-page operations (`vdo_get_page` through `vdo_invalidate_page_cache`), tree/forest operations (`vdo_find_block_map_slot`, `vdo_write_tree_page`, `vdo_traverse_forest`), lifecycle operations (`vdo_decode_block_map`, `vdo_free_block_map`, drain/resume/grow), and mapping operations (`vdo_get_mapped_block`, `vdo_put_mapped_block`, `vdo_update_block_map_page`). Callers are expected to run load/save operations on the admin thread and normal mapping operations on the owning logical-zone thread.

## State And Persistence Behavior

The declared state mirrors persistent block-map pages and journal coupling. `page_info::recovery_lock` and `tree_page::recovery_lock` hold the earliest journal sequence needed by an unwritten page. `dirty_lists` bins cache and tree pages by recovery-journal era and expires old pages for writeback. `block_map` records the root origin/count for persisted map roots, the nonce used to validate pages, current/pending era points, active and prepared forests, and per-zone state.

## Dependencies And Integration Points

The header imports admin state, completions, encodings, int maps, statistics, VIOs, wait queues, and VDO numeric/types definitions. It is included by data-path code, recovery/growth code, and metadata-management code that needs to translate logical blocks, update mappings, or traverse allocated block-map pages.

## Risks And Edge Cases

- The single-threaded zone model is part of the API contract, not just an implementation detail.
- `struct block_map` uses a flexible array of zones; allocation must match the logical-zone count.
- `struct vdo_page_completion` is both a completion and a wait-queue entry, so callers must not reuse it while queued or ready.
- Dirty-era arrays are sized by `maximum_age`; invalid zero or very small values would break expiration assumptions.
- `vdo_convert_maximum_age` multiplies `age` before division; callers should use sane configured values.

## Test Signals

Compile-time signals include type visibility, enum size assumptions, and prototypes matching `block-map.c`. Behavioral tests should validate completion ownership, page-release requirements, dirty-era aging, conversion of maximum age, growth preparation/replacement, and statistics aggregation across zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.c

## Purpose

`completion.c` implements VDO's lightweight asynchronous continuation primitive. A `vdo_completion` carries a callback, error handler, target thread, result, queue state, and parent pointer so multi-stage operations can move between VDO work queues without conventional locking between zones.

## Important APIs, Types, And Functions

- `vdo_initialize_completion`: clears a completion, assigns its owning VDO and type, then resets result/complete state.
- `vdo_set_completion_result`: records the first non-success result without masking an older error.
- `vdo_launch_completion_with_priority`: runs immediately if already on the target thread and not forced to requeue, otherwise enqueues to the target work queue.
- `vdo_finish_completion`: marks a completion complete and launches its callback if present.
- `vdo_enqueue_completion`: validates the target thread, clears `requeue`, sets priority, and enqueues on the VDO work queue.
- `vdo_requeue_completion_if_needed`: helper for callbacks that must resume on a specific thread.

## Control Flow

Operations prepare a completion with the next callback, error handler, target thread, and parent. Launching compares the target callback thread to `vdo_get_callback_thread_id`; matching-thread callbacks run inline unless `requeue` is set. Mismatched callbacks are queued. When a completion is run, `completion.h` dispatches to the error handler if `result` is not `VDO_SUCCESS` and an error handler exists; otherwise it calls the normal callback.

`vdo_finish_completion` is used when an asynchronous child operation is complete and should notify its parent callback. `complete` is a programming-error detector, not a cross-thread completion status.

## State And Persistence Behavior

This file does not persist data. It mutates in-memory completion fields: result, complete flag, requeue flag, priority, queue link metadata, callback thread id, callback, error handler, and parent. Result handling is sticky: after the first error, later success or errors do not overwrite it.

## Dependencies And Integration Points

The implementation depends on VDO thread configuration, `vdo_enqueue_work_queue`, callback-thread identity, `status-codes.h`, and assert/log helpers. It is the common substrate for `data_vio`, block-map cache I/O, VIO metadata/data I/O, admin actions, and pool release processing.

## Risks And Edge Cases

- Callers may not inspect or mutate most completion fields from arbitrary threads; ownership follows the currently executing callback thread.
- Calling `vdo_set_completion_result` or `vdo_finish_completion` on an already complete completion is a programming error.
- A null callback with `vdo_run_completion` would crash; callers must only launch runnable completions or finish completions with callback checks.
- `vdo_enqueue_completion` calls `BUG()` after an invalid thread assertion, so corrupted callback thread IDs are fatal.
- `requeue` is cleared on enqueue, so callers that need repeated forced queuing must set it before each launch.

## Test Signals

Tests should cover first-error-wins result behavior, immediate execution on the correct thread, queued execution on a different thread, forced requeue, invalid thread assertions, finish-without-callback behavior, and error-handler dispatch. Runtime failures often appear as completion type assertions, invalid thread BUGs, stack growth from missing requeue, or lost parent callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.h

## Purpose

`completion.h` declares and inlines the common VDO completion API. It provides small helpers for running, resetting, preparing, launching, failing, and type-checking asynchronous continuations.

## Important APIs, Types, And Functions

- `vdo_run_completion`: dispatches to `error_handler` for non-success results, otherwise to `callback`.
- `vdo_reset_completion`: clears result and complete state while preserving type, VDO, and parent-related fields.
- `vdo_launch_completion`, `vdo_launch_completion_with_priority`, and `vdo_enqueue_completion`: scheduling entry points.
- `vdo_continue_completion` and `vdo_fail_completion`: result-setting continuation helpers.
- `vdo_assert_completion_type`: runtime type check for container casts.
- `vdo_set_completion_callback`, `vdo_launch_completion_callback`, `vdo_prepare_completion`, and `vdo_prepare_completion_for_requeue`: callback setup helpers.
- `vdo_requeue_completion_if_needed`: thread-affinity helper.

## Control Flow

Most users call `vdo_prepare_completion` to reset and bind the next stage, then `vdo_launch_completion`. If the current stage obtained a result code, it uses `vdo_continue_completion`; fatal paths use `vdo_fail_completion`. Inline launch helpers are thin wrappers around the out-of-line scheduler in `completion.c`.

## State And Persistence Behavior

The header defines no durable state. It controls how a `struct vdo_completion` is reused between stages. Reset intentionally does not clear callback, error handler, parent, or target thread; prepare does reset those relevant fields for a new stage.

## Dependencies And Integration Points

The header depends on VDO status codes, types, and assertion helpers. It is included across the VDO subsystem wherever objects embed `struct vdo_completion`, including data VIOs, metadata VIOs, page completions, pool completions, and admin completions.

## Risks And Edge Cases

- `vdo_run_completion` assumes `callback` is non-null when no error handler is selected.
- `vdo_assert_completion_type` returns an error code, but many container helpers use it only for logging/assertion before continuing.
- `vdo_prepare_completion_for_requeue` forces one queued hop only because enqueue clears `requeue`.
- Reusing a completion without `vdo_reset_completion` can retain stale error state.

## Test Signals

Compile coverage should catch prototype drift with `completion.c`. Unit-style tests should verify reset/prepare field effects, callback versus error-handler selection, type assertion behavior, launch callback convenience helpers, and no stale result after reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/completion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/constants.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/constants.h

## Purpose

`constants.h` centralizes VDO-wide fixed limits and defaults used by the data path, block map, journals, slabs, thread configuration, and block sizing. These constants define major layout and scalability assumptions for the VDO target.

## Important APIs, Types, And Functions

- Block-map geometry: `VDO_BLOCK_MAP_ENTRIES_PER_PAGE`, `VDO_BLOCK_MAP_FLAT_PAGE_ORIGIN`, `VDO_BLOCK_MAP_TREE_HEIGHT`, and `DEFAULT_VDO_BLOCK_MAP_TREE_ROOT_COUNT`.
- I/O submission defaults: `VDO_BIO_ROTATION_INTERVAL_LIMIT`, `DEFAULT_VDO_BIO_SUBMIT_QUEUE_COUNT`, and `DEFAULT_VDO_BIO_SUBMIT_QUEUE_ROTATE_INTERVAL`.
- Journal and slab defaults: `DEFAULT_VDO_RECOVERY_JOURNAL_SIZE`, `DEFAULT_VDO_SLAB_JOURNAL_SIZE`, and `RECOVERY_JOURNAL_STARTING_SEQUENCE_NUMBER`.
- Lock and restoration limits: `VDO_LOCK_MAP_CAPACITY` and `MAXIMUM_SIMULTANEOUS_VDO_BLOCK_MAP_RESTORATION_READS`.
- Zone and thread limits: `MAX_VDO_LOGICAL_ZONES`, `MAX_VDO_PHYSICAL_ZONES`, and `MAXIMUM_VDO_THREADS`.
- Slab sizing: `DEFAULT_VDO_SLAB_BLOCKS`, `MIN_VDO_SLAB_BLOCKS`, `MAX_VDO_SLAB_BLOCKS`, and `MAX_VDO_SLABS`.
- Request/block sizing: `MAXIMUM_VDO_USER_VIOS`, `VDO_BLOCK_SIZE`, `VDO_SECTORS_PER_BLOCK`, `VDO_SECTOR_SIZE`, and `VDO_ZERO_BLOCK`.

## Control Flow

This header contains no runtime control flow. Its enum constants are compiled into allocation sizing, validation, tree traversal, bio splitting/submission, and on-disk layout calculations throughout VDO.

## State And Persistence Behavior

Several constants affect persistent format interpretation. `VDO_BLOCK_SIZE`, block-map geometry, journal sizes, root count defaults, slab limits, and `VDO_ZERO_BLOCK` are baked into block-map pages, journal behavior, and physical-space layout. Changing them would require coordinated format migration.

## Dependencies And Integration Points

The file includes Linux block-device definitions for `SECTOR_SHIFT` and VDO `types.h`. It is used by block-map code, data VIOs, slab depot, journals, thread configuration, I/O submitters, and format/configuration code.

## Risks And Edge Cases

- `VDO_BLOCK_MAP_ENTRIES_PER_PAGE` must match the packed on-disk `struct block_map_page` size; `block-map.c` has a `BUILD_BUG_ON` for this.
- `VDO_BLOCK_SIZE` is assumed to be 4096 and not larger than `PAGE_SIZE` in `data-vio.c`.
- Zone/thread maxima constrain configuration validation and array sizing.
- `VDO_ZERO_BLOCK` is a reserved physical block for zero mappings; treating it as an allocatable data block would corrupt zero/discard semantics.

## Test Signals

Build-time checks should catch block-map entry count and block size assumptions. Configuration tests should cover min/default/max slab blocks, maximum zones/threads, journal defaults, and correct sector/block conversions for partial bios and discards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/cpu.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/cpu.h

## Purpose

`cpu.h` provides small CPU-cache prefetch helpers for UDS/VDO code. It wraps compiler builtins so callers can request read or write prefetching for one address or a range of cache lines.

## Important APIs, Types, And Functions

- `uds_prefetch_address(address, for_write)`: calls `__builtin_prefetch` for read or write when `for_write` is compile-time constant.
- `uds_prefetch_range(start, size, for_write)`: computes the cache-line span for an address range and prefetches each line using `uds_prefetch_address`.

## Control Flow

`uds_prefetch_address` first checks `__builtin_constant_p(for_write)`. With optimization disabled or non-constant flags, it does nothing. `uds_prefetch_range` calculates an initial alignment offset, derives the number of `L1_CACHE_BYTES` lines touched by the range, then loops line by line.

## State And Persistence Behavior

The file has no persistent or logical state. Prefetching is a performance hint only and must not be required for correctness. The comments explicitly allow invalid addresses because prefetch hints should not fault in the same way as normal loads/stores.

## Dependencies And Integration Points

The header depends on Linux `cache.h` for `L1_CACHE_BYTES` and standard integer/pointer types via surrounding includes. It can be included by indexing, hashing, or data-path code that scans memory buffers.

## Risks And Edge Cases

- `for_write` must be constant for the helper to emit a builtin call.
- `uds_prefetch_range` adds one cache line after integer division, so it may prefetch one extra line beyond the exact range. That is acceptable for a hint but relevant to performance analysis.
- Very large `size` values can generate long loops; callers should use it for bounded hot ranges.

## Test Signals

Compile tests across GCC/Clang and optimized/unoptimized builds are the main signal. Microbenchmarks can compare hot-path scans with and without prefetching, but correctness tests should not depend on observable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.c

## Purpose

`data-vio.c` implements the lifecycle of user data I/O requests in VDO. It manages a bounded pool of `data_vio` objects, turns incoming bios into block-sized logical operations, serializes operations by logical block, performs reads, partial write read-modify-write, discard splitting, allocation, dedupe, compression, physical writes, recovery-journal updates, reference-count changes, block-map updates, acknowledgement, cleanup, and pool recycling.

## Important APIs, Types, And Functions

- Pool API: `make_data_vio_pool`, `free_data_vio_pool`, `vdo_launch_bio`, `drain_data_vio_pool`, `resume_data_vio_pool`, `dump_data_vio_pool`, and active/max request getters.
- Compression status API: `get_data_vio_compression_status`, `advance_data_vio_compression_stage`, and `cancel_data_vio_compression`.
- Cleanup/error API: `complete_data_vio`, `handle_data_vio_error`, `get_data_vio_operation_name`, and cleanup stages.
- Allocation/write API: `data_vio_allocate_data_block`, `release_data_vio_allocation_lock`, `update_metadata_for_data_vio_write`, `write_data_vio`, `launch_compress_data_vio`, and `continue_data_vio_with_block_map_slot`.
- Read API: `read_block`, `complete_read`, `complete_zero_read`, `modify_for_partial_write`, and `uncompress_data_vio`.
- Metadata update flow: `journal_remapping`, `increment_reference_count`, `decrement_reference_count`, and `update_block_map`.

## Control Flow

`vdo_launch_bio` admits a bio into the pool. It may block the submitting thread if no data VIO is available or if discard permits are exhausted. Once assigned, `launch_bio` classifies the request as read, write, discard, partial, zero, and/or FUA, copies full-block write data into the VIO buffer, computes the LBN, and enqueues `attempt_logical_block_lock` on the logical-zone thread.

The logical lock path serializes operations on the same LBN through `logical_zone->lbn_operations`. Reads behind a writing lock holder can be served from the lock holder after allocation succeeds. Otherwise waiters queue on the lock holder, and compression may be cancelled to prevent indefinite packer blocking.

For reads, `continue_data_vio_with_block_map_slot` calls `vdo_get_mapped_block`, then `read_block` reads the mapped PBN, reads the compressed block if needed, or synthesizes zeros for unmapped/zero blocks. Partial reads and compressed reads copy data back to the user bio on a CPU queue. Partial writes first read the old block, modify the requested range, then return to the write path.

For writes, the code acquires a flush generation lock, allocates a new physical block unless the operation is a full zero write or full discard, and may acknowledge non-FUA writes after allocation and before dedupe/compression/physical write. The dedupe path hashes data and acquires a hash lock. Compression uses LZ4 on the CPU queue and may attempt packer insertion; if not compressed or packed, `write_data_vio` writes the full block to the allocated PBN.

After the new data location is known, `update_metadata_for_data_vio_write` reads the old mapping, writes a recovery-journal remapping entry, updates reference counts for old and new PBNs, and rendezvous in `update_block_map`. Once both reference operations complete, `vdo_put_mapped_block` updates the block map. Cleanup then releases hash locks, allocation locks, recovery locks, logical locks, and flush generation locks before either launching the next discard block or returning the VIO to the pool.

Pool release processing is batched. Completed VIOs go through a funnel queue, `process_release_callback` acknowledges any still-unacknowledged bio, transfers discard permits fairly, assigns returned VIOs to oldest waiting reads/writes or permitted discards, wakes blocked submitters, and reschedules if the funnel still has entries.

## State And Persistence Behavior

The durable ordering is recovery journal entry first, reference-count updates, and block-map update. `data_vio->recovery_sequence_number` carries the journal entry lock until `vdo_update_block_map_page` transfers it to the dirty block-map page. Reference updaters describe increment/decrement journal operations for the slab depot. Flush generation locks prevent flush completion from racing ahead of acknowledged writes.

In-memory state includes the pool's limiters, wait queues, funnel queue, per-VIO logical lock, tree lock, mapped/new/duplicate PBNs, allocation lock, hash lock, compression state, recovery journal point, user bio pointer, discard progress, and async operation name. `allocation_succeeded` is read across threads with `READ_ONCE` because readers waiting behind a write may copy data from the lock holder.

Acknowledgement can happen before all metadata is durable for non-FUA writes after allocation succeeds; FUA and multi-block discard constraints delay acknowledgement. Fatal errors often enter read-only mode, especially after user bio acknowledgement or when `VDO_READ_ONLY` is encountered.

## Dependencies And Integration Points

The file integrates with Linux bios and block status conversion, VDO work queues/completions, logical zones, physical zones and PBN locks, slab depot reference counts, block map lookup/update, recovery journal, dedupe hash zones, packer/compression, MurmurHash3, LZ4, admin state, funnel queues, stats, and dump/logging facilities.

## Risks And Edge Cases

- Pool admission intentionally blocks submitter threads. Waiter wakeups and limiter counters must remain balanced or I/O can hang.
- Discards can span many blocks and reuse the same VIO; cleanup must correctly relaunch the next LBN and preserve remaining discard state.
- Early acknowledgement means post-ack fatal metadata errors must transition VDO read-only because the user cannot be failed anymore.
- Reads served from an allocating write lock holder require `allocation_succeeded` ordering and must not expose data before a real allocation exists.
- Compression cancellation and packer blocking are concurrency-sensitive; lock waiters must not wait forever behind a VIO stuck in the packer.
- The reference-count rendezvous uses two completions and `first_reference_operation_complete`; a missed callback would block block-map updates.
- Partial writes depend on correct zero-fill, old-block read, and bio copy offsets.
- `bio->bi_private` is reused to store `jiffies` while waiting for permits, then later stores VIO context for submitted bios.

## Test Signals

Tests should cover pool exhaustion and wakeup fairness, discard permit limiting, drain/resume with waiters, full reads, zero reads, compressed reads, partial reads, partial writes, full zero writes, full and multi-block discards, FUA writes, no-space allocation fallback to dedupe, compression disabled/cancelled/packer paths, hash-lock contention, logical-lock transfer, post-ack metadata failure read-only transition, reference-count update rendezvous, and block-map update failure. Runtime signals include async operation names in error logs, `bios_acknowledged` stats, pool max-busy stats, VIO error stats, read-only notifier state, and dump output for busy VIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.h

## Purpose

`data-vio.h` defines the central data-path request object for VDO and declares the APIs used to launch, route, read, write, compress, allocate, update metadata for, and complete user data VIOs. It also provides thread-affinity helper wrappers for moving a `data_vio` between logical, physical, hash, journal, packer, CPU, bio, and acknowledgement queues.

## Important APIs, Types, And Functions

- `enum async_operation_number`: debug/error labels for the last asynchronous stage.
- Lock/location types: `struct lbn_lock`, `struct block_map_tree_slot`, `struct tree_lock`, and `struct zoned_pbn`.
- Compression types: `enum data_vio_compression_stage`, `struct data_vio_compression_status`, and `struct compression_state`.
- Allocation and reference update types: `struct allocation` and `struct reference_updater`.
- `struct data_vio`: embeds `struct vio`, waiters, logical/tree locks, mapped/new/duplicate locations, hash/dedupe state, reference updaters, flags, recovery state, page completion, user bio, discard progress, compression buffers, and pool linkage.
- Pool and lifecycle API: `make_data_vio_pool`, `free_data_vio_pool`, `vdo_launch_bio`, `drain_data_vio_pool`, `resume_data_vio_pool`, `dump_data_vio_pool`, pool stats getters, `complete_data_vio`, and `handle_data_vio_error`.
- Data-path API: compression status helpers, `data_vio_allocate_data_block`, `release_data_vio_allocation_lock`, `uncompress_data_vio`, `update_metadata_for_data_vio_write`, `write_data_vio`, `launch_compress_data_vio`, and `continue_data_vio_with_block_map_slot`.

## Control Flow

The header's inline helpers encode the expected state machine transfers. `continue_data_vio` relaunches the embedded completion. `continue_data_vio_with_error` records a result and relaunches. The `set_data_vio_*_callback` and `launch_data_vio_*_callback` families bind the completion to the relevant zone/thread and then launch it, optionally with a priority.

The public functions declared here are implemented in `data-vio.c` and by peer modules such as hash-zone, packer, physical-zone, and block-map code. Callers should use the thread-specific helpers rather than setting completion thread IDs manually.

## State And Persistence Behavior

`struct data_vio` is the transient carrier for persistent metadata changes. It stores old and new mappings, journal operation descriptors, recovery journal sequence/point, allocation PBN/lock, and page-completion state. Some fields are reset on reuse while fields after the embedded `vio` allocation boundary keep allocated buffers and completions across pool reuse.

The flags (`read`, `write`, `fua`, `is_zero`, `is_discard`, `is_partial`, `is_duplicate`, etc.) drive ordering, acknowledgement, and metadata updates. `recovery_sequence_number` must be cleared only after its journal lock is transferred or released.

## Dependencies And Integration Points

The header includes Linux bio/list/atomic support and VDO modules for block map, completion, constants, dedupe, encodings, logical/physical zones, indexer, VIOs, wait queues, and core VDO types. It is included by modules that need to inspect or continue data-path state, including block-map allocation, hash/dedupe, packer/compression, physical-zone allocation/reference updates, and dump/debug code.

## Risks And Edge Cases

- Many inline assert helpers dereference zone pointers; the corresponding `zoned_pbn` or lock state must be initialized before use.
- `data_vio_has_allocation` treats `VDO_ZERO_BLOCK` as no allocation, matching zero-block reservation.
- The reset boundary in `data-vio.c` depends on `offsetof(struct data_vio, vio)` and `offsetof(struct compression_state, block)`; moving fields across those boundaries changes reuse semantics.
- Completion container casts depend on `vio.type == VIO_TYPE_DATA` and completion type correctness.
- Thread helper misuse can run physical-zone, hash-zone, or journal operations on the wrong queue.

## Test Signals

Compile coverage should catch signature mismatches with peer modules. Runtime tests should validate thread assertions for each launch helper, data_vio reuse/reset behavior, allocation presence handling, compression stage transitions, reference-updater container conversion, and correctness of public continuation points used by block-map, hash, packer, and physical-zone code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/data-vio.h -->
