# Group Research: group_669_kvdo_sources_block_storage_kvdo_vdo_volume_index_ops_h_sources_block_dc7b768e060f

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index-ops.h -->
# File Research: sources/block-storage/kvdo/vdo/volume-index-ops.h

## Purpose
Defines the abstract volume-index interface used by the UDS/VDO index code. The volume index maps chunk names to virtual chapters, supports lookup/update/removal, persistence save/restore, per-zone chapter advancement, sparse sampling queries, and statistics collection.

## Public Types
- `struct volume_index_stats`: aggregate memory and behavior counters for an index portion, including allocation, rebalance time/count, record/collision/discard/overflow counts, delta-list count, and early flush count.
- `struct volume_index_record`: mutable handle returned by `get_volume_index_record()`. It carries public result state (`virtual_chapter`, `is_collision`, `is_found`) plus private state tying the lookup to a delta-index entry, optional sampled-index mutex, zone, name, and owning `volume_index`.
- `struct volume_index`: vtable for concrete implementations. Methods cover lifecycle, record lookup, stats, zone mapping, sample detection, sampled/dense lookups, chapter movement, tag setting, and save/restore phases.

## Key APIs
- Creation/sizing:
  - `make_volume_index()`
  - `compute_volume_index_save_blocks()`
- Persistence:
  - `load_volume_index()`
  - `save_volume_index()`
  - inline wrappers for `start_*`, `finish_*`, and `abort_restoring_volume_index()`
- Record operations:
  - `get_volume_index_record()`
  - `put_volume_index_record()`
  - `remove_volume_index_record()`
  - `set_volume_index_record_chapter()`
- Chapter/range control:
  - `set_volume_index_open_chapter()`
  - `set_volume_index_zone_open_chapter()`
- Lookup/stat helpers:
  - `lookup_volume_index_name()`
  - `lookup_volume_index_sampled_name()`
  - `is_volume_index_sample()`
  - `get_volume_index_zone()`
  - `get_volume_index_stats()`
  - `get_volume_index_combined_stats()`

## Implementation Notes
This header is intentionally dispatch-oriented. Almost every operation is an inline vtable call, allowing versioned implementations such as `volume-index005.c` and `volume-index006.c` to share one external API.

`volume_index_record` is stateful: callers must first populate it through `get_volume_index_record()`, then reuse that handle for insert/update/delete. The private `magic` field is validated by the concrete 005 implementation to prevent illegal record reuse or operations on uninitialized handles.

The optional `mutex` field is used by sampled sparse indexes. In the 006 implementation, sampled records are backed by the hook subindex and carry a per-zone mutex so later `put`, `remove`, or `set_chapter` operations can synchronize with concurrent read-only sample lookups.

## Dependencies
Includes core UDS/VDO types from `compiler.h`, `config.h`, `delta-index.h`, `uds-threads.h`, and `uds.h`.

## Invariants and Risks
- A `volume_index` object must have all vtable entries initialized before use.
- `free_volume_index()` tolerates `NULL`; most other wrappers do not.
- `volume_index_record` operations are valid only after successful `get_volume_index_record()`.
- Persistence is split into start/finish phases, so callers must complete or abort restore/save flows consistently.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index-ops.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index005.c -->
# File Research: sources/block-storage/kvdo/vdo/volume-index005.c

## Purpose
Implements volume index format/version 005: a dense-only volume index backed by `struct delta_index`. It maps chunk-name-derived hash fields to delta-list entries whose payload is a compact chapter number. It handles lazy LRU invalidation of expired chapters, collision entries, save/restore, sizing, and statistics.

## Core Data Structures
- `struct volume_index_zone`: per-zone indexed virtual chapter low/high bounds and early-flush counter.
- `struct volume_index5`: concrete implementation embedding `struct volume_index common`, `struct delta_index`, flush state, zones, nonce, bit masks, chapter/list counts, and sizing controls.
- `struct chapter_range`: compact range of index-chapter values to flush.
- `struct vi005_data`: persisted header with magic `MI5-0005`, volume nonce, virtual chapter range, and saved delta-list span.
- `struct parameters005`: computed construction/sizing parameters such as address bits, chapter bits, mean delta, delta-list count, estimated memory size, and target free space.

