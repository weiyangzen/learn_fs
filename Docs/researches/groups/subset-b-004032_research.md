# subset-b-004032 Research

Grouped research for dm-vdo UDS indexer source files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.c

## Purpose
Implements the on-disk layout manager for a UDS index. It computes the fixed block layout for the superblock, configuration block, volume region, alternating save regions, and seal block; creates new layouts; validates existing layouts; and saves or loads volatile index state through `index_save_layout` slots.

## Important APIs, Types, And Functions
The file defines private layout metadata structures: `region_header`, `layout_region`, `region_table`, `super_block_data`, `index_save_layout`, `sub_index_layout`, `index_layout`, and `save_layout_sizes`. Public entry points are `uds_compute_index_size()`, `uds_make_index_layout()`, `uds_free_index_layout()`, `uds_replace_index_layout_storage()`, `uds_load_index_state()`, `uds_save_index_state()`, `uds_discard_open_chapter()`, `uds_open_volume_bufio()`, and `uds_get_volume_nonce()`.

Key helpers include `compute_sizes()`, `initialize_layout()`, `create_index_layout()`, `save_layout()`, `load_index_layout()`, `find_latest_uds_index_save_slot()`, `setup_uds_index_save_slot()`, `load_super_block()`, `reconstitute_layout()`, `load_index_save()`, and `verify_uds_index_config()`. Nonces are generated with MurmurHash3-derived `generate_primary_nonce()` and `generate_secondary_nonce()`.

## Control Flow
Creation starts from `uds_make_index_layout(config, true, ...)`, builds an `io_factory`, checks backing-device capacity, computes region sizes, allocates save-slot metadata, writes empty save headers, writes configuration contents, and writes the superblock layout header. Loading follows `uds_make_index_layout(config, false, ...)`, reads the superblock, validates version/magic/nonce/region positions, validates saved configuration against the requested configuration, and loads each save slot header.

State load chooses the latest valid save slot by timestamp and nonce, restores index chapter counters, loads the saved open chapter, opens per-zone volume-index readers, restores the volume index, then reads the index page map. State save chooses the oldest save slot, invalidates it first, instantiates a fresh save layout with timestamp and nonce, writes open-chapter data, volume-index zones, and page-map data, then writes the save header last so incomplete saves are not selected later.

## State And Persistence
The storage format is block-aligned at 4 KiB. There are two alternating save regions so a previous clean save survives a failed newer save. Superblock versions 3 and 7 are accepted, versions 4 through 6 are explicitly rejected, and converted version 7 layouts carry `volume_offset` and `start_offset`. Save validity depends on nonzero zone count, nonzero timestamp, and a nonce derived from the volume nonce and save offset. `uds_discard_open_chapter()` zeroes the saved open-chapter block to force rebuild after a new chapter has been committed.

## Dependencies And Integration Points
Depends on `config`, `open-chapter`, `volume-index`, `index-page-map`, `io-factory`, `numeric` encoding helpers, `murmurhash3`, allocation helpers, logging, and time/random APIs. It integrates upward with `index.c` during `uds_make_index()`, `uds_save_index()`, and rebuild/no-rebuild open modes, and downward with dm-bufio through `io-factory`.

## Risks
Region offset arithmetic is correctness-critical, especially converted layouts using start and volume offsets. Save-slot invalidation-before-write protects against torn saves, but any future change that writes the header before all payloads would corrupt clean-load detection. Version and payload-size checks are strict; changing serialized structures requires explicit compatibility handling. The code allocates per-zone reader/writer arrays sized by `MAX_ZONES`, so geometry and zone-count validation elsewhere must remain aligned.

## Test Signals
Useful tests include create/load/no-rebuild/rebuild open paths, simulated interrupted saves, corrupted magic/version/nonce/region tables, converted version 7 layouts, backing device too small, storage replacement followed by save, and round trips that verify open chapter, page map, and volume index restore to the same chapter counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.h

## Purpose
Declares the opaque layout API used by the UDS index to manage persistent storage format, saved state, volume-region dm-bufio access, and backing-device replacement.

## Important APIs, Types, And Functions
The header forward-declares `struct index_layout` and exposes `uds_make_index_layout()`, `uds_free_index_layout()`, `uds_replace_index_layout_storage()`, `uds_load_index_state()`, `uds_save_index_state()`, `uds_discard_open_chapter()`, `uds_get_volume_nonce()`, and `uds_open_volume_bufio()`. `uds_make_index_layout()` takes a `struct uds_configuration`, a `new_layout` flag, and returns an initialized layout; `uds_open_volume_bufio()` returns a dm-bufio client positioned on the volume region.

## Control Flow
The header forms the boundary between high-level index lifecycle code and on-disk layout implementation. `index.c` calls it during index construction, save, load, recovery, storage replacement, and chapter-writer cleanup of saved open-chapter data. `volume.c` can use `uds_open_volume_bufio()` to access only the volume region without knowing the whole on-disk map.

## State And Persistence
The header intentionally hides serialized metadata and save-slot details. Callers only see the ability to create/load a layout, save/load index state, discard a saved open chapter, and fetch the volume nonce used to bind lower-level persisted structures to the layout.

