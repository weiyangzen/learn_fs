# Group Research: group_933_linux_dm_sources_block_storage_linux_dm_drivers_md_raid5_c_bf7a19e683e8

Scope checked against `Docs/research_subset_a.md`: the file is under `sources/block-storage/linux-dm`, which is included in Research Subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/raid5.c

Read completely: 8846 lines, 254763 bytes.

## Purpose

`raid5.c` implements the Linux MD RAID4, RAID5, and RAID6 personalities. It supplies the full MD personality surface for parity arrays: request submission, stripe-cache management, parity generation/check/repair, degraded I/O, read-error correction, write-error and bad-block handling, bitmap sequencing, discard, journal/PPL integration hooks, resync/recovery/replacement, reshape/resize, hot add/remove, quiesce, takeover, sysfs tuning, module registration, and teardown.

The file is the central stripe state machine for RAID456. It depends on private definitions in `raid5.h`, MD core in `md.h`, bitmap support in `md-bitmap.h`, RAID0 takeover metadata in `raid0.h`, and parity-log integration in `raid5-log.h`.

## Core Data Model

The central runtime object is `struct r5conf`, stored in `mddev->private`. It owns array geometry (`level`, `algorithm`, `raid_disks`, `previous_raid_disks`, chunk sizes, degradation tolerance), device slots (`struct disk_info` with main/replacement rdevs and extra pages), stripe hash table, inactive/handle/hold/delayed/bitmap lists, per-stripe locks, worker groups, percpu async scratch buffers, cache sizing state, reshape progress/safety checkpoints, pending aligned-read retry state, journal/cache counters, bitmap batch counters, and wait queues.

Each cached stripe is a `struct stripe_head`, allocated from a geometry-sized slab cache. A stripe records the logical stripe sector, generation, parity/Q/data indexes, device pages, per-device bios, state bits, refcount, batch linkage, journal/PPL fields, and operation targets. Per-device `struct r5dev` fields track `toread`, `towrite`, `written`, page/orig_page, physical sector, flags such as `R5_UPTODATE`, `R5_LOCKED`, `R5_Wantread`, `R5_Wantwrite`, `R5_Wantcompute`, `R5_InJournal`, bad-block/write-error markers, and replacement-read preference.

`struct stripe_head_state` is rebuilt by `analyse_stripe()` for each handle pass. It summarizes counts and decisions: locked/up-to-date blocks, pending reads/writes, failed members, sync/replacement/reshape mode, journal occupancy, blocked rdev, bad-block handling, and requested async operations.

## Stripe Cache And Scheduling

The file maintains a hash table of active stripes keyed by logical stripe sector and protected by multiple hash locks plus `device_lock`. `raid5_get_active_stripe()` either finds an existing stripe with the requested generation or pulls one from an inactive list, initializes mapping with `init_stripe()`, and handles cache exhaustion by setting allocation/reclaim flags and waiting.

Stripe release is optimized through an IRQ-safe lockless release list (`conf->released_stripes`) and block plug callbacks (`raid5_unplug()` / `release_stripe_plug()`). `do_release_stripe()` decides whether a stripe returns to inactive cache, handle queues, delayed lists, bitmap-delay lists, or RAID5-cache full/partial lists. The code is careful to keep `STRIPE_HANDLE`, `STRIPE_DELAYED`, `STRIPE_PREREAD_ACTIVE`, and cached-journal state balanced before dropping the final reference.

Work can run on the MD thread (`raid5d`) or optional NUMA worker groups (`raid5_do_work`). `__get_priority_stripe()` chooses handle, low-priority, or hold-list stripes and limits preread bypass so full-stripe writes do not starve delayed read-modify-write stripes. `handle_active_stripes()` processes stripes in bounded batches, flushes journal work, and releases completed stripes back to inactive lists.

## Layout Mapping

`raid5_compute_sector()` maps a logical array sector to a physical stripe sector and data disk index. It supports RAID4 fixed parity, RAID5 left/right symmetric/asymmetric layouts, parity-at-0/parity-at-N layouts, RAID6 rotating layouts, DDF restart/continue algorithms, and RAID6 variants with Q fixed at the last disk.

