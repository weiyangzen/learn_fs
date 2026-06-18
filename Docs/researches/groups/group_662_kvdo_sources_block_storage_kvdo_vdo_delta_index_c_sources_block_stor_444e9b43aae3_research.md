# Group Research: group_662_kvdo_sources_block_storage_kvdo_vdo_delta_index_c_sources_block_stor_444e9b43aae3

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/delta-index.c -->
# File Research: sources/block-storage/kvdo/vdo/delta-index.c

## Purpose
Implements UDS/VDO’s delta index: a compact key-value store where sorted integer keys are represented as deltas and values are fixed-width payloads. It supports mutable in-memory indexes, immutable packed chapter-index pages, persistence save/restore, collision records containing full chunk names, and statistics/logging.

## Main Concepts
- `delta_zone` owns a contiguous bitstream arena containing many `delta_list` streams plus guard lists at both ends.
- Delta entries store value bits followed by Huffman-style variable-length delta bits.
- Collision entries are encoded as `delta == 0` after the first list entry and carry a 256-bit full chunk name.
- Mutable indexes have allocated list headers and temporary offset arrays; immutable page indexes infer list boundaries from a packed page header table.
- Guard bytes at the tail are set to all ones to prevent corrupted variable-length decode from scanning into unsafe memory.

## Key Behavior
- Initialization: `initialize_delta_index()` allocates zones, divides list ranges across zones, computes coding constants, and initializes evenly spaced empty lists.
- Bit operations: `get_field()`, `set_field()`, `get_big_field()`, `move_bits()`, and helpers manipulate unaligned little-endian bit ranges.
- Page support: `pack_delta_index_page()` packs mutable lists into immutable pages; `initialize_delta_index_page()` validates page nonce, list ordering, guard bytes, and endian format.
- Persistence: `start_saving_delta_index()` writes a zone header and per-list sizes; `finish_saving_delta_index()` writes non-empty list payloads. Restore mirrors this through `start_restoring_delta_index()` and `finish_restoring_delta_index()`.
- Search/iteration: `start_delta_index_search()` initializes an iterator, `next_delta_index_entry()` decodes entries, and `get_delta_index_entry()` searches through possible collision chains.
- Mutation: `put_delta_index_entry()` inserts normal or collision entries, updating neighbor deltas and expanding/rebalancing zones as needed. `remove_delta_index_entry()` deletes entries and repairs the following delta.
- Accounting: stats aggregate allocated memory, records, collisions, discards, overflows, and rebalance time.

## Dependencies
Uses VDO/UDS support for buffers, buffered readers/writers, allocation, assertions, logging, endian unaligned access, hashing constants, timing, and CPU prefetching.

## Invariants and Risks
- The implementation assumes native little-endian behavior for hot bitstream utilities.
- Delta list size is capped by `uint16_t`; insertion sets overflow state and returns `UDS_OVERFLOW`.
- Correctness depends on guard list placement and tail bytes remaining all ones.
- Restore validates zone order, list count, tag, list size, and collision count before loading data.
- `write_guard_delta_list()` writes the in-memory save-info struct directly rather than using the endian helper used elsewhere, which is safe only if the packed layout and endian expectations match the reader’s assumptions.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/delta-index.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/delta-index.h -->
# File Research: sources/block-storage/kvdo/vdo/delta-index.h

## Purpose
Declares the delta index data structures and public API used by UDS/VDO dedupe index code.

## Main Interfaces
- `struct delta_list`: bit offset, bit size, and cached search position.
- `struct delta_zone`: memory arena, list headers, save writer, coding constants, stats, list range, and tag.
- `struct delta_index`: zone array, global list counts, per-zone load counters, mutability, and tag.
- `struct delta_index_page`: wrapper for treating an immutable chapter-index page as a one-zone delta index.
- `struct delta_index_entry`: iterator/search result/insertion point for a delta list.
- `struct delta_index_stats`: aggregate stats from zones.