## Dependencies And Integration Points
Includes `config.h`, `indexer.h`, and `io-factory.h`, so it connects configuration, public UDS types, block devices, and dm-bufio. It is included by `index.h`, `index.c`, and storage-facing volume code.

## Risks
Because the type is opaque, callers must respect API sequencing: create layout before volume/index construction, do not use after free, and drain requests before save. `uds_replace_index_layout_storage()` assumes the replacement device is compatible with the existing layout, so session-level checks and block-device management matter.

## Test Signals
Compile coverage should catch signature drift. Integration tests should verify callers can create, load, save, replace storage, open the volume bufio client, and recover the volume nonce without depending on private layout fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.c

## Purpose
Implements the compact page map that records, for each chapter and index page except the final one, the highest delta-list number stored on that page. This lets volume lookups read only the relevant chapter-index page for a record name.

## Important APIs, Types, And Functions
Public functions are `uds_make_index_page_map()`, `uds_free_index_page_map()`, `uds_update_index_page_map()`, `uds_find_index_page_number()`, `uds_get_list_number_bounds()`, `uds_compute_index_page_map_save_size()`, `uds_write_index_page_map()`, and `uds_read_index_page_map()`. The serialized format begins with magic `ALBIPM02`, then `last_update`, then little-endian u16 entries.

## Control Flow
Allocation sizes the entries array as `chapters_per_volume * (index_pages_per_chapter - 1)`. During chapter write or rebuild, `uds_update_index_page_map()` records the last delta list for each non-final index page and updates `last_update` to the virtual chapter number. Lookup hashes a record name to a chapter delta list, scans that chapter's per-page bounds, and returns the first page whose high list is greater than or equal to the desired list.

## State And Persistence
State is an in-memory u16 array plus `last_update`. The last page of each chapter is omitted because its upper bound is always `delta_lists_per_chapter - 1`. Save/load are whole-map operations through buffered writer/reader objects and validate only the magic before decoding the rest.

## Dependencies And Integration Points
Uses geometry fields, hash helpers, numeric encoding, memory allocation, and buffered I/O. `index-layout.c` saves and restores it in an index save region; `index.c` rebuilds it from on-disk chapter index pages during recovery; `sparse-cache.c` and volume lookup code use it to select cached index pages.

## Risks
The implementation assumes u16 is sufficient for each highest delta-list value, so geometry must keep `delta_lists_per_chapter` within that bound. A stale or corrupt map can send lookups to the wrong index page and create false misses. Load validates the magic but not monotonicity of entries, so recovery/rebuild tests should catch malformed page boundaries.

## Test Signals
Test map allocation for dense and sparse geometries, update behavior for final and non-final pages, lookup boundaries around each page transition, save/load round trips, bad magic handling, and rebuild comparison against actual chapter-index page `lowest_list_number` and `highest_list_number`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.h

## Purpose
Declares the page-map structure and API used to map record-name delta lists to physical chapter-index pages.

## Important APIs, Types, And Functions
`struct index_page_map` contains a geometry pointer, `last_update`, `entries_per_chapter`, and the u16 `entries` array. The header exposes allocation/free, read/write, update, lookup, list-bound calculation, and saved-size computation functions.

## Control Flow
Writers call `uds_update_index_page_map()` as chapter index pages are produced or replayed. Readers call `uds_find_index_page_number()` to decide which index page to fetch, and `uds_get_list_number_bounds()` to interpret the list span represented by a page.

## State And Persistence
The header describes an in-memory object backed by a serialized save-region payload. The `last_update` field is used by rebuild and logging paths to detect whether replay changed the map.

## Dependencies And Integration Points
Includes `geometry.h` and `io-factory.h`, tying it to fixed index geometry and buffered save/load streams. It is shared by volume lookup, sparse-cache search, index rebuild, and layout save/restore code.

## Risks
Callers must pass chapter numbers in physical chapter space for lookups and updates where required. Confusing virtual and physical chapter numbers can index the wrong entries. The map depends on geometry immutability across save/load.

## Test Signals
Compile tests should catch API changes; functional tests should validate physical chapter indexing, final-page bounds, and persistence through `index-layout` saves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-page-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.c

## Purpose
Implements the public UDS session lifecycle and request admission layer. A session owns at most one open index, tracks state flags, drains in-flight requests for suspend/close/save, queues callbacks, and converts internal UDS status codes to errno values for callers.

## Important APIs, Types, And Functions
Public functions are `uds_create_index_session()`, `uds_destroy_index_session()`, `uds_open_index()`, `uds_close_index()`, `uds_suspend_index_session()`, `uds_resume_index_session()`, `uds_flush_index_session()`, `uds_get_index_session_stats()`, `uds_launch_request()`, and `uds_wait_cond()`. Internal state flags include loading, loaded, disabled, suspended, waiting, closing, and destroying. `index_load_context` coordinates pausable rebuilds with statuses `INDEX_OPENING`, `INDEX_READY`, `INDEX_SUSPENDING`, `INDEX_SUSPENDED`, and `INDEX_FREEING`.

## Control Flow
Opening validates parameters, marks the session loading, copies parameters, creates a configuration, and calls `uds_make_index()`. Requests validate callback and request type, reset internal request fields, acquire a request reference only if the session is exactly loaded, and enqueue into the index. Index completion enters `enter_callback_stage()`, which disables the session on any request error, then sends the request to the callback queue. Callback processing updates stats, converts status, invokes the client callback, and releases the request reference.

