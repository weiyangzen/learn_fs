# Group Research: group_667_kvdo_sources_block_storage_kvdo_vdo_slab_summary_h_sources_block_sto_fca6b7f8fb77

Scope verified against `Docs/research_subset_a.md`; all listed files are under `sources/block-storage/kvdo`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary.h -->
# File Research: sources/block-storage/kvdo/vdo/slab-summary.h

This header defines the in-memory model and API for VDO slab summaries. A slab summary stores restart/recovery hints per slab: rough free-block count, clean/dirty state, whether ref counts must be loaded, and slab-journal tail block offset.

Key structures:
- `struct slab_status`: small scrub-ordering record with slab number, cleanliness, and 7-bit emptiness hint.
- `struct slab_summary_block`: one persisted summary block, with active entry array, outgoing packed buffer, write VIO, and waiter queues for current/next writes.
- `struct slab_summary_zone`: per-physical-zone summary state, admin state, write count, zone thread id, and flexible array of summary blocks.
- `struct slab_summary`: global summary container with partition origin, hint scaling, blocks/entries sizing, active zone list, and atomic write statistics.

Public API covers construction/freeing, zone lookup, zone drain/resume, entry updates, summarized value accessors, slab status extraction, origin reset after partition movement, load, and statistics collection. The header depends on slab, layout, completion, admin-state, wait-queue, and statistics types, reflecting its role as a metadata component coordinated by physical-zone threads.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab-summary.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab.c -->
# File Research: sources/block-storage/kvdo/vdo/slab.c

This file implements lifecycle and state transitions for a single VDO slab. `vdo_make_slab()` allocates a `vdo_slab`, sets partition-relative start/end and translated metadata origins, creates its slab journal, and either marks the slab new with freshly allocated ref counts or normal-operation for later load.

Reference-count handling is central:
- `vdo_allocate_ref_counts_for_slab()` enforces single allocation and creates ref-count storage from slab configuration.
- `vdo_modify_slab_reference_count()` ignores zero-block slabs, preserves ref-count state for unrecovered slabs while releasing journal references, otherwise adjusts counts and updates free-block accounting when free status changes.
- `vdo_acquire_provisional_reference()` gives PBN locks provisional references and decrements free accounting if a provisional ref was acquired.

Admin-state integration:
- `initiate_slab_action()` dispatches draining, loading, and resuming behavior.
- Draining drains slab journal and ref counts, then `vdo_check_if_slab_drained()` completes when both are inactive.
- Loading decodes the slab journal, and normal/new load completion can allocate ref counts in `vdo_notify_slab_journal_is_loaded()`.

Recovery/scrubbing helpers manage `enum slab_rebuild_status`: unrecovered, replaying, rebuilding, rebuilt, and high-priority scrub states. `vdo_should_save_fully_built_slab()` decides whether rebuilt ref counts need persistence based on summary flags, non-empty data, or non-blank journal. Debug logging reports slab priority/free space or rebuild status plus journal/ref-count details.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/slab.h -->
# File Research: sources/block-storage/kvdo/vdo/slab.h

This header declares `struct vdo_slab`, the allocator-owned unit containing data blocks, reference-count metadata, and a slab journal. It records allocator ownership, journal/ref-count pointers, slab number, start/end PBNs, metadata origins, admin state, rebuild status, scrub tracking, and allocation priority.

The persisted/operational status enum covers rebuilt, replaying, requiring scrubbing, high-priority scrubbing, and rebuilding. Inline helpers classify unrecovered, replaying, and rebuilding slabs, and convert list entries back to slabs.

Public functions expose slab construction/freeing, ref-count allocation, zone lookup, recovery marking, opening, free-block query, reference modification, provisional reference acquisition, PBN-to-slab-block translation, save decision, admin action start/load/drain/resume notification, scrub completion, and debug dump.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/slab.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/sparse-cache.c -->
# File Research: sources/block-storage/kvdo/vdo/sparse-cache.c

This file implements the UDS sparse chapter index cache. The cache stores complete sparse chapter indexes for fallback dedupe lookup after faster paths fail. Its critical design is unsynchronized reads by zone threads with cache membership changes coordinated only through triage-issued barrier messages and `update_sparse_cache()`.

