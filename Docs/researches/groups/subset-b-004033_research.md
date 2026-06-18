# subset-b-004033 research

This grouped report covers VDO/UDS volume storage, maps, I/O submission, logging, zones, memory allocation, statistics, hashing, packing, assertions, and priority queue support under `sources/distributed-fs/ceph-client/drivers/md/dm-vdo`. Each section preserves the original source path so reconciliation can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.c

## Purpose
`volume.c` implements the UDS index volume: a persistent circular log of deduplication chapters stored through `dm-bufio`. It reads, writes, caches, invalidates, and rebuilds volume chapter pages. A chapter contains static delta-index pages followed by sorted record pages. The file is the bridge between in-memory indexing requests and on-disk chapter/index/record layout.

## Important APIs, Types, and Functions
The main exported API is `uds_make_volume()`, `uds_free_volume()`, `uds_replace_volume_storage()`, `uds_find_volume_chapter_boundaries()`, `uds_search_volume_page_cache()`, `uds_search_volume_page_cache_for_rebuild()`, `uds_search_cached_record_page()`, `uds_forget_chapter()`, `uds_write_chapter()`, `uds_prefetch_volume_chapter()`, `uds_read_chapter_index_from_volume()`, `uds_get_volume_record_page()`, and `uds_get_volume_index_page()`. Internals center on physical-page mapping helpers, the `page_cache` LRU, `queued_read` processing, `search_pending_counter` invalidation protection, record-page binary-tree searches, chapter-index validation, record page encoding, and chapter probing.

## Control Flow
Reads first map virtual chapter/page coordinates to physical page numbers. Zone threads perform a fast cache lookup under a per-zone pending-search counter; cache misses are enqueued to reader threads unless the caller is in a synchronous rebuild path. Reader threads reserve circular queue entries, read pages with `dm_bufio_read()`, initialize index pages when needed, install pages into the cache, perform the queued lookup immediately, then requeue waiting requests to `STAGE_INDEX`. Writes pack index pages from `open_chapter_index`, update the index page map, donate newly written index pages into the cache, encode sorted records into heap-ordered binary-search pages, mark buffers dirty, and finally flush dirty buffers. Rebuild probing validates chapter index pages, detects empty or partially written tails, then finds lowest/highest virtual chapter numbers across the circular volume.

## State and Persistence Behavior
Persistent state is the chapter log on the block device. Runtime state includes `dm_bufio_client`, `index_page_map`, optional sparse cache, radix sorter, record pointer workspace, and page cache arrays. Cache entries own `dm_buffer` references until eviction/free. Pending search counters and memory barriers protect readers from cache invalidation while not holding the read-thread mutex. `uds_forget_chapter()` invalidates all physical pages for a virtual chapter, including pending reads. `uds_replace_volume_storage()` drops all cached buffers and sparse-cache entries before reopening storage.

## Dependencies and Integration Points
This file depends on `dm-bufio`, UDS geometry/config/chapter-index/index-page-map/radix-sort/sparse-cache code, VDO logging, memory allocation, assertions, and thread/condition helpers. Requests are requeued through `uds_enqueue_request()`. Volume results feed the UDS index search path and rebuild path; writes are driven when open chapters close.

## Risks and Edge Cases
Concurrency is subtle: cache installation, invalidation, async read completion, and search-pending counters must keep memory barriers paired. Reader queue saturation blocks enqueuers on a condition variable. Corrupt chapter-index pages can poison rebuild boundary discovery. `MAX_BAD_CHAPTERS` limits tolerated contiguous bad chapters. Cache slot counts are capped by `VOLUME_CACHE_MAX_ENTRIES`; configuration errors can fail initialization. Index page map mismatches are treated as corrupt data except during rebuild lookup mode.

## Test Signals
Useful tests include cache hit/miss searches, queued duplicate page reads, invalidation during pending reads, volume writes followed by immediate searches, rebuild boundary scans with empty, full, wrapped, and partially written volumes, dm-bufio read/write errors, sparse index configurations, and shutdown with reader threads blocked on the queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.h

## Purpose
`volume.h` defines the UDS volume interface and the internal cache/read-queue structures shared with `volume.c`. It documents that a volume is both the persistent chapter region and the code object that manages storage I/O.

## Important APIs, Types, and Functions
`enum index_lookup_mode` distinguishes normal lookup from rebuild lookup. `struct queued_read` represents one pending physical page read plus linked waiting requests. `struct cached_page` holds a `dm_buffer`, physical page number, LRU timestamp, and decoded `delta_index_page`. `struct page_cache` owns cache arrays, physical-page-to-cache/read-queue index, pending-search counters, read-queue cursors, and an LRU clock. `struct volume` owns geometry, bufio client, nonce, sorter, sparse cache, page cache, index page map, reader-thread synchronization, lookup mode, and reserved buffer count. The prototypes expose construction, teardown, storage replacement, search, write, prefetch, and page read helpers.

## Control Flow
The header has no runtime logic, but it defines the contracts used by index search and rebuild code: callers create a `volume`, search page cache or record pages, forget overwritten chapters, write closed chapters, prefetch chapters, and read index/record pages by chapter/page.

## State and Persistence Behavior
The structs separate persistent volume data from volatile cache state. `volume->client` is the handle to durable chapter storage; `page_cache` and `sparse_cache` are only runtime accelerators. Read-queue indices are circular buffer cursors, and `search_pending_counter` is cacheline-aligned to avoid cross-zone contention.

## Dependencies and Integration Points
The header includes Linux atomic/cache/dm-bufio types plus UDS geometry, layout, indexer, index page map, radix sort, sparse cache, and VDO assertion/thread utilities. It is included by volume implementation and index/rebuild code that needs volume operations.

