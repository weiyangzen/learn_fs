# File Research: sources/block-storage/linux-dm/drivers/md/raid5-cache.c

## Purpose

`raid5-cache.c` implements the RAID5/RAID6 journal and write-back cache used by the MD RAID5 personality. It provides log-device initialization, metadata formatting, write-through journaling, write-back caching, cache flush/reclaim, crash recovery/replay, sysfs mode switching, clustered state interactions through MD core, and helper hooks consumed by the RAID5 stripe state machine through `raid5-log.h`.

The file stores journal metadata and payloads in fixed 4 KiB blocks (`BLOCK_SECTORS == 8`) and explicitly supports only `PAGE_SIZE == 4096`.

## Major Runtime Objects

`struct r5l_log` is the per-array journal/cache state. It stores the journal `rdev`, UUID CRC seed, rounded log-device size, reclaim threshold, log tail (`last_checkpoint`, `last_cp_seq`), log head (`log_start`, `seq`), next checkpoint, current in-progress I/O unit, ordered I/O-unit lists, flush bio, no-memory and no-space stripe queues, mempools, reclaim thread, write-back mode, cached stripe list, deferred work, writeback-disable work, and a radix tree used to detect cached chunk-sized "big stripes".

`struct r5l_io_unit` is one metadata block plus its associated payload pages. It tracks meta page/offset, current bio, pending stripes, sequence and log range, ordered list membership, stripes attached to the I/O unit, flush/FUA flags, deferred submission state, and flush-only bios.

The I/O-unit state machine is monotonic: `IO_UNIT_RUNNING` to `IO_UNIT_IO_START` to `IO_UNIT_IO_END` to `IO_UNIT_STRIPE_END`, enforced by `__r5l_set_io_unit_state()`.

`struct r5l_recovery_ctx` is a recovery-only scanner context containing the current meta page, recovery log position/sequence, counts of recovered data-parity and data-only stripes, cached stripe list, and a read-ahead page pool.

## Write-Through And Write-Back Model

The top-level comment defines two stripe phases:

- Writing-out phase: parity is calculated, data/parity are journaled, data/parity are written to RAID disks, and upper writes complete.
- Caching phase: write-back cache commits write data to the journal and completes upper I/O without immediately writing RAID disks.

`r5c_is_writeback()` tests whether the log is present and in write-back mode. The sysfs attribute `r5c_journal_mode` exposes `write-through` and `write-back`, backed by `r5c_journal_mode_show()`, `r5c_journal_mode_store()`, and exported `r5c_journal_mode_set()`. Write-back mode is rejected when the array is degraded.

`r5c_update_on_rdev_error()` schedules asynchronous write-back disable if the array becomes degraded or the journal device errors.

## Log Ring And Space Accounting

`r5l_ring_add()` and `r5l_ring_distance()` implement wraparound arithmetic over the journal area. `r5l_has_free_space()` compares used log space between checkpoint and head against a reservation.

`r5c_log_required_to_flush_cache()` estimates worst-case log space needed to flush all cached stripes. `r5c_update_log_state()` sets or clears `R5C_LOG_TIGHT` and `R5C_LOG_CRITICAL` according to free space versus that estimate and wakes reclaim when leaving critical state. These bits influence whether new stripes can enter the journal or must wait in `no_space_stripes`.

`r5c_calculate_new_cp()` chooses the next checkpoint. In write-through mode it uses `log->next_checkpoint`; in write-back mode it uses the first stripe still present in `stripe_in_journal_list`, because earlier journal space cannot be reused while cached data-only stripes still depend on it.

## Logging New Stripe Data

`r5l_get_meta()` ensures a current metadata block has room or creates a new one with `r5l_new_meta()`. New metadata blocks carry magic, version, sequence, position, and later a CRC computed in `r5l_submit_current_io()`.

`r5l_append_payload_meta()` appends data or parity payload descriptors with target location and CRCs. `r5l_append_payload_page()` appends the corresponding page to the current bio and splits the bio if the ring wraps. `r5l_append_flush_payload()` appends a flush marker for a stripe after it has been written to RAID disks, avoiding extra journal writes during quiesce.

`r5l_log_stripe()` is the common writer. It appends all selected data pages and parity pages, records flush/FUA requirements, links the stripe into the current I/O unit, increments pending stripe count, and for write-back mode adds the stripe to `stripe_in_journal_list` on first journal residency.