## Major Behavior
The file distinguishes three chapter number forms:
- Virtual chapter: 64-bit external chapter number.
- Index chapter: low-order bits stored in the delta index.
- Rolling chapter: index chapter adjusted relative to a zone’s current low virtual chapter.

`extract_address()` and `extract_dlist_num()` split hash-derived volume-index bytes into an address key and a delta-list number. Delta lists are distributed over zones by the delta-index layer.

`get_volume_index_record_005()` is the central lookup routine. It derives address/list/zone, lazily flushes invalid entries if a list’s `flush_chapters[]` lags behind the zone low chapter, then returns a `volume_index_record` describing either an existing entry or an insertion point.

## Lazy Flushing
`flush_invalid_entries()` advances a delta-index iterator and removes entries whose stored chapter falls inside an expired range. `get_volume_index_entry()` uses it while preserving the lookup insertion offset and while scanning collision records. After processing, it narrows the next flush range so future lookups avoid repeating work.

`set_volume_index_zone_open_chapter_005()` updates a zone’s indexed range when the open chapter moves. It handles:
- backward moves that empty or trim newest entries,
- forward moves preserving all or part of the old range,
- large jumps that reset the range,
- early expiration when zone bit usage exceeds `max_zone_bits`.

`remove_newest_chapters()` renumbers or explicitly flushes entries when a zone moves backward into overlapping state.

## Record Mutation
- `put_volume_index_record()` validates the record magic and chapter range, optionally locks `record->mutex`, inserts into the delta index, updates found/collision state, and logs `UDS_OVERFLOW`.
- `remove_volume_index_record()` validates an existing record, invalidates its magic, optionally locks, then removes the delta entry.
- `set_volume_index_record_chapter()` validates and updates the stored chapter payload after range checking.

These exported functions serve the common API declared in `volume-index-ops.h`.

## Persistence
`start_saving_volume_index_005()` writes:
1. `vi005_data` header,
2. `flush_chapters` array for the zone’s delta-list range,
3. delta-index contents via `start_saving_delta_index()`.

`finish_saving_volume_index_005()` delegates to `finish_saving_delta_index()`.

`start_restoring_volume_index_005()` reads one header and flush-range array per reader/zone stream, validates magic and nonce consistency, reconciles virtual chapter bounds, initializes all zone ranges, then starts delta-index restore.

`abort_restoring_volume_index_005()` and `finish_restoring_volume_index_005()` delegate to the delta-index restore lifecycle.

## Sizing and Construction
`compute_volume_index_parameters005()` computes dense-index parameters from geometry and configuration. Important constraints:
- Sparse geometry is rejected.
- `records_per_chapter` and `chapters_per_volume` must be nonzero.
- delta-list count is at least `MAX_ZONES * MAX_ZONES` unless tests override `min_volume_index_delta_lists`.
- reduced geometry rounds chapters up to preserve hash-to-delta-list mapping.

The memory estimate accounts for live chapters plus estimated invalid chapters retained by lazy LRU. `compute_volume_index_save_bytes005()` adds header, flush ranges, and delta-index save bytes.

`make_volume_index005()` allocates and initializes the concrete object, vtable, delta index, flush-chapter array, and zones.

## Statistics
`get_volume_index_stats_005()` reports all data as dense stats and zeroes sparse stats. It includes delta-index stats plus memory for `volume_index5`, `flush_chapters`, and zones.

## Dependencies
Uses `buffer.h`, `config.h`, `errors.h`, `geometry.h`, `hash-utils.h`, `logger.h`, `memory-alloc.h`, `uds.h`, `delta-index.h` through the public ops header.

## Invariants and Risks
- `volume_index_record_magic` guards legal record operations.
- Stored chapter payload is limited by `chapter_mask`; virtual chapters are reconstructed relative to zone low.
- Lazy flushing means lookup can mutate the index.
- `min_volume_index_delta_lists` is intentionally externally mutable for tests.
- Save/restore depends on matching nonce and consistent per-zone headers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index005.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index005.h -->
# File Research: sources/block-storage/kvdo/vdo/volume-index005.h

