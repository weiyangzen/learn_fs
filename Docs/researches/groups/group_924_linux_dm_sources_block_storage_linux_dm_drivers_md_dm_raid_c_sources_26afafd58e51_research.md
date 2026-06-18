# Group Research: group_924_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_raid_c_sources_26afafd58e51

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/linux-dm`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-raid.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-raid.c

## Purpose

`dm-raid.c` implements the Device Mapper `raid` target for MD-backed RAID0, RAID1, RAID10, RAID4, RAID5, and RAID6 mappings. It parses DM table syntax, owns the MD `mddev` lifecycle, manages component metadata devices and data devices, supports array activation, recovery, resize, reshape, takeover between compatible RAID levels, optional RAID4/5/6 journal devices, status output, and runtime sync-action messages.

## Core Model

`struct raid_set` is the target context. It embeds an MD `struct mddev`, the selected `raid_type`, constructor/runtime flags, requested disk counts and layout parameters, computed array/device sizes, optional RAID456 journal device state, and a flexible array of `raid_dev` entries. Each `raid_dev` owns a metadata `dm_dev`, data `dm_dev`, and MD `md_rdev`.

The target maintains separate constructor flags for options such as `sync`, `nosync`, `rebuild`, `daemon_sleep`, recovery-rate limits, RAID1 write-mostly/write-behind, RAID456 stripe cache, bitmap region size, RAID10 copies/format, `delta_disks`, `data_offset`, `journal_dev`, and `journal_mode`. Valid flags are constrained per RAID level.

## Table Parsing And Validation

Constructor syntax is:

`<raid_type> <#raid_params> <raid_params...> <#raid_devs> [<meta_dev> <data_dev>]...`

The parser validates chunk size, RAID-specific options, duplicate options, mutual exclusions such as `sync`/`nosync` and `rebuild` with sync directives, recovery-rate ordering, RAID10 copies/format, reshape disk deltas, data-offset alignment, journal-device size, and journal-mode dependency on `journal_dev`.

Device parsing supports `- -`, `- <data_dev>`, and `<meta_dev> <data_dev>`, but rejects `<meta_dev> -`. Metadata availability determines whether the MD array is persistent or external. Rebuild devices are marked out-of-sync with recovery offset zero, while normal devices start as in-sync until metadata overrides them.

## Metadata And Assembly

The DM RAID superblock uses magic `DM_RAID_MAGIC` and little-endian fields for array events, failed-device bitmaps, disk recovery offset, array resync offset, level, layout, chunk sectors, and v1.9 metadata extensions for reshape state, new layout, delta disks, array sectors, data offsets, device sectors, and extended failed-device bits.

`analyse_superblocks()` reads metadata devices, chooses the freshest superblock by event count, initializes new superblocks for first-use or rebuild devices, validates compatible/incompatible feature flags, restores recovery and reshape state, checks device reordering rules, marks failed devices, validates redundancy, and configures bitmap placement unless the set is RAID0 or journaled RAID456.

## Resize, Reshape, And Takeover

The file distinguishes first-use arrays, recovering arrays, ongoing reshapes, requested takeovers, requested reshapes, growth, shrink, and unchanged reloads. Takeover validation encodes allowed MD personality conversions, including selected RAID0/1/4/5/6/10 transitions and RAID10 layout restrictions.

Reshape support covers disk add/remove, layout changes, chunk-size changes, RAID1 mirror count changes, and out-of-place reshape using `data_offset`/`new_data_offset`. `rs_prepare_reshape()`, `rs_setup_reshape()`, and `rs_start_reshape()` coordinate constructor intent with MD personality `check_reshape` and `start_reshape`, update superblocks before reload-sensitive transitions, and adjust capacity before/after disk removal or growth.

## I/O, Suspend, Resume, And Status

`raid_map()` submits bios to MD with `md_handle_request()`, but requeues bios beyond current `mddev->array_sectors` during add-disk reshape. The target advertises one flush bio and conditionally one discard bio; RAID456 discard is disabled unless all devices support discard and the module parameter `devices_handle_discard_safely` is set.

`raid_preresume()` updates superblocks, loads dirty bitmaps, applies growth, resizes bitmaps, seeds recovery state, and starts reshape if requested. `raid_resume()` unfreezes recovery, resumes MD, and can attempt to restore previously faulty devices. `raid_postsuspend()` stops writes and suspends MD.

