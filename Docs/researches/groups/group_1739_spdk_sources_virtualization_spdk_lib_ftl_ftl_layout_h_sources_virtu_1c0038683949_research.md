# Group Research: SPDK FTL Layout, NV Cache, P2L, Relocation, Writer, Superblock, Trace, and Management

Scope verified against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. The listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_layout.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_layout.h

Defines the persistent and runtime layout model for SPDK FTL metadata/data regions. The central enum `ftl_layout_region_type` assigns stable region IDs for superblock, L2P, band metadata, valid map, NV-cache metadata/data, base data, P2L checkpoints, trim metadata/logs, and P2L IO logs.

Key structures:
- `ftl_layout_region_descriptor`: persisted version, block offset, and block count.
- `ftl_layout_region`: named region with type, mirror type, current descriptor, entry geometry, VSS metadata size, and target bdev/io channel.
- `ftl_layout`: top-level geometry for base, NV cache, L2P, P2L checkpoints, all regions, and their `ftl_md` objects.
- `ftl_md_layout_ops`: device-specific hooks for region creation/open.

Important APIs cover layout setup, superblock-only setup/clear, region validation, base metadata sizing, region lookup, blob serialization/deserialization, layout offset calculation, and upgrade helpers for adding/dropping regions.

Architectural role: this header is the contract tying base-device metadata, NV-cache metadata, superblock upgrade logic, and management initialization together.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_layout.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.c

Implements the non-volatile cache lifecycle, write path, compaction path, recovery helpers, chunk state persistence, scrubbing, throttling, and JSON property reporting.

Major behaviors:
- Initialization allocates chunk objects, metadata pools, P2L map pools, chunk metadata pools, free-state persistence pools, and compactor objects.
- Chunks move through `FREE`, `OPEN`, `CLOSED`, and `INACTIVE`; lists and counters track free/open/full/compacting/inactive/free-persist chunks.
- User writes reserve sequential space in the current/open chunk, pin L2P, submit through the NV-cache device type, update L2P to cache addresses, and advance/close chunks.
- Closing a chunk writes tail P2L metadata, computes its CRC, persists chunk metadata as `CLOSED`, then moves it to the full list.
- Compaction reads valid cache blocks, pins LBAs, verifies current L2P still points to cache addresses, queues valid data to the base writer, then frees compacted chunks.
- Recovery restores chunk states, walks tail metadata, recovers open chunks through the cache-device implementation, persists recovered P2L maps, and closes recovered chunks.
- Shutdown/upgrade paths halt opening, close the current chunk by skipping unwritten blocks, persist free-state transitions, and optionally keep compaction running for upgrade preparation.

Notable risk/behavior: most IO failure handling aborts unless `SPDK_FTL_RETRY_ON_ERROR` is enabled. Resource sizing is tightly coupled to `FTL_MAX_OPEN_CHUNKS`, `FTL_MAX_COMPACTED_CHUNKS`, and `FTL_NV_CACHE_NUM_COMPACTORS`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.h

Declares NV-cache state, chunk metadata, compactor state, throttling parameters, and management/recovery entry points.

Important definitions:
- `FTL_NVC_VERSION_CURRENT` is version 2.
- `FTL_NV_CACHE_NUM_COMPACTORS` is 8.
- Throttle constants define 20 ms update intervals and a proportional modifier clamped between -0.8 and 0.5.
- `ftl_chunk_state` models `FREE`, `OPEN`, `CLOSED`, and `INACTIVE`.

`struct ftl_nv_cache_chunk_md` is exactly one FTL block and stores version, open/close sequence IDs, write/read/compaction pointers, state, P2L tail-map checksum, P2L IO log type, and reserved space.

`struct ftl_nv_cache` owns bdev handles, mempools, chunk lists/counters, compactor list, sequence state, free targets, compaction bandwidth SMA, and throttle accounting.

Public functions cover init/deinit, read/write, metadata fill, chunk-map access, state save/load, halt/resume checks, tail metadata sizing, recovery management hooks, address lookup, trim sequence acquisition, and chunk metadata initialization.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache_io.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache_io.h

Provides two inline wrappers for NV-cache block IO with optional metadata:
- `ftl_nv_cache_bdev_read_blocks_with_md`
- `ftl_nv_cache_bdev_write_blocks_with_md`

Each wrapper checks whether the underlying bdev exposes metadata via `spdk_bdev_get_md_size`. If metadata exists, it calls the SPDK `_with_md` API and substitutes global fallback buffers (`g_ftl_read_buf` or `g_ftl_write_buf`) when the caller passes `NULL` metadata. If no metadata exists, it calls the plain block read/write API.