## Risks and Edge Cases
Because several internal structures are visible, callers must still respect the intended ownership: direct mutation of cache fields would bypass locking and barriers. Cache sizing uses `u16` slots and flags, so callers must honor implementation limits. `lookup_mode` changes corruption handling semantics and should be controlled by rebuild code only.

## Test Signals
Compile coverage should catch signature drift across index modules. Runtime signals come from successful volume construction/destruction, reader-thread startup, cache size accounting, normal and rebuild lookup paths, and storage replacement with no stale `dm_buffer` references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.c

## Purpose
`int-map.c` implements an opaque map from `u64` integer keys to non-NULL pointer values using non-concurrent hopscotch hashing. It is used where VDO needs fast in-memory lookup without per-entry allocation, such as active PBN/LBN locks and bio merge tracking.

## Important APIs, Types, and Functions
The public API is `vdo_int_map_create()`, `vdo_int_map_free()`, `vdo_int_map_size()`, `vdo_int_map_get()`, `vdo_int_map_put()`, and `vdo_int_map_remove()`. `struct bucket` stores biased hop offsets plus key/value. `struct int_map` tracks size, capacity, bucket count, and bucket array. Key internals include `hash_key()`, `select_bucket()`, `search_hop_list()`, `find_empty_bucket()`, `move_empty_bucket()`, `find_or_make_vacancy()`, `resize_buckets()`, and `update_mapping()`.

## Control Flow
Creation allocates an expanded bucket array sized from the requested capacity and default load factor. Lookup hashes a key to a neighborhood and scans that neighborhood's sorted hop list. Insert first checks for an existing key, then finds or creates an empty bucket in the target neighborhood. If no vacancy can be moved within range, the map grows by roughly 50%, rehashes all entries, and retries. Remove splices the matching bucket out of its neighborhood hop list and clears the value.

## State and Persistence Behavior
All state is volatile heap memory. The map owns only the bucket array and map object, not mapped values. It never shrinks after removals. Values must be non-NULL because NULL marks an empty bucket. There is no internal locking; callers serialize access when used concurrently.

## Dependencies and Integration Points
The implementation uses VDO allocation/logging/assertion helpers, `numeric.h` for integer conventions, Linux min/max helpers, and VDO error codes. It is integrated by logical zones, physical zones, and I/O submitter merge maps.

## Risks and Edge Cases
Resize is expensive and may cause high insertion latency; capacity should be chosen for expected peak size when latency matters. Hop relocation relies on biased offsets and packed buckets, so off-by-one bugs would corrupt lookup chains. `vdo_int_map_put()` rejects NULL values with `-EINVAL`. Failed resize restores the old map, but callers must still handle insertion failure. The implementation is explicitly not thread-safe.

## Test Signals
Tests should cover create with zero and explicit capacity, insert/get/remove, duplicate insert with update false/true, old-value return, growth under high load, deletion from head/middle/tail hop lists, NULL insertion rejection, and caller-side locking in concurrent integration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.h

## Purpose
`int-map.h` declares the opaque integer-to-pointer map used by VDO subsystems. It states the key contract: `u64` keys, `void *` values, and no support for NULL values.

## Important APIs, Types, and Functions
The header forward-declares `struct int_map` and exposes creation, free, size, get, put, and remove functions. `vdo_int_map_put()` takes an `update` flag and optional old-value output so callers can either insert-only or replace existing mappings.

## Control Flow
The header defines no logic, but callers follow a lifecycle: create a map, perform get/put/remove operations, then free it after all external value ownership has been handled.

## State and Persistence Behavior
Map state is private to `int-map.c`; the header enforces opacity. Persistence is not involved. Since values are not owned by the map, freeing a map does not free stored objects.

## Dependencies and Integration Points
It includes Linux compiler and type definitions. The interface is used by zone lock tables and bio submission merge tables.

## Risks and Edge Cases
Callers must not store NULL values, must serialize concurrent access, and must free or otherwise own mapped values separately. `update=false` is important for lock-acquisition races because it returns the existing holder without overwriting it.

## Test Signals
Compile-time API compatibility plus integration tests for physical/logical zone lock maps and I/O submitter merge maps are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/int-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.c

## Purpose
`io-submitter.c` owns VDO bio-submission work queues. It keeps potentially blocking `submit_bio*()` calls off other VDO threads, starts block plugs on bio threads, routes data and metadata I/O to the backing device, counts statistics, and opportunistically merges adjacent data bios before submission.

## Important APIs, Types, and Functions
`struct io_submitter` stores bio-queue count, rotation interval, and per-queue data. `struct bio_queue_data` holds a work queue, `blk_plug`, merge `int_map`, mutex, and queue number. Public functions are `vdo_make_io_submitter()`, `vdo_cleanup_io_submitter()`, `vdo_free_io_submitter()`, `vdo_submit_vio()`, `vdo_submit_data_vio()`, `__submit_metadata_vio()`, and `vdo_submit_metadata_vio_wait()`. Important internals include `send_bio_to_device()`, `submit_data_vio()`, `try_bio_map_merge()`, and merge-map helpers.

## Control Flow
Initialization allocates one bio queue per configured bio thread, creates an `int_map` sized for active requests, and creates VDO work queues whose start/finish hooks start and finish `blk_plug`. Data VIO submission first initializes a single-bio list, checks the merge map for adjacent same-priority same-direction bios, and either merges into a pending VIO or schedules submission on the bio zone. Submission removes the head/tail sector mappings and submits the merged bio list. Metadata submission resets the VIO bio, marks it `REQ_META`, assigns a bio-zone callback, and launches by metadata priority. The synchronous metadata path calls `submit_bio_wait()` before full queue infrastructure is available.

## State and Persistence Behavior
State is runtime-only. Merge maps are protected by per-queue mutexes and map the current head and tail sectors of each pending merged bio list. Stats are updated in `send_bio_to_device()`. Cleanup finishes queues before `vdo_free_io_submitter()` releases queue references and maps.

