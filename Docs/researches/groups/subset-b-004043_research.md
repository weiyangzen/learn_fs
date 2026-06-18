# subset-b-004043 research

This grouped report covers Linux MD RAID10 and RAID5 journal/cache files under `sources/distributed-fs/ceph-client`. Each section preserves the original source path so the reconciliation step can split it into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid10.c -->
# sources/distributed-fs/ceph-client/drivers/md/raid10.c

## Purpose
`raid10.c` implements the Linux MD RAID10 personality. It combines RAID0-style striping with RAID1-style mirroring, maps virtual array sectors onto near, far, offset, and far-set copy layouts, accepts normal block I/O from the MD core, and drives background resync, recovery, replacement, reshape, discard, error handling, and personality registration.

## Important APIs, Types, and Functions
The file registers `raid10_personality` with MD and supplies the personality callbacks `raid10_make_request()`, `raid10_run()`, `raid10_free()`, `raid10_status()`, `raid10_error()`, `raid10_add_disk()`, `raid10_remove_disk()`, `raid10_spare_active()`, `raid10_sync_request()`, `raid10_quiesce()`, `raid10_size()`, `raid10_resize()`, `raid10_takeover()`, `raid10_check_reshape()`, `raid10_start_reshape()`, `raid10_finish_reshape()`, and `raid10_update_reshape_pos()`.

The central runtime objects come from `raid10.h`: `struct r10conf` is the array configuration, synchronization, pool, geometry, retry, and reshape state; `struct raid10_info` is one mirror slot with primary and replacement rdev pointers; and `struct r10bio` is the per-request private bio that tracks mapped devices, cloned bios, completion counts, state flags, and retry linkage. Important internal helpers include `setup_geo()`, `calc_sectors()`, `raid10_find_phys()`, `raid10_find_virt()`, `read_balance()`, `wait_barrier()`, `raise_barrier()`, `lower_barrier()`, `raid10_read_request()`, `raid10_write_request()`, `raid10_handle_discard()`, `raid10d()`, `sync_request_write()`, `recovery_request_write()`, `fix_read_error()`, `handle_write_completed()`, and `reshape_request()`.

## Control Flow
Module init registers the MD personality, and `raid10_run()` creates or activates `r10conf`, installs the daemon thread, validates layout and clustered restrictions, binds member `md_rdev` objects to mirror slots, stacks queue limits, checks that every logical block has at least one available copy, computes array size, and schedules reshape if metadata says one is in progress.

Normal I/O enters through `raid10_make_request()`. Flush bios are delegated to `md_flush_request()`. Discards first try the specialized aligned discard path in `raid10_handle_discard()`. Other bios are split on chunk boundaries when needed, wrapped in an `r10bio`, and sent to `raid10_read_request()` or `raid10_write_request()`. Reads call `regular_request_wait()` to pass reshape/resync barriers, then `read_balance()` maps all physical copies and chooses a readable mirror by bad-block status, synchronization state, pending count, rotational status, and head-position heuristics. Writes map all copies, wait for blocked bad-block devices, split around bad regions when possible, clone one bio per primary or replacement target, and queue writes through the RAID1 plug helper or `pending_bio_list`.

Completion paths update the composite `r10bio` state. Successful reads call `raid_end_bio_io()`. Recoverable read errors set `R10BIO_ReadError` and are retried by `raid10d()`. Write completions set `R10BIO_Uptodate` when a healthy in-sync copy succeeded, mark `WriteErrorSeen` and `WantReplacement` on failures, optionally clear known bad blocks with `R10BIO_MadeGood`, and queue complex handling to `raid10d()`. The daemon drains pending writes, retry requests, delayed endio requests, resync comparisons, recovery writes, reshape writes, and read-error repair work in process context.