Architectural role: this isolates NV-cache IO callers from metadata-capable versus data-only bdev differences and keeps call sites in compaction, chunk tail metadata, and user reads simpler.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_nv_cache_io.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_p2l.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_p2l.c

Implements P2L checkpoint management for open base-device bands. Checkpoints emulate/replace VSS-style progress tracking for base writes.

Core object: `struct ftl_p2l_ckpt`, which binds a checkpoint metadata region, VSS metadata page buffer, page counts, pages-per-transfer, and debug bitmap state.

Main flows:
- `ftl_p2l_ckpt_init/deinit` allocate four checkpoint region handlers and manage free/in-use lists.
- `ftl_p2l_ckpt_issue` records an xfer-sized write request into checkpoint pages, updates band P2L entries for relocation/compaction writes, writes sequence/count/checksum metadata, and persists pages.
- Management persistence finds bands assigned to checkpoint regions and serializes their in-memory P2L into checkpoint metadata during clean shutdown.
- Restore functions recover band P2L from checkpoint pages, validate sequence IDs and CRCs, reacquire the matching checkpoint object, and place the band iterator at the restored write offset.
- Debug paths validate expected checkpoint page coverage.

Interactions: used by writers/bands to maintain crash-recoverable mapping for open bands and by management restore/finalization paths after clean or dirty startup.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_p2l.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_p2l_log.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_p2l_log.c

Implements P2L IO log regions for non-VSS cache operation. Each persisted page contains a header plus multiple log items mapping LBA ranges to cache addresses and sequence IDs.

Key structures:
- `ftl_pl2_log_item`: LBA, block count, sequence ID, and FTL address.
- `ftl_p2l_log_page`: VSS/header plus packed log items, exactly one FTL block.
- `ftl_p2l_log_page_ctrl`: page plus owning log, entry index, IO list, and metadata IO context.
- `ftl_p2l_log`: per-region object with free/in-use linkage, pending IO queue, md handle, page pool, sequence ID, callbacks, and read context.

Write path: queued FTL IOs are packed into log pages, CRCed with checksum field excluded, persisted with `ftl_md_persist_entries`, and completed through the supplied callback.

Read path: pages are read concurrently through a mempool-bounded queue depth, filtered by sequence ID, validated by index/checksum/count, then expanded item-by-item through the read callback.

Notable issue: file uses `ftl_pl2_log_item` naming while the subsystem is P2L, likely a typo but functionally local.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_p2l_log.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_reloc.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_reloc.c

Implements garbage-collection relocation from base-device bands into new writer bands.

Core model:
- `ftl_reloc` owns the current GC band, completed-band queue, max queue depth, halt state, and move objects.
- `ftl_reloc_move` owns one `ftl_rq` and transitions through `READ`, `PIN`, `WRITE`, `WAIT`, and `HALT`.

Main flow:
- Relocation selects GC bands with `ftl_band_get_next_gc`, walks valid-map bits, reads valid runs, pads request entries when needed, and advances the band iterator.
- After reads complete, it pins each valid LBA, retries pin failures by unpinning and reentering pin state, then queues the request to the GC writer.
- Write completion updates L2P from old addresses to new base addresses and unpins LBAs.
- Finished bands are freed if empty; otherwise errors push them back through close-state handling.
- Halt preserves upgrade behavior: if preparing upgrade and no free bands exist, relocation may keep running to reclaim one.

Architectural role: this is the base-device GC engine that supplies free bands and keeps valid data reachable while invalidating old locations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_reloc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_rq.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_rq.c

Defines allocation, destruction, and unpinning for internal FTL transfer requests.

`ftl_rq_new` allocates a request sized for `dev->xfer_size` entries, DMA payload buffer, optional DMA metadata buffer, and initializes each entry with index, invalid address/LBA, payload pointer, optional metadata pointer, and zero sequence ID.

`ftl_rq_del` frees DMA payload, DMA metadata, and the request object.

`ftl_rq_unpin` walks entries up to `rq->iter.count` and calls `ftl_l2p_unpin` for any pin context whose LBA is valid.

This utility underpins relocation, NV-cache compaction, writer padding, and checkpoint IO paths.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_rq.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb.c

Dispatches superblock operations by on-disk superblock version.

`struct sb_ops` contains version-specific hooks for magic validation, blob-area checks/load/store, region upgrade, layout apply, and layout dump. `sb_get_ops` maps versions 0-5:
- v0-v2 use legacy v2 magic checks.
- v3-v4 use v3 magic and v3 layout blob load/dump.
- v5 uses v3 magic plus v5 blob validation/store/load, region upgrade, layout apply, and dump.