## Dependencies and Integration Points
This file depends on Linux `bio`, `blk_plug`, mutexes, VDO work queues, VIO/data_vio helpers, the backing device accessor, `int-map`, logging, memory allocation, and VDO admin state. It is called by data write paths, metadata read/write paths, packer compressed writes, and journal/block-map code.

## Risks and Edge Cases
Merge tracking assumes serialized access through the per-queue mutex and only tracks head/tail sectors. Map insertion failure is logged as an assertion-only condition, so memory pressure can reduce merge correctness diagnostics. Metadata error-handler thread assumptions are documented as fragile if future callers change callback threading. Submitting while quiescent is assertion-logged but not hard-blocked beyond existing state handling. Cleanup order matters to avoid work-queue races.

## Test Signals
Validate data reads/writes and metadata I/O under multiple bio thread counts, merge of adjacent bios in both directions, no merge across priority or direction, flush VIO submission, sync metadata I/O before work queues, stats counters, queue cleanup, and backing-device error completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.h

## Purpose
`io-submitter.h` exposes the VDO I/O submitter abstraction and convenience wrappers for metadata and flush VIO submission.

## Important APIs, Types, and Functions
The header forward-declares `struct io_submitter` and declares create/cleanup/free functions plus data and metadata submission entry points. Inline helpers `vdo_submit_metadata_vio()`, `vdo_submit_metadata_vio_with_size()`, and `vdo_submit_flush_vio()` normalize common calls to `__submit_metadata_vio()`.

## Control Flow
Callers create the submitter during VDO setup, submit data VIOs through `vdo_submit_data_vio()`, submit metadata through the inline wrappers, optionally use the synchronous metadata wait helper early in startup, and finally cleanup/free during shutdown.

## State and Persistence Behavior
The header exposes no internals. All submitter state is runtime work-queue and merge-map state owned by the implementation. There is no persistence.

## Dependencies and Integration Points
It includes Linux `bio` declarations, VDO constants, and VDO types. Integration points include metadata subsystems that need physical block I/O and data paths that submit user data or compressed blocks.

## Risks and Edge Cases
The flush helper currently uses `REQ_OP_WRITE | REQ_PREFLUSH` with a FIXME asking whether plain `REQ_OP_FLUSH` is enough. Callers passing custom size/data must ensure buffers remain valid until completion.

## Test Signals
Compile coverage of inline wrappers and runtime tests for metadata read/write, custom-size metadata writes, flush submission, and early synchronous metadata reads are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/io-submitter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.c

## Purpose
`logger.c` implements VDO logging on top of kernel `printk` APIs. It applies the module log level, formats context-aware prefixes for interrupt, VDO device, VDO kernel thread, and generic process contexts, and provides error-string and assertion support.

## Important APIs, Types, and Functions
Public functions are `vdo_get_log_level()`, `vdo_log_embedded_message()`, `vdo_vlog_strerror()`, `__vdo_log_strerror()`, `vdo_log_backtrace()`, `__vdo_log_message()`, and `vdo_pause_for_logger()`. Internals include `get_current_interrupt_type()`, `emit_log_message_to_kernel()`, and `emit_log_message()`.

## Control Flow
`vdo_get_log_level()` clamps an invalid global level back to default. Logging calls build `va_format` values, choose output priority, and emit through `pr_crit`, `pr_err`, `pr_warn`, `pr_info`, `pr_debug`, or generic `printk`. Prefix selection first handles interrupt context, then registered device IDs, then own kernel threads, then generic process/module names. Error logging resolves VDO/UDS error strings and appends numeric codes.

## State and Persistence Behavior
`vdo_log_level` is global runtime state read with `READ_ONCE()` and corrected with `WRITE_ONCE()`. No log state is persistent. `vdo_pause_for_logger()` sleeps briefly to reduce message loss after heavy logging.

## Dependencies and Integration Points
The file depends on Linux current task, interrupt context, printk, module, scheduler, VDO error string conversion, thread-device IDs, and thread-utils naming. It is used across nearly all VDO/UDS modules and by `permassert.c`.

## Risks and Edge Cases
Logging can be called from interrupt contexts, so context detection and formatting avoid blocking work except for explicit pause. Invalid priorities fall back to default `printk`. `va_list` handling uses `va_copy()` because ABI representation can vary. High-volume logging still risks kernel log loss, hence rate-limited macros in the header and pause helper.

## Test Signals
Test log level clamping, each priority path, error-string formatting, interrupt-context prefixing where feasible, device-thread prefixing, assertion backtrace logging, and rate-limited macro behavior from callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.h

## Purpose
`logger.h` defines VDO logging priorities, module prefixing, public logging functions, and convenience macros used throughout VDO/UDS code.

## Important APIs, Types, and Functions
The header maps `VDO_LOG_*` constants to kernel log levels, declares `vdo_log_level`, `vdo_get_log_level()`, embedded/error/string/backtrace functions, and macros such as `vdo_log_error_strerror()`, `vdo_log_warning()`, `vdo_log_info()`, and `vdo_log_ratelimit()`.

## Control Flow
Macros wrap calls to implementation functions with the standard `VDO_LOGGING_MODULE_NAME`. `vdo_log_ratelimit()` creates a static ratelimit state at each call site and invokes the supplied log function only when allowed.

## State and Persistence Behavior
The only exposed state is the global runtime log level. No persistent state is defined.

## Dependencies and Integration Points
The header includes kernel log level, module, ratelimit, and device-mapper definitions. It is a common dependency of VDO modules and assertion helpers.

## Risks and Edge Cases
Because logging macros preserve caller errno only by convention in implementation, callers should avoid relying on side effects. Rate-limit state is per macro expansion site. Module prefixing depends on device-mapper `DM_NAME`.

## Test Signals
Compile-time format checking via `__printf` attributes, rate-limited logging coverage, and integration logs from error paths are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.c