Suspend waits for competing state changes, either pauses a rebuild through `load_context` or drains active requests and optionally saves the index, then marks the session suspended. Resume can replace the block device and resume paused replay. Close and destroy drain requests, save/free the index when appropriate, and finish queues.

## State And Persistence
Session state is protected by `request_mutex`; `request_count` tracks asynchronous requests and state transitions waiting for callbacks. Statistics are updated with `READ_ONCE`/`WRITE_ONCE` style counters. Persistence occurs indirectly through `uds_save_index()` during suspend, close, or destroy unless the index is already suspended.

## Dependencies And Integration Points
Integrates with `index.c` through `uds_make_index()`, `uds_save_index()`, `uds_free_index()`, `uds_enqueue_request()`, and `uds_wait_for_idle_index()`. It depends on request queues for callback serialization, configuration creation, logging, allocation, and kernel wait queues.

## Risks
Any request error permanently disables the open index until close, so errors from lower layers have broad operational impact. State flag combinations are subtle during loading plus suspended rebuild; missed broadcasts can hang suspend/resume/destroy. `get_index_session()` increments `request_count` before state validation and must release it on every rejection path. `uds_wait_cond()` uses `TASK_IDLE`, so all callers must hold the paired mutex and recheck conditions.

## Test Signals
Tests should cover request validation, callback completion, disable-on-error, suspend with and without save, suspend/resume during rebuild, storage replacement on resume, close while busy, destroy during suspended load, stats aggregation, and rejection of launches while suspended/loading/disabled/no-index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.h

## Purpose
Defines the private session data structures used by the public UDS API implementation and index rebuild suspend/resume coordination.

## Important APIs, Types, And Functions
`struct session_stats` stores request outcome counters by operation and location. `enum index_suspend_status` describes load/rebuild state. `struct index_load_context` contains a mutex, condition variable, and suspend status. `struct uds_index_session` stores the current state flags, open `uds_index`, callback queue, copied parameters, load context, request mutex/condition, request count, and stats.

## Control Flow
The implementation in `index-session.c` mutates these fields during open, request launch, callback completion, suspend, resume, close, destroy, and stats collection. `index.c` observes `index_load_context` while replaying chapters during rebuild so suspend and destroy can pause or abort long recovery.

## State And Persistence
The header does not serialize anything directly. It defines volatile session state that gates access to a persistent index and determines when save operations are allowed to run.

## Dependencies And Integration Points
Includes Linux atomic/cache headers, thread utilities, configuration, and public UDS API declarations. The cache-line alignment on `session_stats` reduces false sharing for frequently updated counters.

## Risks
The state integer is intentionally opaque bit state from the C file; adding fields or changing ownership requires preserving locking rules around `request_mutex` and `load_context.mutex`. Stats are not atomic counters, so readers rely on relaxed snapshot semantics rather than exact concurrent totals.

## Test Signals
Compile-time checks should catch structure-user drift. Runtime signals are correct state transitions under concurrent request launch, suspend/resume, close, and rebuild interruption, plus stats snapshots that do not crash or regress under concurrent callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.c

## Purpose
Implements the core UDS index engine. It dispatches requests to per-zone workers, coordinates sparse-cache barrier messages, manages open chapter rollover, writes closed chapters through a writer thread, loads or rebuilds indexes, and exposes save/free/stats/enqueue operations to the session layer.

## Important APIs, Types, And Functions
Public functions are `uds_make_index()`, `uds_free_index()`, `uds_wait_for_idle_index()`, `uds_save_index()`, `uds_replace_index_storage()`, `uds_get_index_stats()`, and `uds_enqueue_request()`. Private `struct chapter_writer` owns the writer thread, condition variable, per-zone completed chapter pointers, an open-chapter index, and collated record buffer. `struct index_zone` and `struct uds_index` are declared in `index.h`.

Core helpers include `triage_request()`, `dispatch_index_request()`, `execute_zone_request()`, `search_index_zone()`, `remove_from_index_zone()`, `open_next_chapter()`, `close_chapters()`, `load_index()`, `rebuild_index()`, `replay_volume()`, `replay_chapter()`, and `replay_record()`.

## Control Flow
Requests enter at `uds_enqueue_request()`. Sparse multi-zone indexes use a triage queue to detect when a sampled record points to a sparse chapter that needs caching; triage enqueues one barrier message per zone before forwarding the original request. Zone workers handle control messages or normal requests. Normal search/update/delete first uses the volume index to locate a likely chapter, resolves the record in the open chapter, writing chapter, dense volume pages, or sparse cache, then updates/removes volume-index entries and the open chapter as request type requires.

When an open chapter zone fills or receives a chapter-closed announcement, `open_next_chapter()` swaps active and writing chapters, advances per-zone chapter counters, announces closure to other zones, and hands the old chapter to the writer. The writer waits until all zones have submitted the same chapter, optionally discards a saved open chapter, collates and writes the chapter to the volume, advances global chapter counters, and wakes waiting zones.

Opening creates layout, volume, zones, volume index, queues, and writer thread. Loading restores saved state; failed loads under `UDS_LOAD` trigger rebuild by scanning volume chapter boundaries, replaying record pages, and rebuilding the page map.