## Exported Operations
- Lifecycle: `initialize_delta_index()`, `initialize_delta_index_page()`, `uninitialize_delta_index()`, `empty_delta_index()`, `empty_delta_zone()`.
- Immutable page packing: `pack_delta_index_page()`.
- Save/restore: `start_restoring_delta_index()`, `finish_restoring_delta_index()`, `abort_restoring_delta_index()`, `start_saving_delta_index()`, `finish_saving_delta_index()`, `write_guard_delta_list()`.
- Search/mutate: `start_delta_index_search()`, `next_delta_index_entry()`, `get_delta_index_entry()`, `put_delta_index_entry()`, `remove_delta_index_entry()`, value/collision accessors.
- Sizing/stats: `compute_delta_index_save_bytes()`, `compute_delta_index_size()`, `get_delta_index_page_count()`, zone bit/allocation helpers.

## Invariants
Callers must respect mutable versus immutable indexes: mutation/value-setting APIs assert mutable entries. `delta_index_entry` fields marked private are state carried between module calls and should not be externally mutated.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/delta-index.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/device-config.c -->
# File Research: sources/block-storage/kvdo/vdo/device-config.c

## Purpose
Parses and validates Device Mapper table arguments for the VDO target, owns `device_config` allocation/freeing, and validates whether a new table can modify an existing VDO.

## Main Behavior
- Supports table versions `V0` through `V4`, with argument-count compatibility arrays for older formats.
- Parses original table string for status/table output preservation.
- Extracts parent device name, physical block count, logical block size mode, cache size, block map age, optional settings, and thread counts.
- Handles legacy skipped fields: read cache options, MD RAID5 optimization, write policy, and pool name.
- Optional arguments include `deduplication`, `compression`, `maxDiscard`, and thread parameters (`cpu`, `ack`, `bio`, `bioRotationInterval`, `logical`, `physical`, `hash`).
- Opens the backing block device through `dm_get_device()` and fills version-0 physical size from the block device.

## Validation
- Logical size must be 4K-aligned.
- Logical, physical, and hash zone counts must be all zero or all non-zero.
- Block map cache must be sufficient for logical zones.
- Thread counts are bounded by constants and `cpu`/`bio` counts must be non-zero where required.
- `vdo_validate_new_device_config()` rejects changed target start, logical block size, shrinking logical size, cache size changes, block map age changes, physical shrink, and disallowed growth.

## Dependencies
Uses Linux DM APIs, VDO constants/types/status codes, UDS allocation/string helpers, logger, and VDO object references.

## Notable Risk
`vdo_validate_new_device_config()` compares `&config->thread_counts` to itself instead of comparing `to_validate->thread_counts` against `config->thread_counts`. As written, thread configuration changes are not detected by that check.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/device-config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/device-config.h -->
# File Research: sources/block-storage/kvdo/vdo/device-config.h

## Purpose
Defines the parsed Device Mapper table configuration for a VDO target and declares config parsing/validation helpers.

## Main Structures
- `struct thread_count_config`: packed counts for bio ack, bio submit, rotation interval, CPU, logical, physical, and hash zones. The comment notes it is intended for equality comparison.
- `struct device_config`: owns DM target/device references, linked-list membership, original table string, parent device name, physical/logical sizing, block size/cache/age settings, dedupe/compression booleans, thread counts, and discard limit.

## API
- `vdo_as_device_config()` converts a list node to containing config.
- `vdo_parse_device_config()` builds a config from table args.
- `vdo_free_device_config()` releases DM device/string/config allocations.
- `vdo_set_device_config()` links/unlinks a config to a VDO.
- `vdo_validate_new_device_config()` checks table reload compatibility.

## Integration
This header is consumed by the DM target and by VDO lifecycle code that keeps all active table configs on `vdo->device_config_list`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/device-config.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/device-registry.c -->
# File Research: sources/block-storage/kvdo/vdo/device-registry.c

## Purpose
Implements a simple global registry of live VDO instances so target creation/reload paths can find existing devices by pointer, name, or backing device.

## Main Behavior
- `vdo_initialize_device_registry_once()` initializes a global list and rwlock.
- `vdo_register()` asserts the VDO is not already registered, initializes its list node, and appends it.
- `vdo_unregister()` removes the VDO if present.
- `vdo_find_matching()` scans under read lock using caller-supplied `vdo_filter_t`.

## Dependencies
Uses Linux list/rwlock primitives, VDO object `registration` field, UDS assertions, and VDO status codes.

