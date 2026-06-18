# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise.c

## Purpose
`osnoise.c` provides shared osnoise/timerlat tracefs configuration management and command dispatch for `rtla osnoise`, `rtla hwnoise`, and timerlat support. It reads, writes, saves, and restores osnoise tracefs knobs and manages `struct osnoise_tool` lifetimes.

## Important APIs, Types, and Functions
Configuration APIs include `osnoise_set_cpus()`, `osnoise_set_runtime_period()`, `osnoise_set_timerlat_period_us()`, `osnoise_set_stop_us()`, `osnoise_set_stop_total_us()`, `osnoise_set_print_stack()`, `osnoise_set_tracing_thresh()`, `osnoise_set_irq_disable()`, and `osnoise_set_workload()`, with matching restore/put helpers. Tool APIs include `osnoise_context_alloc()`, `osnoise_get_context()`, `osnoise_put_context()`, `osnoise_init_tool()`, `osnoise_init_trace_tool()`, `osnoise_destroy_tool()`, `osnoise_trace_is_off()`, `osnoise_report_missed_events()`, `osnoise_apply_config()`, `osnoise_enable()`, `osnoise_main()`, and `hwnoise_main()`.

## Control Flow
Setter functions lazily read original tracefs values, validate sentinel states, write new values, and store current values for restoration. Context reference counting defers restoration until the last user releases it. `osnoise_apply_config()` enables kernel workload, sets runtime/period defaults when absent, sets `tracing_thresh`, and delegates to `common_apply_config()`. `osnoise_enable()` starts record and primary trace instances, optionally runs warmup and clears buffers, then configures stop thresholds. Command dispatch selects top or hist mode or defaults to top.

## State and Persistence
The file mutates tracefs files under `osnoise/` plus `tracing_thresh`. It restores original values on context destruction: CPUs, runtime/period, stop thresholds, timerlat period, print stack, tracing threshold, IRQ-disable option, and workload option. Trace instances are created and destroyed through trace helpers.

## Dependencies and Integration Points
It depends on tracefs, utilities for parsing and errors, `osnoise.h`, `common.c` loops, mode ops (`osnoise_top_ops`, `osnoise_hist_ops`), and timerlat modules that reuse timerlat-specific setters.

## Risks and Edge Cases
Sentinel values use `0` or `-1` depending on field semantics; bugs can appear if a legitimate kernel value overlaps a sentinel. `osnoise_set_runtime_period()` must preserve `runtime <= period`, and its ordering logic is critical. Option parsing checks strings in `osnoise/options` with substring search, which can be sensitive to option-name overlap. `osnoise_put_irq_disable()` and workload put helpers reset original sentinels inside restore, so later checks can be redundant. Missing kernel support returns different negative values for workload handling, and callers rely on that distinction.

## Test Signals
Use tracefs fixtures or live kernels to test every setter/restore pair, partial failures, runtime/period ordering, missing osnoise options, no cdev-like optional files, command dispatch, warmup buffer cleanup, and missed-event reporting.