`raid5_compute_blocknr()` performs the reverse mapping from a stripe member index back to the logical array sector and verifies the round trip by calling `raid5_compute_sector()`. `stripe_set_idx()` initializes `pd_idx`, `qd_idx`, and DDF layout fields for a stripe generation. Mapping is generation-aware during reshape through current and previous chunk/layout/disk counts.

`raid5_size()` computes usable array sectors from member sectors, chunk alignment, and data disk count, using the smaller of old/new disk counts while reshape is active.

## Request Path

`raid5_make_request()` is the personality entry point. It handles flushes through `log_handle_flush_request()` or MD flush fallback, starts MD write accounting, tries chunk-aligned direct reads on clean non-reshaping arrays, handles discard separately, splits logical bios across stripe boundaries, resolves reshape old/new mapping with `gen_lock`, attaches bios to stripe device queues with `add_stripe_bio()`, and schedules stripes.

`add_stripe_bio()` inserts bios into per-device ordered chains, rejects overlaps, enforces PPL’s consecutive-data-chunk requirement, records write hints, marks full-overwrite coverage, starts bitmap writes for first writes in a stripe, and can batch adjacent full-stripe writes when no journal/PPL is active.

Chunk-aligned reads (`chunk_aligned_read()` / `raid5_read_one_chunk()`) bypass the stripe cache when the target member is in sync, no reshape is active, no bad blocks are present, and the r5cache does not hold a big cached stripe. Failed aligned reads are retried through the normal stripe path by `retry_aligned_read()`.

Discard handling (`make_discard_request()`) is conservative: it is disabled during reshape, works at whole-stripe granularity, waits for sync/overlap conflicts, marks all data members as overwrite/discard writes, starts bitmap accounting, and relies on queue setup plus the `devices_handle_discard_safely` module parameter before advertising discard support.

## Stripe State Machine

`handle_stripe()` is the main state machine. It prevents concurrent handlers with `STRIPE_ACTIVE`, breaks failed batches, promotes sync requests, analyzes all member devices, blocks on pending superblock/bad-block updates, schedules biofill for completed read data, fails impossible stripes, completes write returns, handles cached data endio, reads or computes missing data, dispatches new writes, runs parity check/repair, writes replacement devices, completes sync/replacement, repairs read errors by rewrite/readback, handles reshape expansion, processes bad-block side effects, launches async operations, submits bios, and then clears active state.

`analyse_stripe()` derives per-stripe truth from rdev and replacement state under RCU. It prefers sufficiently recovered replacements for reads, detects blocked rdevs or blocked bad-block logs, determines `R5_Insync`, tracks write-error/made-good flags requiring process-context bad-block updates, counts failed members, and decides whether sync is recovery, replacement, or ordinary resync.

Read service is split between `handle_stripe_fill()`, `need_this_block()`, and `fetch_block()`. The code reads blocks needed for pending reads, partial writes, sync/replacement, degraded reconstruction, or expansion. When enough data is already available it schedules compute operations instead of device reads, including RAID6 two-failure recovery paths.

Write service is split between `handle_stripe_dirtying()` and `schedule_reconstruction()`. The implementation chooses read-modify-write or reconstruct-write by counting required prereads, honoring `rmw_level`, degraded constraints, recovery checkpoint safety, journal/cache restrictions, and full-stripe overwrites. It then schedules prexor, biodrain, partial-parity capture, and parity reconstruction as needed.

## Async Operations

`raid_run_ops()` dispatches the requested async pipeline using per-CPU scratch buffers and the async_tx API:

- `ops_run_biofill()` copies stripe-cache pages into completed read bios.
- `ops_run_compute5()` and `ops_run_compute6_*()` reconstruct missing RAID5/RAID6 blocks.
- `ops_run_prexor5()` and `ops_run_prexor6()` prepare read-modify-write parity deltas.
- `ops_run_partial_parity()` is called for PPL before data drain where applicable.
- `ops_run_biodrain()` copies write bio data into stripe pages and marks FUA/sync/discard properties.
- `ops_run_reconstruct5()` and `ops_run_reconstruct6()` generate P or P+Q parity for writes, expansion, or repair.
- `ops_run_check_p()` and `ops_run_check_pq()` validate parity during check/repair.
- `ops_run_io()` submits actual member-device reads, writes, replacement writes, and discards.