## Invariants
Registry scans are linear; comments explicitly accept this because the set should be small. Write-side operations hold the write lock, and lookup holds the read lock.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/device-registry.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/device-registry.h -->
# File Research: sources/block-storage/kvdo/vdo/device-registry.h

## Purpose
Declares the VDO global registry API.

## API
- `vdo_filter_t`: predicate callback for matching a `struct vdo`.
- `vdo_initialize_device_registry_once()`: one-time setup.
- `vdo_register()` / `vdo_unregister()`: manage registry membership.
- `vdo_find_matching()`: returns the first VDO matching a supplied predicate/context.

## Integration
Used by the DM target constructor to prevent backing-device sharing and to locate an existing VDO by device name during table reload.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/device-registry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dirty-lists.c -->
# File Research: sources/block-storage/kvdo/vdo/dirty-lists.c

## Purpose
Implements age-bucketed dirty element tracking. Elements are held in a ring of lists by dirty period and expired via callback when they exceed a maximum age or when all dirty lists are flushed.

## Main Behavior
- `vdo_make_dirty_lists()` allocates a flexible-array structure with `maximum_age` list heads.
- `vdo_set_dirty_lists_current_period()` initializes oldest/current period and ring offset.
- `vdo_add_to_dirty_lists()` moves an element into the correct period bucket, expires it immediately if too old, and ignores updates that do not make the element newly older.
- `vdo_advance_dirty_lists_period()` advances periods and expires buckets as they age out.
- `vdo_flush_dirty_lists()` expires every pending bucket.
- Expired elements are spliced into an `expired` list and passed to the caller callback, which must empty the list.

## Invariants
The callback is required to remove all expired elements. Period advancement expires at most as needed to keep `next_period - oldest_period <= maximum_age`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dirty-lists.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dirty-lists.h -->
# File Research: sources/block-storage/kvdo/vdo/dirty-lists.h

## Purpose
Declares the opaque dirty-list tracker used for age-based writeback/expiry.

## API
- `vdo_dirty_callback`: callback invoked with expired elements and context.
- `vdo_make_dirty_lists()`: allocate tracker.
- `vdo_set_dirty_lists_current_period()`: one-time initial period setup.
- `vdo_add_to_dirty_lists()`: add or move a list entry by old/new dirty period.
- `vdo_advance_dirty_lists_period()`: advance current period and expire old lists.
- `vdo_flush_dirty_lists()`: expire all outstanding dirty entries.

## Integration
Designed for intrusive Linux `list_head` entries owned by caller structures.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dirty-lists.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dm-vdo-target.c -->
# File Research: sources/block-storage/kvdo/vdo/dm-vdo-target.c

## Purpose
Defines the Linux Device Mapper target module for VDO transparent deduplication/compression.

## Main Behavior
- `vdo_map_bio()` handles incoming bios, counts them, routes flush/prefllush bios through the flusher, and launches normal bios through the data VIO pool.
- `vdo_io_hints()` sets logical/physical block size, IO size hints, discard limits, and discard granularity.
- `vdo_status()` emits info/status/table/IMA responses.
- `vdo_message()` handles `stats`, `dump`, `dump-on-shutdown`, dedupe index messages, and compression on/off messages.
- `vdo_ctr()` allocates or reuses an instance number, parses table config, modifies existing named VDOs, or initializes a new VDO.
- `vdo_dtr()` detaches a table config and destroys the VDO when the final config reference is removed.
- Suspend/resume hooks coordinate VDO admin states, loading metadata, validating backing size, and resuming operation.
- Module init/exit initializes UDS subsystems, sysfs, registry, status codes, DM target registration, and instance tracking.

## Integration
Connects many subsystems: config parsing, registry, VDO load/resume/suspend, data VIO pool, dedupe controls, io submitter, thread registry, sysfs, stats, and logging.

## Invariants and Risks
- Rejects sharing one backing device with multiple live VDOs.
- Uses target singleton feature.
- Normal bio mapping asserts VDO is in a normal admin state and avoids re-entering from an owned work queue.
- Discard-limit field differs by kernel/RHEL version (`max_discard_sectors` versus `max_hw_discard_sectors`).
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dm-vdo-target.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dump.c -->
# File Research: sources/block-storage/kvdo/vdo/dump.c