Background sync uses `raid10_sync_request()`. Resync reads all copies at a virtual address, compares pages, and writes mismatching or unreadable copies from an authoritative copy. Recovery iterates physical sectors for out-of-sync devices and builds linked `r10bio` requests that read from a working copy and write to the rebuilding primary and/or replacement. Reshape uses `reshape_request()` to read from the previous geometry, write into the new geometry, update safe metadata checkpoints, and coordinate cluster resync windows.

## State and Persistence Behavior
Persistent array state lives in MD superblocks and rdev metadata, not directly in this file. This code updates MD flags and metadata-visible fields such as `mddev->degraded`, `mddev->array_sectors`, `mddev->dev_sectors`, `mddev->resync_max_sectors`, `mddev->reshape_position`, `mddev->layout`, `mddev->chunk_sectors`, rdev `recovery_offset`, rdev `data_offset`/`new_data_offset`, and bad-block records. It sets `MD_SB_CHANGE_DEVS` and `MD_SB_CHANGE_PENDING` when device state or reshape checkpoints must be persisted.

Volatile state is held in `r10conf`: current and previous geometries, mirror arrays, mempools, temporary page, retry lists, pending write list, resync barrier counters, cluster sync window, reshape progress/safety positions, and the daemon thread. The barrier scheme uses `resync_lock`, `nr_pending`, `nr_waiting`, `barrier`, `array_freeze_pending`, and `wait_barrier` to prevent normal I/O from overlapping with resync, recovery, device reconfiguration, or reshape ranges. RCU and rdev `nr_pending` counts protect member pointers that can be removed asynchronously.

## Dependencies and Integration Points
The file integrates with the MD core (`md.h`, personality registration, md threads, md bitmaps, recovery flags, superblock updates, cluster hooks, integrity stacking), the block layer (bios, bio splitting, queue limits, discard, flush, atomic write limits, blk plugs), common RAID1/RAID10 helpers from `raid1-10.c`, RAID0 takeover data from `raid0.h`, and clustered MD support from `md-cluster.h`. It also uses bad-block helpers, rdev flags, sysfs notifications, trace remapping, and md bitmap operations for resync/recovery tracking.

## Risks and Edge Cases
The geometry mapping is dense and supports legacy far-set variants, near/far/offset layouts, reshape previous/current geometry selection, and clustered restrictions; mistakes can misdirect I/O. Barrier accounting must balance every `wait_barrier()` with `allow_barrier()` and every background `raise_barrier()` with `lower_barrier()`, otherwise normal I/O or recovery can deadlock. rdev pointers can disappear under removal, so paths must obey the RCU/refcount rules documented in the header. Write-error handling must avoid acknowledging a user write before enough mirrors are durable, and bad-block splitting must reject atomic writes when the write cannot be kept atomic. Reshape has strict offset-distance requirements to avoid overwriting data that has not yet been copied. Several FIXME comments remain around reshape read/write bad-block handling.

## Test Signals
Useful signals include successful assembly of near, far, offset, and far-set layouts; reads selecting healthy mirrors under bad blocks and degraded states; write completion across primary and replacement devices; resync mismatch correction; recovery to spare and replacement devices; read-error repair and bad-block recording; discard behavior for aligned large ranges and fallback for small or reshape-spanning ranges; online reshape forward and backward with metadata checkpoint restart; clustered RAID10 near-layout resync window broadcasts; queue-limit propagation; and module personality registration aliases `md-raid10`, `md-level-10`, and `md-personality-9`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid10.h -->
# sources/distributed-fs/ceph-client/drivers/md/raid10.h

## Purpose
`raid10.h` defines the private data structures and state flags shared by the MD RAID10 implementation. It captures the array geometry, mirror slots, per-array runtime state, per-I/O request state, and the concurrency rules for accessing removable member devices.

