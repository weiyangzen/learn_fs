# File Research: sources/block-storage/linux-dm/drivers/md/raid5-log.h

## Purpose

`raid5-log.h` declares the log/cache and partial parity log hooks used by the MD RAID5/RAID6 implementation. It provides a small dispatch facade so the RAID5 stripe code can call a common set of helpers whether the array uses the dedicated RAID5 journal/cache (`r5l`/`r5c`) or partial parity log (`ppl`).

## Declared Interfaces

The header declares RAID5 journal/cache functions implemented primarily by `raid5-cache.c`:

- Log lifecycle: `r5l_init_log()`, `r5l_start()`, `r5l_exit_log()`.
- Log write and dispatch: `r5l_write_stripe()`, `r5l_write_stripe_run()`, `r5l_flush_stripe_to_raid()`, `r5l_stripe_write_finished()`.
- Flush/quiesce/error helpers: `r5l_handle_flush_request()`, `r5l_quiesce()`, `r5l_log_disk_error()`, `r5l_wake_reclaim()`.
- Write-back cache helpers: `r5c_is_writeback()`, `r5c_try_caching_write()`, `r5c_finish_stripe_write_out()`, `r5c_release_extra_page()`, `r5c_use_extra_page()`, `r5c_handle_cached_data_endio()`, `r5c_cache_data()`, `r5c_make_stripe_write_out()`, `r5c_flush_cache()`, `r5c_check_stripe_cache_usage()`, `r5c_check_cached_full_stripe()`, `r5c_update_on_rdev_error()`, `r5c_big_stripe_cached()`.
- Sysfs: `r5c_journal_mode`.

It also declares PPL interfaces implemented outside this file group:

- `ppl_init_log()`, `ppl_exit_log()`, `ppl_write_stripe()`, `ppl_write_stripe_run()`, `ppl_stripe_write_finished()`, `ppl_modify_log()`, `ppl_quiesce()`, `ppl_handle_flush_request()`, and `ppl_write_hint`.

The `ops_run_partial_parity()` declaration exposes a parity operation helper used by PPL or RAID5 operations.

## Inline Dispatch Helpers

`raid5_has_log()` tests `MD_HAS_JOURNAL`; `raid5_has_ppl()` tests `MD_HAS_PPL`.

`log_stripe()` chooses how a stripe is protected:

- If `conf->log` exists and the stripe is not in `STRIPE_R5C_CACHING`, it calls `r5l_write_stripe()` unless an extra page is still pending.
- If `conf->log` exists and the stripe is caching with `STRIPE_LOG_TRAPPED`, it calls `r5c_cache_data()`.
- If there is no journal but PPL is enabled, it calls `ppl_write_stripe()`.
- Otherwise it returns `-EAGAIN` so the caller proceeds without this log path.

Other inline helpers dispatch completion, run, flush, flush-request handling, quiesce, exit, init, and log modification:

- `log_stripe_write_finished()`
- `log_write_stripe_run()`
- `log_flush_stripe_to_raid()`
- `log_handle_flush_request()`
- `log_quiesce()`
- `log_exit()`
- `log_init()`
- `log_modify()`

## Dependencies And Integration

The header expects RAID5 types such as `struct r5conf`, `struct r5l_log`, `struct stripe_head`, `struct stripe_head_state`, and `struct raid5_percpu` to be visible to the including implementation. It also depends on MD flags (`MD_HAS_JOURNAL`, `MD_HAS_PPL`), stripe flags (`STRIPE_R5C_CACHING`, `STRIPE_LOG_TRAPPED`), block bios, sysfs entries, DMA async descriptors, and MD rdev structures.

It is included by RAID5 implementation code so the stripe state machine can remain agnostic to whether it is using journal/cache or PPL, while still preserving the special write-back caching phase rules.

## Notable Risks And Invariants

- `conf->log` takes precedence over PPL for most operations.
- `log_handle_flush_request()` passes `conf->log` to `ppl_handle_flush_request()` in the PPL branch; PPL implementations must tolerate the expected argument form from this shared facade.
- `log_stripe()` intentionally returns `0` without logging if `s->waiting_extra_page` is true in writing-out phase, delaying the stripe until the needed page is available.
- Callers must only use cache-specific helpers when write-back state and stripe flags match the RAID5 cache state machine.

## Testing Signals

Tests should cover all facade branches: journal write-through, write-back caching, PPL-only arrays, arrays without log/PPL returning `-EAGAIN`, flush-only bios, quiesce, exit/init selection, and log modification for PPL-enabled arrays.
