# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/osnoise_top.c

## Purpose
`osnoise_top.c` implements `rtla osnoise top` and `rtla hwnoise`, producing a live or final per-CPU summary of noise runtime, total noise, CPU availability, max samples, and noise source counts.

## Important APIs, Types, and Functions
`struct osnoise_top_cpu` stores cumulative runtime/noise, maximum noise/sample, source counters, and cycle count per CPU. `struct osnoise_top_data` owns the per-CPU array. Important functions include `osnoise_top_handler()`, `osnoise_top_header()`, `osnoise_top_print()`, `osnoise_print_stats()`, `osnoise_top_parse_args()`, `osnoise_top_apply_config()`, and `osnoise_init_top()`. The file exports `struct tool_ops osnoise_top_ops`.

## Control Flow
`osnoise_init_top()` allocates state and registers a raw event handler for `ftrace:osnoise`. The handler updates per-CPU sums and maxima from event fields. The parser handles osnoise runtime/period/threshold/stop options, auto mode, trace output, event filters/triggers, quiet/debug/duration/scheduling/cgroup options, warmup, trace buffer size, and threshold/end actions. `hwnoise` mode sets a shorter runtime than period and later enables `OSNOISE_IRQ_DISABLE`. `top_main_loop()` from `common.c` periodically collects events and calls `osnoise_print_stats()`.

## State and Persistence
Per-CPU counters are in memory. Configuration changes are applied through `osnoise_apply_config()` and restored by context cleanup. Trace actions may write snapshots.

## Dependencies and Integration Points
It depends on libtraceevent field extraction, trace sequence printing, common option parsing, actions, and osnoise tracefs configuration. Terminal color/clear behavior is enabled only for TTY output and non-quiet mode.

## Risks and Edge Cases
CPU availability percentage assumes `sum_runtime` is nonzero and uses integer scaling. Output columns depend on mode and may be wide for many CPUs or noninteractive terminals. The parser requires root and enforces runtime/period bounds, but invalid numeric strings depend on utility parsing behavior. `hwnoise` shares osnoise top ops with mode-specific configuration, so regressions in common top logic affect both tools.

## Test Signals
Run top and hwnoise modes with quiet/non-quiet output, CPU masks, auto/trace modes, threshold/end actions, terminal/non-terminal stdout, and missing event fields. Validate counters against known synthetic osnoise events where possible.
