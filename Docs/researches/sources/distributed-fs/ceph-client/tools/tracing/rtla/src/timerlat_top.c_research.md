# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_top.c

## Purpose

`timerlat_top.c` implements the `rtla timerlat top` subcommand. It provides a live per-CPU summary of timer latency, showing current, minimum, average, and maximum values for IRQ, timerlat thread, and optional user-thread return contexts.

## Important APIs, Types, and Functions

`struct timerlat_top_cpu` stores current/count/min/sum/max fields for IRQ, thread, and user contexts. `struct timerlat_top_data` owns the per-CPU array. Important functions are `timerlat_alloc_top()`, `timerlat_top_update()`, `timerlat_top_handler()`, `timerlat_top_bpf_pull_data()`, `timerlat_top_print()`, `timerlat_top_print_sum()`, `timerlat_print_stats()`, `timerlat_top_parse_args()`, `timerlat_init_top()`, and `timerlat_top_bpf_main_loop()`. `timerlat_top_ops` registers the subcommand with the shared rtla tool framework.

## Control Flow and Data Flow

After parsing and initialization, tracefs mode uses the shared `top_main_loop()`, while BPF mode calls `timerlat_top_bpf_main_loop()`. Tracefs samples arrive through `timerlat_top_handler()` and update per-CPU state unless `aa_only` is active. BPF mode periodically waits for either sleep interval expiry or a tracer stop, pulls current/count/min/max/sum maps, prints live output unless quiet, runs threshold handling when the tracer stops, and restarts BPF tracing if the session should continue.

## State and Persistence Behavior

All measurement state is volatile in `timerlat_top_data`. Minimum fields start at all-bits-one, averages are derived from sums and counts, and `cur_*` fields hold the latest sample or BPF current map value. Pretty terminal output is enabled only for a tty and non-quiet mode. Trace output may be persisted through action configuration; the top table itself is not persisted.

## Dependencies and Integration Points

The file integrates with the same timerlat/common stack as `timerlat_hist.c`: tracefs, libtraceevent, BPF timerlat maps, threshold and end actions, auto-analysis, workload dispatch, scheduler/cgroup helpers, timerlat tracer configuration, and the shared `tool_ops` dispatcher.

## Risks and Edge Cases

`--aa-only` suppresses normal sample parsing and output, so it depends on auto-analysis stop conditions rather than top-table data. `--no-aa` and `--aa-only` are mutually exclusive. BPF mode must detach after completion. Counts are per context; CPUs with no IRQ/thread count are treated as offline or inactive and skipped. Lost trace events can make current and aggregate statistics stale or incomplete.

## Test Signals

Tests should cover live and quiet modes, `--aa-only`, BPF map pull of all summary types, tracefs event updates for context 0/1/user, pretty-output gating on `isatty()`, user workload termination detection, threshold action restart behavior, and printed summaries with CPUs that have only one context populated.