## State And Persistence
The index tracks global and per-zone oldest/newest virtual chapters, `need_to_save`, `has_saved_open_chapter`, `last_save`, and `prev_save`. Clean saves are delegated to `index-layout.c`; dirty state begins on request execution. Rebuild reconstructs volatile volume-index/page-map state from persistent volume chapters. The saved open chapter is invalidated after the first post-load chapter write so future unclean shutdowns require recovery.

## Dependencies And Integration Points
Depends on `index-layout`, `volume`, `volume-index`, `open-chapter`, `sparse-cache`, request queues, hash utilities, allocation, and logging. It is called by `index-session.c` and calls into storage-facing volume APIs for cached index/record pages, chapter writes, rebuild boundaries, prefetching, and storage replacement.

## Risks
The most delicate area is coordination across zone workers and the writer thread: zones may not get more than one chapter ahead, and all zones must participate in sparse-cache barriers. Requeued requests cache location state that may become stale and must be invalidated when chapter advice changes. Volume-index collisions and chapter-index overflow are intentionally lossy in some cases, so false misses or dropped dedupe opportunities are expected but must not corrupt metadata. Save requires requests to be drained; calling it with active mutation would persist inconsistent open-chapter and volume-index state.

## Test Signals
Exercise all request types, open-chapter hits, writing-chapter hits, dense lookups, sparse lookups, collision and overflow handling, chapter rollover with multiple zones, sparse barrier ordering, rebuild from unclean shutdown, no-rebuild failure on dirty state, save/load round trips, stats memory accounting, and storage replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.h

## Purpose
Defines the internal high-level UDS index structures and functions shared by session, layout, sparse cache, open chapter, volume, and volume-index code.

## Important APIs, Types, And Functions
`index_callback_fn` is the callback used by the index to return completed requests to the session layer. `struct index_zone` stores per-zone open and writing chapters plus oldest/newest virtual chapter counters. `struct uds_index` stores persistent layout, volume index, volume object, zones, global chapter counters, save flags, writer, callback, triage queue, and flexible array of zone queues. `enum request_stage` selects triage, index, or message queueing.

The header exposes `uds_make_index()`, `uds_save_index()`, `uds_free_index()`, `uds_replace_index_storage()`, `uds_get_index_stats()`, `uds_enqueue_request()`, and `uds_wait_for_idle_index()`.

## Control Flow
Session code creates the index with a load context and callback, launches requests by enqueueing them, drains with `uds_wait_for_idle_index()`, saves through `uds_save_index()`, and frees through `uds_free_index()`. Sparse-cache code receives `struct index_zone` pointers so it can coordinate cache updates per zone.

## State And Persistence
The header declares both mutable runtime state and fields that mirror persistent chapter state (`oldest_virtual_chapter`, `newest_virtual_chapter`, `last_save`, saved-open-chapter flag). Actual serialization is implemented by `index-layout.c`.

## Dependencies And Integration Points
Includes layout, session, open chapter, volume, and volume-index headers. This makes it a central internal integration header rather than a public client API.

## Risks
Because the flexible array of queue pointers is counted by `zone_count`, allocation must use `vdo_allocate_extended()` consistently. Direct field access by multiple files makes invariants about chapter counters and save flags easy to break if future code bypasses existing helper paths.

## Test Signals
Build coverage should catch structural changes. Runtime tests should validate zone-count allocation, queue dispatch by stage, save/free ordering, and interactions with sparse-cache updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/indexer.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/indexer.h

## Purpose
Defines the public UDS API: request types, open modes, parameters, record name/data formats, index statistics, request structure, session operations, and condition-variable helpers.

## Important APIs, Types, And Functions
Important enums are `uds_request_type`, `uds_open_index_type`, `uds_index_region`, and `uds_zone_message_type`. Important data structures are `uds_record_name`, `uds_record_data`, `uds_volume_record`, `uds_parameters`, `uds_index_stats`, `uds_zone_message`, `uds_request`, and `cond_var`. Public functions include `uds_compute_index_size()`, session create/open/suspend/resume/flush/close/destroy/stat APIs, and `uds_launch_request()`.

`struct uds_request` separates required client inputs, callback outputs, and an internal `struct_group` used by queues, index routing, message handling, and location tracking. Records use 16-byte names and 16-byte metadata.

## Control Flow
Clients create a session, open or create an index with `uds_parameters`, initialize a request, and call `uds_launch_request()`. Completion is asynchronous through the request callback. Session control APIs gate new requests and can save, suspend, resume, flush, or close the index.

## State And Persistence
The header describes client-visible state and statistics rather than persistence mechanics. `uds_parameters` carry block device, size, offset, memory size, sparse flag, nonce, zone count, and read-thread count, which determine the persistent layout and geometry produced by implementation files.

## Dependencies And Integration Points
Includes kernel mutex/wait/types headers and `funnel-queue.h`. It is the top-level interface consumed by dm-vdo code outside the indexer and by all internal indexer modules.

## Risks
Clients must not mutate internal request fields and must keep request storage valid until callback. Invalid names are not structurally rejected, but poor hash distribution can reduce capacity. API state rules matter: operations during suspended/loading/disabled states fail with busy/no-index/disabled errors.