## Purpose
`logical-zone.c` creates and manages logical zones, which serialize logical block operations, track write flush generations, coordinate zone drains/resumes, and choose physical allocation zones.

## Important APIs, Types, and Functions
Public functions are `vdo_make_logical_zones()`, `vdo_free_logical_zones()`, `vdo_drain_logical_zones()`, `vdo_resume_logical_zones()`, `vdo_increment_logical_zone_flush_generation()`, `vdo_acquire_flush_generation_lock()`, `vdo_release_flush_generation_lock()`, `vdo_get_next_allocation_zone()`, and `vdo_dump_logical_zone()`. Internals include completion conversion, action-manager zone thread lookup, per-zone initialization, admin-state drain/resume actions, oldest-generation tracking, and flusher notification callbacks.

## Control Flow
Creation allocates a flexible `logical_zones` object, initializes each zone's LBN operation map, completion, block-map-zone pointer, state, write list, allocation-zone pointer, and thread. It then creates an action manager to schedule administrative operations across zone threads. Write VIOs acquire the current flush generation and are queued on `write_vios`; release removes them and may notify the flusher when the oldest active generation advances. Drains complete only when the zone is draining, no notification is in progress, and the write list is empty. Allocation zones rotate every `ALLOCATIONS_PER_ZONE` allocations.

## State and Persistence Behavior
State is runtime-only: LBN operation maps, active write list, flush counters, notification flags, and admin states. Flush generations persist only as in-memory ordering contracts while VIOs are active; durable flush behavior is completed by the flusher and lower metadata paths.

## Dependencies and Integration Points
The file integrates with VDO action managers, admin-state machinery, block map zones, physical zones, flush subsystem, data VIO lifecycle, completions, thread configuration, `int-map`, and logging/allocation helpers.

## Risks and Edge Cases
Generation notification crosses logical-zone and flusher threads, so `oldest_active_generation` uses `READ_ONCE()` in dumps and controlled mutation on zone thread. Draining must account for in-flight notifications as well as active writes. The physical allocation-zone choice assumes physical zone count is nonzero. Thread assertions are log-only, so misuse may continue after diagnostics.

## Test Signals
Tests should cover zone creation with multiple logical/physical zones, write acquire/release ordering, flush generation increments, flusher notifications after oldest generation advances, drain waiting for active writes, resume from quiescent state, allocation-zone rotation, and dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.h

## Purpose
`logical-zone.h` defines logical-zone state and declares zone lifecycle, flush-generation, allocation-zone, and dump APIs.

## Important APIs, Types, and Functions
`struct logical_zone` contains a completion for flush notification, owner pointer, zone/thread IDs, active LBN operation map, block-map zone, flush generation counters, notification state, active write list, admin state, current physical allocation zone, allocation counter, and next-zone link. `struct logical_zones` owns the VDO pointer, action manager, zone count, and flexible array of zones. The header declares construction, freeing, drain/resume, generation increment, lock acquire/release, allocation-zone selection, and dump functions.

## Control Flow
The header defines no executable flow, but it establishes that data VIO write paths call acquire/release around flush generations, admin code drains/resumes all zones through the action manager, and allocation code asks the logical zone for the next physical zone.

## State and Persistence Behavior
All fields are runtime state. The active-generation fields provide ordering for flush completion but are not stored on disk.

## Dependencies and Integration Points
It includes Linux lists, admin-state, int-map, and VDO types, and forward-declares physical zones. It is consumed by data VIO, flush, block-map, and VDO setup paths.

## Risks and Edge Cases
The exposed struct makes direct field access possible; correctness depends on callers honoring zone-thread ownership. `oldest_active_generation` is read from another thread, so updates must remain disciplined.

## Test Signals
Compile coverage, data VIO flush-generation lifecycle tests, drain/resume administrative tests, and allocation-zone rotation tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/logical-zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.c

## Purpose
`memory-alloc.c` centralizes VDO/UDS memory allocation. It chooses `kmalloc` or `vmalloc`, zeroes allocations, tracks current and peak memory usage, avoids recursive filesystem/block I/O from restricted threads via `memalloc_noio_save()`, and reports leaks at module exit.

## Important APIs, Types, and Functions
Public functions are `vdo_allocate_memory()`, `vdo_allocate_memory_nowait()`, `vdo_free()`, `vdo_reallocate_memory()`, `vdo_duplicate_string()`, `vdo_memory_init()`, `vdo_memory_exit()`, `vdo_register_allocating_thread()`, `vdo_unregister_allocating_thread()`, `vdo_get_memory_stats()`, and `vdo_report_memory_usage()`. Internal state includes `allocating_threads`, `struct vmalloc_block_info`, and cacheline-aligned `memory_stats`.

## Control Flow
Initialization sets up the spinlock and thread registry. Regular allocation validates the output pointer, returns NULL for size zero, enters NOIO context when the current thread is not registered as allocation-safe, tries `kmalloc` for page-sized-and-smaller unaligned allocations, otherwise allocates a small tracking record and retries `__vmalloc()` for up to roughly one second before logging failure. Successful allocations update stats. Free detects vmalloc addresses and removes matching tracking records before `vfree()`, or updates kmalloc stats before `kfree()`. Reallocation allocates new zeroed memory, copies the smaller of old/new sizes, and frees the old block.

## State and Persistence Behavior
Memory stats are runtime-only and protected by a spinlock. Vmalloc allocations are tracked in a linked list keyed by pointer. `vdo_memory_exit()` assertion-logs nonzero tracked bytes to catch leaks. Thread allocation permissions live in a runtime thread registry.

## Dependencies and Integration Points
The file uses Linux slab/vmalloc/mm/noio APIs, delay helpers, spinlocks, VDO logging, assertions, and thread registry helpers. Nearly all VDO modules allocate through macros in `memory-alloc.h`, making this a global accounting and failure behavior point.