Important invariants:
- Cache membership is represented solely by `cached_chapter_index.virtual_chapter`; `UINT64_MAX` means dead/unused.
- Membership answers from `sparse_cache_contains()` must not vary between coordinated update calls, even if a chapter becomes too old or marked `skip_search`.
- Only zone zero mutates shared cache membership during the barrier-protected critical section; other zone search lists are copied from zone zero afterward.
- Each zone keeps an independent `search_list` LRU order, avoiding synchronization for search and membership checks.

Data model:
- `cached_chapter_index` owns decoded `delta_index_page` entries and backing `volume_page` buffers for one chapter.
- `cached_index_counters` and `sparse_cache_counters` are cache-line aligned to reduce false sharing.
- `search_list` stores an LRU permutation plus `first_dead_entry`, and is overallocated with temporary arrays used by purge.

Key operations:
- `make_sparse_cache()` allocates the cache, barriers, cached chapter arrays, and per-zone search lists.
- `sparse_cache_contains()` linearly searches the caller zone's live entries, scores zone-zero hits/misses, and rotates hits to MRU.
- `purge_search_list()` stable-partitions entries into active, skippable, and dead based on oldest chapter and `skip_search`.
- `update_sparse_cache()` uses begin/end barriers; zone zero purges, evicts/replaces the LRU/dead victim, reads and decodes the target chapter, then copies LRU state to all zones.
- `search_sparse_cache()` searches either one requested chapter or all eligible cached chapters and returns the first possible record page match.

Search performance uses a miss heuristic: zone-zero consecutive misses beyond `SKIP_SEARCH_THRESHOLD / zone_count` set `skip_search`, suppressing whole-cache searches while still allowing explicit hook lookups to clear the flag on hit.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/sparse-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/sparse-cache.h -->
# File Research: sources/block-storage/kvdo/vdo/sparse-cache.h

This header declares the opaque `struct sparse_cache` API for caching complete sparse chapter indexes. It documents that searches are unsynchronized and cache updates require coordinated participation from all index-zone threads through barrier messages.

Public functions:
- `make_sparse_cache()` / `free_sparse_cache()` allocate and destroy the cache.
- `get_sparse_cache_memory_size()` reports chapter-index page memory.
- `sparse_cache_contains()` is the zone-thread membership query.
- `update_sparse_cache()` must be called by all zones with the same virtual chapter for safe mutation.
- `invalidate_sparse_cache()` marks cached entries invalid while preserving membership semantics expected by callers.
- `search_sparse_cache()` searches cached sparse indexes for a chunk name and returns matching virtual chapter and record page.

The API intentionally avoids exposing cache internals so callers follow the barrier discipline described in the header.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/sparse-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/statistics.h -->
# File Research: sources/block-storage/kvdo/vdo/statistics.h

This header defines the versioned VDO statistics ABI, with `STATISTICS_VERSION = 35`. It is a struct-only aggregation header used by stats collection and sysfs/reporting paths.

Covered statistics groups include block allocator, commit pipeline, recovery journal, packer, slab journal, slab summary, reference counts, block map cache, hash locks, error counters, bio classes, memory usage, UDS index, and the top-level `struct vdo_statistics`.

`struct vdo_statistics` combines configuration/identity fields, logical/physical usage, recovery counters, mode string, recovery progress, nested component stats, bio in/out/meta/journal/page-cache counters, active VIO counts, dedupe timeout counts, flush counts, logical block size, memory usage, and index stats. Types come from `types.h`, so block counts remain consistent with on-disk VDO type definitions.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/statistics.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/status-codes.c -->
# File Research: sources/block-storage/kvdo/vdo/status-codes.c

This file defines VDO error metadata and maps internal status codes to OS errno values. `vdo_status_list[]` mirrors `enum vdo_status_codes` and is checked with a static assertion against the enum range.

`vdo_register_status_codes()` uses `perform_once()` to register the VDO error block with the shared UDS error registry. Duplicate registration is treated as success to support statically linked test/module scenarios where multiple copies call registration against shared libuds state.