Status reports table reconstruction, IMA fields, health characters, sync/reshape progress, sync action, mismatch count, data offset, and journal status. Messages drive MD sync actions: `idle`, `frozen`, `resync`, `recover`, `check`, and `repair`.

## Invariants And Risks

- Metadata superblocks are authoritative unless constructor flags deliberately force sync/rebuild/new layout handling.
- `FirstUse` must be cleared before `md_run()` and superblocks must be updated before bitmap load when new devices or layout changes exist.
- `RT_FLAG_*` state gates one-time preresume/resume work, bitmap loading, superblock updates, reshape start, suspension, sync status, and growth.
- RAID10 layout math and reshape constraints are sensitive to near/far/offset copies and disk-count divisibility.
- RAID456 journaled sets cannot be reshaped or taken over.
- Discard on RAID456 is intentionally conservative because discard-zeroing uncertainty can corrupt parity assumptions.
- Capacity changes must occur at the correct point relative to forward/backward reshape to avoid I/O past component end.

## Test Focus

Test constructor grammar, invalid option combinations per RAID level, metadata/no-metadata cases, rebuild devices, failed-device superblock bits, first-use creation, old metadata upgrade, RAID10 format/copy validation, takeover matrix, grow/shrink reloads, out-of-place reshape offsets, interrupted reshape restart, RAID456 journal modes, discard gating, bitmap resize, suspend/resume idempotence, faulty device restoration, status/table/IMA output, and sync-action messages.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-raid1.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-raid1.c

## Purpose

`dm-raid1.c` implements the older Device Mapper `mirror` target. It mirrors writes to multiple legs, chooses readable mirrors for reads, uses a dirty-region log and region hash for synchronization state, performs resync through kcopyd, and optionally exposes leg/log errors to userspace for repair.

## Core Model

`struct mirror_set` owns mirror legs, queued reads/writes/failures/held bios, a `dm_region_hash`, kcopyd and dm-io clients, sync state, log and leg failure flags, suspend state, a default mirror index, a `kmirrord` workqueue, delayed wake timer, and table-event work. Each `struct mirror` stores its `dm_dev`, offset, error count, and error-type bitmap.

Features are `handle_errors` and `keep_log`; `keep_log` requires `handle_errors`. Without handled errors, the target may ignore some leg errors to preserve legacy behavior. With handled errors, failures trigger table events and failed writes may be held for userspace intervention.

## I/O Flow

Writes are always queued to `kmirrord`. The worker classifies writes by region state: clean/dirty regions are written to all mirrors, nosync regions go only to the default mirror, recovering regions are delayed, and remotely recovering regions are requeued with delayed wake. Before synchronized writes, pending counts are incremented and the dirty log is flushed.

Reads are direct-mapped when the region is in sync and an intact mirror is available. If the region is not known in sync, reads are queued to the worker unless they are readahead, which is killed. Failed reads are retried on an alternate mirror if possible after restoring the original bio details.

Flushes are issued to all mirrors via dm-io. Discards are issued to all mirrors but discard failures return `BLK_STS_NOTSUPP` without degrading the array.

## Recovery

Recovery copies a region from the default mirror to all other mirrors using kcopyd. `do_recovery()` asks the region hash to quiesce regions, starts copy work for quiesced regions, and marks the mirror set in sync once the dirty log sync count equals the number of regions.

`recovery_complete()` marks default read errors or destination write errors against the relevant mirrors, then ends the region-hash recovery with success or failure.

## Constructor And Lifecycle

Constructor syntax is:

`<log_type> <#log_params> <log_params...> <#mirrors> [<dev> <offset>]... [<#features> <features...>]`

It creates a dirty log, allocates the mirror set and region hash, opens mirror devices, sets max I/O length to the region size, advertises flush/discard support, allocates per-bio private data, starts the `kmirrord` workqueue, parses features, creates the kcopyd client, and wakes recovery.

Presuspend sets the suspend flag, drains held bios, stops recovery, waits for in-flight recovery, calls log presuspend, and flushes the worker. Resume clears suspend, resumes the log, and restarts recovery. Destruction drains timer/work, destroys kcopyd/workqueue, releases devices, destroys the region hash, and frees context.

## Invariants And Risks