## Purpose
Provides diagnostic dump support for VDO state, queues, VIO pools, hash zones, memory usage, and individual data VIOs.

## Main Behavior
- `vdo_dump()` parses dump options and triggers selected diagnostics.
- `vdo_dump_all()` dumps all known categories.
- Options include queues/threads, VIO pool/pools, VDO status, default, and all.
- `do_dump()` logs active device requests, outstanding bios, work queues, hash zones, data VIO pool, VDO status, and UDS memory usage.
- `dump_data_vio()` logs compact per-VIO state including physical/logical/duplicate block numbers, operation, completion state, flush generation, and flags.
- `dump_vio_waiters()` logs waiters on a VIO wait queue.

## Dependencies
Uses VDO data VIO, dedupe/hash-zone dumping, IO submitter work queues, memory reporting, and logger.

## Notes
The per-VIO dump uses static buffers and assumes only one dump runs at a time; concurrent dumps would garble log lines.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/dump.h -->
# File Research: sources/block-storage/kvdo/vdo/dump.h

## Purpose
Declares VDO diagnostic dump entry points.

## API
- `vdo_dump()`: parse option arguments and dump selected VDO diagnostics.
- `vdo_dump_all()`: dump every supported diagnostic category.
- `dump_data_vio()`: callback-compatible dumper for individual data VIO objects.

## Integration
Used by DM messages and shutdown paths when `dump-on-shutdown` is enabled.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/dump.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/errors.c -->
# File Research: sources/block-storage/kvdo/vdo/errors.c

## Purpose
Maps UDS internal status codes and selected system errors to readable names/messages and Linux errno values. Also allows other error blocks to be registered.

## Main Behavior
- Defines built-in UDS error metadata for `UDS_ERROR_CODE_BASE` range.
- `uds_string_error()` returns a descriptive message for UDS, registered block, success, or system errno.
- `uds_string_error_name()` returns the symbolic name where available.
- `uds_map_to_system_error()` converts internal positive UDS status codes to negative Linux errno values.
- `register_error_block()` adds a non-overlapping named error-code block with metadata.

## Mappings
- Success and negative errno values pass through appropriately.
- Small positive values are treated as errno and negated.
- `UDS_NO_INDEX` and `UDS_CORRUPT_DATA` map to `-ENOENT`.
- `UDS_INDEX_NOT_SAVED_CLEANLY` and `UDS_UNSUPPORTED_VERSION` map to `-EEXIST`.
- `UDS_DISABLED` and unexpected internal errors map to `-EIO`.

## Invariants
Registered error blocks cannot overlap and block names cannot duplicate. Capacity is fixed at six blocks.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/errors.h -->
# File Research: sources/block-storage/kvdo/vdo/errors.h

## Purpose
Defines UDS status codes, error metadata shape, and conversion/registration APIs.

## Main Contents
- `enum uds_status_codes`: success plus internal error codes starting at 1024.
- Reserved block end `UDS_ERROR_CODE_BLOCK_END` leaves room for future UDS errors.
- Error string buffer size constants.
- `struct error_info`: symbolic name and human message.

## API
- `uds_string_error()`
- `uds_string_error_name()`
- `uds_map_to_system_error()`
- `register_error_block()`

## Integration
Shared by low-level UDS structures such as delta index, geometry, buffers, and by higher VDO paths that must return Linux-compatible errno values.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/errors.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/event-count.c -->
# File Research: sources/block-storage/kvdo/vdo/event-count.c

## Purpose
Implements an event count: a lock-free condition-variable-like primitive for producer/consumer structures.

## Main Design
- `state` is an atomic 64-bit value split into low 16-bit waiter count and high 48-bit event counter.
- `event_count_prepare()` issues a token by incrementing waiter count.
- `event_count_broadcast()` increments the event counter, claims current waiters, and posts one semaphore token per waiter.
- `event_count_cancel()` tries to remove an unconsumed waiter token; if already signaled, it consumes the semaphore token instead.
- `event_count_wait()` consumes a token and returns when the event counter differs from the token, optionally timing out and cancelling if possible.