`vdo_map_to_system_error()` normalizes errors for kernel return paths:
- `0` or already-negative errno values pass through.
- Small positive errno macros are negated.
- `VDO_NO_SPACE` maps to `-ENOSPC`.
- `VDO_READ_ONLY` maps to `-EIO`.
- Other VDO/UDS codes are logged with name/message and mapped to `-EIO`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/status-codes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/status-codes.h -->
# File Research: sources/block-storage/kvdo/vdo/status-codes.h

This header allocates VDO status-code ranges after the UDS error-code block and before a PRP block. It defines `VDO_SUCCESS` plus VDO-specific failures such as out-of-range, no space, bad configuration, component busy, unsupported version, checksum mismatch, read-only, corrupt journal, too many slabs, bad mapping, bad magic/nonce, journal overflow, invalid admin state, and sysfs-node creation failure.

It exports `vdo_status_list[]`, `vdo_register_status_codes()`, and `vdo_map_to_system_error()`. The enum comments document intended semantics and must stay in sync with `vdo_status_list[]`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/status-codes.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/string-utils.c -->
# File Research: sources/block-storage/kvdo/vdo/string-utils.c

This file implements fixed-buffer and append formatting helpers. `uds_wrap_vsnprintf()` wraps `vsnprintf()`, supports `buf == NULL` for size probing, returns `UDS_UNEXPECTED_RESULT` on formatting failure, optionally reports required bytes, and can return/log a caller-provided overflow error.

`uds_fixed_sprintf()` is a varargs wrapper that rejects null output buffers. `uds_v_append_to_buffer()` and `uds_append_to_buffer()` append formatted text into an existing `[buffer, buf_end)` span, silently truncating and advancing to `buf_end` on overflow.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/string-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/string-utils.h -->
# File Research: sources/block-storage/kvdo/vdo/string-utils.h

This header declares string helper APIs and an inline `uds_bool_to_string()` returning `"true"` or `"false"`. It includes kernel string/kernel headers and local compiler/type definitions.

The declared helpers provide:
- fixed-size formatting with explicit overflow error reporting,
- `vsnprintf()` wrapping with size-needed output,
- append-to-buffer helpers for varargs and `va_list`.

Functions are annotated with `__printf` for format checking and `__must_check` where callers should handle errors.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/string-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block-codec.c -->
# File Research: sources/block-storage/kvdo/vdo/super-block-codec.c

This file encodes and decodes the VDO super block sector payload. The fixed format is header plus component data plus CRC32 checksum; the whole encoding is constrained to the first sector to reduce torn-write corruption risk even though the backing allocation is a full VDO block.

Key behavior:
- `vdo_initialize_super_block_codec()` creates a component buffer, full-block encoded buffer, and sector-sized block buffer wrapper.
- `vdo_encode_super_block()` resets the block buffer, writes header version `12.0`, copies pre-encoded component data, computes CRC32 over encoded bytes so far, and appends the checksum.
- `vdo_decode_super_block()` decodes/validates the header, restricts the buffer to the declared payload size, copies component data except checksum into `component_buffer`, computes CRC, reads saved checksum, verifies all payload bytes were consumed, and returns `VDO_CHECKSUM_MISMATCH` on mismatch.

The codec depends on buffer primitives, `header` validation, constants such as `VDO_SECTOR_SIZE`, and CRC support from VDO.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block-codec.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block-codec.h -->
# File Research: sources/block-storage/kvdo/vdo/super-block-codec.h

This header defines `struct super_block_codec`, which owns the component-data buffer, sector-scoped block buffer, and full-block encoded super-block memory. The block buffer wraps the first sector of the encoded block, matching the codec's torn-write avoidance design.

It declares initialization/destruction plus encode/decode functions. Callers fill or consume `component_buffer`; the codec handles the enclosing super-block header and checksum.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block-codec.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block.c -->
# File Research: sources/block-storage/kvdo/vdo/super-block.c

This file wraps the super-block codec with asynchronous metadata I/O. `struct vdo_super_block` stores a parent completion, metadata VIO, codec, and `unwriteable` flag.

Lifecycle:
- `allocate_super_block()` allocates the object, initializes the codec, and creates a metadata VIO using the codec's encoded block buffer.
- `vdo_free_super_block()` frees the VIO, codec resources, and object.

