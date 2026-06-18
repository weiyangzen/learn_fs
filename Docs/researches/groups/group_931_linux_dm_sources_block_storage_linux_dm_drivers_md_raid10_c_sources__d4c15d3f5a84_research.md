# Group Research: group_931_linux_dm_sources_block_storage_linux_dm_drivers_md_raid10_c_sources__d4c15d3f5a84

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/linux-dm`, which is included in Research Subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid10.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid10.c

## Purpose

`raid10.c` implements the Linux MD RAID10 personality: a striped mirror layout with configurable near copies, far copies, offset copies, and far-set placement. It registers an `md_personality` named `raid10` and provides the full lifecycle surface used by MD core: request submission, status, error handling, hot add/remove, spare activation, sync/recovery, reshape, resize, takeover from RAID0, quiesce, and module init/exit.

## Main Data And State

The central runtime object is `struct r10conf`, allocated by `setup_conf()` and stored in `mddev->private`. Per-request state is `struct r10bio`. State bits in `r10bio->state` drive async continuation in `raid10d()`: read retry, write error cleanup, sync, recovery, reshape, degraded writes, previous-layout I/O, failfast, and discard.

## Key Behavior

`__raid10_find_phys()` maps virtual sectors to all copy locations across near/far/offset/far-set layouts. `raid10_find_phys()` selects current or previous geometry during reshape, and `raid10_find_virt()` reverses physical-to-virtual mapping for recovery.

`raid10_make_request()` handles flushes, write accounting, discard optimization, chunk-boundary splitting, and dispatches reads/writes. Reads use `read_balance()` to avoid faulty, unrecovered, blocked, or bad-block regions and choose a mirror by pending count, head position, or far-copy address. Writes map all copies, wait for barriers and reshape safety, pin live main/replacement devices, avoid bad-block ranges, start bitmap writes, and submit cloned bios per copy.

The file implements its own barrier protocol around normal I/O versus sync/recovery/reshape. `raid10d()` drains pending writes and retry work, then dispatches based on `r10bio` state to read-error repair, write cleanup, sync, recovery, or reshape continuation.

## Recovery, Resync, And Reshape

`raid10_sync_request()` handles logical resync, physical recovery, and delegates reshape. Resync reads all copies, compares pages, and repairs mismatches unless check-only. Recovery walks physical sectors, maps to readable virtual copies, and writes missing/out-of-sync or replacement targets.

Reshape supports near/offset-style layouts, not classic far layouts. `raid10_start_reshape()` commits new geometry, validates data-offset separation, resizes bitmaps, adds spares, recalculates degradation, and starts `md_do_sync`. `reshape_request()` copies chunks from previous to new layout with persisted safety checkpoints.

## Risks And Invariants

`rdev` access relies on the documented RCU plus `nr_pending` contract. Barriers must remain balanced or the array can hang. Reshape safety depends on correct `reshape_position`, `reshape_safe`, and `offset_diff`. Bad-block handling intentionally splits and narrows bios. Replacement promotion uses memory barriers so readers do not observe both main and replacement absent.

<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid10.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid10.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid10.h

## Purpose

`raid10.h` defines private RAID10 structures and request state bits used by `raid10.c` and shared RAID1/RAID10 helpers.

## Structures

`struct raid10_info` represents one mirror slot: primary `rdev`, optional `replacement`, read-balancing `head_position`, and `recovery_disabled`. The header documents that `rdev` may be cleared asynchronously and must be accessed under `reconfig_mutex`, known recovery/reshape context, or RCU with `nr_pending` acquired before dropping RCU.

`struct r10conf` is per-array state: MD backpointer, mirror arrays, geometry/current-previous reshape state, retry and completion lists, pending writes, barrier counters, resync pools, temp page, split bioset, takeover thread, and clustered resync bounds.

`struct r10bio` wraps normal I/O and background work. It tracks completion count, virtual sector/length, state bits, master bio, read slot, retry linkage, and per-copy `r10dev` entries.

## State Bits

`enum r10bio_state` classifies completion and retry behavior: uptodate, sync, recover, reshape, degraded, read error, made-good bad blocks, write error, previous-layout I/O, failfast, and discard.

## Risks

Allocation size for flexible `r10bio.devs[]` must match geometry. The `r10dev` union is operation-sensitive: reads use `rdev`, while writes/resync use `repl_bio`. Mirror pointer lifetime is the main concurrency hazard.

<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid10.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-cache.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid5-cache.c

## Purpose

`raid5-cache.c` implements the RAID5/RAID6 journal and write-back cache for MD RAID5. It covers journal initialization, metadata formatting, write-through journaling, write-back caching, cache flush/reclaim, crash recovery/replay, sysfs mode switching, and helper hooks consumed through `raid5-log.h`.

## Main State

`struct r5l_log` is the per-array log/cache object: journal device, CRC seed, ring head/tail, current I/O unit, ordered I/O-unit lists, flush bio, no-memory/no-space queues, mempools, reclaim thread, journal mode, cached stripe list, work items, and a radix tree tracking cached chunk-sized “big stripes”.

`struct r5l_io_unit` represents one metadata block and payload pages. It moves monotonically through running, I/O-started, I/O-ended, and stripe-ended states. `struct r5l_recovery_ctx` supports crash replay with a metadata page, recovery position/sequence, cached stripes, and a read-ahead pool.

## Write And Cache Flow

`r5l_write_stripe()` journals writing-out stripes, calculating data/parity checksums and appending payload metadata/pages. `r5c_cache_data()` journals data-only write-back stripes. `r5l_submit_current_io()` seals metadata with CRC and submits it, deferring flush/FUA units until ordering allows.

Completion preserves strict I/O-unit order. Journaled stripes are only run to RAID after earlier metadata is persistent; if write-cache flush is needed, `r5l_flush_stripe_to_raid()` submits a PREFLUSH before running stripes.

`r5c_try_caching_write()` enters write-back caching for clean overwrite stripes, tracks cached big stripes in a radix tree, and requests biodrain. `r5c_finish_stripe_write_out()` clears journal residency, updates counters/tree membership, appends flush payloads, and wakes overlap/sync waiters as needed.

## Reclaim And Recovery

Reclaim has two layers. `r5c_do_reclaim()` flushes cached stripes under stripe-cache or log pressure. `r5l_do_reclaim()` advances checkpoints, writes superblock state, optionally discards freed log space, updates log state, and releases no-space stripes.

Crash recovery scans validated metadata blocks, verifies payload checksums, replays data-parity stripes directly, loads data-only stripes into cache, rewrites data-only stripes to a safe new sequence range, advances the journal tail, and then flushes recovered cached stripes through the normal state machine.

## Configuration

`r5c_journal_mode` exposes `write-through` and `write-back`. `r5c_journal_mode_set()` rejects write-back on degraded arrays and suspends/resumes the array around mode changes. `r5c_update_on_rdev_error()` asynchronously disables write-back on degradation or journal failure.

`r5l_init_log()` validates 4 KiB pages and metadata capacity, allocates pools/bioset/log state, starts reclaim, publishes `conf->log` with RCU, and sets `MD_HAS_JOURNAL`. `r5l_start()` loads or recovers the log. `r5l_exit_log()` tears it down.

## Risks

Correctness depends on ordered I/O-unit progression, accurate log-space reservations, synchronized `stripe_in_journal_list` and radix-tree membership, disabling write-back for degraded arrays, and exact recovery parsing/checksum validation. The implementation rejects unsupported page sizes and overly large arrays whose metadata cannot fit in one page.

<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-log.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid5-log.h

## Purpose

`raid5-log.h` declares RAID5 journal/cache and partial parity log interfaces and provides inline dispatch helpers so RAID5 code can use either the `r5l`/`r5c` journal/cache path or the PPL path.

## Interfaces

It declares journal/cache lifecycle, write, flush, quiesce, reclaim, write-back cache, recovery-support, sysfs, and error hooks implemented primarily by `raid5-cache.c`. It also declares PPL hooks implemented elsewhere and `ops_run_partial_parity()`.

## Inline Dispatch

`raid5_has_log()` tests `MD_HAS_JOURNAL`; `raid5_has_ppl()` tests `MD_HAS_PPL`.

`log_stripe()` routes to `r5l_write_stripe()` for writing-out journal stripes, `r5c_cache_data()` for trapped caching-phase stripes, or `ppl_write_stripe()` for PPL. Related helpers dispatch stripe completion, run, flush, flush-request handling, quiesce, exit, init, and log modification.

## Risks

`conf->log` takes precedence over PPL. `log_stripe()` intentionally delays when an extra page is pending. Callers must preserve RAID5 cache state-machine flags. The PPL flush branch passes `conf->log` through the shared facade, so the PPL implementation must match that expected calling convention.

<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5-log.h -->