## Dependencies
Uses Linux atomics, UDS semaphore wrappers, scheduler yield, memory barriers, allocation, and cache-line alignment.

## Invariants
Every prepared token must be consumed by exactly one wait or cancel call. Tokens should only be held briefly; long delays before wait/cancel hurt performance and can increase contention.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/event-count.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/event-count.h -->
# File Research: sources/block-storage/kvdo/vdo/event-count.h

## Purpose
Declares the opaque event-count synchronization primitive.

## API
- `make_event_count()` / `free_event_count()`
- `event_count_broadcast()`
- `event_count_prepare()`
- `event_count_cancel()`
- `event_count_wait()`

## Usage Contract
Callers prepare a token, re-check their condition, then either cancel the token or wait on it. A timeout pointer is optional and measured as a `ktime_t`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/event-count.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/flush.c -->
# File Research: sources/block-storage/kvdo/vdo/flush.c

## Purpose
Implements VDO flush generation tracking and flush bio completion. It coordinates logical zones, packer flushing, pending flush generations, backing-device submission, allocation-failure handling, and flusher drain/resume.

## Main Behavior
- `vdo_make_flusher()` creates a flusher tied to the packer thread and preallocates a spare `vdo_flush`.
- `vdo_launch_flush()` captures incoming flush bios into a `vdo_flush`; if allocation fails, it queues bios and uses/reuses the spare when possible.
- `flush_vdo()` assigns a new flush generation, queues it for notification, and starts notifying zones if idle.
- Notification walks logical zones, increments each zone generation, then increments the packer generation.
- `vdo_complete_flushes()` completes pending flushes when all logical zones have advanced past that generation.
- Completion forwards original bios to the backing device using selected bio queue rotation and counts acknowledged/outgoing flushes.
- Drain waits for no pending flushes and no queued waiting flush bios.

## Dependencies
Uses admin-state machinery, logical zones, packer, read-only notifier, VDO completions, wait queues, bio lists, thread config, and io submission.

## Invariants
Flusher callbacks assert execution on the flusher/packer thread. Flush generation completion must happen in order via `first_unacknowledged_generation`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/flush.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/flush.h -->
# File Research: sources/block-storage/kvdo/vdo/flush.h

## Purpose
Declares flush request state and flusher APIs.

## Main Structure
- `struct vdo_flush`: completion object, list of covered bios, wait queue entry, and flush generation.

## API
- Lifecycle: `vdo_make_flusher()`, `vdo_free_flusher()`.
- Query/debug: `vdo_get_flusher_thread_id()`, `vdo_dump_flusher()`.
- Operation: `vdo_launch_flush()`, `vdo_complete_flushes()`.
- Admin state: `vdo_drain_flusher()`, `vdo_resume_flusher()`.

## Integration
Used by the DM target map path for flush bios and by suspend/resume administrative flows.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/flush.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/forest.c -->
# File Research: sources/block-storage/kvdo/vdo/forest.c

## Purpose
Builds, expands, replaces, frees, and traverses the VDO block-map forest, which is a set of segmented block-map trees.

## Main Behavior
- `vdo_make_forest()` computes needed tree pages for a requested entry count and builds a new segment if expansion is required.
- `make_segment()` allocates boundaries, page arrays, segment arrays per root, formats root pages, and links each level’s contiguous page region.
- `vdo_abandon_forest()` discards prepared-but-unused expansion.
- `vdo_replace_forest()` swaps a prepared larger forest into active use.
- `vdo_get_tree_page_by_index()` locates a tree page by root, height, and page index across forest segments.
- `vdo_traverse_forest()` launches one cursor per root and walks block-map tree pages asynchronously via metadata VIOs.
- Traversal repairs invalid or out-of-range mapped entries by marking them unmapped and writing the tree page.

## Dependencies
Uses block-map tree/page helpers, dirty lists, recovery/slab journal dependencies, VIO pool, metadata submitter, constants, and VDO completion callbacks.

## Invariants
The forest may have multiple segments from expansion. Traversal uses boundary calculations to avoid keeping mappings past current logical space and calls a supplied callback for allocated non-leaf node PBNs.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/forest.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/forest.h -->
# File Research: sources/block-storage/kvdo/vdo/forest.h