Save/load behavior:
- `vdo_save_super_block()` rejects writes if marked unwriteable or busy, encodes the super block, stores the parent, then submits metadata write with `REQ_PREFLUSH | REQ_FUA`.
- Save errors record metadata I/O errors, log failure, mark the super block unwriteable, and finish the parent to prevent later successful writes from obscuring failed growth/readonly transitions.
- `vdo_load_super_block()` allocates the wrapper and submits a metadata read; completion decodes the super block and finishes the parent.
- Read errors are recorded but still flow through decode completion, letting decode surface the final result.

`vdo_get_super_block_codec()` exposes the codec so component-state code can read/write component data.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block.h -->
# File Research: sources/block-storage/kvdo/vdo/super-block.h

This header declares the opaque `struct vdo_super_block` API. It exposes free, asynchronous save, asynchronous load, and codec accessor functions.

The save/load APIs take physical block offsets and parent `vdo_completion` objects, reflecting that the super block is managed as VDO metadata I/O rather than synchronous direct buffer access.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/super-block.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/sync-completion.c -->
# File Research: sources/block-storage/kvdo/vdo/sync-completion.c

This file implements a bridge from VDO asynchronous completions to synchronous waiting. `struct sync_completion` embeds a `vdo_completion`, Linux `completion`, and target action pointer.

`vdo_perform_synchronous_action()` initializes the embedded completion, launches `run_synchronous_action()` on the requested VDO thread with an optional parent, waits for the Linux completion, and returns the VDO completion result. The launched action has its callback replaced with `complete_synchronous_action()`, which wakes the waiting caller.

This is used where a caller outside a VDO base thread needs to execute an action on a specific VDO thread and block until it completes.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/sync-completion.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/sync-completion.h -->
# File Research: sources/block-storage/kvdo/vdo/sync-completion.h

This header declares `vdo_perform_synchronous_action()`. The function runs a `vdo_action` on a specified VDO thread, optionally with a parent pointer, then waits synchronously for completion and returns the action result.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/sync-completion.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/sysfs.c -->
# File Research: sources/block-storage/kvdo/vdo/sysfs.c

This file defines kernel module parameters for VDO logging and dedupe timing. `log_level` uses custom show/store functions that translate between UDS log priorities and strings. The store path copies at most 10 bytes, strips a trailing newline, and updates the global log level.

Two uint-backed module parameters, `deduplication_timeout_interval` and `min_deduplication_timer_interval`, use `param_set_uint()` and then call dedupe setters so runtime module-param writes update dedupe behavior immediately. Parameters are registered with `module_param_cb()` and mode `0644`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-cond-var.c -->
# File Research: sources/block-storage/kvdo/vdo/thread-cond-var.c

This file implements UDS condition variables using `event_count`. Initialization allocates an event count; signal and broadcast both broadcast to all waiters.

`uds_wait_cond()` and `uds_timed_wait_cond()` prepare an event token, unlock the provided mutex, wait on the event count, then relock the mutex. The timed variant returns `ETIMEDOUT` when the wait expires. `uds_destroy_cond()` frees the event count and clears the pointer.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-cond-var.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-config.c -->
# File Research: sources/block-storage/kvdo/vdo/thread-config.c

This file constructs and names VDO thread layouts. `allocate_thread_config()` allocates the config and arrays for logical, physical, hash, and bio threads, storing zone/thread counts.

`vdo_make_thread_config()` supports two modes:
- Single shared base-thread mode when logical/physical/hash zone counts are all zero: logical, physical, hash, journal, packer, and admin effectively share the same request thread identity.
- Multi-thread mode: assigns admin/journal, packer, logical zone, physical zone, and hash zone thread ids separately.

It always assigns dedupe, optional bio-ack, CPU, and bio thread ids. `vdo_free_thread_config()` releases all arrays.

`vdo_get_thread_name()` maps thread ids to stable queue names: `reqQ`, `journalQ`, `adminQ`, `packerQ`, `dedupeQ`, `ackQ`, `cpuQ`, `logQ<N>`, `physQ<N>`, `hashQ<N>`, `bioQ<N>`, or fallback `reqQ<ID>`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-config.h -->
# File Research: sources/block-storage/kvdo/vdo/thread-config.h