## Purpose
Declares the constructor and save-size API for the dense volume index 005 implementation.

## Public API
- `make_volume_index005(const struct configuration *config, uint64_t volume_nonce, struct volume_index **volume_index)`: creates a concrete 005 volume index.
- `compute_volume_index_save_bytes005(const struct configuration *config, size_t *num_bytes)`: computes persisted byte size for a 005 index under the supplied configuration.

## Dependencies
Includes `volume-index-ops.h`, so callers see the abstract `struct volume_index` API and related types.

## Notes
This header exposes version-specific creation/sizing only. Runtime operations are performed through the common vtable interface in `volume-index-ops.h`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index005.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index006.c -->
# File Research: sources/block-storage/kvdo/vdo/volume-index006.c

## Purpose
Implements volume index format/version 006 as a sparse+dense wrapper over two 005 indexes:
- non-hook index for ordinary dense entries,
- hook index for sampled sparse entries.

It routes operations to the proper subindex based on chunk-name sampling, persists a 006 header plus both subindexes, and adds per-zone synchronization for sparse sampled lookups.

## Core Data Structures
- `struct volume_index_zone`: holds a per-zone `hook_mutex` protecting sampled hook-index access.
- `struct volume_index6`: embeds common vtable, stores sparse sample rate, zone count, non-hook and hook `volume_index` pointers, and zone mutex array.
- `struct vi006_data`: persisted header with magic `MI6-0001` and sparse sample rate.
- `struct split_config`: local pair of derived configurations/geometries for hook and non-hook 005 indexes.

## Routing Model
`is_volume_index_sample_006()` treats a chunk name as sampled when `extract_sampling_bytes(name) % sparse_sample_rate == 0`.

`get_sub_index()` returns `vi_hook` for sampled names and `vi_non_hook` otherwise.

Operations route as follows:
- `get_volume_index_zone_006()` delegates to the selected subindex.
- `get_volume_index_record_006()` delegates to hook or non-hook. Hook records are looked up under the per-zone mutex, and the mutex pointer is saved into `record->mutex` for later mutation operations implemented by 005.
- `lookup_volume_index_name_006()` only checks sampled names. It locks the relevant hook mutex, delegates to `lookup_volume_index_sampled_name()` on the hook subindex, and returns `UINT64_MAX` for non-sampled names.
- `lookup_volume_index_sampled_name_006()` is a defensive stub returning `UINT64_MAX` with a FIXME saying it should never be called.
- Chapter movement updates non-hook first, then hook under the zone mutex.

## Persistence
`start_saving_volume_index_006()` writes the 006 header, then starts saving the non-hook 005 index followed by the hook 005 index to the same buffered writer.

`finish_saving_volume_index_006()` finishes non-hook first, then hook if non-hook succeeded.

`start_restoring_volume_index_006()` reads and validates the 006 header from each reader, enforces consistent sparse sample rate, then starts restore for non-hook and hook indexes.

`finish_restoring_volume_index_006()` finishes both subindexes in order. `abort_restoring_volume_index_006()` aborts both subindexes.

## Configuration Splitting
`split_configuration006()` requires:
- `sparse_chapters_per_volume != 0`,
- `sparse_sample_rate != 0`.

It copies the original config and geometry twice, then:
- hook geometry indexes only sampled records per chapter and no sparse chapters,
- non-hook geometry removes sampled records and only indexes dense chapters,
- both derived geometries use dense 005 indexes internally.

`compute_volume_index_save_bytes006()` returns `sizeof(vi006_data) + non_hook_005_bytes + hook_005_bytes`.

## Construction and Cleanup
`make_volume_index006()`:
1. splits the configuration,
2. allocates `volume_index6`,
3. initializes vtable methods,
4. allocates zone mutexes,
5. creates non-hook 005 index tagged `'d'`,
6. creates hook 005 index tagged `'s'`.

`free_volume_index_006()` destroys per-zone mutexes, frees both subindexes, and frees the wrapper.