## Purpose
Declares block-map forest operations.

## API
- `vdo_entry_callback`: called for each allocated tree-node PBN during traversal.
- `vdo_get_tree_page_by_index()`
- `vdo_make_forest()`
- `vdo_free_forest()`
- `vdo_abandon_forest()`
- `vdo_replace_forest()`
- `vdo_traverse_forest()`

## Integration
The block map owns active and next forests and uses this API during growth, load/recovery, and metadata traversal.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/forest.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/funnel-queue.c -->
# File Research: sources/block-storage/kvdo/vdo/funnel-queue.c

## Purpose
Implements the non-inline portions of a multi-producer, single-consumer funnel queue.

## Main Behavior
- `make_funnel_queue()` allocates a cache-line-aligned queue and initializes a permanent stub entry so newest/oldest are never NULL.
- `funnel_queue_poll()` returns and removes the oldest real entry for the single consumer.
- `is_funnel_queue_empty()` reports whether an entry can currently be retrieved.
- `is_funnel_queue_idle()` distinguishes true idleness from producer transition states.

## Algorithm Notes
The queue uses an atomic exchange on the producer end and a stub node to maintain invariants. It is “almost” lock-free: a producer preempted after swapping `newest` but before writing `previous->next` can temporarily hide later entries from the consumer.

## Invariants
Only one consumer may poll. Callers own entry allocation and must embed `struct funnel_queue_entry` at a consistent offset.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/funnel-queue.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/funnel-queue.h -->
# File Research: sources/block-storage/kvdo/vdo/funnel-queue.h

## Purpose
Defines the funnel queue structures and inline producer enqueue operation.

## Main Contents
- `struct funnel_queue_entry`: intrusive next pointer embedded in queued objects.
- `struct funnel_queue`: cache-line-separated producer `newest`, consumer `oldest`, and stub entry.
- `funnel_queue_put()`: inline multi-producer enqueue using `xchg()` and `previous->next` publication.
- Poll/status allocation API declarations.

## Memory Ordering
`xchg()` provides a full barrier; producer stores must be visible before linking an entry. Consumer polling uses a read barrier before returning the dequeued entry.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/funnel-queue.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/geometry.c -->
# File Research: sources/block-storage/kvdo/vdo/geometry.c

## Purpose
Computes and manages UDS index-volume geometry: chapter/page/record counts, delta-index sizing parameters, sparse/dense chapter behavior, and remapped chapter handling.

## Main Behavior
- `make_geometry()` allocates a geometry object, stores input parameters, and derives records/pages/volume bytes, chapter index pages, delta-list counts, address bits, and payload bits.
- `copy_geometry()` recreates an equivalent geometry.
- `map_to_physical_chapter()` maps virtual chapters to physical chapters, including reduced geometry with a remapped physical chapter 0.
- `has_sparse_chapters()` and `is_chapter_sparse()` decide whether sparse chapters are active for a virtual-chapter range.
- `chapters_to_expire()` decides how many chapters to expire when opening a new chapter, including remapped-chapter exceptions.

## Dependencies
Uses `delta-index` sizing, `compute_bits()`, geometry constants, allocation, and logging/assertion infrastructure.

## Invariants
Derived fields depend on record size, page size, record pages per chapter, and sparse chapter count. Reduced geometry is detected by an odd `chapters_per_volume`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/geometry.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/geometry.h -->
# File Research: sources/block-storage/kvdo/vdo/geometry.h

## Purpose
Defines UDS index geometry fields, defaults, and helper predicates.

## Main Structure
`struct geometry` stores primary layout inputs plus derived values: pages per volume/chapter, bytes per volume, records per page/chapter/volume, delta lists, mean delta, payload/address bits, sparse/dense chapter counts, and remap metadata.

## Constants
Defines default page size, records per page/chapter, chapters per volume, sparse chapter defaults, delta-list bits, mean delta bits, and open-chapter load ratio.

## API
- `make_geometry()`, `copy_geometry()`, `free_geometry()`
- `map_to_physical_chapter()`
- `is_reduced_geometry()`, `is_sparse_geometry()`
- `has_sparse_chapters()`, `is_chapter_sparse()`
- `chapters_to_expire()`