This header defines `struct thread_config`, containing zone counts, total thread count, special-purpose thread ids, and arrays for logical, physical, hash, and bio threads.

It declares construction/freeing and thread-name formatting. Inline getters return the thread id for a logical, physical, or hash zone after log-only bounds assertions. Note the assertions use `<=` against counts, so callers must still pass valid zero-based zone indexes to avoid out-of-range array access.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-config.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-device.c -->
# File Research: sources/block-storage/kvdo/vdo/thread-device.c

This file provides a device-id-specific thread registry used for logging context. It owns a static `thread_registry` and wraps generic registry functions.

`uds_register_thread_device_id()` associates the current thread with an unsigned device id pointer. `uds_unregister_thread_device_id()` removes the current thread. `uds_get_thread_device_id()` returns the registered id or `-1` if none exists. `uds_initialize_thread_device_registry()` initializes the static registry.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-device.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-device.h -->
# File Research: sources/block-storage/kvdo/vdo/thread-device.h

This header declares the thread-to-device-id registry API. It depends on `thread-registry.h` for `struct registered_thread` and exposes register, unregister, lookup, and registry initialization functions.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-device.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-registry.c -->
# File Research: sources/block-storage/kvdo/vdo/thread-registry.c

This file implements a generic current-task registry using a spinlock-protected RCU list. It avoids logging while holding locks, because logging itself may use registry functions.

`uds_register_thread()` initializes a caller-owned `registered_thread`, removes any stale entry for `current`, appends the new entry with RCU list operations, and synchronizes before reinitializing a replaced entry. `uds_unregister_thread()` removes the current thread's entry and synchronizes before list reinitialization. `uds_lookup_thread()` uses an RCU read-side section to find the pointer associated with `current`.

The registry stores arbitrary `const void *` pointers, enabling multiple contextual registries such as device id or allocation tracking.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-registry.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-registry.h -->
# File Research: sources/block-storage/kvdo/vdo/thread-registry.h

This header defines `struct thread_registry` as an RCU list plus spinlock, and `struct registered_thread` as a caller-owned list node containing an associated pointer and task pointer.

It declares initialization, current-thread registration, current-thread unregistration, and lookup. Callers must keep `registered_thread` storage valid while registered.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/thread-registry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/time-utils.c -->
# File Research: sources/block-storage/kvdo/vdo/time-utils.c

This file implements `current_time_us()`, returning realtime wall-clock microseconds by calling `current_time_ns(CLOCK_REALTIME)` and dividing by `NSEC_PER_USEC`.

The file includes assertion/string/time headers and kernel delay/time headers, but the only runtime behavior is the wall-clock microsecond helper.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/time-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/time-utils.h -->
# File Research: sources/block-storage/kvdo/vdo/time-utils.h

This header provides time helpers around kernel `ktime` APIs. `current_time_ns(clockid_t)` returns monotonic or realtime nanoseconds and is inline so constant clock ids compile to a single call.

It also defines inline second/nanosecond conversions:
- `seconds_to_ktime()`
- `ktime_to_seconds()`

The non-inline `current_time_us()` returns wall-clock microseconds. Includes come from local compiler/type definitions plus kernel time headers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/time-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/type-defs.h -->
# File Research: sources/block-storage/kvdo/vdo/type-defs.h

This small compatibility header includes kernel standard/type headers, defines `byte` as `unsigned char`, and defines several integer limit macros (`CHAR_BIT`, `INT64_MAX`, `UCHAR_MAX`, `UINT8_MAX`, `UINT16_MAX`, `UINT64_MAX`) using casts.

It is a foundational include used by many VDO/UDS headers for fixed-width type and byte naming consistency in kernel code.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/type-defs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/types.h -->
# File Research: sources/block-storage/kvdo/vdo/types.h

This header defines core VDO scalar types and persisted enums. Block, page, PBN/LBN, nonce, sequence, slab, slot, and zone count types are typedefs over fixed-width integers.