## Dependencies
Uses `buffer.h`, `errors.h`, `hash-utils.h`, `logger.h`, `memory-alloc.h`, `permassert.h`, `uds-threads.h`, and `volume-index005.h`.

## Invariants and Risks
- Hook lookup is the only multithreaded sparse operation explicitly supported; zone mutexes protect it from hook-index mutations and open-chapter changes.
- 006 relies on 005 for actual delta-index storage and most record mutation.
- The sampled lookup path returns sparse virtual chapters only for sampled names.
- Save/restore stream layout is nested: 006 header, non-hook 005 payload, hook 005 payload.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index006.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index006.h -->
# File Research: sources/block-storage/kvdo/vdo/volume-index006.h

## Purpose
Declares the constructor and save-size API for the sparse+dense volume index 006 implementation.

## Public API
- `make_volume_index006(const struct configuration *config, uint64_t volume_nonce, struct volume_index **volume_index)`: creates a 006 wrapper index.
- `compute_volume_index_save_bytes006(const struct configuration *config, size_t *num_bytes)`: computes persisted byte size for a 006 index.

## Dependencies
Includes `volume-index-ops.h`, exposing the common abstract volume-index interface.

## Notes
The 006 implementation is version-specific at construction time but presents the same `struct volume_index` vtable interface to callers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-index006.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-store.c -->
# File Research: sources/block-storage/kvdo/vdo/volume-store.c

## Purpose
Implements the volume backing-store adapter on top of Linux `dm-bufio`. It opens/closes storage, reads pages, prepares writable buffers, marks writes dirty, syncs dirty buffers, and manages page-buffer references.

## Main Functions
- `close_volume_store()`: destroys the `dm_bufio_client` and clears the pointer.
- `initialize_volume_page()`: initializes a `volume_page` by setting its buffer pointer to `NULL`.
- `destroy_volume_page()`: releases any referenced buffer.
- `open_volume_store()`: opens a bufio client through `open_uds_volume_bufio()`.
- `prefetch_volume_pages()`: calls `dm_bufio_prefetch()`.
- `prepare_to_write_volume_page()`: releases any prior page buffer, obtains a new writable bufio buffer with `dm_bufio_new()`, and stores it in the page.
- `read_volume_page()`: releases prior page buffer, reads with `dm_bufio_read()`, stores the returned buffer, and logs read failures.
- `release_volume_page()`: releases a held `dm_buffer` and clears the pointer.
- `swap_volume_pages()`: swaps two `volume_page` structs by value.
- `sync_volume_store()`: writes dirty buffers with `dm_bufio_write_dirty_buffers()` and logs sync errors.
- `write_volume_page()`: marks the current buffer dirty.

## Dependencies
Includes `geometry.h`, `index-layout.h`, `logger.h`, and `volume-store.h`. The header brings in `dm-bufio`.

## Implementation Notes
The `volume_page` object is a reference holder for a `dm_buffer`, not an owned memory allocation. Data access is via `dm_bufio_get_block_data()` from the header’s `get_page_data()` helper.

`write_volume_page()` ignores the `physical_page` argument because the bufio buffer already identifies the block; it only marks the buffer dirty.

## Invariants and Risks
- Callers must release or destroy pages to drop bufio references.
- `prepare_to_write_volume_page()` and `read_volume_page()` both release previous page state before replacing it.
- `sync_volume_store()` converts the bufio return convention by negating `dm_bufio_write_dirty_buffers()` result.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-store.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-store.h -->
# File Research: sources/block-storage/kvdo/vdo/volume-store.h

## Purpose
Defines the volume-store abstraction over `dm-bufio` for fixed-size volume pages.

## Public Types
- `struct volume_store`: holds a `struct dm_bufio_client *`.
- `struct volume_page`: holds a `struct dm_buffer *`.

## Public API
- Lifecycle:
  - `open_volume_store()`
  - `close_volume_store()`
  - `initialize_volume_page()`
  - `destroy_volume_page()`
  - `release_volume_page()`