## Integration
Consumed by hash utilities, chapter index logic, and index volume layout code.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/geometry.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/hash-utils.c -->
# File Research: sources/block-storage/kvdo/vdo/hash-utils.c

## Purpose
Provides small hash-related utility implementation.

## Main Behavior
- `compute_bits()` returns the number of bits required to represent a maximum unsigned integer value.
- `hash_utils_compile_time_assertions()` asserts `UDS_CHUNK_NAME_SIZE == 16`.

## Integration
`compute_bits()` is used by delta-index and geometry sizing code.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/hash-utils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/hash-utils.h -->
# File Research: sources/block-storage/kvdo/vdo/hash-utils.h

## Purpose
Defines how UDS chunk-name bytes are partitioned for volume index, chapter index, and sampling, and provides inline extraction/mapping helpers.

## Main Helpers
- `extract_volume_index_bytes()`: first 8 bytes as big-endian 64-bit value.
- `extract_chapter_index_bytes()`: next 6 bytes as a 48-bit value.
- `extract_sampling_bytes()`: final 2 bytes.
- `hash_to_chapter_delta_list()`: maps a name to chapter delta-list number.
- `hash_to_chapter_delta_address()`: maps a name to delta address within that list.
- `name_to_hash_slot()`: maps to an open-chapter hash slot.

## Dependencies
Uses geometry-derived address/list bit counts and unaligned big-endian accessors.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/hash-utils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/header.c -->
# File Research: sources/block-storage/kvdo/vdo/header.c

## Purpose
Implements encoding, decoding, and validation of versioned VDO on-disk structure headers.

## Main Behavior
- `vdo_validate_version()` checks exact major/minor match and logs mismatch.
- `vdo_validate_header()` verifies component id, version, and size constraints.
- `vdo_encode_header()` writes component id, packed version, and size to a buffer in little-endian format.
- `vdo_decode_header()` reads those fields back.
- `vdo_encode_version_number()` / `vdo_decode_version_number()` handle packed version numbers.

## Dependencies
Uses VDO buffer helpers, status codes, logger, and header packing helpers from the header.

## Invariants
Header validation can require exact size or allow actual size to be larger than expected. Version validation here requires exact match; the separate upgradable-version predicate is declared in the header but not used here.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/header.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/header.h -->
# File Research: sources/block-storage/kvdo/vdo/header.h

## Purpose
Defines version-number and generic component-header formats used by VDO on-disk data.

## Main Contents
- `struct version_number`: native major/minor version.
- `struct packed_version_number`: little-endian on-disk version.
- Component IDs for super block, fixed layout, recovery journal, slab depot, block map, and geometry block.
- `struct header`: component id, version, and data size.
- `VDO_ENCODED_HEADER_SIZE`.

## API and Inline Helpers
- Version equality/upgradability predicates.
- Header/version encode/decode/validate declarations.
- `vdo_pack_version_number()` and `vdo_unpack_version_number()` convert between native and little-endian packed form.

## Integration
Used by persistent metadata components to identify format, size, and version compatibility.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/header.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/heap.c -->
# File Research: sources/block-storage/kvdo/vdo/heap.c

## Purpose
Implements a generic in-place max-heap wrapper over caller-owned arrays, including heapify, pop-max, full sort, and incremental sort.

## Main Behavior
- `initialize_heap()` stores comparator/swapper/capacity/element size and shifts the array pointer so indexes can be treated as 1-based byte offsets.
- `build_heap()` heapifies up to capacity using bottom-up sift-down in O(N).
- `pop_max_heap_element()` removes the root, optionally copies it to the caller, moves the final leaf to root, and restores heap invariant.
- `sort_heap()` performs in-place heapsort, leaving the heap empty and array sorted from minimum to maximum.
- `sort_next_heap_element()` performs one heapsort step and returns the next sorted element pointer.

## Dependencies
Uses caller-provided comparator and swapper, numeric min helper, status/error headers, and standard memory copy.

## Notable Risk
`sift_heap_down()` computes `right_child` as `left_child + heap->element_size`; this is consistent with the file’s byte-offset indexing scheme, but any future change to element-index rather than byte-index arithmetic would break the heap.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/heap.c -->