Persisted enums include:
- `enum vdo_state`: dirty/new/clean/read-only/force-rebuild/recovering/replaying/rebuild-for-upgrade.
- `enum journal_operation`: data/block-map increment/decrement operations.
- `enum partition_id`: block map, block allocator, recovery journal, slab summary.
- `enum vdo_metadata_type`: recovery journal and slab journal.

It also defines `struct block_map_slot`, `struct data_location`, and packed `struct slab_config`, which records slab total/data/ref-count/journal block counts plus journal flush/block/scrub thresholds. These definitions are shared across metadata, allocator, journal, and layout code.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-sysfs.c -->
# File Research: sources/block-storage/kvdo/vdo/uds-sysfs.c

This file builds a UDS-specific sysfs tree at `/sys/uds` with a `parameter` subdirectory. The current parameter exposed is `log_level`.

It defines minimal kobject types for empty directories and parameter files:
- `empty_object_type` has no attributes and no-op release.
- `parameter_object_type` uses custom show/store dispatch through `struct parameter_attribute`.

`buffer_to_string()` copies sysfs input, NUL-terminates it, and strips a trailing newline. The `log_level` parameter reads/writes the global UDS log level using string/priority conversion helpers.

`uds_init_sysfs()` initializes and adds `/sys/uds` and `/sys/uds/parameter`, tracking booleans so `uds_put_sysfs()` can release only successfully added kobjects on failure or module unload.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-sysfs.h -->
# File Research: sources/block-storage/kvdo/vdo/uds-sysfs.h

This header declares UDS sysfs lifecycle functions:
- `uds_init_sysfs()` initializes the `/sys/<module_name>` tree and returns `0` or a kernel error.
- `uds_put_sysfs()` tears the tree down during module unload.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-threads.c -->
# File Research: sources/block-storage/kvdo/vdo/uds-threads.c

This file implements UDS kernel thread wrappers, once-only initialization, barriers, and scheduler yielding. A static hlist tracks live UDS kernel threads so `uds_thread_exit()` can complete the correct completion object.

Thread lifecycle:
- `uds_create_thread()` allocates `struct thread`, starts a `kthread_run()` wrapper, and derives thread names with colon-prefix inheritance from the current thread name.
- `thread_starter()` records the task, registers allocation tracking, invokes the caller thread function, unregisters, and completes `thread_done`.
- `uds_join_threads()` waits interruptibly until completion, removes the thread from the live hlist, and frees it.
- `uds_thread_exit()` locates the current thread, unregisters allocation tracking, and exits with the appropriate kernel API depending on `module_put_and_kthread_exit`.

Synchronization:
- `perform_once()` uses atomic compare/exchange states `NOT_DONE`, `IN_PROGRESS`, and `COMPLETE`, yielding while another thread initializes.
- `uds_initialize_barrier()`, `uds_enter_barrier()`, and destroy implement a reusable semaphore-based rendezvous; exactly one arriving thread is flagged as winner/last.
- `uds_get_thread_id()`, `uds_get_num_cores()`, and `uds_yield_scheduler()` wrap kernel primitives.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-threads.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-threads.h -->
# File Research: sources/block-storage/kvdo/vdo/uds-threads.h

This header declares the UDS threading abstraction over Linux kernel primitives. It defines `struct cond_var`, opaque `struct thread`, and `struct barrier` implemented with semaphores and arrival counters.

Declared APIs cover thread creation/join/exit, current thread id, CPU count, once-only initialization, barriers, condition variables, scheduler yield, and inline mutex/semaphore wrappers.

The semaphore acquire helper intentionally loops on `down_interruptible()` and sleeps briefly after signals to avoid long kernel stall warnings and CPU spinning during operations such as dmsetup-driven waits. `uds_attempt_semaphore()` supports try-acquire or timed acquire based on a relative `ktime_t`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/uds-threads.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/uds.h -->
# File Research: sources/block-storage/kvdo/vdo/uds.h

This header is the public UDS API definition for index sessions and asynchronous chunk operations. It defines request types (`POST`, `UPDATE`, `DELETE`, `QUERY`, `QUERY_NO_UPDATE`) and index open types (`LOAD`, `CREATE`, `NO_REBUILD`).