- IO:
  - `read_volume_page()`
  - `prepare_to_write_volume_page()`
  - `write_volume_page()`
  - `sync_volume_store()`
  - `prefetch_volume_pages()`
- Utilities:
  - `get_page_data()`
  - `swap_volume_pages()`

## Dependencies
Includes `common.h`, `compiler.h`, `memory-alloc.h`, and Linux `<linux/dm-bufio.h>`. Forward-declares `struct index_layout`.

## Notes
The abstraction hides bufio details from the volume and page-cache code while keeping page data access cheap through the inline `get_page_data()` helper.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume-store.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume.c -->
# File Research: sources/block-storage/kvdo/vdo/volume.c

## Purpose
Implements persisted chapter storage for the UDS/VDO volume. It manages:
- physical page mapping,
- asynchronous and synchronous page reads,
- page-cache coordination,
- reader threads,
- index-page and record-page search,
- chapter writes,
- volume boundary discovery after restart,
- volume construction, replacement, and cleanup.

## Page Mapping
Physical page zero is reserved for the header. Chapter pages begin at physical page one:
- `map_to_physical_page(geometry, chapter, page)` returns `1 + pages_per_chapter * chapter + page`.
- `map_to_page_number()` and `map_to_chapter_number()` reverse physical pages to chapter-local coordinates.
- `is_record_page()` identifies record pages as pages after the chapter’s index pages.

## Reader Thread Model
`enqueue_page_read()` records a queued page read in the page cache, waits if read queues are full, and signals reader threads. It rejects new reads during shutdown.

`read_thread_function()` loops under `read_threads_mutex`:
1. reserves a queued read entry,
2. selects a cache victim,
3. reads the volume page outside the mutex,
4. initializes index pages when needed,
5. inserts the page into cache unless invalidated,
6. searches the newly read page for queued requests,
7. requeues requests to `STAGE_INDEX`,
8. releases the read-queue entry and broadcasts completion.

Invalidation and pending-search counters are used to avoid races with page-cache invalidation while requests are searching cached pages.

## Page Retrieval
- `get_volume_page_locked()`: caller holds read mutex; returns cached page or synchronously reads it.
- `get_volume_page_protected()`: request path that may queue asynchronous read. It carefully toggles pending-search state and read mutex ownership to prevent cache invalidation races.
- `get_volume_page()`: synchronous convenience wrapper used by rebuild/explorer/tests and other single-threaded paths.

`read_page_locked()` performs either synchronous reads when there is no request/session, or enqueues asynchronous reads for live request processing.

## Search Flow
`search_cached_index_page()`:
- maps chapter/index page to physical page,
- begins pending-search protection,
- fetches page through `get_volume_page_protected()`,
- searches the initialized chapter index page for a record-page number,
- ends pending-search protection.

`search_cached_record_page()`:
- validates the record-page number,
- fetches the record page under pending-search protection,
- searches the record page for the chunk name,
- returns duplicate metadata if found.

`search_volume_page_cache()` combines index-page lookup and record-page search. If a request resumes from an earlier asynchronous index-page read, it uses the saved record-page number in `request->old_metadata`.

## Writing Chapters
`write_index_pages()` writes all index pages for a chapter:
- prepares scratch bufio page,
- packs open-chapter delta lists,
- writes/marks the page dirty,
- optionally copies page bytes for tests,
- updates the index-page map,
- donates the freshly written index page into the page cache.

`write_record_pages()` writes sorted/encoded record pages from the open chapter’s 1-based record array.

`write_chapter()` maps the virtual chapter to its physical chapter slot, writes index pages, writes record pages, releases the scratch page, and syncs the volume store.

## Cache and Invalidation
`forget_chapter()` invalidates cached pages for a physical chapter under the read mutex.

`donate_index_page_locked()` swaps scratch page data into a cache victim, initializes its chapter-index representation, and inserts it into the page cache. This keeps recently written index pages available without rereading them.

`get_cache_size()` combines page-cache memory and sparse-cache memory when geometry is sparse.