## Risks and Edge Cases
The vmalloc tracking record itself is allocated through `vdo_allocate()`, creating nested accounting that must be freed carefully. `remove_vmalloc_block()` logs if a pointer is not found. Alignment is considered only in the kmalloc/vmalloc choice; callers requiring cache alignment use the header wrapper. Incorrect thread registration can cause allocation from I/O paths without NOIO protection or noisy false warnings.

## Test Signals
Tests should cover kmalloc and vmalloc paths, zero-size allocation, allocation failure, nowait allocation, reallocation growth/shrink/free, duplicate string, stats current/peak values, leak detection at exit, NOIO behavior for unregistered threads, and freeing unknown or stale pointers through fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.h

## Purpose
`memory-alloc.h` exposes VDO's tracked allocation interface and type-safe allocation macros.

## Important APIs, Types, and Functions
Macros `vdo_allocate()` and `vdo_allocate_extended()` calculate byte sizes using `size_mul()` and `struct_size()`. `vdo_allocate_cache_aligned()` requests cacheline alignment. `vdo_forget()` atomically nulls a pointer variable and returns the old value for transfer/free patterns. Functions declare allocation, nowait allocation, reallocation, string duplication, free, memory lifecycle, allocating-thread registration, stats retrieval, and reporting.

## Control Flow
Callers normally use `vdo_allocate(count, what, &ptr)` or `vdo_allocate_extended(count, field, what, &ptr)`, then release with `vdo_free()` or transfer ownership with `vdo_forget()`.

## State and Persistence Behavior
The header declares runtime memory accounting functions but no persistent state. `vdo_forget()` changes caller-owned pointer state to prevent reuse after ownership transfer.

## Dependencies and Integration Points
It includes Linux cache, I/O page size, overflow helpers, VDO assertions, and thread-registry types. It is included throughout the VDO tree.

## Risks and Edge Cases
Macro type inference depends on passing an address of a pointer with the expected target type. `vdo_forget()` casts through `void **`; callers must not pass expressions with unexpected side effects. Allocation macros rely on overflow-aware helpers.

## Test Signals
Compile-time macro use across flexible-array allocations, cache-aligned allocation tests, `vdo_forget()` ownership transfer patterns, and memory stat queries validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/memory-alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.c

## Purpose
`message-stats.c` serializes VDO runtime statistics and configuration into a textual, brace-delimited message format used by device-mapper status/config reporting paths.

## Important APIs, Types, and Functions
Public functions are `vdo_write_stats()` and `vdo_write_config()`. Small writer helpers serialize `u64`, `u32`, `u8`, booleans, strings, and block counts while advancing `buf` and reducing `maxlen`. Structured writers cover block allocator, commit, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash lock, errors, bio stats, memory usage, index stats, full VDO stats, index memory, and index config.

## Control Flow
`vdo_write_stats()` allocates a temporary `struct vdo_statistics`, fetches a snapshot with `vdo_fetch_statistics()`, writes all fields through nested writer helpers, and frees the snapshot. `vdo_write_config()` writes version, physical/logical sizes, slab size, and index config directly from `vdo->states.vdo.config` and geometry. All helpers append with `scnprintf()` and update the caller's remaining buffer length.

## State and Persistence Behavior
The file does not own persistent state. It observes current statistics snapshots and configuration. Output is transient text written into caller-provided buffers.

## Dependencies and Integration Points
It depends on VDO dedupe/indexer/statistics/thread-device/VDO structures, logging, and allocation. It integrates with status-message paths that expose VDO operational counters and configuration to userspace.

## Risks and Edge Cases
The writers subtract `count` from an unsigned `maxlen`; if callers provide an already exhausted buffer, truncation behavior depends on `scnprintf()` return semantics and could underflow if misused. Output is manually formatted and must stay compatible with userspace parsers. `vdo_write_stats()` can fail only if temporary allocation fails.

## Test Signals
Validate full stats and config output for normal and small buffers, parser compatibility, fractional index memory values, every nested statistics block, allocation failure in stats snapshot, and stable field names expected by management tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.h

## Purpose
`message-stats.h` declares the public VDO status/config serialization functions.

## Important APIs, Types, and Functions
It declares `vdo_write_config(struct vdo *vdo, char **buf, unsigned int *maxlen)` and `vdo_write_stats(struct vdo *vdo, char *buf, unsigned int maxlen)`.

## Control Flow
The header defines no logic. Status paths call these functions with a VDO instance and output buffer to produce current config or stats text.

## State and Persistence Behavior
No state is declared. Output is transient and derived from live VDO state.

## Dependencies and Integration Points
It includes `types.h` for `struct vdo` visibility. It is used by device-mapper target/status code.

## Risks and Edge Cases
Callers must pass valid buffers and lengths; `vdo_write_config()` mutates the buffer pointer and length by reference, while `vdo_write_stats()` takes them by value.

## Test Signals
Compile coverage in status code and runtime status/config output validation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.c

## Purpose
`murmurhash3.c` provides a kernel-adapted implementation of MurmurHash3 x64 128-bit hashing for non-cryptographic hashing needs.

## Important APIs, Types, and Functions
The exported function is `murmurhash3_128(const void *key, const int len, const u32 seed, void *out)`. Helpers are `rotl64()`/`ROTL64` and `fmix64()` for final avalanche mixing.

## Control Flow
The function initializes two 64-bit hash lanes from the seed, processes 16-byte little-endian blocks with Murmur constants, handles a switch-based tail for 0-15 remaining bytes, xors in length, mixes the lanes together, finalizes each lane with `fmix64()`, mixes again, and stores two 64-bit words to `out`.

## State and Persistence Behavior
There is no state or persistence. Output is deterministic for key bytes, length, and seed.

## Dependencies and Integration Points
It uses Linux unaligned little-endian access helpers and compiler/types declarations from the header. It is suitable for in-kernel hash tables or content/index hashing where cryptographic security is not required.