Core public data:
- `UDS_CHUNK_NAME_SIZE` and `UDS_METADATA_SIZE` are both 16 bytes.
- `uds_memory_config_size_t` supports positive GB sizes plus negative sub-GB and reduced-chapter constants.
- `struct uds_parameters` configures index storage name, size, offset, memory size, sparse mode, nonce, zone count, and read-thread count.
- `struct uds_index_stats` reports index resource usage, collision/discard counts, operation counters, and current time.

`struct uds_request` is the async operation object. Client-visible fields include chunk name, old/new metadata, callback, session, operation type, status, and found flag. Internal fields carry zone number, queue/list links, index pointer, sparse-cache/zone control message, batching flags, virtual chapter, and lookup location.

The API declares index sizing, session create/open/suspend/resume/flush/close/destroy, parameter/stat retrieval, and `uds_start_chunk_operation()` for asynchronous dedupe/index requests.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/uds.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component-states.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-component-states.c

This file encodes and decodes the complete component payload stored inside the VDO super block. It defines the current volume format version as `67.0`.

Decode flow:
- `vdo_decode_component_states()` reads and checks the release version against geometry, decodes and validates the volume version, then decodes VDO component data, fixed layout, recovery journal state, slab depot state, and block map state in order.
- On decode failure after layout allocation, it frees the fixed layout.
- `vdo_validate_component_states()` checks the geometry nonce against the superblock nonce and validates the VDO config against physical/logical sizes.

Encode flow:
- `vdo_encode_component_states()` resets the buffer and writes release version, volume version, VDO component, fixed layout, recovery journal, slab depot, and block map states.
- It computes expected encoded size from component helpers and log-only asserts the final payload length matches.

`vdo_destroy_component_states()` currently frees the decoded layout allocation. The file is the glue between component-specific format codecs and the super-block codec.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component-states.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component-states.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-component-states.h

This header declares the aggregate `struct vdo_component_states` persisted in the super block: release version, volume version, VDO component, block map state, recovery journal state, slab depot state, and fixed layout.

It exposes destroy, decode, validate, and encode functions, plus the external volume version constant `VDO_VOLUME_VERSION_67_0`. Comments document that volume major/minor versions must change when on-disk representations change.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component-states.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-component.c

This file handles the VDO component portion of super-block component data. The current component-data format version is `41.0`.

Encoding/decoding:
- Defines packed little-endian `packed_vdo_config` and `packed_vdo_component_41_0`.
- `vdo_get_component_encoded_size()` returns version header plus packed component size.
- `vdo_encode_component()` writes the component-data version and packed state.
- `vdo_decode_component()` reads and validates version, then decodes format `41.0`.

`vdo_validate_config()` enforces configuration constraints:
- slab size must be nonzero, power of two, and within maximum slab bits;
- slab journal blocks must meet minimum and not exceed slab size;
- derived slab config must contain at least one data block;
- physical blocks must be nonzero, within maximum, and equal the supplied physical size;
- logical blocks, when externally specified, must match and be within maximum;
- recovery journal size must be nonzero and power of two.

Errors are returned as assertions/status codes, with physical/logical mismatches logged and reported as `VDO_PARAMETER_MISMATCH`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-component.h

This header defines the persisted VDO service component: `struct vdo_config` and `struct vdo_component`. The config stores logical block count, physical block count, slab size, recovery journal size, and slab journal block count. The component stores VDO state, complete/read-only recovery counters, config, and nonce.

It declares encoded-size, encode, decode, and config-validation functions used by the super-block component-state layer.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-component.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-layout.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-layout.c

This file implements fixed partition layouts and the VDO-specific layout wrapper. `fixed_layout` tracks a free range and linked list of `partition` records; partitions have id, layout pointer, layer offset, partition-local base, count, and next pointer.

Fixed-layout operations:
- `vdo_make_fixed_layout()` creates an initially unpartitioned layout over `[start_offset, start_offset + total_blocks)`.
- `vdo_make_fixed_layout_partition()` carves a partition from the beginning or end, supports `VDO_ALL_FREE_BLOCKS`, rejects duplicate ids and insufficient space, updates free bounds, and prepends to the partition list.
- Translation helpers convert between partition-relative and layer PBNs with range checking.
- Accessors return total size, available blocks, partition size/offset/base, and partition lookup by id.