`r5l_write_stripe()` is the write-through/writing-out entry from the RAID5 state machine. It rejects unsupported cases such as batched stripes, missing parity write intent, and syncing stripes. It calculates page CRCs, sets `STRIPE_LOG_TRAPPED`, reserves log space, and either logs the stripe, queues it for no-memory retry, or queues it behind reclaim. Write-back mode is more conservative when log space is critical and the stripe is not already cached.

`r5c_cache_data()` logs data-only pages for caching-phase write-back stripes and follows the same no-space/no-memory fallback rules.

`r5l_write_stripe_run()` closes and submits the current I/O unit.

## I/O Completion And Ordering

`r5l_do_submit_io()` transitions an I/O unit to I/O-start and submits split and current bios, applying PREFLUSH/FUA flags. Journal-device errors call `md_error()` but still let stripe processing continue so the RAID5 state machine can make progress.

`r5l_log_endio()` frees the written meta page, marks the I/O unit complete, and either moves ordered I/O units to `io_end_ios` for later cache flush or immediately runs their stripes. It also dispatches deferred flush/FUA I/O once ordering permits and completes flush-only bios.

Ordering is strict: stripes from an I/O unit are only written to RAID disks when all earlier journal metadata is persistent. `r5l_log_run_stripes()` and `r5l_move_to_end_ios()` preserve list order and stop at the first not-yet-complete I/O unit.

When write caches require a flush before RAID writes, `r5l_flush_stripe_to_raid()` moves `io_end_ios` into `flushing_ios`, submits `flush_bio` with `REQ_PREFLUSH`, and `r5l_log_flush_endio()` then runs those stripes and moves units to `finished_ios`.

`r5l_stripe_write_finished()` and `__r5l_stripe_write_finished()` mark I/O units as stripe-ended after all attached stripes finish writing to RAID. `r5l_complete_finished_ios()` advances `next_checkpoint`, frees completed I/O units, and wakes no-memory stripes.

## Write-Back Cache Stripe Management

`r5c_try_caching_write()` tries to handle RAID5 writes entirely in caching phase. It enters caching state for clean stripes, rejects degraded/syncing/non-overwrite cases into writing-out phase, records cached big-stripe membership in a radix tree, sets `R5_Wantwrite`, `R5_Wantdrain`, `R5_LOCKED`, and requests `STRIPE_OP_BIODRAIN` so data is drained to journal.

`r5c_make_stripe_write_out()` leaves caching phase and marks preread active. `r5c_finish_stripe_write_out()` clears `R5_InJournal`, overlap flags, pending full-write counters, journal-list membership, big-stripe radix counts, cached/full/partial counters, appends a flush payload, and re-handles sync-requested stripes now that cache data has reached RAID disks.

`r5c_check_stripe_cache_usage()` and `r5c_check_cached_full_stripe()` wake reclaim under stripe-cache pressure or when enough full stripes are cached. `r5c_flush_cache()` selects full stripes first, then partial stripes, and `r5c_flush_stripe()` moves them into active handle state for writing-out.

`r5c_big_stripe_cached()` lets chunk-aligned reads avoid chunks that have dirty write-back data in the radix tree.

`r5c_handle_cached_data_endio()` completes upper write bios after data-only cache logging, marks devices uptodate, and ends bitmap writes. `r5c_release_extra_page()` and `r5c_use_extra_page()` manage temporary original pages used by cache-related prexor/write-out paths.

## Reclaim

The reclaim thread callback `r5l_reclaim_thread()` runs `r5c_do_reclaim()` then `r5l_do_reclaim()`.

`r5c_do_reclaim()` flushes cached stripes under stripe-cache pressure, flushes stripes near the journal tail when log space is tight, releases no-space stripes when no longer critical, and wakes the RAID5 thread.

`r5l_do_reclaim()` waits until enough reclaimable space exists, computes the next checkpoint, writes the superblock via `r5l_write_super_and_discard_space()`, advances `last_checkpoint`, updates log state, and releases no-space stripes. `r5l_write_super_and_discard_space()` also discards freed journal regions when supported, after trying to force superblock persistence; comments document a trylock workaround to avoid deadlock with quiesce.