The operation completions transition `check_state` and `reconstruct_state`, mark targets up-to-date, clear run bits, and requeue the stripe for another handle pass.

## Error Handling And Bad Blocks

`raid5_end_read_request()` marks successful reads up-to-date, clears corrected read-error state, resets read error counters, and handles journal orig-page reads. Failed reads increment read-error counters unless protection-specific, decide whether to retry, mark read-no-merge for narrow retries, set `R5_ReadError`, record uncorrectable bad blocks when possible, or fail the rdev with `md_error()`.

`raid5_end_write_request()` handles main and replacement writes differently. Replacement write failures fail the replacement. Main write failures mark the stripe degraded, set `WriteErrorSeen`, set `R5_WriteError`, and request replacement recovery. Successful writes over known bad blocks set made-good flags so `handle_stripe()` can clear bad-block records later.

`raid5_error()` refuses to fail an in-sync device if that would exceed redundancy, otherwise marks the rdev faulty/blocked, recalculates degradation, requests metadata updates, interrupts recovery, logs the failure, and notifies the r5cache layer.

`handle_failed_stripe()` fails all pending writes and written bios on a stripe that cannot be served, records read-error bad blocks where possible, fails unreadable reads when the array has exceeded redundancy, ends bitmap writes, clears locks, and updates pending full-write accounting. `handle_failed_sync()` aborts or completes recovery/sync and records bad blocks on rebuilding targets when possible.

## Bitmap, Journal, PPL, And Cache Integration

The opening bitmap comment documents the batch protocol around `seq_flush`, `seq_write`, and `bm_seq`. Writes set `STRIPE_BIT_DELAY` until bitmap updates have been unplugged; `raid5d()` advances bitmap batches, calls `md_bitmap_unplug()`, and activates delayed stripes only after the relevant bitmap batch is durable.

Journal and write-back cache integration is abstracted through `raid5-log.h` helpers such as `log_init()`, `log_stripe()`, `log_write_stripe_run()`, `log_flush_stripe_to_raid()`, `r5c_try_caching_write()`, `r5c_finish_stripe_write_out()`, `r5c_make_stripe_write_out()`, and cache-list counters. The stripe machine treats journal-trapped stripes, cached full/partial stripes, log pressure, log failure, and cached data endio as first-class states.

PPL is enabled through the same log abstraction when `MD_HAS_PPL` is set. This file allocates `ppl_page` per stripe, restricts PPL write ranges in `add_stripe_bio()`, requests `STRIPE_OP_PARTIAL_PARITY` before draining non-full writes, exposes the PPL write-hint sysfs attribute, and allows runtime consistency-policy switching between `ppl` and `resync` where valid.

## Sync, Recovery, Replacement, And Reshape

`raid5_sync_request()` handles resync/recovery/replacement at stripe granularity. It skips clean bitmap-covered stripes, requests sync on stripes with `STRIPE_SYNC_REQUESTED`, prevents quiesce conflicts, tracks still-degraded recovery for bitmap accounting, and delegates reshape work to `reshape_request()`.

`reshape_request()` performs RAID456 reshape in chunks. It creates destination stripes in the new layout, marks them expanding, zero-fills blocks beyond the old array size, advances `reshape_progress`, marks source stripes in the previous layout, copies data through `handle_stripe_expansion()`, updates metadata checkpoints when crash-safety requires it or every 10 seconds, and records `reshape_safe` once the superblock update is complete.

`raid5_start_reshape()` validates device availability, stripe cache capacity, and array size, commits new geometry under `gen_lock`, suspends/resumes to drain old assumptions, adds spares for expansions, recalculates degradation, sets recovery bits, and starts `md_do_sync` as a reshape thread. `end_reshape()` and `raid5_finish_reshape()` finalize geometry, recovery offsets, layout/chunk fields, disk count changes, and queue I/O hints.

`raid5_spare_active()`, `raid5_add_disk()`, and `raid5_remove_disk()` manage main and replacement rdevs. Replacement promotion uses RCU assignment and memory barriers so readers may see duplicate pointers but should not see neither pointer. Journal devices are treated specially through `log_init()`, `r5l_start()`, `log_modify()`, and `log_exit()`.