- Dirty-log flush failure is sticky in `ms->log_failure` until userspace reload/intervention.
- Pending region counts are decremented in `mirror_end_io()`, not in the write callback.
- If the primary fails while out of sync and `keep_log` is disabled, reads may continue to target the same failing primary to avoid serving stale data.
- Held bios during handled-error paths are requeued on noflush suspend and failed otherwise.
- Read retry depends on successful `dm_bio_record()` before remapping.
- `kmirrord` is the serialization point for region-state updates, recovery scheduling, read fallback, writes, and failure handling.

## Test Focus

Test constructor parsing, feature validation, log creation failures, mirror device offsets, read balancing only for in-sync regions, read retry after leg failure, write classification by region state, log flush failure behavior, handled versus unhandled errors, `keep_log`, all-legs-dead behavior, discard failure semantics, recovery completion errors, suspend with held bios, noflush suspend requeue, status health characters, and table/IMA output.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-raid1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-region-hash.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-region-hash.c

## Purpose

`dm-region-hash.c` provides the dirty-region state machine used by the mirror target. It tracks which regions are clean, dirty, nosync, recovering, quiesced for recovery, recovered, or failed recovery, and coordinates delayed bios with dirty-log updates.

## Data Structures

`struct dm_region_hash` stores the region size/shift, dirty log, hash table, list locks, recovery concurrency limit, recovery semaphore, in-flight recovery count, clean/quiesced/recovered/failed lists, mempool, target offset, and callbacks for dispatching bios and waking workers/waiters.

`struct dm_region` stores the region key, state, hash/list nodes, pending I/O count, and delayed bios. Clean regions may be omitted from the hash, while dirty/nosync/recovering regions remain present until state transitions allow removal.

## State Transitions

`dm_rh_inc_pending()` allocates/fetches regions for normal writes, increments pending counts, turns clean regions dirty, removes them from the clean list, and marks the dirty log. Flush and discard bios are ignored for region pending counts.

`dm_rh_dec()` decrements pending counts. When a region reaches zero pending I/O, dirty regions become clean and move to `clean_regions`, recovering regions move to `quiesced_regions`, and regions affected by flush failure become nosync.

`dm_rh_update_states()` removes clean/recovered lists from the hash, clears dirty-log regions, completes successful or failed resync work, frees region objects, and flushes the dirty log.

## Recovery Coordination

`dm_rh_start_recovery()` releases `max_recovery` semaphore slots and wakes workers. `dm_rh_stop_recovery()` consumes those slots to stop new recovery. `dm_rh_recovery_prepare()` asks the dirty log for resync work, marks chosen regions recovering, and either moves already-quiesced regions to the quiesced list or waits for pending I/O to drain.

`dm_rh_recovery_start()` hands quiesced regions to the caller. `dm_rh_recovery_end()` places completed regions on the recovered or failed-recovered list and wakes workers. Completion dispatches delayed bios before waking recovery waiters so suspend cannot finish before queued work is visible.

## Invariants And Risks

- `hash_lock` protects the hash table; `region_lock` protects region state, lists, and delayed bios.
- Dirty-log errors from `in_sync()` are treated as nosync.
- `dm_rh_mark_nosync()` is not interrupt-safe and assumes the region hash entry exists for in-flight writes.
- Flush failure prevents later regions from being marked clean because durability ordering is uncertain.
- `recovery_in_flight` includes an extra reference during prepare to avoid racing stop-recovery.
- Destroy requires no quiesced regions and no pending I/O in remaining hash entries.

## Test Focus

Test clean-to-dirty-to-clean transitions, nosync marking after failed writes, flush failure effects, delayed bios for recovering regions, recovery semaphore start/stop behavior, failed recovery with handled/unhandled errors, dirty-log callback errors, hash allocation races, suspend wait ordering, and destroy assertions with pending/quiesced regions.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-region-hash.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-rq.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-rq.c

## Purpose

`dm-rq.c` implements request-based Device Mapper support on blk-mq. It creates the request queue/tag set, initializes per-request target I/O state, asks request-based targets to clone and map requests, dispatches cloned requests, handles partial bio completions, target endio decisions, requeue paths, statistics, and queue quiesce/unquiesce helpers.

## Request State

Each request has a `struct dm_rq_target_io` in the blk-mq PDU. It stores the mapped device, target, original request, clone request, deferred work field, error, target `map_info`, stats auxiliary data, start duration, sector count, and completed byte count.

Clone bios are allocated with a front-padded `struct dm_rq_clone_bio_info`, linking original bio, target I/O, and embedded clone bio. This supports partial completion accounting for cloned requests.