## Important APIs, Types, and Functions
`struct raid10_info` represents one logical mirror position and stores a primary `rdev`, an optional `replacement`, and a head-position estimate used by read balancing. `struct r10conf` stores the owning `mddev`, mirror arrays for current/new/old layouts, device lock, current and previous `struct geom`, copy count, device-sector calculations, reshape progress/safety state, retry and endio lists, pending write list, resync barrier counters, mempools, bioset, temporary page, daemon thread pointer, and clustered resync range. The embedded `struct geom` describes `raid_disks`, `near_copies`, `far_copies`, `far_offset`, `stride`, `far_set_size`, `chunk_shift`, and `chunk_mask`.

`struct r10bio` is the private request object used for normal I/O, resync, recovery, reshape, and discard. It records completion count, virtual sector, sector count, state bits, owning `mddev`, original `master_bio`, read slot, retry list node, and a flexible array of mapped per-copy `struct r10dev` entries. Each `r10dev` can hold a cloned bio plus either a replacement bio for writes/resync or the selected rdev for reads. `enum r10bio_state` defines flags such as `R10BIO_Uptodate`, `R10BIO_IsSync`, `R10BIO_IsRecover`, `R10BIO_IsReshape`, `R10BIO_ReadError`, `R10BIO_Returned`, `R10BIO_MadeGood`, `R10BIO_WriteError`, `R10BIO_Previous`, `R10BIO_FailFast`, and `R10BIO_Discard`.

## Control Flow
The header has no executable code, but it defines the objects that `raid10.c` allocates, fills, passes to endio callbacks, queues on daemon retry lists, and uses to translate between logical and physical sectors. Normal request flow allocates an `r10bio` from `r10bio_pool`, fills `devs[]` through geometry mapping, and frees it when the master bio completes. Resync and recovery allocate larger `r10bio` objects from `r10buf_pool` so each mapped device has preallocated bios and pages.

## State and Persistence Behavior
The header describes volatile in-memory state. Persistent state is referenced indirectly through `mddev`, `md_rdev`, rdev flags, recovery offsets, bad-block records, and MD superblock fields. The leading comment is an important persistence and lifetime contract: `raid10_info.rdev` may be set to `NULL` asynchronously by disk removal, and safe access requires `mddev->reconfig_mutex`, a known resync/recovery/reshape context, or RCU lookup plus incrementing `rdev->nr_pending`.

## Dependencies and Integration Points
The declarations depend on MD core types (`struct mddev`, `struct md_rdev`, `struct md_thread`), block-layer `struct bio`, Linux synchronization primitives, mempools, biosets, wait queues, and list heads. The header is private to the MD RAID10 personality and is included by `raid10.c`, which also includes common RAID1/RAID10 helper code.

## Risks and Edge Cases
The flexible `devs[]` sizing must match the active geometry or endio lookup and memory-pool freeing can walk invalid entries. The union inside `struct r10dev` changes meaning between read and write/resync paths, so callers must honor `read_slot` and state bits. `R10BIO_Previous` is critical during reshape because it determines whether device addresses use old or new data offsets. Incorrect rdev lifetime handling can race hot-remove and lead to use-after-free or stalled removal.

## Test Signals
Compile coverage should validate all users of `struct r10conf`, `struct r10bio`, and `enum r10bio_state`. Runtime signals come from the `raid10.c` paths that allocate/free mempools, hot-remove devices while I/O is active, run replacement recovery, retry read/write errors, and reshape while normal I/O is crossing old/new geometry boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5-cache.c -->
# sources/distributed-fs/ceph-client/drivers/md/raid5-cache.c

## Purpose
`raid5-cache.c` implements the MD RAID5/RAID6 journal device support and write-back cache. It logs data/parity updates to a dedicated journal rdev, orders flush/FUA operations, reclaims ring-buffer log space, exposes and enforces write-through versus write-back journal modes, and replays journal contents after crashes so pending data reaches the RAID disks or is restored into the stripe cache.