## Risks and Edge Cases
The implementation writes `out` as `u64 *`, so callers must provide at least 16 bytes and tolerate unaligned stores if applicable. Length is `int`; negative lengths would be invalid caller behavior. It is not cryptographic and must not be used for adversarial integrity or authentication.

## Test Signals
Known MurmurHash3 x64_128 test vectors for multiple lengths, seeds, unaligned keys, and tail sizes 0-15 are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.h

## Purpose
`murmurhash3.h` declares the MurmurHash3 128-bit hashing function used by VDO/UDS code.

## Important APIs, Types, and Functions
It exposes `murmurhash3_128(const void *key, int len, u32 seed, void *out)`.

## Control Flow
No logic is defined here; callers pass key bytes, length, seed, and output storage to the implementation.

## State and Persistence Behavior
No state is declared. Hash output is deterministic and transient.

## Dependencies and Integration Points
The header includes Linux compiler and type definitions. It can be included by any module needing this non-cryptographic hash.

## Risks and Edge Cases
The output buffer size contract is implicit; callers must provide enough space for the 128-bit result. The hash is not security-sensitive.

## Test Signals
Compile coverage and known-vector tests for callers validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/murmurhash3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/numeric.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/numeric.h

## Purpose
`numeric.h` defines small inline helpers for little-endian integer serialization/deserialization from byte buffers while advancing an offset cursor.

## Important APIs, Types, and Functions
Helpers include `decode_s64_le()`, `encode_s64_le()`, `decode_u64_le()`, `encode_u64_le()`, `decode_s32_le()`, `encode_s32_le()`, `decode_u32_le()`, `encode_u32_le()`, `decode_u16_le()`, and `encode_u16_le()`.

## Control Flow
Each decode reads an unaligned little-endian integer at `buffer + *offset`, stores it to the output, and increments the offset by the type size. Each encode writes the value to `data + *offset` in little-endian order and increments the offset.

## State and Persistence Behavior
The only state mutation is the caller-provided offset cursor. The helpers are commonly used for persistent on-disk or wire-format structures where byte order must be fixed.

## Dependencies and Integration Points
It includes Linux unaligned, kernel, and type headers. It supports UDS/VDO encoders and decoders that need source-tree-local numeric helpers.

## Risks and Edge Cases
There is no bounds checking; callers must ensure the buffer has enough bytes. Signed helpers rely on storing through the corresponding unaligned unsigned access width. Offset pointer must be valid and initialized.

## Test Signals
Round-trip tests for each width/sign, unaligned buffer addresses, offset advancement, and known little-endian byte sequences validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/numeric.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.c

## Purpose
`packer.c` batches multiple compressed data VIO fragments into one compressed physical block. It improves space efficiency by only writing compressed form when at least two fragments fit into a block, manages packer bins, writes compressed blocks, shares resulting PBN locks, handles cancellation/rendezvous, and supports flush/drain/resume.

## Important APIs, Types, and Functions
Public APIs include `vdo_get_compressed_block_fragment()`, `vdo_make_packer()`, `vdo_free_packer()`, `vdo_get_packer_statistics()`, `vdo_attempt_packing()`, `vdo_flush_packer()`, `vdo_remove_lock_holder_from_packer()`, `vdo_increment_packer_flush_generation()`, `vdo_drain_packer()`, `vdo_resume_packer()`, and `vdo_dump_packer()`. Key internals include sorted bin insertion, bin allocation, `abort_packing()`, compressed-write completion/error handlers, `remove_from_bin()`, `initialize_compressed_block()`, `pack_fragment()`, `write_bin()`, `select_bin()`, and drain checks.

## Control Flow
Incoming compressed VIOs arrive on the packer thread in `DATA_VIO_COMPRESSING`. The packer increments in-packer stats, rejects VIOs during drain/flush-generation mismatch, selects the first best-fit bin, advances compression state, and enqueues the VIO. Full or overflowed bins are written: the first uncanceled VIO becomes the agent, its scratch block becomes the compressed block, other fragments are copied into slots, and single-fragment batches are aborted to normal write. Successful compressed writes release all client VIOs with a shared compressed write lock and mapping state. Errors reset clients back to normal write. Flush writes all non-empty bins; drain prevents new entries and completes after bins and canceled rendezvous state clear.

## State and Persistence Behavior
Persistent output is the compressed block format: a packed version number and little-endian fragment sizes followed by fragment data. Runtime state includes sorted bins, a canceled bin, admin state, flush generation, and statistics. Packer state is volatile but controls durable mapping state for compressed fragments.

## Dependencies and Integration Points
The packer integrates with admin-state, completions, data VIO compression stages, physical-zone allocation/PBN locks, VIO bio setup, I/O submitter, VDO read-only state, encodings/version packing, constants, statistics, and logging/allocation/assertion helpers.

## Risks and Edge Cases
Correctness depends on packer-thread confinement and compression-stage transitions. Single compressed fragments must not be written because they save no space. Cancellation requires rendezvous through the canceled bin, and lock-holder removal must update slot indexes. Fragment size and version validation protect readers. Flush generation prevents older writes from remaining packed across flush boundaries. Error recovery must avoid leaking PBN locks or leaving waiters in bins.

## Test Signals
Test fragment extraction with valid/invalid versions, slot states, offsets, and oversized sizes; packing two or more fragments; single-fragment abort; bin sorting/overflow; cancellation and lock-holder removal; compressed write success/error; read-only handling; packer flush/drain/resume; stats counters; and flush-generation advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.h

## Purpose
`packer.h` defines the compressed block on-disk overlay, packer bin/packer runtime structures, default bin count, and public packer API.