Exported functions are thin dispatchers:
- `ftl_superblock_check_magic`
- `ftl_superblock_is_blob_area_empty`
- `ftl_superblock_validate_blob_area`
- `ftl_superblock_store_blob_area`
- `ftl_superblock_load_blob_area`
- `ftl_superblock_md_layout_upgrade_region`
- `ftl_superblock_md_layout_apply`
- `ftl_superblock_md_layout_dump`

Unsupported missing mandatory ops generally abort; optional validation/apply can default to success.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb.h

Public header for superblock helpers. It includes common and current superblock definitions and forward-declares `spdk_ftl_dev` and `ftl_layout_region`.

Declared APIs validate magic, inspect/validate/store/load the superblock blob area, upgrade a metadata layout region to a new version, apply the metadata layout from the superblock, and dump the superblock metadata layout.

Architectural role: management and upgrade code use this header to keep version-specific superblock handling behind a small dispatch interface.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb_common.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb_common.h

Defines common superblock constants and version-independent packed structures.

Important content:
- `FTL_SUPERBLOCK_SIZE` is 128 KiB.
- `FTL_SUPERBLOCK_MAGIC` is built from four 16-bit constants.
- `ftl_superblock_gc_info` stores high-priority GC band, current band ID, physical reclaim-unit ID, and transaction validity marker.
- `ftl_superblock_header` stores magic, CRC, and version.
- `ftl_superblock_v3_md_region` describes older metadata layout region entries.
- `ftl_superblock_v5_md_blob_hdr` points to variable-size blobs inside the superblock blob area.
- `ftl_superblock_shm` stores shared-memory restart state: SHM ready/clean, in-progress trim info, and GC info.

Static asserts enforce packed structure sizes for disk format stability.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb_common.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb_current.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb_current.h

Defines the current superblock format, version 5.

`struct ftl_superblock` contains:
- common header and UUID
- current sequence ID
- clean shutdown flag
- surfaced LBA count
- overprovisioning
- maximum relocation queue depth
- upgrade-ready flag
- last L2P checkpoint sequence boundary
- GC info
- blob-area end pointer
- NV-cache and base-device type names
- v5 blob headers for NV-cache metadata layout, base metadata layout, and layout parameters
- flexible blob-area start

Static asserts verify header placement and that the fixed structure fits in `FTL_SUPERBLOCK_SIZE`.

Role: this is the persisted compatibility anchor for FTL startup, shutdown, layout upgrade, and dirty/clean recovery decisions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_sb_current.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_trace.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_trace.c

Debug-only SPDK trace integration for FTL.

When `DEBUG` is defined, the file registers FTL trace owner/type and tracepoint descriptions for internal/user sources, including band relocation/write, limits, read/write/trim scheduling/submission/completion, and metadata read/write events.

Runtime helpers:
- `ftl_trace_alloc_id` atomically allocates event IDs.
- `ftl_trace_reloc_band` and `ftl_trace_write_band` emit internal band events.
- `ftl_trace_lba_io_init` records user IO scheduling.
- `ftl_trace_submission` records read/write/trim submission addresses and counts.
- `ftl_trace_completion` records read/write/trim completion location/type.
- `ftl_trace_limits` records throttling/limit state.

In non-debug builds these functions are macro-elided by `ftl_trace.h`, so there is no runtime tracing cost.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_trace.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_trace.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_trace.h

Declares the debug trace API and provides no-op macros outside `DEBUG`.

Defines:
- `FTL_TRACE_INVALID_ID`
- `enum ftl_trace_completion`: invalid/cache/disk completion source
- `struct ftl_trace`: monotonically increasing event ID counter

In debug builds, it declares allocation and event-recording helpers for relocation, writes, LBA IO lifecycle, submissions, completions, and limits. In non-debug builds, all trace calls compile away and allocation returns `FTL_TRACE_INVALID_ID`.

Role: gives FTL code a uniform trace interface without sprinkling `#ifdef DEBUG` through call sites.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_utils.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_utils.h

Small umbrella header for common FTL utility headers:
- `utils/ftl_defs.h`
- `utils/ftl_mempool.h`
- `utils/ftl_conf.h`
- `utils/ftl_md.h`
- `utils/ftl_property.h`

It has no logic of its own. Its role is convenience inclusion for modules that need the common definitions, memory pool, configuration, metadata, and property helpers.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_writer.c -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_writer.c

Implements the sequential base-band writer used by user-data compaction and GC relocation.