## Volume Boundary Discovery
`probe_chapter()` reads all index pages for a physical chapter and validates:
- consistent virtual chapter number across index pages,
- expected delta-list range progression,
- chapter-index page structure,
- virtual chapter maps back to the physical chapter.

`find_real_end_of_volume()` works backward from the configured volume end, skipping corrupt trailing chapters to find the actual last usable physical chapter.

`find_volume_chapter_boundaries()` uses that real end and delegates to `find_volume_chapter_boundaries_impl()`.

`find_volume_chapter_boundaries_impl()` performs a binary-search-like scan over circular chapter order to find lowest/highest virtual chapter numbers, tolerating a bounded run of bad chapters and accounting for remapped physical chapters.

## Construction and Lifecycle
`allocate_volume()` allocates the volume, copies geometry, computes reserved bufio buffers, opens the volume store, initializes scratch page, radix sorter, record pointer array, sparse cache if needed, page cache, and index-page map.

`make_volume()` initializes mutex/condition variables, allocates reader-thread handles, starts configured reader threads, and returns the constructed volume.

`replace_volume_storage()` swaps the underlying index-layout storage, releases scratch/page-cache/sparse-cache state, closes the old store, and opens a new store.

`free_volume()` stops reader threads, destroys scratch/cache/store/sync primitives, frees map/sorter/geometry/record pointers, and frees the volume.

## Dependencies
Uses chapter/index/page-cache/storage helpers from `chapter-index.h`, `config.h`, `geometry.h`, `hash-utils.h`, `index.h`, `record-page.h`, `sparse-cache.h`, `uds-threads.h`, `volume-store.h`, and logging/assertion/memory utilities.

## Invariants and Risks
- Read mutex and pending-search counters must be ordered carefully; many comments document race-prevention requirements.
- Reader threads must be stopped before caches and volume store are destroyed.
- Index-page validation is skipped differently in rebuild lookup mode.
- Boundary discovery assumes at most one contiguous bad-chapter run, capped by `MAX_BAD_CHAPTERS`.
- `read_chapter_index_from_volume()` initializes a local `volume_page` but reads into the caller-provided `volume_pages[]`; cleanup of those pages is caller-sensitive.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/volume.h -->
# File Research: sources/block-storage/kvdo/vdo/volume.h

## Purpose
Declares the `struct volume` state and public operations for persisted chapter IO, page-cache search, chapter writing, cache management, boundary discovery, and physical page mapping.

## Public Types
- `enum reader_state`: bit flags for reader thread state:
  - `READER_STATE_RUN`
  - `READER_STATE_EXIT`
  - `READER_STATE_STOP`
- `enum index_lookup_mode`:
  - `LOOKUP_NORMAL`
  - `LOOKUP_FOR_REBUILD`
- `struct volume`: owns geometry, volume store, scratch page, nonce, sorting helpers, sparse/page caches, index-page map, reader-thread synchronization, reader-thread array/state, lookup mode, read-thread count, and reserved buffer count.

## Public API Groups
Lifecycle:
- `make_volume()`
- `free_volume()`
- `replace_volume_storage()`

Read/search:
- `enqueue_page_read()`
- `search_volume_page_cache()`
- `search_cached_record_page()`
- `get_volume_page_locked()`
- `get_volume_page_protected()`
- `get_volume_page()`
- `read_chapter_index_from_volume()`

Write/invalidate:
- `forget_chapter()`
- `write_index_pages()`
- `write_record_pages()`
- `write_chapter()`

Discovery/utilities:
- `find_volume_chapter_boundaries()`
- `find_volume_chapter_boundaries_impl()`
- `get_cache_size()`
- `map_to_physical_page()`

## Dependencies
Includes core configuration and index/cache/storage headers:
`common.h`, `config.h`, `chapter-index.h`, `index-layout.h`, `index-page-map.h`, `page-cache.h`, `radix-sort.h`, `sparse-cache.h`, `uds.h`, `uds-threads.h`, and `volume-store.h`.

## Notes
The header exposes some functions primarily for tests or rebuild/single-threaded code, especially direct page-fetch helpers and `find_volume_chapter_boundaries_impl()`.

