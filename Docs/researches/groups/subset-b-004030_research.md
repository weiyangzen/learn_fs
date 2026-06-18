# subset-b-004030 Research

Grouped research for dm-vdo source files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.c

## Purpose
Implements VDO write deduplication coordination around content hashes and the kernel UDS index. The file is centered on per-hash-zone `hash_lock` state machines that let concurrent `data_vio` writes with the same record name share one index lookup, one verified duplicate PBN lock, and one newly written copy when no duplicate exists. Deduplication is an optimization rather than a correctness requirement, so slow or unavailable index operations are deliberately timed out and the writes continue without dedupe.

## Important APIs, Types, And Functions
The public entry points are `vdo_make_hash_zones()`, `vdo_free_hash_zones()`, `vdo_start_dedupe_index()`, `vdo_resume_hash_zones()`, `vdo_drain_hash_zones()`, `vdo_finish_dedupe_index()`, `vdo_acquire_hash_lock()`, `vdo_continue_hash_lock()`, `vdo_release_hash_lock()`, `vdo_clean_failed_hash_lock()`, `vdo_share_compressed_write_lock()`, `vdo_get_duplicate_lock()`, `vdo_select_hash_zone()`, `vdo_get_dedupe_statistics()`, `vdo_dump_hash_zones()`, `vdo_message_dedupe_index()`, and the timer-tuning setters.

`struct hash_lock` is the internal state-machine object. It tracks the record name, registered map state, duplicate PBN and `pbn_lock`, lock agent, waiter queue, holder list, advice-update flags, verification status, and reference counts. Its states are `INITIALIZING`, `QUERYING`, `WRITING`, `UPDATING`, `LOCKING`, `VERIFYING`, `DEDUPING`, `UNLOCKING`, and `BYPASSING`.

`struct hash_zone` owns the lock map, lock pool, UDS request context pool, pending and available context lists, timeout funnel queue, timer, statistics, and completion for one hash-zone thread. `struct hash_zones` owns the shared UDS index session, global dedupe/index state, action manager, ratelimiter, timeout counters, and the array of zones.

`struct dedupe_context` wraps a UDS request so the file can time out a request without reusing the caller-visible request object before the UDS callback has actually returned.

## Control Flow
New writes enter through `vdo_acquire_hash_lock()` on the selected hash-zone thread. `acquire_lock()` either creates/registers a lock from the zone pool or returns the existing lock for the record name. Hash collisions are checked by comparing block data against an existing holder; on collision the write bypasses dedupe to prevent corruption.

The common no-duplicate path is `INITIALIZING -> QUERYING -> WRITING -> BYPASSING`. `start_querying()` launches `UDS_POST` when the agent already has an allocation, or `UDS_QUERY` otherwise. `finish_querying()` decodes UDS advice with `decode_uds_advice()` and either proceeds to `start_locking()` or writes a new block with `start_writing()`. `finish_writing()` records the just-written location as the verified duplicate for any waiters, starts a UDS update if advice changed, or exits.

The duplicate path is `QUERYING -> LOCKING -> VERIFYING -> DEDUPING -> UNLOCKING`. `lock_duplicate_pbn()` runs in the physical zone, rejects write locks and exhausted increment limits, acquires or attaches to a read PBN lock, and acquires a provisional reference for previously unheld candidate blocks. `start_verifying()` reads the candidate block, optionally decompresses it, compares the full VDO block with `blocks_equal()`, and `finish_verifying()` decides whether to dedupe or treat advice as stale. In `DEDUPING`, there is no exclusive agent; the agent and waiters are launched in parallel through `launch_dedupe()`.

When the duplicate PBN has no remaining reference increments, `fork_hash_lock()` replaces the registered lock with a new one and moves the current waiter set to it. The old lock continues cleanup and loses UDS update authority; the new lock writes a fresh copy and may update advice.