## Test Signals
API tests should verify request type behavior, callback reuse safety, invalid argument handling, index size calculation, stats fields, sparse/dense configurations, and lifecycle operations under concurrent clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/indexer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.c

## Purpose
Provides low-level block-device I/O helpers for the indexer. It wraps dm-bufio clients in an `io_factory`, plus bounded sequential buffered readers and writers for contiguous index regions.

## Important APIs, Types, And Functions
Private types are `io_factory`, `buffered_reader`, and `buffered_writer`. Public functions include `uds_make_io_factory()`, `uds_replace_storage()`, `uds_put_io_factory()`, `uds_get_writable_size()`, `uds_make_bufio()`, `uds_make_buffered_reader()`, `uds_free_buffered_reader()`, `uds_read_from_buffered_reader()`, `uds_verify_buffered_data()`, `uds_make_buffered_writer()`, `uds_free_buffered_writer()`, `uds_write_to_buffered_writer()`, and `uds_flush_buffered_writer()`.

## Control Flow
The factory stores a block device and reference count. Readers create a dm-bufio client with a sector offset, prefetch up to four blocks, and sequentially copy bytes from 4 KiB buffers, refusing reads beyond their block limit. Writers create new dm-bufio buffers, append data or zero-fill when data is NULL, mark full buffers dirty, release them, and write dirty buffers when freed.

## State And Persistence
I/O state is bounded by `(offset, block_count)` region windows. Writers zero-fill unwritten bytes in the current block before marking it dirty, which keeps serialized regions deterministic and avoids leaving stale data in partial blocks. `uds_replace_storage()` swaps the backing block device pointer for future clients.

## Dependencies And Integration Points
Depends on Linux block-device and dm-bufio APIs, atomic reference counting, allocation, logging, and numeric constants. It is used by layout, volume, page-map, open-chapter, and volume-index persistence code.

## Risks
The factory does not own an opened reference to the block device in this file; callers must manage block-device lifetime. Existing reader/writer clients keep their dm-bufio clients, so storage replacement should happen only when no old clients are active. `uds_verify_buffered_data()` restores reader position on mismatch and depends on valid `end/start` state; misuse before any positioning could be fragile.

## Test Signals
Tests should cover boundary reads/writes, out-of-range errors, partial block zero-fill, verify success and failure with position restoration, dirty-buffer sync failures, prefetch behavior across sequential blocks, and storage replacement followed by new reader/writer creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.h

## Purpose
Declares the storage I/O abstraction used by UDS layout and volume code to access contiguous regions of a block device.

## Important APIs, Types, And Functions
Defines `UDS_BLOCK_SIZE` as 4096 and `SECTORS_PER_BLOCK`. Forward-declares `buffered_reader`, `buffered_writer`, and `io_factory`. Exposes factory creation/replacement/release, writable-size query, raw dm-bufio client creation, sequential reader creation/read/verify/free, and sequential writer creation/write/flush/free.

## Control Flow
Callers create a factory from a block device, then create dm-bufio clients or bounded buffered readers/writers for specific regions. Writers append serialized payloads and flush; readers consume serialized payloads and can verify magic bytes.

## State And Persistence
The header hides all mutable I/O cursor state. Persistence semantics are block-sized and rely on dm-bufio flushing in the implementation.

## Dependencies And Integration Points
Includes `linux/dm-bufio.h` and therefore ties indexer persistence to the device-mapper buffer I/O layer. It is included by layout, page-map, open-chapter, volume-index, and volume modules.

## Risks
All offsets are in UDS blocks, not bytes or sectors, except where callers pass higher-level configuration offsets that have already been normalized. Mixing units can place readers/writers on wrong regions.

## Test Signals
Compile coverage and integration tests should verify offset handling, block-size assumptions, and reader/writer round trips for every serialized structure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.c

## Purpose
Implements per-zone in-memory open chapters, which hold the newest records before they are committed to the volume. It supports lookup, insert/update, delete marking, close-to-volume collation, and save/load of live open-chapter records.

## Important APIs, Types, And Functions
Public functions are `uds_make_open_chapter()`, `uds_reset_open_chapter()`, `uds_search_open_chapter()`, `uds_put_open_chapter()`, `uds_remove_from_open_chapter()`, `uds_free_open_chapter()`, `uds_close_open_chapter()`, `uds_save_open_chapter()`, `uds_load_open_chapter()`, and `uds_compute_saved_open_chapter_size()`. Private helpers include `probe_chapter_slots()`, `fill_delta_chapter_index()`, and `load_version20()`. The saved format uses magic `ALBOC` and version `02.00`.

## Control Flow
Allocation divides `records_per_chapter` by zone count for per-zone capacity and creates a power-of-two hash table at twice that capacity. Searches and puts use quadratic probing from a name-derived hash slot. Insert updates an existing record or appends a new 1-based record number. Delete marks a slot indexed by record number rather than removing hash-chain entries.

Closing empties an open-chapter index for the virtual chapter, interleaves records from zones to preserve temporal locality, replaces deleted or unused slots with a valid fill record so record pages are full, populates the chapter delta index, and writes the chapter to the volume. Save writes non-deleted records interleaved across zones. Load verifies magic/version, reads records, assigns each to the current zone mapping, and discards overflow records if a new zone distribution is too small.