## Mapping And Completion

`dm_mq_queue_rq()` rejects requests during suspend, finds the immutable or live target, checks target busy state, starts the original request, initializes target I/O, sets `tio->ti`, and calls `map_request()`.

`map_request()` calls the target’s `clone_and_map_rq()`. Remapped requests are prepared with `blk_rq_prep_clone()`, traced, and inserted with `blk_insert_cloned_request()`. Resource errors clean up the clone and requeue the original. Submitted, requeue, delay-requeue, and kill outcomes are handled according to DM map return codes.

Clone completion reaches `end_clone_request()`, which completes the original request through blk-mq softirq. `dm_softirq_done()` calls `dm_done()` for mapped clones, allowing target `rq_end_io()` to return done, incomplete, immediate requeue, or delayed requeue. Completion updates stats, releases clone resources through target `release_clone_rq()`, ends the original request, and drops the mapped-device reference.

## Queue Setup

`dm_mq_init_request_queue()` allocates and initializes a blk-mq tag set with stacking/merge flags, configurable queue depth and hardware queue count, and PDU size equal to `dm_rq_target_io` plus any immutable target per-I/O data. Cleanup frees the tag set.

Module parameters include reserved request-based I/Os, blk-mq hardware queues, queue depth, and compatibility-only `use_blk_mq`.

## Invariants And Risks

- `dm_get()` in `dm_start_request()` must be balanced by `dm_put()` through `rq_completed()` at every completion or requeue path.
- Target-specific per-I/O data lives immediately after `dm_rq_target_io` when `per_io_data_size` is configured.
- Partial completion uses `blk_update_request()` rather than `blk_mq_end_request()` to preserve clone/original ordering.
- Target endio is skipped for unmapped clone failures marked with `RQF_FAILED`.
- Resource errors must unprepare and release clone requests before requeueing.
- Discard/write-same/write-zeroes target errors can disable unsupported features on the mapped device.

## Test Focus

Test map return codes, clone allocation failure, insert resource errors, target busy requeue, suspend requeue, partial bio completion, clone bio error propagation, rq_end_io requeue/delay/incomplete paths, stats accounting balance, per-I/O PDU setup, feature disabling on target errors, queue depth parameter bounds, and cleanup after init failures.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-rq.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-rq.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-rq.h

## Purpose

`dm-rq.h` is the internal header for request-based Device Mapper support.

## API And Data

It forward-declares `struct mapped_device` and defines `struct dm_rq_clone_bio_info`, the front-padded metadata used when cloning bios for request-based DM. The struct stores the original bio, associated `dm_rq_target_io`, and embedded clone bio. The embedded bio must remain last because allocation uses `bio_alloc_bioset()` front padding.

The header declares blk-mq request-queue setup/cleanup, queue start/stop helpers, requeue kicking, reserved request-based I/O count lookup, and compatibility sysfs attribute show/store functions for the deprecated sequential I/O merge deadline.

## Invariants And Risks

- `struct dm_rq_clone_bio_info` layout is ABI-like within the module: `clone` must stay last.
- Callers rely on queue helpers mapping directly to blk-mq quiesce/unquiesce and requeue behavior.
- The deprecated sysfs attributes are preserved for userspace compatibility even though they no longer tune a real heuristic.

## Test Focus

Test that request-based queue init users include this header consistently, clone-bio front padding resolves back to metadata correctly, queue start/stop invoke blk-mq behavior, requeue kick is exported, and compatibility attributes remain readable/writable.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-rq.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap-persistent.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap-persistent.c

## Purpose

`dm-snap-persistent.c` implements the persistent snapshot exception store. It records origin-to-COW chunk mappings on the COW device so snapshots survive reboot, supports committing new exceptions, reading metadata during activation, invalidating snapshots, merging committed exceptions back, and reporting COW usage.

## On-Disk Format

Chunk 0 contains `disk_header` with magic `SNAP_MAGIC`, validity flag, disk version, and chunk size. Metadata areas follow after the header. Each metadata area is one chunk containing `disk_exception` entries, and metadata chunks are interleaved with exception data chunks. A `new_chunk` value of zero terminates the exception list because chunk zero is reserved for the header.

All on-disk values are little-endian. Disk version is fixed at `SNAPSHOT_DISK_VERSION`; incompatible versions are rejected rather than migrated.

## Runtime State

