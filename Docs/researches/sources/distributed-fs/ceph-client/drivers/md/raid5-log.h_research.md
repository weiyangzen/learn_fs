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