## Important APIs, Types, and Functions
`struct compressed_block_header` stores a packed version and fragment sizes. `struct compressed_block` overlays the header and data area. `VDO_COMPRESSED_BLOCK_DATA_SIZE` and `VDO_MAX_COMPRESSED_FRAGMENT_SIZE` define compressed-fragment limits. `struct packer_bin` stores sorted-list links, used slots, free space, and incoming data VIO pointers. `struct packer` stores thread ID, bin count/list, canceled bin, admin state, flush generation, and statistics. The header declares compressed-fragment lookup, packer lifecycle, statistics, packing/flush/drain/resume, lock-holder removal, generation increment, and dump functions.

## Control Flow
The header sets the data contracts used by compression paths: compressed reads decode fragments from `compressed_block`, write paths submit VIOs to the packer, administrative paths flush/drain/resume it, and diagnostics query stats/dumps.

## State and Persistence Behavior
`compressed_block_header` and `compressed_block` describe durable block layout. `packer_bin` and `packer` describe volatile batching state. `flush_generation` and `admin_state` gate which VIOs can remain in the packer.

## Dependencies and Integration Points
It includes Linux lists plus VDO admin-state, constants, encodings, statistics, types, and wait-queue definitions. It is used by data VIO compression/write paths and compressed read decode paths.

## Risks and Edge Cases
The compressed block layout is packed and versioned; changing header size or slot count affects disk compatibility. Flexible arrays require correct allocation through `vdo_allocate_extended()`. Bin incoming slots are bounded by `VDO_MAX_COMPRESSION_SLOTS`.

## Test Signals
Compile-time layout checks, compressed block decode vectors, packer lifecycle tests, and admin drain/flush behavior validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/packer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.c

## Purpose
`permassert.c` implements VDO permanent assertion failure logging. Unlike a kernel BUG, assertions return a VDO/UDS error code after logging diagnostic context and a stack trace.

## Important APIs, Types, and Functions
The single public function is `vdo_assertion_failed(const char *expression_string, const char *file_name, int line_number, const char *format, ...)`.

## Control Flow
On assertion failure, the function formats the caller-supplied message inside a standard assertion prefix/suffix with expression, file, and line, logs it at error priority via `vdo_log_embedded_message()`, emits a backtrace, ends the varargs, and returns `UDS_ASSERTION_FAILED`.

## State and Persistence Behavior
No state is stored. The only side effect is kernel logging.

## Dependencies and Integration Points
It depends on `errors.h` for the assertion error code and `logger.h` for logging/backtrace. The macros in `permassert.h` route failed assertions here throughout VDO/UDS.

## Risks and Edge Cases
Assertions are not fatal by themselves; callers must return or handle the error where `VDO_ASSERT()` is used. `VDO_ASSERT_LOG_ONLY()` callers intentionally continue after logging, which can expose later failures if used for invariants that should stop flow.

## Test Signals
Inject failed assertions and verify return code, formatted expression/file/line, message content, and backtrace logging. Compile-time format checking comes from the header attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.h

## Purpose
`permassert.h` defines VDO assertion macros that log permanent assertion failures and return error codes instead of crashing the kernel.

## Important APIs, Types, and Functions
`vdo_must_use()` applies `__must_check` to expressions. `VDO_ASSERT(expr, ...)` returns `VDO_SUCCESS` or an assertion error and must be checked. `VDO_ASSERT_LOG_ONLY(expr, ...)` logs only. `__VDO_ASSERT` performs the conditional dispatch. The header declares `vdo_assertion_failed()`.

## Control Flow
Macros evaluate the expression with `likely()`. On false, they stringify the expression, pass file and line metadata plus the caller format to `vdo_assertion_failed()`, and either require the result be used or allow log-only behavior.

## State and Persistence Behavior
No state is stored. Effects are log messages and returned error codes.

## Dependencies and Integration Points
It includes Linux compiler attributes and VDO error definitions. It is included by most VDO/UDS files for invariant checks.

## Risks and Edge Cases
`VDO_ASSERT_LOG_ONLY()` should not be used where continued execution is unsafe. The format arguments must match because failures call a varargs logger. Ignoring `VDO_ASSERT()` results should trigger compiler warnings through `vdo_must_use()`.

## Test Signals
Compile checks for ignored return values, successful and failed assertions, log-only behavior, and format attribute warnings are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/permassert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.c

## Purpose
`physical-zone.c` manages physical zones, PBN locks, and block allocation. It serializes in-flight operations by physical block number, pools lock objects, handles read/write/block-map write lock semantics, manages provisional references, and rotates allocation attempts across zones or waits for slab scrubbing.

## Important APIs, Types, and Functions
Public functions include `vdo_is_pbn_read_lock()`, `vdo_downgrade_pbn_write_lock()`, `vdo_claim_pbn_lock_increment()`, `vdo_assign_pbn_lock_provisional_reference()`, `vdo_unassign_pbn_lock_provisional_reference()`, `vdo_make_physical_zones()`, `vdo_free_physical_zones()`, `vdo_get_physical_zone_pbn_lock()`, `vdo_attempt_physical_zone_pbn_lock()`, `vdo_allocate_block_in_zone()`, `vdo_release_physical_zone_pbn_lock()`, and `vdo_dump_physical_zone()`. Internal structures include `pbn_lock_implementation`, `idle_pbn_lock`, and `pbn_lock_pool`.

## Control Flow
Zone initialization creates an `int_map` for active PBN operations, a fixed lock pool sized for user VIOs, links the zone to a block allocator and next zone, and creates the zone thread. Lock acquisition borrows a lock before insertion to avoid double map access; insertion with `update=false` either installs the new lock or returns an existing lock and returns the spare to the pool. Allocation obtains a block from the current zone allocator, locks it, marks a provisional reference, and returns to the caller. On no-space, the data VIO may cycle through zones or enqueue as a clean-slab waiter before retrying. Release decrements holder count, removes the map entry when last holder exits, releases provisional references, and returns the lock to the pool.