The comments document important concurrency contracts: callers of protected page access must manage pending-search state as expected, while locked page access requires `read_threads_mutex`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/volume.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/wait-queue.c -->
# File Research: sources/block-storage/kvdo/vdo/wait-queue.c

## Purpose
Implements a small intrusive FIFO wait queue using a circular singly linked list. It supports enqueue, dequeue, notify, transfer, matching extraction, and debug iteration.

## Queue Model
`struct wait_queue` stores only:
- `last_waiter`: tail of the circular list,
- `queue_length`.

The head is `last_waiter->next_waiter`. An empty queue has `last_waiter == NULL`; a single waiter points to itself.

## Main Functions
- `enqueue_waiter()`: asserts the waiter is not already queued, then appends it at tail in O(1).
- `transfer_all_waiters()`: splices all waiters from one queue to another, preserving circular-list structure and emptying the source.
- `notify_all_waiters()`: moves the current queue to a temporary queue first, then drains it with `notify_next_waiter()` so callbacks can safely requeue waiters without causing an infinite loop.
- `get_first_waiter()`: returns the head/oldest waiter.
- `dequeue_matching_waiters()`: drains the source into an iteration queue, requeues nonmatches, collects matches, rolls back on enqueue error, then transfers matches to the caller’s matched queue.
- `dequeue_next_waiter()`: removes and returns the head/oldest waiter, clearing its `next_waiter`.
- `notify_next_waiter()`: dequeues one waiter and invokes either the supplied callback or the waiter’s own callback.
- `get_next_waiter()`: iteration helper for debug scans.

## Dependencies
Includes `wait-queue.h`, `permassert.h`, and `status-codes.h`.

## Invariants and Risks
- A waiter may be in at most one queue; `next_waiter == NULL` means not queued.
- Callback invocation happens after dequeue, so callbacks are free to requeue the waiter.
- The queue is not internally synchronized; callers must provide locking if used concurrently.
- `notify_next_waiter()` assumes a non-NULL effective callback after fallback to `waiter->callback`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/wait-queue.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/wait-queue.h -->
# File Research: sources/block-storage/kvdo/vdo/wait-queue.h

## Purpose
Defines intrusive wait-queue data structures and APIs. The file documents the circular-list representation and provides inline helpers for initialization and simple state queries.

## Public Types
- `struct wait_queue`: queue tail pointer plus length.
- `waiter_callback`: callback invoked when a waiter is notified.
- `waiter_match`: predicate used to extract matching waiters.
- `struct waiter`: intrusive queue node with `next_waiter` and optional per-waiter callback.

## Public API
- Inline helpers:
  - `is_waiting()`
  - `initialize_wait_queue()`
  - `has_waiters()`
  - `count_waiters()`
- Queue operations:
  - `enqueue_waiter()`
  - `notify_all_waiters()`
  - `notify_next_waiter()`
  - `transfer_all_waiters()`
  - `get_first_waiter()`
  - `dequeue_matching_waiters()`
  - `dequeue_next_waiter()`
  - `get_next_waiter()`

## Dependencies
Includes `compiler.h` and `type-defs.h`.

## Notes
The implementation is intentionally compact: the queue owns no waiter memory and uses the waiters’ embedded `next_waiter` links.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/wait-queue.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/workQueue.c -->
# File Research: sources/block-storage/kvdo/vdo/workQueue.c

## Purpose
Implements VDO kernel work queues for `vdo_completion` processing. It supports:
- simple single-thread queues,
- round-robin queues composed of multiple simple queues,
- priority funnel queues,
- kthread lifecycle,
- reduced wakeup behavior,
- debug dumping and current-work-queue introspection.

## Core Data Structures
- `struct vdo_work_queue`: common external object with name, round-robin flag, owner thread, and queue type.
- `struct simple_work_queue`: one worker kthread, priority funnel queues, private data, parent pointer, wait queues, startup state, idle/wakeup atomics, and debug timestamp.
- `struct round_robin_work_queue`: common object plus array of subordinate simple queues.
- Per-CPU `service_queue_rotor`: used to distribute submissions across round-robin subqueues.