## State And Persistence
Runtime state includes `size`, `deletions`, 1-based record array, and hash slots with record number and deleted flag. Saved state contains only live records, not deleted tombstones or hash slots; load rebuilds the open chapter from records. The code deliberately prevents loaded zones from filling completely so rollover remains possible.

## Dependencies And Integration Points
Depends on geometry, hash utilities, chapter-index construction, volume writes, buffered I/O, numeric helpers, allocation, and logging. It is used by `index.c` zone processing and `index-layout.c` save/load.

## Risks
`fill_delta_chapter_index()` assumes at least one filled zone can provide a non-deleted fill record when replacing holes; chapter close should only be triggered by a filled zone. Deleted flag storage overlays the slot array and uses record-number indexing, so capacity/slot-count relationships are critical. Save/load with changed zone counts can drop newest records for overloaded zones, reducing dedupe history after reconfiguration.

## Test Signals
Test probing collision chains, update-in-place, delete and reinsert behavior, capacity rollover, close with deleted records, delta-index overflow warnings, save/load with same and different zone counts, invalid magic/version, and full-page volume writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.h

## Purpose
Declares the open-chapter data structures and operations used by zone workers and persistence code.

## Important APIs, Types, And Functions
Defines `OPEN_CHAPTER_RECORD_NUMBER_BITS`, `struct open_chapter_zone_slot`, and `struct open_chapter_zone`. The zone stores capacity, current size, deletion count, record array, slot count, and flexible hash slot array. The API exposes allocation, reset, search, put, remove, free, close-to-volume, save, load, and saved-size computation.

## Control Flow
Index zones use search/put/remove while processing requests. The chapter writer uses `uds_close_open_chapter()` when all zones have closed a chapter. Layout save/load uses the serialization helpers.

## State And Persistence
The header makes clear that record number 0 means unused and records are 1-based. Deleted records remain in memory until reset or save/load, where only live records are serialized.

## Dependencies And Integration Points
Includes chapter-index, geometry, index, and volume headers. This links request processing, chapter-index generation, and volume writes.

## Risks
Bitfield width limits record numbers to `OPEN_CHAPTER_RECORD_NUMBER_BITS`; geometry must not allow per-zone capacities beyond that. Direct users must not assume hash slots and record arrays have the same semantic index except for the intentional deleted flag overlay.

## Test Signals
Build and unit tests should exercise slot bitfield limits, per-zone capacity calculation, and close/save/load integration with volume geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/open-chapter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.c

## Purpose
Implements a reusable in-place American Flag radix sorter for arrays of pointers to fixed-length byte keys. It is used where deterministic bytewise ordering of record names or index keys is needed without moving the key storage itself.

## Important APIs, Types, And Functions
Public functions are `uds_make_radix_sorter()`, `uds_free_radix_sorter()`, and `uds_radix_sort()`. Private types are `sort_key_t`, `histogram`, `task`, and `radix_sorter`. Important helpers are `measure_bins()`, `push_bins()`, `insertion_sort()`, `insert_key()`, `swap_keys()`, and `push_task()`.

## Control Flow
`uds_make_radix_sorter(count, ...)` allocates one object with a task stack sized roughly by `count / INSERTION_SORT_THRESHOLD`. `uds_radix_sort()` handles empty/zero-length/small cases, then manually processes tasks from a stack. For each task it counts byte frequencies at the current offset, computes pile endpoints, pushes large piles back onto the stack and small piles onto an insertion-sort list, performs in-place pile swaps until all bins are positioned, clears reused histogram state as it goes, and insertion-sorts small piles.

## State And Persistence
There is no persistent state. The sorter holds reusable scratch state (`histogram`, pile pointers, insertion task list, and stack) sized for a maximum count. Input keys are immutable byte arrays; the array of key pointers is reordered. The algorithm is unstable.

## Dependencies And Integration Points
Depends on allocation and string/memcmp utilities. It is a general helper for indexer components that need sorted key pointers, likely chapter-index or volume code outside this subset.

## Risks
The implementation relies on the histogram being zeroed by prior processing rather than clearing it before every bin measurement. Any early exit path must clear it, and any modification to bin loops must preserve that invariant. The sorter rejects counts greater than its configured capacity but only after small-count fast path. Stack sizing is algorithm-specific; unexpected push growth returns `UDS_BAD_STATE`.

## Test Signals
Test zero count, zero length, small insertion-sort paths, already sorted/reverse/random keys, duplicate keys, keys with long shared prefixes, all 256 byte values, count greater than sorter capacity, and reuse of a sorter across multiple sorts after an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.h

## Purpose
Declares the reusable radix sorter API for byte-array key pointers.

## Important APIs, Types, And Functions
Forward-declares `struct radix_sorter` and exposes `uds_make_radix_sorter()`, `uds_free_radix_sorter()`, and `uds_radix_sort()`. The sort takes `const unsigned char *keys[]`, a count, and fixed key length.

## Control Flow
Callers allocate a sorter for a maximum count, call `uds_radix_sort()` for one or more arrays within that capacity, then free the sorter. The implementation chooses insertion sort for small piles.

## State And Persistence
The sorter is scratch memory only and has no persistent format. Sorting mutates only the pointer array, not the key bytes.