## Important APIs, Types, and Functions
The file defines the private `struct r5l_log`, which owns the journal rdev, ring positions (`last_checkpoint`, `log_start`, `next_checkpoint`), sequence counters, I/O mutex and lists, current `r5l_io_unit`, reclaim thread, mempools, bioset, pending no-space/no-memory stripe lists, journal mode, write-back stripe lists, and the radix tree used to block chunk-aligned reads when a big stripe is cached. `struct r5l_io_unit` represents one metadata block plus following data/parity pages in the log and tracks pending stripes, flush/FUA flags, split bios, ordering deferral, and state transitions. `struct r5l_recovery_ctx` tracks recovery scan position, readahead pool, cached stripes, and recovery counters.

Exported or header-visible entry points include `r5l_init_log()`, `r5l_start()`, `r5l_exit_log()`, `r5l_write_stripe()`, `r5l_write_stripe_run()`, `r5l_flush_stripe_to_raid()`, `r5l_stripe_write_finished()`, `r5l_handle_flush_request()`, `r5l_quiesce()`, `r5l_log_disk_error()`, `r5c_is_writeback()`, `r5c_try_caching_write()`, `r5c_cache_data()`, `r5c_finish_stripe_write_out()`, `r5c_release_extra_page()`, `r5c_use_extra_page()`, `r5c_flush_cache()`, `r5c_check_stripe_cache_usage()`, `r5c_check_cached_full_stripe()`, `r5c_update_on_rdev_error()`, `r5c_handle_cached_data_endio()`, `r5c_big_stripe_cached()`, and exported `r5c_journal_mode_set()`. The sysfs entry `r5c_journal_mode` provides mode show/store handlers.

## Control Flow
`r5l_init_log()` allocates and initializes the log object, verifies `PAGE_SIZE == 4096` and metadata size limits, creates the I/O-unit cache, mempools, bioset, reclaim thread, work items, stripe lists, and sets `MD_HAS_JOURNAL`. `r5l_start()` calls `r5l_load_log()`, which validates or creates the first metadata block, initializes ring size and checkpoint state, and runs `r5l_recovery_log()` if an existing log must be replayed.

For write-through operation, `r5l_write_stripe()` checks the stripe is eligible, calculates data and parity checksums, reserves ring space, appends payload metadata and pages into the current I/O unit, and later `r5l_write_stripe_run()` submits the current unit. After the metadata/data reaches the journal, `r5l_log_endio()` marks the unit as logged, runs or queues stripes in order, and the RAID5 state machine writes data/parity to array disks. `r5l_stripe_write_finished()` decrements the I/O unit when stripe write-out completes so reclaim can advance the checkpoint.

For write-back operation, `r5c_try_caching_write()` puts clean overwrite stripes into `STRIPE_R5C_CACHING`, accounts them in the big-stripe radix tree, drains pending write bios, and traps them for `r5c_cache_data()`. Cached data is written only to the journal and user bios can complete from cached data. Reclaim later calls `r5c_flush_cache()` and `r5c_make_stripe_write_out()` to move full or partial cached stripes into write-out phase, where parity is journaled and then data/parity is written to RAID disks. `r5c_finish_stripe_write_out()` clears journal state, removes stripes from journal lists and radix-tree accounting, appends flush payloads, and wakes any sync waiting for the stripe.

Flush handling is mode-dependent. Write-through can complete empty flushes once the journal guarantees recovery; write-back attaches empty flush bios to an I/O unit with preflush ordering. FUA data in write-back forces both FUA and preflush on the log I/O. I/O units with flush/FUA are deferred until they reach the front of `running_ios` to preserve log ordering.

Reclaim runs in `r5l_reclaim_thread()`. It first applies write-back cache pressure policy in `r5c_do_reclaim()`, then `r5l_do_reclaim()` waits for enough reclaimable I/O units, writes the journal tail to MD metadata via `r5l_write_super_and_discard_space()`, updates `last_checkpoint`, updates tight/critical log state, optionally discards freed journal sectors, and releases no-space stripes.