UDS query timeout flow is separate. `query_index()` gets a `dedupe_context`, puts it on the pending list, starts the zone timer, and calls `uds_launch_request()`. `finish_index_operation()` either requeues the requester to the hash zone or marks a timed-out context complete for later reuse. `timeout_index_operations_callback()` moves overdue pending contexts out of the pending list, clears the `data_vio` context pointer, continues those writes without dedupe, and reports rate-limited timeout statistics.

## State And Persistence
The dedupe index is persisted by UDS in the index region configured from `volume_geometry`; this file opens, creates, closes, suspends, resumes, and queries that index through `uds_*` APIs. Hash locks, contexts, wait queues, and timers are volatile runtime state. Duplicate PBN locks and provisional references protect on-disk block lifetimes while dedupe decisions are in flight, but the lock objects themselves are not persistent.

Index state is represented as `IS_CLOSED`, `IS_CHANGING`, or `IS_OPENED`, plus target state, `create_flag`, `dedupe_flag`, and `error_flag`. `vdo_start_dedupe_index()`, `vdo_message_dedupe_index()`, resume, and drain/suspend operations manipulate these fields under `zones->lock` and launch `change_dedupe_state()` on the dedupe thread.

## Dependencies And Integration Points
This file depends on VDO's thread/completion system, `data_vio` write path, physical-zone PBN locks, slab depot reference accounting, packer/compression callbacks, int-map hash tables, wait queues, action manager, admin states, statistics, and logger/memory helpers. External integration is with the UDS indexer API: `uds_create_index_session()`, `uds_open_index()`, `uds_launch_request()`, `uds_suspend_index_session()`, `uds_resume_index_session()`, `uds_close_index()`, `uds_get_index_session_stats()`, and `uds_destroy_index_session()`.

The DM target calls this through load/resume/suspend phases and dmsetup index messages. Data path integration comes from `data-vio.c`, which selects hash zones, acquires hash locks, continues locks after write/dedupe completion, and cleans failed locks.

## Risks
The main risk is state-machine correctness across asynchronous thread transitions. Most fields are only safe on the hash-zone thread, while UDS callbacks, physical-zone callbacks, CPU callbacks, bio completions, and timer completions race through explicit state transitions. A missed context state transition could reuse a UDS request too early or leave a data_vio waiting forever.

Physical reference accounting is high risk: stale advice, compressed-block slots, PBN write locks, provisional references, and increment-limit rollover must be handled exactly or dedupe can create leaks, premature frees, or data corruption. The hash collision fallback is essential because identical record names are not sufficient proof of identical data.

Timeout tuning affects performance more than correctness. Too short an interval suppresses useful dedupe; too long an interval can stall writes behind slow UDS operations. The header declares `vdo_get_dedupe_index_timeout_count()` but this source does not define it, so builds that reference it would fail unless the prototype is stale and unused.

## Test Signals
Useful tests include concurrent identical writes, hash collision injection, stale-advice cases, compressed-write dedupe, out-of-reference rollover, UDS timeout behavior, and suspend/resume while queries are pending. Runtime signals are stable `hash_lock` pool return assertions, no stuck waiters, increasing valid/stale advice counters, bounded `dedupe_advice_timeouts`, successful `index-enable`, `index-disable`, `index-close`, and `index-create` messages, and no PBN lock/refcount assertions during stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.h

## Purpose
Declares the public interface and core shared structures for dm-vdo dedupe hash zones. It exposes just enough of `dedupe.c` for the VDO data path, target lifecycle, statistics, dump, and message handlers to create hash zones, route writes to the right zone, acquire/release hash locks, manage the UDS index, and tune index timeouts.

## Important APIs, Types, And Data
`struct dedupe_context` contains a `struct uds_request`, zone pointer, list/funnel entries, submission time, requestor `data_vio`, and atomic state. It is embedded in each `hash_zone` as a fixed-size pool of `MAXIMUM_VDO_USER_VIOS` contexts so timed-out UDS requests can remain owned by UDS until their callbacks complete.

`struct hash_zone` is intentionally visible because other VDO code needs fields such as `zone_number`, `thread_id`, and admin/completion state. It contains an `admin_state`, per-zone thread id, `int_map` from record name keys to hash locks, free lock pool, `hash_lock_statistics`, the lock array, available/pending dedupe-context lists, timeout funnel queue, timer, completion, active context count, atomic timer state, and the context pool.