## Dependencies And Integration Points
No indexer-specific includes beyond the API itself; it is a utility module available to other indexer code.

## Risks
The algorithm is explicitly unstable, so callers must not rely on relative ordering of equal keys. The sorter capacity must be at least the largest count passed to sort.

## Test Signals
Compile coverage plus sorting tests for fixed-length names, duplicate keys, and sorter reuse are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.c

## Purpose
Implements the sparse chapter-index cache used by sparse UDS indexes after dense/open/writing chapter lookups fail. It caches complete chapter indexes, maintains per-zone LRU search lists, and uses barrier coordination so cache membership changes are lock-free for normal reads.

## Important APIs, Types, And Functions
Public functions are `uds_make_sparse_cache()`, `uds_free_sparse_cache()`, `uds_sparse_cache_contains()`, `uds_update_sparse_cache()`, `uds_invalidate_sparse_cache()`, and `uds_search_sparse_cache()`. Private types include `cached_chapter_index`, `cached_index_counters`, `search_list`, `threads_barrier`, and `sparse_cache`.

Important helpers are `enter_threads_barrier()`, `initialize_cached_chapter_index()`, `make_search_list()`, `set_newest_entry()`, `purge_search_list()`, `cache_chapter_index()`, `copy_search_list()`, `should_skip_chapter()`, and `search_cached_chapter_index()`.

## Control Flow
Normal membership checks linearly scan the calling zone's search list up to `first_dead_entry`, update that zone's LRU order, and only zone zero updates hit/miss scoring. Cache update is called once by every zone for the same virtual chapter. All zones enter a begin barrier; zone zero purges dead/skipped entries, moves an eviction candidate to the front, reads the requested chapter index from the volume if still valid, and copies its search list to all other zones; all zones then leave through an end barrier.

Search scans active cached chapters unless a specific virtual chapter is requested. It skips dead, expired, or heuristic-skipped chapters, finds the right index page through the page map, searches that delta index page, promotes hits in the local LRU list, and records zone-zero hit/miss scores. Many misses set `skip_search` to avoid repeated full-cache scans until a targeted hook hit clears it.

## State And Persistence
The cache is volatile. Each cached entry owns dm-bufio page buffers and decoded `delta_index_page` arrays. `virtual_chapter == NO_CHAPTER` is the sole membership-dead marker. Search lists are per-zone and cache-line aligned; cache entry counters are also separated to reduce false sharing. No read locks are taken outside coordinated update barriers.

## Dependencies And Integration Points
Depends on geometry, chapter-index search, volume chapter-index reads, index zones, page maps, dm-bufio, semaphores, allocation, logging, and assertions. `index.c` creates sparse barrier messages through triage and invokes updates from zone workers.

## Risks
Correctness relies on every zone reaching `uds_update_sparse_cache()` exactly once for the same chapter; missing or duplicated barrier messages can deadlock or diverge cache membership. `uds_sparse_cache_contains()` must remain invariant between updates even for expired or skipped chapters. Zone zero is the only writer inside the critical section, so any future mutation outside that path risks races with lock-free readers. `__down()` loops on interrupted semaphore waits, so deadlocks can consume time even if signals arrive.

## Test Signals
Test single-zone simulated updates, multi-zone barrier ordering, cache hit/miss search, LRU promotion, eviction of dead entries before live entries, skip threshold behavior, expired chapter handling, invalidate/free releasing dm-bufio buffers, and fault injection for volume chapter-index read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.h

## Purpose
Declares the sparse-cache API and documents its concurrency contract for lock-free reads with barrier-coordinated membership updates.

## Important APIs, Types, And Functions
Forward-declares `struct index_zone` and `struct sparse_cache`. Exposes creation/free, membership query, coordinated update, invalidate, and search functions. Search returns a virtual chapter and record page for a record name.

## Control Flow
Index triage decides when a sparse chapter might need caching, then zone workers call `uds_update_sparse_cache()`. Normal request processing calls `uds_sparse_cache_contains()` for a known chapter or `uds_search_sparse_cache()` after volume-index miss.

## State And Persistence
The header emphasizes that cache membership must not change between coordinated update calls and that all zones must observe identical membership. It contains no persistent format; sparse chapter pages remain stored in the volume and are cached in memory.

## Dependencies And Integration Points
Includes geometry and public indexer types. It integrates directly with `index.c` zone workers and volume/page-map code through the implementation.

## Risks
Callers must obey the "all zones, same chapter" update rule. Membership checks are not a substitute for searchability: expired and skip-search chapters may still be members but be skipped by full-cache search.

## Test Signals
Concurrency tests should validate no read locks are needed between barriers, cache membership consistency across zones, and correct search results when chapters are skipped or expired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/sparse-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.c

## Purpose
Implements the primary in-memory UDS volume index, mapping record names to virtual chapters. It uses delta indexes to store compact chapter hints, splits sparse indexes into hook and non-hook subindexes, lazily flushes invalid entries, persists per-zone index streams, and provides record-level mutation operations.