## Startup, Configuration, And Teardown

`setup_conf()` validates level/layout/chunk size, allocates `r5conf`, pending bio records, disk slots and extra pages, biosets, hash tables, per-CPU scratch buffers, stripe slab/cache, shrinker, worker structures, and the private MD thread. It binds existing rdevs and replacements, computes current/previous geometry, initializes RAID5/6 parity policy, and sizes the initial stripe cache.

`raid5_run()` initializes accounting, validates journal/bitmap/PPL combinations, validates reshape restart safety, rejects unsafe dirty degraded starts unless explicitly allowed or protected by PPL, sets array size and queue limits, advertises discard only under strict conditions, starts reshape if already in progress, creates sysfs attributes, and initializes the journal/PPL layer.

`free_conf()` tears down log state, shrinker, worker groups, stripe cache, percpu hotplug state, disk extra pages, biosets, hash tables, pending data, and configuration memory. `raid5_free()` also exits MD accounting and records that sysfs attributes should be removed.

Sysfs controls include stripe cache size, active stripe count, preread bypass threshold, group thread count, skip-copy/stable-writes behavior, RMW policy, stripe size on non-default page-size builds, r5cache journal mode, and PPL write hint.

## Personality Registration And Takeover

The file registers three MD personalities: `raid4`, `raid5`, and `raid6`. All share the same request, run, start, free, status, error, disk hotplug, spare activation, sync, resize, reshape, quiesce, and consistency-policy code, with level-specific reshape validation and takeover functions.

Takeover support includes RAID0-to-RAID4/5 for single-zone RAID0, RAID1-to-RAID5 for two-drive arrays, RAID4-to-RAID5, RAID5-to-RAID4 when parity is fixed at N, RAID6-to-RAID5 for compatible Q-at-end layouts, and RAID5-to-RAID6 through corresponding `_6` layouts. The module allocates a global `raid5wq`, registers CPU hotplug callbacks for percpu scratch buffers, registers personalities at init, and unregisters/destroys them at exit.

## Dependencies And Integration Points

Important external dependencies include MD core request/recovery/accounting APIs, rdev flags and bad-block APIs, MD bitmap APIs, r5cache/journal/PPL APIs, block-layer bio cloning/splitting/submission/queue-limit APIs, async_tx XOR/PQ engines, RAID6 syndrome helpers, RCU-protected device pointer access, CPU hotplug and percpu allocation, kernel shrinkers, workqueues, sysfs, trace remap events, and block plug callbacks.

## Notable Invariants And Risks

- Stripe refcounts, `STRIPE_ACTIVE`, `STRIPE_HANDLE`, release lists, and inactive lists must stay balanced; lost references or stale list bits can deadlock the stripe cache.
- Rdev access relies on RCU plus `nr_pending`, or on contexts where recovery/configuration rules make removal impossible.
- Bitmap batching must preserve `seq_flush`, `seq_write`, and per-stripe `bm_seq` ordering so writes are never issued before the corresponding bitmap bit is durable.
- RMW versus RCW selection is correctness-sensitive when parity may be dirty, the array is degraded, or r5cache/PPL state is present.
- RAID6 two-failure recovery depends on exact slot conversion between disk indexes, DDF syndrome order, and async RAID6 recovery helpers.
- Reshape safety depends on generation tracking, old/new mapping, `reshape_progress`, `reshape_safe`, `min_offset_diff`, metadata checkpoint timing, and blocking normal I/O in unsafe overlap windows.
- Discard is intentionally gated because parity arrays require discarded data to read back as zero or equivalent safe behavior.
- Batched full-stripe writes cannot be used with journal/PPL and must be broken on errors, expansion, overlap, or state transitions.

## Testing Signals

High-value coverage includes layout round trips for all RAID4/5/6 algorithms, degraded read/write with one and two failures, bad-block write-error/made-good transitions, aligned-read retry fallback, bitmap batch ordering, full-stripe batching and error breakup, RMW/RCW selection under dirty parity, PPL partial parity scheduling, r5cache write-back/log-failure paths, discard safety/alignment, replacement promotion races, resize/reshape forward and backward restart, sysfs tuning changes under load, and takeover validation for RAID0/1/4/5/6 conversions.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/raid5.c -->