`struct hash_zones` and `struct hash_lock` are opaque outside the interface except where direct zone selection is required. The main data-path functions are `vdo_select_hash_zone()`, `vdo_acquire_hash_lock()`, `vdo_continue_hash_lock()`, `vdo_release_hash_lock()`, `vdo_clean_failed_hash_lock()`, `vdo_share_compressed_write_lock()`, and `vdo_get_duplicate_lock()`.

Lifecycle and admin APIs are `vdo_make_hash_zones()`, `vdo_free_hash_zones()`, `vdo_drain_hash_zones()`, `vdo_resume_hash_zones()`, `vdo_finish_dedupe_index()`, `vdo_start_dedupe_index()`, `vdo_set_dedupe_state_normal()`, `vdo_message_dedupe_index()`, `vdo_get_dedupe_index_state_name()`, and `vdo_dump_hash_zones()`. Statistics and tuning APIs include `vdo_get_dedupe_statistics()`, `vdo_get_dedupe_index_timeout_count()`, `vdo_dedupe_index_timeout_interval`, `vdo_dedupe_index_min_timer_interval`, and their setter functions.

## Control Flow
The header divides integration into three lanes. Construction and destruction happen during VDO load/unload through `vdo_make_hash_zones()`, `vdo_finish_dedupe_index()`, and `vdo_free_hash_zones()`. Administrative state changes happen during target load/resume/suspend and dmsetup messages through the index-state APIs. Write-path operations select a zone from a UDS record name, enter the hash-zone thread, acquire or share a hash lock, and later continue or release it as the `data_vio` completes asynchronous write or dedupe work.

The exported timeout variables are module-wide settings, in milliseconds, used by `dedupe.c` to derive jiffies for timer scheduling. The setters clamp and convert these values before they are consumed by zone timers.

## State And Persistence
The header exposes volatile runtime structures only. The UDS index itself is persistent, but no on-disk format is defined here. `hash_zone` state is per-VDO runtime state and must be drained before suspend or shutdown. The `dedupe_context` pool and timer fields are transient and are meaningful only while the containing VDO is active.

## Dependencies And Integration Points
It includes Linux list/timer APIs, the UDS `indexer.h` request types, and VDO admin-state, constants, statistics, types, and wait-queue definitions. `data-vio` users depend on the lock APIs; `dm-vdo-target.c` depends on lifecycle and dmsetup message entry points; `dump.c` depends on `vdo_dump_hash_zones()`; statistics code depends on `vdo_get_dedupe_statistics()`.

## Risks
Because `struct hash_zone` is not opaque, external code can theoretically depend on internal fields and make future refactoring harder. Callers must obey the threading contract implied by the implementation: lock acquisition, continuation, and release must occur on the appropriate hash-zone thread unless the implementation explicitly launches a callback to another zone. The declared `vdo_get_dedupe_index_timeout_count()` has no matching implementation in the searched dm-vdo sources, which is a stale-API risk if future code calls it.

## Test Signals
Header-level test signals are compile coverage of all users, sparse/lockdep checks for timer/list/admin-state usage where available, and ensuring no unresolved symbol appears for declared APIs. Runtime tests should exercise lifecycle calls in the target load/resume/suspend paths and data-path lock calls under concurrent writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dedupe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dm-vdo-target.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dm-vdo-target.c

## Purpose
Implements the Linux device-mapper target named `vdo`. It parses dmsetup table lines into `device_config`, constructs or reuses a VDO instance, maps incoming bios into the VDO data path, exposes status and messages, coordinates suspend/resume/load/grow administrative phase machines, and registers/unregisters the target module.

## Important APIs, Types, And Functions
The device-mapper surface is `vdo_ctr()`, `vdo_dtr()`, `vdo_map_bio()`, `vdo_io_hints()`, `vdo_iterate_devices()`, `vdo_status()`, `vdo_message()`, `vdo_presuspend()`, `vdo_postsuspend()`, `vdo_preresume()`, and `vdo_resume()`, collected in `struct target_type vdo_target_bio`.

