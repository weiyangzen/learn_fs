# Group Research: group_663_kvdo_sources_block_storage_kvdo_vdo_heap_h_sources_block_storage_kvd_678e25c4e0b7

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/kvdo`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/heap.h -->
# File Research: sources/block-storage/kvdo/vdo/heap.h

Generic heap interface for fixed-size array elements.

Key responsibilities:
- Defines `heap_comparator` and `heap_swapper` callbacks used to compare and exchange arbitrary element types.
- Defines `struct heap`, a 1-based heap view over caller-provided storage with capacity, element size, current count, comparator, and swapper.
- Declares setup and operations: `initialize_heap()`, `build_heap()`, `pop_max_heap_element()`, `sort_heap()`, and `sort_next_heap_element()`.
- Provides `is_heap_empty()` inline.

Important behavior:
- The header documents a max-heap invariant, though the comment says every child "must be at least as large as its children", which appears to intend "every parent".
- The heap does not own storage; callers provide the backing array and element callbacks.
- Sorting and pop behavior depend entirely on the comparator/swapper being O(1) and correct for the array element type.

Dependencies:
- Uses `type-defs.h` for `byte`, `bool`, and related base types.

Notable risks:
- The 1-based array convention is explicit; callers must allocate/pass storage compatible with that convention.
- No ownership, locking, or bounds semantics are visible in the header beyond capacity/count fields.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/heap.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-layout.c -->
# File Research: sources/block-storage/kvdo/vdo/index-layout.c

On-disk UDS index layout manager for block-device backed index storage, including superblock layout, region tables, two clean-save slots, save/load of index state, and volume-region access.

Key responsibilities:
- Defines the single-file index layout format: super/header/config/index/seal regions, one sub-index, a volume region, and two `RL_KIND_SAVE` regions.
- Defines save-region sublayout: save header, index page map, per-zone volume-index regions, saved open chapter, and optional free space.
- Computes required index size from `struct configuration` geometry via `compute_sizes()` and exports `uds_compute_index_size()`.
- Generates and validates nonces using `murmurhash3_128()`: primary superblock nonce, sub-index nonce, and per-save nonce.
- Encodes/decodes little-endian `region_header`, `layout_region`, superblock data, `index_save_data`, and versioned `index_state_data301`.
- Loads existing layout from storage, validates magic/version/config, reconstructs region boundaries, and loads valid save-region metadata.
- Creates new layouts, invalidates old save slots, writes the top-level layout header and config region.
- Selects latest valid save for load and oldest/invalid save for overwrite.
- Saves and loads clean index state by coordinating saved open chapters, volume index zones, and index page maps.
- Exposes `make_uds_index_layout()`, `free_uds_index_layout()`, `replace_index_layout_storage()`, `load_index_state()`, `save_index_state()`, `discard_index_state_data()`, `discard_open_chapter()`, `get_uds_volume_nonce()`, and `open_uds_volume_bufio()`.

Important behavior:
- The persistent format uses 4K `UDS_BLOCK_SIZE` blocks; region headers and regions begin on block boundaries.
- Supported superblock versions are 3 and 7; versions 4-6 are explicitly rejected.
- Version 7 represents converted layouts with `volume_offset`/`start_offset`; older versions treat both as zero.
- Save validity requires nonzero zone count, nonzero timestamp, and a save nonce matching the sub-index nonce plus save start block and timestamp.
- `save_index_state()` first invalidates the selected old slot, instantiates a fresh save layout, writes the open chapter, writes all volume-index zones, writes the page map, then writes the save header last to make the slot valid.
- `load_index_state()` selects the latest valid save slot and restores newest/oldest chapter numbers, last-save chapter, saved open chapters, volume index, and page map.
- `discard_open_chapter()` zeroes one block of the latest save's open-chapter region so later recovery knows a clean saved open chapter is no longer available.
- `open_uds_volume_bufio()` returns a dm-bufio client over the volume region, adjusted for converted-layout offsets.

Dependencies:
- Storage access is through `io_factory`, `buffered_reader`, `buffered_writer`, and dm-bufio.
- Relies on `configuration`, `geometry`, config serialization, open-chapter save/load, volume-index save/load, index-page-map save/load, random/time utilities, memory allocation, logging, and little-endian buffer helpers.
- Uses `linux/murmurhash3.h` for nonce hashing.

Notable risks:
- Region reconstruction is strict about offsets, kinds, instances, counts, and versions; minor layout drift becomes `UDS_CORRUPT_DATA` or unsupported-version failure.
- `discard_index_state_data()` stores the last failing result in `saved_result` but logs/returns `result` after the loop, which may not be the same variable value if multiple slots are attempted.
- `make_index_save_region_table()` stores `payload` and `type` as `size_t` before assigning to 16-bit fields; current values are small, but the type mismatch matters for future expansion.
- Clean-save atomicity depends on invalidating the old slot before writing a new one and committing the new save header last.
- Save arrays are bounded by `MAX_ZONES`; callers must keep `zone_count` within that contract.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-layout.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-layout.h -->
# File Research: sources/block-storage/kvdo/vdo/index-layout.h

Public interface for UDS index layout storage.

Key responsibilities:
- Forward-declares opaque `struct index_layout`.
- Declares layout lifecycle: `make_uds_index_layout()` and `free_uds_index_layout()`.
- Declares backing-store replacement through `replace_index_layout_storage()`.
- Declares clean-state persistence APIs: `load_index_state()`, `save_index_state()`, `discard_index_state_data()`, and `discard_open_chapter()`.
- Declares accessors for volume nonce and dm-bufio access to the volume region.

Dependencies:
- Includes `buffer.h`, `config.h`, `io-factory.h`, and `uds.h`.
- Exposes `struct uds_index` in function signatures without defining it here.

Notable risks:
- The API is stateful and opaque; callers rely on implementation-side validation and correct save-slot ordering.
- `discard_index_state_data()` lacks `__must_check`, unlike most mutating persistence calls.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-layout.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-page-map.c -->
# File Research: sources/block-storage/kvdo/vdo/index-page-map.c

Persistent map from chapter/index-page number to highest delta-list number stored on each index page.

Key responsibilities:
- Allocates and frees `struct index_page_map`.
- Maintains a compact two-dimensional array: chapter number by index page, omitting the last page in each chapter because its upper bound is implied by geometry.
- Updates map entries as chapter index pages are built or rebuilt.
- Finds the index page for a chunk name by hashing to a chapter delta list and scanning the chapter's page bounds.
- Provides lower/upper delta-list bounds for a chapter index page.
- Serializes/deserializes the page map with magic `ALBIPM02`, `last_update`, and little-endian `uint16_t` entries.

Important behavior:
- `entries_per_chapter` is `index_pages_per_chapter - 1`.
- `last_update` records the virtual chapter number of the last map update.
- `find_index_page_number()` returns the first page whose recorded high list is >= the hashed list, or the implicit final page.
- `compute_index_page_map_save_size()` returns exact serialized size for save-region sizing.
- Read validates magic before consuming `last_update` and entries.

Dependencies:
- Uses `geometry`, `hash-utils`, buffer serialization, buffered reader/writer, memory allocation, logging, and UDS error codes.

Notable risks:
- Assumes `index_pages_per_chapter >= 1`; if it were 0, `entries_per_chapter` underflows.
- Lookups scan per chapter linearly over index pages; acceptable if page count is small.
- Integrity checking is limited to magic and buffer read success; entry monotonicity is validated elsewhere during rebuild.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-page-map.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-page-map.h -->
# File Research: sources/block-storage/kvdo/vdo/index-page-map.h

Header defining the index-page-map structure and persistence/search API.

Key responsibilities:
- Defines `struct index_page_map` with geometry pointer, `last_update`, per-chapter entry count, and `uint16_t` entries array.
- Declares allocation/free, read/write, update, lookup, bounds query, and serialized-size computation functions.

Dependencies:
- Includes buffered reader/writer, common types, and geometry.

Notable risks:
- The map keeps a raw pointer to `const struct geometry`; the geometry must outlive the map.
- Entry storage is implementation-owned but directly visible through the struct definition, so external code could mutate it without validation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-page-map.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-session.c -->
# File Research: sources/block-storage/kvdo/vdo/index-session.c

Session-level API mediator for opening, closing, suspending, resuming, destroying, and issuing asynchronous requests against a UDS index.

Key responsibilities:
- Manages session state flags: loading, loaded, disabled, suspended, waiting, closing, destroying.
- Tracks in-flight asynchronous requests with `request_count` and drains them for suspend/close/destroy/flush.
- Creates the callback request queue and forwards completed index requests to user callbacks.
- Validates request types and callbacks in `uds_start_chunk_operation()`, resets internal request fields, obtains a session reference, and enqueues requests to the index.
- Converts internal UDS statuses to system errors at callback/API boundaries.
- Updates per-session statistics for posts, updates, deletes, queries, locations, and request totals.
- Opens indexes with `uds_open_index()`, including parameter name ownership and create/load/no-rebuild modes.
- Suspends and resumes sessions, including special coordination with an in-progress rebuild through `index_load_context`.
- Saves/free indexes on close and destroy.
- Returns parameter copies and statistics snapshots.

Important behavior:
- Any successful async request increments `request_count`; callback completion releases it.
- Any request callback status other than `UDS_SUCCESS` marks the session disabled. A disabled index rejects later requests until close/reopen.
- Suspend blocks new requests by setting `IS_FLAG_WAITING`, drains or saves depending on the `save` parameter, and then marks the session suspended.
- If suspend races with rebuild, it changes load context to `INDEX_SUSPENDING` and waits for rebuild code to publish `INDEX_SUSPENDED` or `INDEX_READY`.
- Resume can replace backing storage if a new name is supplied, then wakes a suspended rebuild by returning load context to `INDEX_OPENING`.
- Destroy handles the special case of a suspended load by setting `INDEX_FREEING` and waiting until loading exits.

Dependencies:
- Depends on `index.c` APIs, request queues, configuration building, logging, memory allocation, mutexes/condition variables, and time utilities.

Notable risks:
- `get_index_session()` increments `request_count` before checking state, then must release on non-loaded states; this is correct but fragile.
- Statistics use `READ_ONCE`/`WRITE_ONCE` increments rather than atomics; they are intended as approximate thread-safe counters.
- `uds_resume_index_session()` returns raw `result` on some no-work paths instead of always mapping through `uds_map_to_system_error()`.
- A single internal request error disables the whole session, which is conservative but broad.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-session.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index-session.h -->
# File Research: sources/block-storage/kvdo/vdo/index-session.h

Internal session state definitions for UDS index operations.

Key responsibilities:
- Defines cache-line-aligned `struct session_stats` counters for request outcomes and locations.
- Defines `enum index_suspend_status` for load/rebuild coordination: opening, ready, suspending, suspended, freeing.
- Defines `struct index_load_context` with mutex, condition variable, and status.
- Defines `struct uds_index_session`, holding state flags, current `uds_index`, callback queue, parameters, load context, request drain synchronization, request count, and stats.

Dependencies:
- Includes kernel atomics, config, CPU cache-line sizing, UDS threads, and public UDS types.

Notable risks:
- State is an integer bitfield whose valid combinations are enforced by `index-session.c`, not the type system.
- Stats are embedded and aligned, but individual fields are plain `uint64_t`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index-session.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index.c -->
# File Research: sources/block-storage/kvdo/vdo/index.c

Core UDS index engine: request dispatch, zone coordination, chapter closing/writing, clean-load handling, and rebuild replay.

Key responsibilities:
- Routes requests through optional sparse triage queue, per-zone index queues, and message queues.
- Implements sparse-cache barrier coordination for multi-zone sparse indexes.
- Maintains per-zone open and writing chapters, plus index-level oldest/newest virtual chapter counters.
- Handles zone messages for sparse-cache barriers and chapter-close announcements.
- Searches and updates the volume index, open chapters, writing chapters, dense page cache, and sparse cache for post/update/query/delete requests.
- Runs a chapter-writer thread that waits for all zones to close a chapter, writes the closed chapter to the volume, expires old chapters, and wakes zones.
- Creates/free index zones, queues, volume, volume index, layout, and chapter writer.
- Loads cleanly saved index state via `load_index_state()`, or rebuilds by replaying chapters from the volume if clean load fails and rebuild is allowed.
- Saves index state on demand with `save_index()`.
- Exposes queue enqueueing and stats aggregation.

Important behavior:
- For a request, the volume index gives a virtual chapter hint; the engine resolves it against open chapter, recently writing chapter, sparse cache, or dense volume page cache.
- Query-without-update stops after lookup; post/update may move found records into the current open chapter and update the volume index to the newest chapter.
- Delete removes the volume-index record and removes/marks the record in the open chapter if needed.
- When a zone fills or is told another zone closed the current chapter, it swaps open/writing chapters, announces closure to peers, advances per-zone chapter counters, and possibly expires old chapters.
- The chapter writer only writes once all zones submit a chapter. It discards the saved open chapter after the first post-load chapter close.
- Rebuild finds valid volume chapter boundaries, sets virtual chapter range, rebuilds the page map, and replays record pages into the volume index, skipping non-sample records for chapters that will be sparse.
- `make_index()` marks load context ready after successful create/load/rebuild and initializes all zones to the index chapter range.
- `save_index()` waits for idle, records `last_save`, writes layout state, and sets `has_saved_open_chapter`.

Dependencies:
- Depends on layout, volume, open chapter, volume-index operations, sparse cache, request queues, geometry/hash helpers, and logging.

Notable risks:
- The chapter-writer rendezvous is subtle: per-zone and global newest/oldest chapter counters must stay coherent.
- Sparse-cache barriers allocate synthetic requests and assert allocation success in one path.
- `try`/requeue semantics rely on request fields such as `location`, `virtual_chapter`, and `requeued` remaining coherent across queue passes.
- `replay_record()` may intentionally lose duplicate/overflow records during rebuild.
- `index->need_to_save` is set when executing zone requests before dispatch; failures can mark sessions disabled but still leave save state dirty.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/index.h -->
# File Research: sources/block-storage/kvdo/vdo/index.h

Internal declarations for the UDS index engine.

Key responsibilities:
- Defines `index_callback_t`.
- Defines `struct index_zone` with open/writing chapters and per-zone virtual chapter range.
- Defines `struct uds_index`, including layout, volume index, volume, zones, chapter counters, save flags, chapter writer, callback, triage queue, and flexible array of zone queues.
- Defines request stages: triage, index, and message.
- Declares lifecycle, save, storage replacement, stats, enqueue, and idle-wait functions.

Dependencies:
- Includes layout/session/open-chapter/volume/volume-index headers.

Notable risks:
- `struct uds_index` exposes many mutable fields across modules; synchronization contracts are mostly implicit in queue/thread ownership.
- `zone_queues[]` is a flexible array; allocation must include space for `zone_count` queue pointers.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/index.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/instance-number.c -->
# File Research: sources/block-storage/kvdo/vdo/instance-number.c

Global VDO instance-number allocator backed by a growable bitmap.

Key responsibilities:
- Tracks allocated instance numbers in a flat `unsigned long` bit array.
- Initializes and destroys global mutex-protected tracking state.
- Allocates the next free instance number, growing capacity as needed.
- Releases previously allocated instance numbers.
- Starts with minimum capacity for 1000 instances and grows by 100 bits.

Important behavior:
- Allocation scans from `next_instance` and wraps to zero if needed.
- The first allocation lazily grows the bitmap because initial `words` is `NULL`.
- Successive starts of the same volume can get different instance numbers, helping external monitoring detect reset stats.
- Cleanup asserts no instances remain allocated.

Dependencies:
- Uses Linux bit operations, mutexes, UDS memory allocation/reallocation, numeric helpers, and assertions.

Notable risks:
- All state is global; callers must initialize/cleanup exactly once at module lifecycle boundaries.
- Release only asserts on invalid/double release and otherwise continues.
- Bitmap scanning is O(n), intentionally accepted for expected device counts.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/instance-number.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/instance-number.h -->
# File Research: sources/block-storage/kvdo/vdo/instance-number.h

Tiny public interface for VDO instance-number tracking.

Key responsibilities:
- Declares allocate/release calls.
- Declares module-level initialize and cleanup functions.

Dependencies:
- No includes; uses basic C integer types expected from including context.

Notable risks:
- Does not annotate `vdo_allocate_instance()` as `__must_check`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/instance-number.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/int-map.c -->
# File Research: sources/block-storage/kvdo/vdo/int-map.c

Pointer-valued `uint64_t` map implemented with non-concurrent hopscotch hashing.

Key responsibilities:
- Implements `make_int_map()`, `free_int_map()`, `int_map_size()`, `int_map_get()`, `int_map_put()`, and `int_map_remove()`.
- Uses packed buckets containing `first_hop`, `next_hop`, key, and non-NULL value.
- Hashes keys with a CityHash-derived 64-bit mixer and scales 32 hash bits into the capacity without modulo division.
- Maintains sorted biased-offset hop lists per neighborhood.
- Finds or creates vacancies by probing and moving entries closer to their home neighborhood.
- Resizes by 1.5x and rehashes all entries when a suitable vacancy cannot be found.

Important behavior:
- `initial_load` defaults to 75%; values over 100 are rejected.
- Capacity is number of neighborhoods; bucket array includes `NEIGHBORHOOD - 1` extra buckets to avoid wraparound at the end.
- NULL values are invalid because NULL marks empty buckets.
- `int_map_put()` can either update existing values or preserve them while still returning the old value.
- The map grows but never shrinks.
- Deletes truly remove entries and splice hop lists, avoiding tombstones.

Dependencies:
- Uses UDS memory allocation, logging, numeric helpers, assertions, and error codes.

Notable risks:
- No internal locking; callers must serialize access.
- Resize is expensive and can cause high insertion latency.
- `NEIGHBORHOOD` is 255 to fit biased offsets in `uint8_t`; changing this affects packed encoding.
- The packed bucket layout may create unaligned key/value accesses on some architectures, relying on compiler/architecture support.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/int-map.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/int-map.h -->
# File Research: sources/block-storage/kvdo/vdo/int-map.h

Public interface for the integer-to-pointer map.

Key responsibilities:
- Documents `int_map` as a `uint64_t` to non-NULL pointer map.
- Declares opaque `struct int_map`.
- Declares allocation/free, size, get, put, and remove operations.

Dependencies:
- Includes `compiler.h` and `type-defs.h`.

Notable risks:
- Header documents expected constant-time operations but insertion can resize linearly.
- Values are not owned by the map and must not be NULL.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/int-map.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/io-factory.c -->
# File Research: sources/block-storage/kvdo/vdo/io-factory.c

Kernel block-device I/O factory for UDS index storage and dm-bufio region access.

Key responsibilities:
- Opens block devices by `major:minor` string or path.
- Abstracts kernel API differences across upstream/RHEL versions with `blkdev_get_*`, `bdev_open_*`, or `bdev_file_open_*`.
- Reference-counts `struct io_factory` instances.
- Replaces the backing storage for an existing factory.
- Reports writable size via block-device inode size.
- Creates dm-bufio clients for aligned regions.
- Opens UDS buffered readers/writers over 4K-block regions.

Important behavior:
- Requires read/write block-device open mode.
- `make_uds_io_factory()` returns the factory with refcount 1.
- `put_uds_io_factory()` closes/releases the backing handle when refcount reaches zero.
- `make_uds_bufio()` validates sector-aligned offsets and block sizes that are multiples of `UDS_BLOCK_SIZE`.
- Buffered reader/writer helpers require region size to be a multiple of `UDS_BLOCK_SIZE` and reserve one dm-bufio buffer.

Dependencies:
- Linux block-device, mount, version, dm-bufio APIs; UDS logging and memory allocation.

Notable risks:
- Conditional API compatibility branches are complex and version-sensitive.
- `replace_uds_storage()` swaps the backing device without explicit synchronization; callers must ensure no unsafe concurrent users.
- The `new_layout` parameter to `create_layout_factory()` in `index-layout.c` is unused by this layer.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/io-factory.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/io-factory.h -->
# File Research: sources/block-storage/kvdo/vdo/io-factory.h

Public interface for UDS index storage access.

Key responsibilities:
- Declares opaque `struct io_factory`.
- Defines `UDS_BLOCK_SIZE` as 4096 bytes.
- Declares factory lifecycle, backing-store replacement, refcount operations, writable-size query, dm-bufio creation, and buffered reader/writer creation.

Dependencies:
- Includes buffered reader/writer APIs and Linux dm-bufio.

Notable risks:
- Documentation mentions block device or file, but the implementation in this tree is block-device oriented.
- Header notes remaining hardcoded 4K constants should be converted to `UDS_BLOCK_SIZE`.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/io-factory.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/io-submitter.c -->
# File Research: sources/block-storage/kvdo/vdo/io-submitter.c

VDO bio submission coordinator with per-bio-thread queues, block-layer plugging, and adjacent data-bio merge tracking.

Key responsibilities:
- Defines `bio_queue_data` with work queue, `blk_plug`, `int_map` merge map, mutex, and queue number.
- Defines `io_submitter` containing bio queue data for configured bio threads.
- Starts/finishes block plugs when bio work queues run.
- Counts submitted bios into data/meta/journal/page-cache stats.
- Submits bios to the backing device with `submit_bio_noacct()`.
- Merges adjacent data VIO bios by sector when priority and direction match.
- Submits data VIO I/O through bio-zone callbacks, or leaves merged VIOs pending until the head/tail owner submits.
- Submits metadata VIO I/O by resetting the bio and scheduling `process_vio_io()` on the appropriate bio-zone thread.
- Creates, cleans up, and frees the I/O submitter and per-thread merge maps.

Important behavior:
- Merge maps store only head and tail sectors for each merged bio list.
- Back merges append to previous tail; front merges prepend to next head.
- If a VIO merges into another pending list, it is not immediately launched.
- `process_data_vio_io()` extracts the merged bio list under lock, removes head/tail map entries, then submits each bio.
- Flush operations are submitted as metadata with `REQ_OP_WRITE | REQ_PREFLUSH`.
- Creation sizes each queue's `int_map` as `max_requests_active * 2`, allowing both first and last sector entries.

Dependencies:
- Linux bio/block APIs, VDO work queues, completions, VIO/data_vio types, atomic stats, `int-map`, assertions, memory allocation, logger, and thread config.

Notable risks:
- `merge_to_prev_tail()` and `merge_to_next_head()` assign `result` twice and only return the second insertion result, so a first insertion failure can be overwritten.
- Comments state `int_map_put()` failure is ignored except for assertions.
- Merge correctness depends on serialized access through each queue's mutex and stable bio-zone assignment.
- Cleanup and free are split to avoid races; callers must call them in the intended order.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/io-submitter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/io-submitter.h -->
# File Research: sources/block-storage/kvdo/vdo/io-submitter.h

Header for VDO I/O submission helpers.

Key responsibilities:
- Declares I/O submitter lifecycle: `vdo_make_io_submitter()`, `vdo_cleanup_io_submitter()`, and `vdo_free_io_submitter()`.
- Declares direct VIO processing, data VIO submission, and metadata VIO submission.
- Provides inline helpers `submit_metadata_vio()` and `submit_flush_vio()`.

Dependencies:
- Includes Linux bio, completion, kernel types, and VIO definitions.

Notable risks:
- `submit_flush_vio()` contains a FIXME asking whether pure `REQ_OP_FLUSH` can be used.
- Opaque `struct io_submitter` is forward-declared in `kernel-types.h`, not here.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/io-submitter.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/journal-point.h -->
# File Research: sources/block-storage/kvdo/vdo/journal-point.h

Inline utilities and packed format for recovery/slab journal positions.

Key responsibilities:
- Defines `journal_entry_count_t`.
- Defines `struct journal_point` as sequence number plus entry count.
- Defines packed little-endian `struct packed_journal_point`.
- Provides inline advance, validity, ordering, equality, pack, and unpack helpers.

Important behavior:
- Packed encoding stores low 48 bits of sequence number shifted left 16 bits plus 16-bit entry count.
- `vdo_advance_journal_point()` wraps entry count to zero and increments sequence number at `entries_per_block`.
- Valid points require non-NULL pointer and sequence number > 0.

Dependencies:
- Includes numeric helpers and VDO types.

Notable risks:
- Header notes the packed format assumes top 16 bits of sequence number are zero long-term.
- Inline pack does not validate sequence-number width or entry-count bounds.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/journal-point.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/kernel-types.h -->
# File Research: sources/block-storage/kvdo/vdo/kernel-types.h

Central kernel-facing VDO type aliases, enums, priorities, forward declarations, and a zoned physical block helper.

Key responsibilities:
- Defines small-width types such as `compressed_fragment_count_t`, `page_size_t`, `thread_count_t`, `thread_id_t`, and `vio_count_t`.
- Defines `VDO_INVALID_THREAD_ID`.
- Defines data VIO operation bit flags and masks.
- Defines `enum vio_type` for data and metadata/statistics categories.
- Provides inline helpers to classify data versus metadata VIO types.
- Defines completion priority constants for bio, CPU, UDS, and default queues.
- Defines `enum vio_priority` and `enum vdo_zone_type`.
- Forward-declares many core VDO structures.
- Defines `struct zoned_pbn` containing PBN, mapping state, and physical zone pointer.

Dependencies:
- Includes `types.h` and Linux version headers.

Notable risks:
- Many core subsystems depend on these enum numeric values for queue priority and instrumentation.
- Thread IDs are `uint8_t`, so thread-count assumptions are bounded by that representation.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/kernel-types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/linux/murmurhash3.h -->
# File Research: sources/block-storage/kvdo/vdo/linux/murmurhash3.h

Minimal MurmurHash3 declaration header.

Key responsibilities:
- Provides LGPL/public-domain notice for MurmurHash3.
- Includes Linux integer types.
- Declares `murmurhash3_128(const void *key, int len, uint32_t seed, void *out)`.

Dependencies:
- Requires `<linux/types.h>`.

Notable risks:
- Only the prototype is present; callers must link the implementation elsewhere.
- `len` is `int`, so callers with size_t lengths must ensure values fit.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/linux/murmurhash3.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/lock-counter.c -->
# File Research: sources/block-storage/kvdo/vdo/lock-counter.c

Shared per-lock reference counter set for recovery journal, logical zones, and physical zones.

Key responsibilities:
- Allocates lock-counter arrays for journal, logical, and physical zone lock references.
- Tracks per-zone per-lock counters in `uint16_t` arrays, grouped by zone to reduce cache-line contention.
- Tracks aggregate logical/physical zone holder counts with `atomic_t` arrays.
- Tracks journal decrements from other zones with atomic decrement counts.
- Tests lock state for logical/physical zones, with journal locks blocking both.
- Initializes journal-zone lock counts.
- Acquires/releases logical and physical zone references.
- Releases journal-zone references from journal or other zones.
- Sends a completion notification when some lock may have become unlocked.
- Supports notification acknowledge, suspend, and resume.

Important behavior:
- Journal-zone lock state is `journal_value != journal_decrement_count`.
- Non-journal zone count increments only when a zone's local counter goes from 0 to 1, and decrements only when it goes from 1 to 0.
- Only one unlock notification can be in flight; state transitions use atomic compare-exchange.
- Suspended counters suppress new notifications until resumed.
- Several operations assert they run on the journal thread or not from the journal zone.

Dependencies:
- VDO completions, VDO thread callback IDs, memory allocation, atomics, barriers, assertions, and VDO zone types.

Notable risks:
- Local `uint16_t` counters are not atomic; correctness depends on zone/thread ownership.
- Notification is edge-style and coalesced; the owner must rescan locks and call `vdo_acknowledge_lock_unlock()`.
- `get_counter()` handles `VDO_ZONE_TYPE_JOURNAL` as a single-zone array but computes `locks * zone_id + lock_number`; journal callers pass zone 0.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/lock-counter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/lock-counter.h -->
# File Research: sources/block-storage/kvdo/vdo/lock-counter.h

Public API for VDO lock-counter sets.

Key responsibilities:
- Documents the per-zone reference-count locking model and notification contract.
- Declares creation/free, lock-state query, journal initialization, acquire/release operations, journal release operations, acknowledge, suspend, and resume.

Dependencies:
- Includes completion and VDO types.

Notable risks:
- The owner callback must understand that notification means “some lock may be released”, not which lock.
- Correct use depends on thread-context constraints documented in the `.c` file more than in the signatures.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/lock-counter.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/logger.c -->
# File Research: sources/block-storage/kvdo/vdo/logger.c

Kernel logging implementation for UDS/VDO.

Key responsibilities:
- Maps string names to UDS log priorities and priorities to printable names.
- Stores a global log level, defaulting to `UDS_LOG_INFO`.
- Maps UDS priorities to kernel `KERN_*` prefixes.
- Formats log messages differently for interrupt context, VDO/UDS kernel threads, device-associated threads, and other processes.
- Supports packed two-part varargs log messages.
- Logs error messages with decoded UDS/system error text.
- Emits stack traces and provides a short pause to let kernel logs flush.

Important behavior:
- Messages with priority numerically greater than current log level are dropped.
- Interrupt context logs include interrupt type (`NMI`, `HI`, `SI`, or `INTR`) and omit process context.
- Device-associated logs include module, device instance, and task name.
- Uses `va_copy()` for both varargs sections to handle implementation-specific `va_list`.

Dependencies:
- Linux printk, hardirq context helpers, module/current task state, stack dump, delay, thread-device ID, UDS thread/string error helpers.

Notable risks:
- `log_level` is a plain global int without locking.
- Logging from interrupt context intentionally avoids device/thread lookup.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/logger.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/logger.h -->
# File Research: sources/block-storage/kvdo/vdo/logger.h

Logging API and convenience macros for UDS/VDO kernel code.

Key responsibilities:
- Defines UDS log priority constants compatible with syslog ordering.
- Defines `UDS_LOGGING_MODULE_NAME` from `THIS_MODULE->name` or `"vdo"`.
- Provides a `uds_log_ratelimit()` wrapper macro.
- Declares log-level get/set and priority conversion helpers.
- Declares varargs logging functions and strerror logging helpers.
- Defines level-specific macros: debug, info, notice, warning, error, fatal, and corresponding strerror variants.
- Declares `uds_log_backtrace()` and `uds_pause_for_logger()`.

Dependencies:
- Linux module and ratelimit headers.

Notable risks:
- The strerror macros include trailing semicolons in macro definitions; they are intended for statement use.
- The rate-limit macro creates one static ratelimit state per call site.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/logger.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/kvdo/vdo/logical-zone.c -->
# File Research: sources/block-storage/kvdo/vdo/logical-zone.c

Logical-zone creation, drain/resume orchestration, LBN operation map setup, allocation selector setup, and flush-generation tracking.

Key responsibilities:
- Allocates and initializes `struct logical_zones` and each `logical_zone`.
- Creates per-zone `int_map` for LBN operations and allocation selectors.
- Creates default logical-zone threads and an action manager for zone-wide admin operations.
- Frees logical zones, selectors, and LBN operation maps.
- Drains logical zones through admin-state machinery, completing when no writes or notifications remain.
- Resumes logical zones from quiescent state.
- Tracks per-zone flush generations and active write VIOs.
- Acquires/releases a write data VIO’s flush-generation lock.
- Notifies the flusher when the oldest active generation advances.
- Dumps logical-zone state for debugging.

Important behavior:
- Each logical zone is tied to a configured logical-zone thread and block-map zone.
- `write_vios` list order is used to determine the oldest active flush generation.
- `vdo_increment_logical_zone_flush_generation()` increments the generation, resets per-generation I/O count, and updates oldest active generation.
- `vdo_acquire_flush_generation_lock()` rejects acquisition unless zone admin state is normal.
- Releasing a generation lock removes the VIO from `write_vios`; if oldest active generation advances and no notification is already in flight, it launches a completion to the flusher thread.
- Notification completion returns to the logical-zone thread and may chain additional notifications until caught up.
- Drain completion waits for no active writes and no in-flight flusher notification.

Dependencies:
- Action manager, admin state, allocation selector, block map, completion, constants, data VIO, flusher, `int-map`, logger, memory allocation, assertions, and VDO thread configuration.

Notable risks:
- Correctness relies on operations running on the zone thread; assertions are log-only.
- `ios_in_flush_generation` is incremented but not decremented here; it is a generation counter/stat, not active count.
- Drain can be delayed by a pending flusher notification even after writes are gone.
<!-- END FILE RESEARCH: sources/block-storage/kvdo/vdo/logical-zone.c -->