Main behavior:
- `ftl_writer_init` initializes queues, limits, halt state, and writer type.
- `get_band` lazily obtains/open-prepares a free band, uses `next_band` when available, enforces a maximum number of open bands split across writers, and sets band ownership callbacks.
- `ftl_writer_run` closes full bands, obtains a writable band, pops one queued `ftl_rq`, and submits it through `ftl_band_rq_write`.
- `ftl_writer_band_state_change` handles `FULL` by moving bands to the full queue and `CLOSED` by releasing ownership and updating last close sequence ID.
- `ftl_writer_is_halted` waits for full bands, active band queue depth, and upgrade padding. During upgrade-prep shutdown it can pad an open band with an internally allocated request.
- `ftl_writer_get_free_blocks` reports remaining user blocks in current and next band.

Role: bridges higher-level relocation/compaction request queues to the low-level band write implementation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_writer.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_writer.h -->
# File Research: sources/virtualization/spdk/lib/ftl/ftl_writer.h

Declares `struct ftl_writer` and writer APIs.

State includes the owning device, request queue, current and next bands, full-band queue, write limit threshold, halt flag, writer band type, last sequence ID, and optional padding request.

Exposed operations initialize the writer, run one scheduling pass, react to band state changes, halt/resume, check halted state, enqueue requests, and query free blocks.

Note: `ftl_writer_is_halted` and `ftl_writer_run` are declared twice in this header, which is harmless but redundant.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/ftl_writer.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.c

Implements the generic asynchronous FTL management process engine.

Key model:
- A process descriptor supplies named steps, optional per-process context, init/deinit handlers, and error handler.
- Each step has action, optional cleanup, timing/status fields, and optional step context.
- Actions run on the FTL core thread; final completion is posted back to the caller thread.
- Completed action steps with cleanup are pushed onto rollback todo in reverse order.
- `ftl_mngt_fail_step` marks failure, records the current step as failed, switches to rollback, and executes cleanup steps.

Important APIs:
- `ftl_mngt_process_execute`
- `ftl_mngt_process_rollback`
- context accessors
- `ftl_mngt_next_step`, `skip_step`, `continue_step`, `fail_step`
- child process invocation and rollback invocation

Role: all startup, shutdown, restore, scrub, metadata, property, and recovery flows are assembled as deterministic step machines over this engine.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.h -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.h

Public interface for the FTL management process framework.

Defines callback types:
- `ftl_mngt_fn`
- `ftl_mngt_init_fn`
- `ftl_mngt_completion`

Defines descriptors:
- `ftl_mngt_step_desc`: name, optional context size, action, optional cleanup.
- `ftl_mngt_process_desc`: name, process context size, error/init/deinit handlers, and flexible step array.

Exports process execution/rollback, context accessors, finish/next/skip/continue/fail controls, nested process calls, and top-level management entry points for startup, trim, and shutdown.

Design note: callbacks are explicitly step-only APIs; the engine owns sequencing, rollback ordering, and caller completion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_band.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_band.c

Management helpers for band allocation, metadata binding, physical grouping, address initialization, and startup finalization.

Important flows:
- `ftl_dev_init_bands` calculates usable band count from base bdev size minus reserved base metadata bands, allocates band array, and initially places bands on `shut_bands`.
- `ftl_band_init_md` attaches per-band metadata and valid-map slices.
- `decorate_bands` groups logical bands into larger physical reclaim units, dropping unaligned tail bands.
- `ftl_mngt_initialize_band_address` sets each band start and tail metadata address from the base data region.
- `ftl_recover_max_seq` combines max band and NV-cache sequence IDs into `sb->seq_id` and writer/NV-cache last sequence IDs.
- `ftl_mngt_finalize_init_bands` classifies free/shut/open bands, reattaches open bands to user/GC writers, restores P2L maps from SHM or checkpoints, recalculates free counts/limits, and validates GC can start.

This file is central to recovering writer state after startup and ensuring GC has a viable path when free bands are scarce.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_band.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_bdev.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_bdev.c

Management helpers for opening, validating, claiming, and closing base and NV-cache bdevs.

Base bdev handling:
- Opens by name read/write, claims through dummy `ftl_lib` module, validates 4 KiB block size and minimum 20 GiB capacity.
- Creates IO channel, derives transfer size, validates power-of-two xfer size, selects base device type, records metadata size, requires metadata layout ops, rejects zoned devices, initializes base layout tracker.
- Cleanup releases IO channel, bdev claim/descriptor, and layout tracker.

Cache bdev handling:
- Opens/claims by name, validates 4 KiB block size and minimum 5 GiB capacity, creates cache IO channel.
- Selects NV-cache device type, forces `nv_cache->md_size` to `sizeof(union ftl_md_vss)`, requires layout region creation ops, and initializes NV-cache layout tracker.
- Cleanup mirrors base close behavior.