The table parser is built from `get_version_number()`, `parse_device_config()`, `parse_optional_arguments()`, `parse_key_value_pairs()`, `parse_thread_config_string()`, `parse_memory()`, `parse_slab_size()`, and boolean/key-value helpers. Table versions 0 through 4 are accepted; older unused fields are skipped for compatibility. Optional settings include deduplication, compression, sparse index, index memory, slab size, max discard blocks, and VDO thread counts.

Administrative flow is encoded by `enum admin_phases` and `ADMIN_PHASE_NAMES`. `perform_admin_operation()` serializes admin work with `admin->busy`, launches a `vdo_completion`, and waits for callback completion. Major phase callbacks are `pre_load_callback()`, `load_callback()`, `suspend_callback()`, `resume_callback()`, `grow_logical_callback()`, and `grow_physical_callback()`, with error handlers for load and growth.

Instance identity is managed by `struct instance_tracker` plus `allocate_instance()`, `release_instance()`, and a growable bitmap. Existing active VDOs are found by device name or backing device through the global VDO registry helpers.

## Control Flow
Construction begins in `vdo_ctr()`. If no running VDO has the DM device name, `construct_new_vdo()` allocates an instance number, parses the table, calls `vdo_make()`, and runs `PRE_LOAD` phases. Pre-load either formats a new layout by clearing layout and saving super/geometry blocks or loads existing super block data and calls `decode_vdo()`. `decode_vdo()` decodes component states, validates block map age, enables read-only handling, and constructs the recovery journal, slab depot, block map, physical zones, logical zones, and hash zones.

If a VDO with the same name already exists, `update_existing_vdo()` parses a new config and `prepare_to_modify()` validates immutable fields, prepares block-map growth, and prepares physical growth layout/slabs when allowed.

`vdo_preresume_registered()` is the main activation path. A pre-loaded VDO runs `LOAD` phases: start loading, open the recovery journal, load or repair the slab depot, mark the volume dirty, initialize block map from journal, prepare allocator, scrub unrecovered slabs, and enable compression/deduplication. Then pending logical and physical grows are applied. If the VDO is not already normal, `RESUME` phases resume dedupe, depot, journal, block map, logical zones, packer, flusher, and data_vio pool.

Suspension is split between `vdo_presuspend()` choosing saving vs no-flush suspending and `vdo_postsuspend()` running `SUSPEND` phases. These drain packer, data_vios, dedupe hash zones, flusher, logical zones, block map, recovery journal, slab depot, wait for read-only transitions, and optionally write clean component state.

Bio mapping is straightforward: flush/prefush bios go to `vdo_launch_flush()`, other bios go to the data_vio pool through `vdo_launch_bio()`. A guard rejects re-entry from a VDO-owned work queue to avoid deadlock.

## State And Persistence
Persistent state is primarily geometry and super block component data, recovery journal state, slab depot state, block map state, and layout partitions. This file drives when that state is written: initial format, load dirtying, suspend clean save, resume dirty save, and grow commits. Runtime state includes active `device_config` objects, VDO admin state, processing-message flag, instance bitmap, thread/device registration, and pending `next_layout` or block-map growth preparation.

Logical growth persists by updating `states.vdo.config.logical_blocks`, saving components, then growing the block map. Physical growth persists by copying journal and slab summary partitions to the new layout, replacing `vdo->layout`, updating physical block count and depot size, saving components, then enabling new slabs.

## Dependencies And Integration Points
This file is the integration hub for Linux device-mapper, block layer queue limits, dm-kcopyd, module parameters, VDO registries, thread registry, admin-state helpers, completion infrastructure, encodings, recovery journal, slab depot, block map, data_vio pool, flush path, dedupe, dump, repair, and message statistics.

User-visible integration includes dmsetup table syntax, `dmsetup status`, `dmsetup table`, `dmsetup message stats`, `config`, `dump`, `dump-on-shutdown`, `compression on/off`, and dedupe index messages. Kernel integration includes `dm_register_target()` in `vdo_init()` and `dm_unregister_target()` in module teardown.