## State and Persistence Behavior
Runtime state includes per-zone active lock map, fixed lock pool, allocator pointer, and next-zone ring. Persistent effects are indirect through block allocator/reference-count changes. Provisional references represent on-disk reference accounting obligations that must be released if a lock is abandoned.

## Dependencies and Integration Points
The file integrates with block allocator/slab depot, data VIO allocation state, wait queues, completions, dedupe/reference update paths, physical thread configuration, `int-map`, VDO constants/status codes, and logging/allocation/assertion helpers.

## Risks and Edge Cases
Lock pool exhaustion is treated as a serious lock error; sizing assumes at most two locks per user VIO. `vdo_attempt_physical_zone_pbn_lock()` contains unreachable assertion code after returning the spare lock, so diagnostics for an existing lock's holder count may not run. Increment claims on read locks are atomic because compressed-block dedupe can involve multiple hash-zone threads. Allocation retry must avoid touching a VIO after it has been dispatched to another zone or waiter. Releasing provisional references on error is critical to avoid reference leaks.

## Test Signals
Test lock acquire existing/new cases, holder-count sharing/release, write-to-read downgrade, increment claim limits, provisional reference assign/release, pool exhaustion fault injection, allocation success/no-space/wait-for-scrub cycling, multi-zone rotation, and cleanup with all locks returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.h

## Purpose
`physical-zone.h` defines physical-zone and PBN lock data structures plus APIs for physical block locking, allocation, and release.

## Important APIs, Types, and Functions
`enum pbn_lock_type` defines read, data write, and block-map write locks. `struct pbn_lock` stores implementation pointer, holder count, compressed fragment lock count, provisional-reference flag, read-lock increment limit, and atomic increment claims. `struct physical_zone` stores zone/thread IDs, active PBN operation map, lock pool, block allocator, and next zone. `struct physical_zones` owns the flexible zone array. The header declares lock type checks, downgrade/claim/provisional helpers, zone lifecycle, lock get/acquire/release, allocation, and dump functions.

## Control Flow
The header contract lets data/block-map paths acquire or observe PBN locks in the responsible physical zone, allocate new blocks from zones, share/downgrade locks, and release locks when operations complete.

## State and Persistence Behavior
Structs represent runtime locking and allocation coordination. Provisional-reference flags map to persistent reference-count obligations managed in the implementation.

## Dependencies and Integration Points
It includes Linux atomic operations and VDO types. It is used by data VIO, dedupe, block map, packer, and allocation paths.

## Risks and Edge Cases
Direct field access requires thread discipline. `holder_count`, `fragment_locks`, and `increments_claimed` enforce reference safety for compressed and dedupe flows; misuse can overflow references or release locks too early.

## Test Signals
Compile coverage plus physical-zone allocation, lock sharing, compressed-write lock sharing, and reference-count tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.c

## Purpose
`priority-table.c` implements a bounded integer-priority queue with O(1) enqueue, dequeue, remove, reset, and empty checks. It is used where VDO needs fast scheduling among a small priority range.

## Important APIs, Types, and Functions
Public functions are `vdo_make_priority_table()`, `vdo_free_priority_table()`, `vdo_reset_priority_table()`, `vdo_priority_table_enqueue()`, `vdo_priority_table_dequeue()`, `vdo_priority_table_remove()`, and `vdo_is_priority_table_empty()`. Internals include `struct bucket` for one priority queue and `struct priority_table` with `max_priority`, `search_vector`, and flexible bucket array. `mark_bucket_empty()` updates the bit vector when a bucket drains.

## Control Flow
Creation validates `max_priority <= 63`, allocates a flexible bucket array, initializes each list head, and clears the search vector. Enqueue clamps too-high priorities to `max_priority`, appends to the bucket list, and sets the priority bit. Dequeue finds the highest non-empty priority using `ilog2(search_vector)`, removes the first entry from that bucket, clears the bit if the bucket is now empty, and returns the embedded list entry. Remove deletes an arbitrary entry and clears the bucket bit if that entry made its bucket empty. Reset reinitializes all lists and clears all bits.

## State and Persistence Behavior
All state is volatile. The table does not own queued objects; callers embed `list_head` entries in their own structures.

## Dependencies and Integration Points
It uses Linux lists/log2, VDO memory allocation, assertions, and status/error codes. Work queues and scheduling structures can use it for bounded-priority dispatch.

## Risks and Edge Cases
Priority range is limited by the 64-bit search vector. The implementation assumes a queued entry's list links are not used elsewhere while in the table. Removing an entry after reset or double-removing would corrupt lists. No locking is provided.

## Test Signals
Test max-priority validation, enqueue/dequeue ordering, FIFO behavior within the same priority, priority clamping, arbitrary remove from head/middle/tail buckets, reset with queued entries, empty checks, and caller-side locking where used concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.h

## Purpose
`priority-table.h` declares a compact bounded-priority queue abstraction for entries with embedded Linux `list_head` links.

## Important APIs, Types, and Functions
It forward-declares `struct priority_table` and declares make/free, enqueue, reset, dequeue, remove, and empty-check functions. The file-level comments define the design: an array of priority buckets plus a bit-vector hint for non-empty buckets.

## Control Flow
Callers create a table with a maximum priority, enqueue embedded list entries with integer priorities, dequeue the highest-priority available entry, optionally remove arbitrary entries, reset, and free.

## State and Persistence Behavior
No persistent state is involved. The table owns bucket/list heads but not queued objects.

## Dependencies and Integration Points
It includes Linux list support. It can be used by VDO work queues or other bounded scheduler paths.

## Risks and Edge Cases
Callers must ensure an embedded list entry is not simultaneously in another list and must serialize access if multiple threads operate on the same table. Priorities above the configured maximum are clamped by the implementation.

## Test Signals
Compile coverage plus queue ordering, removal, and reset tests validate the declared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/priority-table.h -->
