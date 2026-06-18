# sources/distributed-fs/ceph-client/kernel/time/timekeeping_debug.c

## Purpose
This file provides debugfs and accounting support for timekeeping suspend diagnostics. It tracks suspend sleep-time duration bins and counts multigrain timestamp floor swaps for debug visibility.

## Important APIs, types, and functions
It defines per-CPU `timekeeping_mg_floor_swaps` and a `sleep_time_bin[NUM_BINS]` histogram. `tk_debug_sleep_time_show()` renders the sleep-time histogram through seq_file. `tk_debug_sleep_time_init()` creates the `sleep_time` debugfs file at late init. `tk_debug_account_sleep_time()` accounts one suspend duration and emits a deferred PM debug message. `timekeeping_get_mg_floor_swaps()` sums per-CPU floor swap counters using `data_race()`.

## Control flow
At late init, debugfs registration creates a read-only `sleep_time` file. When suspend sleep time is injected, `timekeeping.c` calls `tk_debug_account_sleep_time()`, which bins `tv_sec` with `fls()` capped at `NUM_BINS - 1`, increments the bin, and logs the duration. Reads of debugfs iterate nonzero bins and print ranges and counts.

## State and persistence behavior
State is in memory only: a global histogram and per-CPU counters. It is not persistent across reboot. The histogram increment is not explicitly locked, reflecting debug-only use. Per-CPU multigrain counters are incremented through inline helpers in `timekeeping_internal.h` and summed locklessly for diagnostics.

## Dependencies and integration points
The file depends on debugfs, seq_file, PM suspend debug logging, and `timekeeping_internal.h`. It is compiled under debugfs support and complements the main suspend accounting in `timekeeping.c` and multigrain timestamp logic.

## Risks
The debug histogram is intentionally lightweight and may race under unusual concurrent accounting, so it should not be used as a strict accounting source. Bin boundaries are powers of two seconds; extremely long durations are capped into the final bin. Debugfs creation failures are ignored, matching typical diagnostics behavior but limiting observability.

## Test signals
Signals include debugfs presence of `sleep_time`, readable histogram formatting, PM debug logs after suspend/resume, and nonzero multigrain floor swap counts when filesystem timestamp paths use fine-grained updates. Build coverage should include `CONFIG_DEBUG_FS` enabled and disabled, where stubs in the internal header replace this functionality.