## Risks
The highest risks are admin phase ordering and persistence ordering. Marking the VDO dirty/clean at the wrong time, draining components in the wrong order, or committing growth metadata before copies/slab preparation are safe can lead to recovery failures or read-only entry. Error handling intentionally enters read-only mode in many cases, so tests must verify both success and degraded paths.

Table compatibility is another risk. Version-specific argument counts and skipped legacy fields must remain synchronized with tools. Thread count validation requires logical, physical, and hash zones to be all zero or all non-zero; cache-size validation depends on logical-zone count.

Concurrent lifecycle and message handling are controlled by `admin->busy` and `processing_message`. Races around table reloads, multiple target references to one VDO, and backing-device changes are sensitive. The singleton target feature prevents multiple targets, but the code still handles multiple `device_config` references for reloads.

## Test Signals
Compile with `CONFIG_DM_VDO` and run dmsetup create/load/reload/resume/suspend/remove flows across table versions and optional arguments. Runtime signals include successful status/table/config/stats messages, correct queue limits, flush/discard behavior, no bio submission from VDO-owned queues, successful clean suspend and dirty resume, read-only transition on injected load errors, logical and physical growth across suspend/resume, and no leaked instance numbers or device references on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dm-vdo-target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.c

## Purpose
Provides diagnostic dump support for dm-vdo. It implements the `dump` dmsetup message path and shutdown dump helper, logging work queues, hash-zone/index state, data_vio pool state, VDO status, and memory usage. It also implements the data_vio pool item dumper used by the pool dump.

## Important APIs, Types, And Functions
Public functions are `vdo_dump()`, `vdo_dump_all()`, and `dump_data_vio()`. Internally, `enum dump_options` and `enum dump_option_flags` define selectable categories: queues/threads, VIO pool, and VDO status. `DEFAULT_DUMP_FLAGS` includes queues and VDO status, while options such as `viopool`, `pools`, `queues`, `threads`, `vdo`, `default`, and `all` control the exact output.

`parse_dump_options()` accepts case-insensitive option prefixes via `is_arg_string()`, accumulates flags, rejects unknown option names, and applies defaults unless an explicit option set requested `FLAG_SKIP_DEFAULT`. `do_dump()` emits the high-level dump and calls subsystem dump functions. `dump_vio_waiters()`, `encode_vio_dump_flags()`, and `dump_data_vio()` produce compact per-data_vio log lines.

## Control Flow
`dm-vdo-target.c` routes a `dmsetup message ... dump [options...]` to `vdo_dump()`. After parsing, `do_dump()` logs the trigger reason, active/max data_vio pool usage, outstanding bio count, and device name. If queue output is enabled and threads exist, each VDO work queue is dumped. Hash zones are always dumped. The data_vio pool is dumped with or without detailed pool contents depending on `FLAG_SHOW_VIO_POOL`. VDO status and memory usage are then logged.

`vdo_dump_all()` bypasses parsing and passes all flags, used for shutdown when `dump-on-shutdown` has been requested. `dump_data_vio()` is invoked as a callback from the data_vio pool dumper and logs block numbers, flush generation, current operation, completion location, compact flags, and logical-block waiters.

## State And Persistence
This file does not mutate persistent VDO state. It reads volatile runtime state: pool active counts, bio counters, thread queues, hash-zone state, data_vio fields, wait queues, and memory usage. Several dump buffers in `dump_data_vio()` are static to avoid repeated allocations during heavy logging; the code assumes only one dump runs at a time and notes that concurrent dumps would garble logs.

## Dependencies And Integration Points
It depends on VDO logging, memory accounting, string helpers, constants, data_vio, dedupe, funnel work queues, I/O submitter, types, and VDO status helpers. It integrates with the DM message handler in `dm-vdo-target.c`, `vdo_dump_hash_zones()` in dedupe, `dump_data_vio_pool()` in the data_vio pool, work queue dump support, and `vdo_report_memory_usage()`.