`r5l_wake_reclaim()` atomically raises the reclaim target and wakes the reclaim thread. `r5l_quiesce()` parks/unparks reclaim and forces reclamation during quiesce.

## Crash Recovery

`r5l_load_log()` validates the journal tail from `rdev->journal_tail`, checks magic/version/CRC/position, creates an empty superblock if needed, initializes log size and reclaim thresholds, then either starts fresh or calls `r5l_recovery_log()`.

Recovery uses a read-ahead pool (`r5l_recovery_allocate_ra_pool()`, `r5l_recovery_fetch_ra_pool()`, `r5l_recovery_read_page()`) to scan log blocks efficiently. `r5l_recovery_read_meta_block()` validates each metadata block by magic, version, sequence, position, meta size, and CRC.

`r5l_recovery_verify_data_checksum_for_mb()` verifies all data/parity pages for a metadata block before loading any of them. A checksum mismatch drops that whole metadata block's payloads but allows scanning to continue for later valid flushed data.

`r5c_recovery_analyze_meta_block()` interprets data, parity, and flush payloads. Data payloads load data pages into cached stripes and set caching state. Parity payloads load parity pages and mark writing-out state. Flush payloads remove already flushed stripes from the recovery cache. If stripe-cache allocation is tight, recovery may replay some stripes or grow the stripe cache.

`r5c_recovery_flush_log()` scans until an invalid metadata block, replays data-parity stripes directly to member and replacement devices, and leaves data-only stripes loaded into stripe cache. `r5c_recovery_rewrite_data_only_stripes()` rewrites data-only stripes to a new safe journal sequence range before changing the journal tail. `r5c_recovery_flush_data_only_stripes()` temporarily enables write-back mode so the stripe state machine flushes recovered data-only stripes to RAID.

The recovery sequence intentionally bumps sequence numbers by a large offset after the first invalid block to prevent a later recovery from treating stale valid-looking metadata after a rewritten block as contiguous log.

## Initialization And Teardown

`r5l_init_log()` validates page size and metadata capacity for the number of disks, allocates and initializes `r5l_log`, computes the UUID CRC seed, initializes lists/locks/work/mempools/bioset/radix tree, registers the reclaim thread, sets default mode to write-through, publishes `conf->log` with RCU, and sets `MD_HAS_JOURNAL`.

`r5l_start()` loads or recovers the log after initialization and calls `r5l_exit_log()` on failure. `r5l_exit_log()` clears `conf->log`, synchronizes RCU, wakes and flushes writeback-disable work, unregisters reclaim, destroys pools/bioset/cache, and frees the log object.

## Dependencies And Integration Points

This file depends on RAID5 structures and flags from `raid5.h`, MD core metadata and threading APIs from `md.h`, bitmap write completion, Linux block-layer bio/page APIs, CRC32C, radix tree APIs, RCU, workqueues, mempools, and MD sysfs entry wiring.

Its exported or externally referenced functions are declared in `raid5-log.h` and are invoked by RAID5 stripe handling, I/O submission, quiesce, recovery startup, sysfs, and degraded-device handling.

## Notable Risks And Invariants

- I/O-unit list order is a correctness requirement: later stripes must not be written to RAID before earlier journal metadata is persistent.
- The I/O-unit state machine must only move forward; `__r5l_set_io_unit_state()` warns on regressions.
- Log-space accounting must reserve enough space for cache flush under tight/critical conditions to avoid deadlock.
- Write-back mode must be disabled for degraded arrays; async disabling must coordinate with superblock updates and array suspension.
- `stripe_in_journal_list` and `big_stripe_tree` membership must stay synchronized with stripe flags and counters.
- Recovery treats checksum mismatch as a reason to drop one metadata block's payloads while continuing the scan; this preserves later flushed data but requires payload-size parsing to be exact.
- The implementation assumes 4 KiB pages and rejects unsupported arrays whose metadata descriptors cannot fit in one page.

## Testing Signals

Important test cases include write-through journal replay, write-back data-only replay, checksum-mismatch recovery, log wraparound and split bios, no-space reclaim, cache-pressure flush selection, degraded-mode writeback disable, null flush and FUA ordering, big-stripe cached read blocking, quiesce/reclaim interactions, and journal-device fault handling.