Recovery scans metadata blocks from `last_checkpoint` with `r5l_recovery_read_meta_block()`, verifies CRCs and payload checksums, reconstructs stripe state with `r5c_recovery_analyze_meta_block()`, replays data-parity stripes directly to array disks, keeps data-only write-back stripes in cache, rewrites those data-only stripes to a safe new journal sequence, writes a new checkpoint, and flushes cached data-only stripes through the normal state machine.

## State and Persistence Behavior
Persistent log state is stored on the journal rdev as 4 KiB metadata blocks and payload pages in a ring. Metadata includes magic, version, sequence number, position, payload descriptors, CRCs, and flush payloads. The journal tail is persisted through `rdev->journal_tail` and MD superblock changes in `r5l_write_super()`. `last_checkpoint` and `last_cp_seq` define recovery start; `log_start` and `seq` define the append head; `next_checkpoint` advances when I/O units settle.

Volatile state includes current and running I/O units, stripe lists, no-space/no-memory queues, write-back cache counts in `r5conf`, log tight/critical bits in `conf->cache_state`, and radix-tree counts for big stripes. `r5c_journal_mode` is runtime configuration exposed by sysfs and external API; it is forced back to write-through when the array becomes degraded or the journal device has an error. No write-back mode is allowed while RAID5 degraded calculation is nonzero.

## Dependencies and Integration Points
The file integrates tightly with `raid5.c` and `raid5.h` stripe state (`struct r5conf`, `struct stripe_head`, `struct stripe_head_state`, `R5_*` device flags, `STRIPE_*` flags), MD core metadata and thread APIs, md bitmap helpers, block bios, CRC32C, radix trees, mempools, workqueues, wait queues, and rdev bad/fault handling. `raid5-log.h` provides the inline dispatch layer used by the main RAID5 state machine to choose journal, write-back cache, or PPL behavior.

## Risks and Edge Cases
The journal format assumes 4 KiB pages and rejects very large arrays whose per-stripe metadata cannot fit in one page. Ring-buffer accounting must never reuse log space before the metadata tail is safely persisted or recovery can replay stale or misordered entries. Flush/FUA ordering depends on the ordered `running_ios` list and deferred submission path. Write-back mode must be disabled before degraded writes to avoid cached data that cannot be safely reconstructed. Recovery intentionally skips an entire metadata block if any data checksum mismatches, but continues scanning later blocks because I/O units can complete out of order. The reclaim path uses `mddev_trylock()` before discard to avoid a quiesce/reclaim deadlock, so discard of freed log space can be missed. Several paths use `BUG_ON()` for supposedly impossible metadata, state, and space conditions, making invariant coverage important.

## Test Signals
Tests should cover journal initialization with valid, empty, and corrupt metadata; write-through full-stripe and partial-stripe writes; write-back overwrite caching and fallback for non-overwrites, syncing, or degraded arrays; empty flush, data flush, and FUA ordering; log wrap-around and split bios; no-space and no-memory stripe queues; reclaim under stripe-cache pressure and log tight/critical thresholds; crash recovery of data-parity and data-only stripes; journal-mode sysfs transitions; write-back disable on rdev/journal error; chunk-aligned read rejection through `r5c_big_stripe_cached()`; quiesce/exit ordering; and PAGE_SIZE/large-disk-count rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5-log.h -->
# sources/distributed-fs/ceph-client/drivers/md/raid5-log.h

## Purpose
`raid5-log.h` is the integration header between the main RAID5/RAID6 state machine, the RAID5 journal/write-back cache implementation in `raid5-cache.c`, and the partial parity log implementation. It declares the log/cache/PPL APIs and provides inline dispatch helpers that let RAID5 code call one logging interface regardless of whether an array has a journal device or PPL enabled.