## Important APIs, Types, And Functions
Public functions include `uds_make_volume_index()`, `uds_free_volume_index()`, `uds_compute_volume_index_save_blocks()`, `uds_get_volume_index_zone()`, `uds_is_volume_index_sample()`, `uds_lookup_volume_index_name()`, `uds_get_volume_index_record()`, `uds_put_volume_index_record()`, `uds_remove_volume_index_record()`, `uds_set_volume_index_record_chapter()`, `uds_set_volume_index_open_chapter()`, `uds_set_volume_index_zone_open_chapter()`, `uds_load_volume_index()`, `uds_save_volume_index()`, and `uds_get_volume_index_stats()`.

Private structures include `sub_index_parameters`, `split_config`, `chapter_range`, serialized `sub_index_data` (`MI5-0005`), and serialized `volume_index_data` (`MI6-0001`). Core helpers compute subindex sizing, split sparse configurations, extract address/list bits from names, convert virtual/index chapter numbers, lazily flush invalid delta entries, restore/save subindexes, and initialize delta indexes.

## Control Flow
Configuration computes delta-list count, address bits, chapter bits, expected memory, and target free space. Dense indexes initialize only `vi_non_hook`. Sparse indexes allocate per-zone hook mutexes, split configuration so sampled hook records are kept for sparse chapters and non-hook records cover dense chapters, then initialize both subindexes with separate delta-index tags.

Record lookup picks the hook subindex for sampled names and non-hook otherwise, derives list and zone from record-name bits, lazily flushes old entries if the delta list has not caught up to the zone's low virtual chapter, and returns a `volume_index_record` that can be mutated. Hook lookups and mutations use a per-zone mutex because sparse-cache triage can perform concurrent read-only hook lookups while normal request processing lazily mutates delta lists.

Saving writes optional sparse header, per-subindex headers with nonce/chapter range/list range, per-list flush chapters, delta-index data, guard lists, and flushes one writer per zone. Loading validates magic, nonce consistency, sparse sample rate consistency, restores flush ranges and delta-index streams, then checks guard lists.

## State And Persistence
Each subindex stores `flush_chapters`, per-zone low/high virtual chapter ranges, delta-index storage, nonce, bit masks, chapter/list counts, and memory accounting. Chapter numbers are stored in truncated index form and converted back to virtual form relative to each zone's low chapter. Old entries are removed lazily during list walks. Early flush can advance a zone's low chapter when delta-zone memory exceeds `max_zone_bits`, trading dedupe history for bounded memory.

## Dependencies And Integration Points
Depends on configuration, geometry, hash utilities, delta-index APIs, numeric encoding, thread/mutex utilities, logging, and allocation. `index.c` uses it for zone routing, request lookup/update/delete, chapter rollover, sparse-cache membership triage, rebuild replay, and stats. `index-layout.c` asks it for save size and delegates save/load.

## Risks
The name-bit partitioning, sparse sample-rate split, and zone mapping must remain stable across saves and reduced-volume configurations. Lazy flushing means lookups are mutating operations; missing hook mutex coverage can race with sparse-cache triage. Collision records disambiguate names only when needed, and overflow can drop entries, reducing dedupe hits. Early flush changes valid chapter ranges under memory pressure, so tests must account for controlled loss of old records.

## Test Signals
Test dense and sparse initialization, sample/non-sample routing, zone selection stability, put/get/update/remove, collision records, overflow handling, lazy flush of invalid entries, open-chapter range advancement, early flush under memory pressure, save/load with guard-list validation, bad magic/nonce/sample-rate failures, stats aggregation, and rebuild replay behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.h

## Purpose
Declares the volume-index data model and API for mapping record names to chapters, including sparse hook support, per-zone locking, record mutation handles, persistence, and statistics.

## Important APIs, Types, And Functions
Defines `NO_CHAPTER`, `struct volume_index_stats`, `struct volume_sub_index_zone`, `struct volume_sub_index`, `struct volume_index_zone`, `struct volume_index`, and `struct volume_index_record`. Public APIs cover creation/free, save-block computation, zone mapping, sparse sampling, hook lookup, record lookup/put/remove/chapter update, open-chapter advancement, save/load, and stats.

## Control Flow
Request processing obtains a `volume_index_record` for a name, checks its public fields (`virtual_chapter`, `is_collision`, `is_found`), and then calls put/remove/set-chapter as needed. Chapter rollover calls the open-chapter setters to advance valid ranges. Sparse-cache triage uses `uds_lookup_volume_index_name()` to decide whether a sampled name references a sparse chapter.

## State And Persistence
The structures expose compact delta-index state, flush watermarks, per-zone virtual chapter ranges, masks, chapter/list counts, memory sizing, sparse sample rate, and per-zone hook mutexes. Save/load are implemented in the C file but declared here for layout integration.

## Dependencies And Integration Points
Includes configuration, delta-index, public indexer types, limits, and thread utilities. It is included by `index.h`, `index.c`, `index-layout.c`, and sparse-cache control paths.

## Risks
`volume_index_record` is a live mutation cursor into the delta index; callers should not retain it across unrelated operations or after removing the record. Hook records carry a mutex pointer that the mutation helpers lock internally. `NO_CHAPTER` is `U64_MAX` and must not collide with valid virtual chapter arithmetic.

## Test Signals
Compile and functional tests should validate record cursor lifecycle, sparse hook locking paths, public field semantics after mutations, save/load declarations, and stats structure population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume-index.h -->
