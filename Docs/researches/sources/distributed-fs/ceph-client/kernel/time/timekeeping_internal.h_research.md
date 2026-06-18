# sources/distributed-fs/ceph-client/kernel/time/timekeeping_internal.h

## Purpose
This internal header defines private helpers for timekeeping debug support, safe clocksource delta calculation, timekeeper lock serialization, and NTP seconds access. It is shared by timekeeping implementation files rather than exposed as a general kernel API.

## Important APIs, types, and functions
Under `CONFIG_DEBUG_FS`, it declares per-CPU `timekeeping_mg_floor_swaps`, `timekeeping_inc_mg_floor_swaps()`, and `tk_debug_account_sleep_time()`. Without debugfs, those become no-op stubs. `clocksource_delta()` computes `(now - last) & mask` but returns zero if the delta exceeds `max_delta`, preventing backward or implausible jumps from advancing time. It also declares `timekeeper_lock_irqsave()`, `timekeeper_unlock_irqrestore()`, and `ktime_get_ntp_seconds()`.

## Control flow
The header provides inline control flow for debug and delta helpers. `clocksource_delta()` is used by timekeeping advancement paths to reject deltas beyond a clocksource-defined safe bound. Debug helpers either increment per-CPU counters or compile away depending on configuration.

## State and persistence behavior
The header itself owns no state, but it declares debug per-CPU counters and functions that manipulate core timekeeper state. `clocksource_delta()` enforces state safety by refusing large deltas rather than attempting recovery in place.

## Dependencies and integration points
It depends on clocksource, spinlock, and time definitions. It is included by `timekeeping.c` and `timekeeping_debug.c`; the delta helper is part of the core update path, and the debug hooks connect multigrain timestamp and suspend accounting to debugfs.

## Risks
Changing `clocksource_delta()` can directly affect time progression after clocksource anomalies, suspend, or cross-CPU inconsistencies. Returning zero on excessive deltas is conservative but can hide clocksource failures as stalled time. Debug conditional declarations must match the compiled implementation to avoid link or silent instrumentation issues.

## Test signals
Build coverage with and without `CONFIG_DEBUG_FS` is essential. Runtime signals include stable timekeeping under clocksource wrap conditions and debugfs counter visibility when enabled. Fault-injection or simulated clocksource tests can validate the max-delta guard.