Encoding format:
- Layout format header is `VDO_FIXED_LAYOUT` version `3.0`.
- Encoded layout stores `first_free`, `last_free`, partition count, and each partition's id/offset/base/count in little-endian order.
- Decode validates the header minimum, ensures enough bytes for declared partitions, allocates a layout, and reconstructs partitions.

VDO layout behavior:
- `vdo_make_partitioned_fixed_layout()` creates standard partitions: block map from beginning, slab summary from end, recovery journal from end, and block allocator from remaining free space.
- `vdo_decode_layout()` validates all required partitions exist before returning `struct vdo_layout`.
- `prepare_to_vdo_grow_layout()` prepares a next layout for physical growth, creates a `dm_kcopyd` client if needed, preserves metadata partition sizes, and rejects too-small growth that would place new journal/summary over old metadata.
- `vdo_grow_layout()` swaps in the prepared layout, while `vdo_finish_layout_growth()` frees unused previous/next layouts.
- `vdo_copy_layout_partition()` uses `dm_kcopyd_copy()` to copy a partition from current to next layout, converting partitions to `dm_io_region`s with VDO geometry bio offset adjustment.

The file is the authoritative partitioning and growth coordinator for VDO metadata placement.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-layout.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-layout.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-layout.h

This header documents and declares fixed-layout and VDO-layout APIs. A fixed layout is a simple partitioning scheme where partitions are carved from a free span; `vdo_layout` wraps it with knowledge of required VDO partitions and physical-growth state.

It declares partition creation, lookup, translation, encoding/decoding, standard VDO partitioned-layout construction, VDO-layout decode/free, partition retrieval, growth preparation/query/swap/cleanup, partition copying, and fixed-layout access.

`struct vdo_layout` holds current, next, and previous fixed layouts, starting offset, and optional `dm_kcopyd_client` used during grow-physical copy operations.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-layout.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-load.c -->
# File Research: sources/block-storage/kvdo/vdo/vdo-load.c

This file implements VDO pre-load and load state machines. Load phases include start, stats/sysfs setup, depot load/recovery/rebuild, marking dirty, allocation prep, slab scrubbing, data reduction startup, finished, journal draining, and waiting for read-only transition.

Pre-load path:
- `vdo_prepare_to_load()` runs admin operation `PRE_LOAD`.
- `pre_load_callback()` starts pre-loading on the admin thread, reads the super block from the data-region start, then `vdo_load_components()` decodes component state.
- `decode_vdo()` decodes/validates super-block state, checks block-map maximum age against recovery journal length, creates read-only notifier and entry, decodes recovery journal, slab depot, block map, logical zones, physical zones, and hash zones.

Load path:
- `vdo_load()` runs admin operation `LOAD`, logs start/started, and treats `VDO_READ_ONLY` as a usable read-only start.
- `load_callback()` advances through phases on the admin thread except journal drain, which is routed to the journal thread.
- It opens the recovery journal, enables read-only entry, initializes sysfs/kobjects, chooses normal/recovery/read-only rebuild depot loading, marks the volume dirty and saves components, initializes block map from journal, prepares slabs for allocation, enters recovery mode if needed, scrubs unrecovered slabs, starts compression/dedupe as configured, and completes admin state.

Error behavior:
- `handle_load_error()` attempts to bring the device online read-only on load errors.
- During read-only rebuild failure at the make-dirty phase, it preserves the error and drains the journal before finishing.
- If final load fails outside success/read-only, `vdo_load()` suspends the VDO into an unresumable stopping state.

The file ties together super-block/component decoding, recovery decisions from `vdo_state`, sysfs initialization, slab depot recovery, read-only notifier behavior, and data-reduction startup.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-load.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-load.h -->
# File Research: sources/block-storage/kvdo/vdo/vdo-load.h

This header declares the two VDO load entry points:
- `vdo_prepare_to_load()` reads and decodes on-disk structures without modifying disk state, intended during VDO construction.
- `vdo_load()` performs the operational load/resume sequence and may transition through recovery, read-only, slab scrub, and data-reduction startup phases.

Both return VDO or kernel-style error codes and require VDO/kernel type definitions.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/vdo-load.h -->