## Completion Processing
`poll_for_completion()` scans priority queues from highest used priority down to zero and returns one completion. The comment explicitly notes priority is not strictly enforced under races.

`enqueue_work_queue_completion()`:
1. validates the completion is not already queued,
2. substitutes default priority if requested,
3. clamps invalid priority to zero after assertion failure,
4. records `completion->my_queue`,
5. pushes into the relevant funnel queue,
6. uses memory barriers, `idle`, and `first_wakeup` atomics to decide whether to wake the worker.

`service_work_queue()` runs optional start hook, repeatedly polls or waits for completions, runs callbacks through `vdo_run_completion_callback()`, yields on `need_resched()`, and runs optional finish hook on exit.

`wait_for_next_completion()` prepares the worker to sleep, marks it idle only after wait setup, polls again to avoid lost wakeups, checks `kthread_should_stop()`, schedules, and clears idle state on exit.

## Lifecycle
`make_simple_work_queue()` allocates the queue, duplicates the name, initializes wait queues/spinlock, allocates priority funnel queues, starts a kthread, records pid, and waits until the runner has entered VDO code.

`make_work_queue()` creates either:
- a simple queue when `thread_count == 1`, or
- a round-robin queue with `thread_count` subordinate simple queues.

`finish_work_queue()` stops simple worker threads or all round-robin subthreads. `free_work_queue()` finishes then frees the appropriate queue form.

## Debug and Introspection
- `dump_work_queue()` logs thread/idle/task-state info for simple or all round-robin queues.
- `dump_completion_to_buffer()` formats queue name and callback function symbol compactly.
- `get_current_work_queue()` returns the current VDO work queue only when running in a VDO work-queue kthread and not interrupt context.
- `get_work_queue_private_data()` returns the simple queue’s private pointer for the current worker thread.
- `get_work_queue_owner()` returns the owner `vdo_thread`.
- `vdo_work_queue_type_is()` compares a queue’s type pointer.

The current-thread detection includes kernel-version-specific handling for pre-5.13 `kthread_func()` behavior around `current->set_child_tid`.

## Dependencies
Uses Linux atomics, kthreads, percpu data, scheduler/task helpers, funnel queues, completion callbacks, logging, allocation, assertions, and string helpers.

## Invariants and Risks
- Completion `my_queue` must be NULL before enqueue and is cleared before callback execution.
- Queue finish assumes no further enqueueing after `finish_work_queue()` begins.
- Wakeup reduction relies on paired barriers and atomic state; comments acknowledge tolerated races with periodic wakeups/scheduling.
- Round-robin distribution is approximate and per-CPU rotor based.
- `vdo_work_queue_type_is()` assumes a valid non-NULL queue pointer.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/workQueue.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/workQueue.h -->
# File Research: sources/block-storage/kvdo/vdo/workQueue.h

## Purpose
Declares the VDO work-queue API and queue-type descriptor used by the completion-processing subsystem.

## Public Types
- `MAX_VDO_WORK_QUEUE_NAME_LEN`: aliases `TASK_COMM_LEN`.
- `struct vdo_work_queue_type`: optional start/finish hooks plus max/default completion priority.

## Public API
- `make_work_queue()`: creates a simple or round-robin work queue.
- `enqueue_work_queue()`: submits a `vdo_completion`.
- `finish_work_queue()`: stops worker threads.
- `free_work_queue()`: finishes and frees the queue.
- `dump_work_queue()`: logs queue state.
- `dump_completion_to_buffer()`: writes compact completion debug info.
- `get_work_queue_private_data()`: returns current queue private data.
- `get_current_work_queue()`: returns the queue for the current worker thread.
- `get_work_queue_owner()`: returns the owning `vdo_thread`.
- `vdo_work_queue_type_is()`: checks queue type identity.

## Dependencies
Includes Linux `<linux/sched.h>` for `TASK_COMM_LEN`, plus `funnel-queue.h`, `kernel-types.h`, and `types.h`.

## Notes
The header exposes `struct vdo_work_queue` opaquely. Implementation details are private to `workQueue.c`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/workQueue.h -->