`struct pstore` stores the exception store, version/valid flags, exceptions per area, current metadata area buffer, zero buffer, separate header buffer, current area index, next free chunk, committed-entry index, pending exception count, commit callbacks, dm-io client, and metadata workqueue.

Metadata I/O uses `dm_io`. Header/metadata chunk I/O can be routed through `ksnaphd` to avoid recursive `submit_bio_noacct()` when synchronous metadata I/O is initiated from sensitive paths. Existing metadata is read with dm-bufio and prefetches up to `DM_PREFETCH_CHUNKS`.

## Activation And Allocation

`persistent_read_metadata()` reads or initializes the header, adjusts chunk size if on-disk metadata overrides the table value, allocates callback storage sized to one metadata area, writes a new header and zeroes area 0 for fresh snapshots, rejects unsupported disk versions, returns invalid-snapshot state if `valid` is false, and otherwise reads all exception areas into the snapshot core via callback.

`persistent_prepare_exception()` checks COW space, assigns `e->new_chunk` from `next_free`, advances over metadata chunks using `skip_metadata()`, and increments pending exception count.

## Commit And Merge

`persistent_commit_exception()` writes the exception into the in-memory current area, records the completion callback, and waits until either all pending exceptions drain or the metadata area fills. If the area fills it zeroes the next area first, then writes the current metadata area with preflush/FUA/sync. On any metadata failure or invalid exception, `ps->valid` becomes false and callbacks are invoked with failure. Full areas advance to the next zeroed in-memory area.

Merge support works backwards from the latest committed exception. `persistent_prepare_merge()` returns a run of consecutive old/new chunk mappings from the current area, loading the previous area if needed. `persistent_commit_merge()` clears merged entries, writes the metadata area with preflush/FUA, decrements `current_committed`, and updates `next_free` for usage reporting.

## Constructor And Status

The constructor allocates `pstore`, initializes defaults, creates the `ksnaphd` workqueue, and accepts option `O` for userspace overflow support. The type is registered as both `persistent` and compatibility alias `P`. Table status emits `P` or `PO` plus chunk size.

## Invariants And Risks

- A valid snapshot depends on successfully writing metadata areas with ordering flags; failures mark the snapshot invalid.
- Chunk zero is never an exception data chunk and doubles as the exception-list terminator.
- `next_free` skips metadata chunks and is exact for allocation before merge; after merge it is mainly a conservative usage-reporting value.
- Callback batching assumes commit manipulation is not concurrent.
- Header writes use a separate buffer because invalidation can occur concurrently with metadata-area writes.
- Existing COW metadata chunk size can override the table-supplied chunk size, requiring buffer reallocation.

## Test Focus

Test fresh snapshot initialization, invalid magic, invalid version, on-disk chunk-size override, chunk-size validation, exception-list termination, dm-bufio prefetch bounds, COW full detection, metadata chunk skipping, out-of-order pending commits, metadata write failure invalidation, zero-next-area failure, callback success/failure batching, merge run detection, merge writes, overflow option parsing, drop-snapshot invalidation, and status output.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap-persistent.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap-transient.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap-transient.c

## Purpose

`dm-snap-transient.c` implements the non-persistent snapshot exception store. It allocates COW chunks sequentially in memory-only state and does not preserve exception metadata across reloads or reboot.

## Behavior

`struct transient_c` contains only `next_free`, the next COW sector to allocate. Metadata reading is a no-op. Preparing an exception checks whether the COW device has enough space for another chunk, assigns `e->new_chunk` from `next_free`, and advances `next_free` by the store chunk size.

Committing an exception immediately invokes the callback with the supplied validity value; no metadata is written. Usage reports allocated sectors as `next_free`, total sectors from the COW device size, and zero metadata sectors.

The constructor initializes `next_free` to zero. The type is registered as both `transient` and compatibility alias `N`. Table status emits `N <chunk_size>`.

## Invariants And Risks

- All exception mappings are volatile and must be reconstructed by the snapshot target’s in-memory state only for the active lifetime.
- Allocation is strictly sequential with no metadata reservations.
- COW exhaustion is detected by comparing `next_free + chunk_size` with the COW device size.
- Commit cannot fail due to store metadata because there is no persistent metadata.

## Test Focus

Test constructor/destructor, no-op metadata read, sequential chunk allocation, COW full handling, commit callback propagation of valid/invalid state, usage accounting, compatibility alias `N`, and table/IMA status output.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-snap-transient.c -->