## Risks
Diagnostic code must avoid making a stressed system worse. `all` or VIO pool dumps can log thousands of lines, so output volume can overwhelm logs during a failure. Prefix matching means abbreviated options are accepted, but ambiguous future option names could change behavior. Static buffers are intentionally not concurrency-safe. The function always dumps hash zones regardless of option flags, so callers requesting narrow output still receive index/hash diagnostics.

## Test Signals
Exercise `dmsetup message <dev> 0 dump`, `dump all`, `dump queues`, `dump viopool`, unknown options, and `dump-on-shutdown`. Check that default output includes queues/status, unknown options return `-EINVAL`, active/outstanding counts are plausible, data_vio lines are bounded and non-overlapping under single dump, and no dump path sleeps or allocates in unsafe contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.h

## Purpose
Declares the dm-vdo diagnostic dump interface. It is a small public header used by the DM target and pool dumping code to trigger whole-device dumps and format individual `data_vio` entries.

## Important APIs
`vdo_dump(struct vdo *vdo, unsigned int argc, char *const *argv, const char *why)` parses dump options and emits the requested diagnostic output. It returns `0` on success or `-EINVAL` for unknown options.

`vdo_dump_all(struct vdo *vdo, const char *why)` emits the broadest dump without option parsing, used when a VDO instance is being shut down with dump-on-shutdown enabled.

`dump_data_vio(void *data)` is a callback-style formatter for a `data_vio` object, declared as `void *` so generic pool-dump code can call it without depending on the concrete type.

## Control Flow
`dm-vdo-target.c` includes this header to process `dump` and `dump-on-shutdown` messages. The data_vio pool implementation can use `dump_data_vio()` as a buffer/pool item printer. The header keeps diagnostic functionality separate from core target lifecycle and data-path headers.

## State And Persistence
No state is declared here. The functions read live VDO runtime state and emit logs only; they do not define any on-disk format or persistent metadata behavior.

## Dependencies And Integration Points
The only local include is `types.h`, which provides forward declarations and VDO type names. Integration points are `dm-vdo-target.c`, `dump.c`, and any pool or diagnostic subsystem that needs the `dump_data_vio()` callback.

## Risks
The narrow header surface is low risk. The main API concern is that `dump_data_vio()` accepts `void *`, so callers must pass an actual `struct data_vio *`; misuse would fail at runtime rather than compile time. Because dump output can be large, callers should route these functions only from explicit diagnostic paths.

## Test Signals
Compile coverage from `dm-vdo-target.c` and pool-dump users is the main signal. Runtime checks are successful dmsetup dump messages and shutdown dumps that include data_vio entries when pool details are requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.c

## Purpose
Implements VDO's machine-independent on-disk metadata encoders, decoders, validators, and initializers. It covers geometry blocks, super block headers and component payloads, layout partitions, block-map state and pages, recovery-journal state and journal entries, slab-depot state and slab sizing, and volume geometry initialization. The file is the compatibility boundary between in-memory VDO structures and persistent metadata.

## Important APIs, Types, And Functions
Version and header constants define the accepted formats: geometry block versions 4.0 and 5.0, block-map header 2.0, recovery-journal header 7.0, slab-depot header 2.0, layout header 3.0, VDO component data 41.0, volume version 67.0, and super block header 12.0. `VDO_GEOMETRY_MAGIC_NUMBER` is `"dmvdo001"`.

Geometry APIs are `vdo_initialize_volume_geometry()`, `vdo_encode_volume_geometry()`, and `vdo_parse_geometry_block()`. Super block/component APIs are `vdo_initialize_component_states()`, `vdo_encode_super_block()`, `vdo_decode_super_block()`, `vdo_decode_component_states()`, `vdo_validate_component_states()`, `vdo_validate_config()`, and `vdo_destroy_component_states()`.