Removal events currently assert, so hot-remove is not gracefully supported here.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_ioch.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_ioch.c

Manages FTL IO channel registration and per-thread channel lifecycle.

`io_channel_create_cb` allocates an `ftl_io_channel`, creates a per-channel map mempool, completion/submission rings sized from `user_io_pool_size`, registers an IO-channel poller, and posts registration to the core thread. The channel is then available through `ftl_io_channel_get_ctx`.

Destroy path unregisters the poller on the owning thread and posts cleanup to the core thread, where queues and mempools are freed and the channel is removed from `dev->ioch_queue`.

Management steps register/unregister the SPDK IO device and get/put the core thread's own IO channel. Unregistration is asynchronous and resumes the management process via callback.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_ioch.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_l2p.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_l2p.c

Thin management wrappers around L2P subsystem operations.

Provides steps for:
- `ftl_l2p_init`
- `ftl_l2p_deinit`
- `ftl_l2p_clear`
- `ftl_l2p_persist`
- `ftl_l2p_trim`
- `ftl_l2p_restore`

Asynchronous L2P callbacks use a shared `l2p_cb` that fails or advances the management step based on status. This file intentionally keeps sequencing in the management descriptor layer and delegates actual L2P behavior elsewhere.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_l2p.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_md.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_md.c

Management helpers for layout setup, metadata object creation/destruction, metadata persist/restore, superblock initialization/validation, and clean/fast shutdown metadata flows.

Key flows:
- `ftl_mngt_init_layout` calls `ftl_layout_setup`.
- `ftl_mngt_init_md` creates `ftl_md` objects for all active layout regions, skips already-created superblock objects, and aliases mirror metadata buffers for no-buffer mirror regions.
- Persist helpers serialize NV-cache state, valid map, P2L checkpoints, band metadata, trim metadata, and superblock.
- Fast persist only saves NV-cache state and relies on shared memory for most metadata.
- Superblock CRC is computed excluding the CRC field, with legacy v2 special sizing.
- Default superblock initialization sets magic/version/UUID/clean flags, max relocation queue depth, overprovisioning, device type names, invalid layout blob IDs, and CRC.
- Superblock restore validates magic, CRC, upgrade compatibility, UUID, LBA count, overprovisioning, and blob area.
- Superblock management creates SHM metadata, lays out/mirrors SB regions, handles retry with new SHM, and runs init or restore sub-processes.
- Restore metadata supports fast startup from SHM or normal disk restore for NV-cache, valid map, band metadata, and trim metadata.

Role: this is the metadata orchestration hub for startup, shutdown, clean restore, fast restart, and upgrade preparation.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_md.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_misc.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_misc.c

Miscellaneous management steps for configuration, memory pools, relocation/NV-cache init, scrubbing, startup finalization, poller control, maps, trim metadata, and property APIs.

Important content:
- Config validation delegates to `ftl_conf_is_valid`.
- P2L map pool is backed by SHM metadata and initialized differently for fast versus non-fast startup.
- Band metadata pool is a normal mempool.
- Relocation and NV-cache init/deinit wrap `ftl_reloc_init/free` and `ftl_nv_cache_init/deinit`.
- NV-cache scrub runs on first create or major upgrade, clearing active cache chunks to avoid stale recovery data.
- Startup finalization detects in-progress trims, registers superblock version property, clears limit stats, marks initialization/SHM-ready, and resumes L2P, relocation, writers, and NV cache.
- Core poller start/stop controls main FTL progress loop; stop waits while poller exists.
- Valid and trim maps are bitmap wrappers over metadata buffers.
- Trim metadata/log clearing use async metadata clear callbacks.
- Property get/set APIs marshal work to the core thread and run property decode/set through management processes with cleanup.

This file binds operational controls around the core FTL data path.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_misc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_p2l.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_p2l.c

Management helpers for P2L checkpoint and P2L IO log metadata.

Functions:
- Initialize/deinitialize checkpoint objects.
- Wipe all P2L checkpoint regions.
- Conditionally wipe P2L IO log regions only if those layout regions have allocated blocks.
- Free checkpoint metadata buffers after use.
- Restore all checkpoint metadata regions unless fast startup can skip disk restore.

The wipe implementation iterates metadata regions sequentially with `ftl_md_clear`. Restore dispatches `ftl_md_restore` to all checkpoint regions and tracks aggregate completion/status in step context.

Role: prepares and restores the metadata regions used by `ftl_p2l.c` and P2L IO log recovery, keeping these operations in the management step model.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_p2l.c -->