## Important APIs, Types, and Functions
The header declares journal lifecycle and operation functions such as `r5l_init_log()`, `r5l_start()`, `r5l_exit_log()`, `r5l_write_stripe()`, `r5l_write_stripe_run()`, `r5l_flush_stripe_to_raid()`, `r5l_stripe_write_finished()`, `r5l_handle_flush_request()`, `r5l_quiesce()`, and `r5l_log_disk_error()`. It declares write-back cache helpers including `r5c_is_writeback()`, `r5c_try_caching_write()`, `r5c_finish_stripe_write_out()`, `r5c_release_extra_page()`, `r5c_use_extra_page()`, `r5c_handle_cached_data_endio()`, `r5c_cache_data()`, `r5c_make_stripe_write_out()`, `r5c_flush_cache()`, `r5c_check_stripe_cache_usage()`, `r5c_check_cached_full_stripe()`, `r5c_update_on_rdev_error()`, `r5c_big_stripe_cached()`, and sysfs entry `r5c_journal_mode`.

For PPL it declares `ppl_init_log()`, `ppl_exit_log()`, `ppl_write_stripe()`, `ppl_write_stripe_run()`, `ppl_stripe_write_finished()`, `ppl_modify_log()`, `ppl_quiesce()`, `ppl_handle_flush_request()`, and sysfs entry `ppl_write_hint`. It also exposes `ops_run_partial_parity()`, which is shared with parity-operation code.

Inline helpers are `raid5_has_log()`, `raid5_has_ppl()`, `log_stripe()`, `log_stripe_write_finished()`, `log_write_stripe_run()`, `log_flush_stripe_to_raid()`, `log_handle_flush_request()`, `log_quiesce()`, `log_exit()`, `log_init()`, and `log_modify()`.

## Control Flow
The header itself has no standalone runtime, but its inlines are on the RAID5 hot path. `log_stripe()` first checks `conf->log`: if the stripe is not in write-back caching phase it sends write-out phase stripes to `r5l_write_stripe()`, unless an extra page is still required; if the stripe is caching and `STRIPE_LOG_TRAPPED` is set, it sends data-only caching writes to `r5c_cache_data()`. If no journal object exists but the array has `MD_HAS_PPL`, it calls `ppl_write_stripe()`. Other helpers similarly choose journal first, then PPL, then no-op or `-ENODEV`/`-EAGAIN` defaults.

## State and Persistence Behavior
This header does not own state. It tests persistent MD capability flags `MD_HAS_JOURNAL` and `MD_HAS_PPL`, and it routes calls based on `conf->log`, stripe state bits, and PPL state managed elsewhere. The persistence semantics are implemented by `raid5-cache.c` for journal/write-back cache and by the PPL implementation for partial parity logs.

## Dependencies and Integration Points
The declarations require RAID5 core types (`struct r5conf`, `struct r5l_log`, `struct stripe_head`, `struct stripe_head_state`, `struct raid5_percpu`), MD device types (`struct mddev`, `struct md_rdev`, `struct md_sysfs_entry`), block bios, sector types, and DMA async descriptors. This header is included by RAID5 code so it can remain agnostic to the active consistency mechanism while preserving fast inline dispatch.

## Risks and Edge Cases
Dispatch priority matters: when `conf->log` is present, journal/cache behavior is used even if PPL flags exist. `log_stripe()` returns `-EAGAIN` when a stripe cannot be handled by the current log/cache path, which the RAID5 state machine must interpret as a signal to continue normal write-out handling. The caching branch depends on `STRIPE_R5C_CACHING` and `STRIPE_LOG_TRAPPED` being set and cleared consistently by `raid5-cache.c`; stale bits could skip necessary logging or repeat a cache write. `log_init()` accepts either a journal device or PPL mode, so callers must ensure array metadata does not request conflicting modes.

## Test Signals
Compile tests should cover both journal and PPL configurations. Runtime signals include RAID5 writes with journal enabled, write-back caching writes, PPL-only arrays, flush request routing, quiesce and exit routing, journal mode sysfs visibility, PPL write-hint sysfs visibility, and fallback behavior when `conf->log` is absent or `log_stripe()` returns `-EAGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/raid5-log.h -->