Layout APIs are `vdo_initialize_layout()`, `vdo_uninitialize_layout()`, `vdo_get_partition()`, and `vdo_get_known_partition()`. Slab APIs are `vdo_configure_slab()`, `vdo_configure_slab_depot()`, and `vdo_decode_slab_journal_entry()`. Block-map APIs are `vdo_format_block_map_page()`, `vdo_validate_block_map_page()`, and `vdo_compute_new_forest_pages()`. `vdo_get_journal_operation_name()` names recovery-journal operation codes.

The low-level helpers use packed structs and explicit little-endian encode/decode functions to avoid host-endian or alignment-dependent disk formats.

## Control Flow
Formatting starts with `vdo_initialize_volume_geometry()`, which asks UDS for the index size, places the index region at block 1, places the data region after the index, copies UUID/index settings, and sets the nonce. `vdo_initialize_component_states()` initializes the VDO config, volume version, recovery journal start, layout beginning one block after the data region start, slab depot state, block map root state, and `VDO_NEW` state.

Writing metadata calls `vdo_encode_volume_geometry()` for geometry and `vdo_encode_super_block()` for super block data. Geometry writes magic, header, fields, region table, index config, and CRC. Super block writes header, fixed component data in a strict order, and CRC, with an assertion that the whole encoding fits in one sector to reduce torn-write exposure.

Loading first calls `vdo_parse_geometry_block()` to validate magic, versioned header, and checksum. `vdo_decode_super_block()` validates the super block header and checksum without decoding all component content. Then `vdo_decode_component_states()` starts at `VDO_COMPONENT_DATA_OFFSET`, validates volume version, and decodes VDO component, layout, recovery journal, slab depot, and block map state. `vdo_validate_component_states()` checks the geometry/superblock nonce match and delegates config validation.

Layout creation carves block-map space from the beginning, slab summary and recovery journal from the end, and gives all remaining middle space to the slab depot. Layout decoding validates partition count and required partition presence, then checks partition coverage.

## State And Persistence
Everything this file encodes is persistent metadata. Geometry stores nonce, UUID, bio offset, index/data region starts, and index memory/sparse settings. The super block stores volume version, VDO state/config, layout, recovery-journal state, slab-depot state, and block-map state. CRCs protect geometry and super block payloads. Version checks reject unsupported incompatible formats rather than attempting partial interpretation.

The file also defines derived persistent layout decisions: slab journal thresholds, reference count block counts, depot first/last blocks, root origin/count, and recovery journal initial sequence.

## Dependencies And Integration Points
It depends on Linux CRC, UUID, log2 helpers, VDO constants/types/numeric packing helpers, logger, memory allocation, assertions, and UDS index-size computation. It integrates with `dm-vdo-target.c` during format/load/grow, with block map code for page formatting/validation and forest growth, with recovery journal code for persisted journal state and entry decoding, with slab depot code for depot configuration, and with UDS for index region sizing.

## Risks
On-disk compatibility is the main risk. Any size, version, field order, endian conversion, or packed-struct change can make existing VDO volumes unloadable or silently misdecoded. `vdo_validate_header()` allows minimum-size validation for variable layouts and exact-size validation for fixed components; using the wrong mode can reject valid metadata or accept malformed data.

Layout validation is subtle. Decoding currently sums required partition counts from `start` and expects that to equal `size`; this assumes exactly the required partitions cover the layout. Duplicate partition IDs, overlapping partitions, or inconsistent free ranges are areas to scrutinize when changing the decoder.

The super block checksum verification skips component decoding until later, so callers must always follow `vdo_decode_super_block()` with `vdo_decode_component_states()` and validation before trusting state. Geometry version 4 compatibility omits `bio_offset`, so mixed-version behavior depends on defaulting that field to zero.

## Test Signals
Tests should round-trip geometry and super block encodings on little- and big-endian builds if possible, inject bad magic/version/size/checksum/nonce values, load version 4 and version 5 geometry blocks, validate boundary slab sizes and journal sizes, verify layout partition coverage and missing/extra partitions, and compare block-map page validity for wrong nonce, uninitialized page, and wrong PBN. Growth tests should verify `vdo_compute_new_forest_pages()` and layout initialization with small and maximum physical sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.c -->
