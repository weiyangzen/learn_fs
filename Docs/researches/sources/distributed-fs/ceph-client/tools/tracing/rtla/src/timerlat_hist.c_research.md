# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/timerlat_hist.c

## Purpose

`timerlat_hist.c` implements the `rtla timerlat hist` subcommand. It collects timer latency samples from the kernel `timerlat` tracer or the rtla BPF timerlat backend and renders per-CPU histograms for IRQ, timerlat thread, and optional user-thread return latency contexts.

## Important APIs, Types, and Functions

The main runtime structures are `struct timerlat_hist_cpu`, which owns per-context bucket arrays plus count/min/sum/max fields, and `struct timerlat_hist_data`, which records `entries` and `bucket_size`. Key functions are `timerlat_alloc_histogram()`, `timerlat_free_histogram()`, `timerlat_hist_update()`, `timerlat_hist_handler()`, `timerlat_hist_bpf_pull_data()`, `timerlat_print_stats()`, `timerlat_hist_parse_args()`, `timerlat_init_hist()`, and `timerlat_hist_main()`. The exported integration object is `timerlat_hist_ops`.

## Control Flow and Data Flow

Startup flows through `timerlat_hist_ops.parse_args`, `init_tool`, `apply_config`, `enable`, and `main`. Tracefs mode registers `timerlat_hist_handler()` for `ftrace:timerlat` events and updates bucket arrays from `context` and `timer_latency`. BPF mode waits for BPF threshold events, optionally runs threshold actions, restarts tracing when requested, detaches BPF, then pulls histogram and summary maps with `timerlat_bpf_get_hist_value()` and `timerlat_bpf_get_summary_value()`. Printing emits the header, bucket rows, overflow row, per-CPU summary, aggregate `ALL` summary, and missed-event report.

## State and Persistence Behavior

Histogram state is heap allocated per process and per CPU. Buckets include an extra overflow slot at `entries`. Minimum values are initialized to all-bits-one so the first sample wins. `output_divisor` converts nanoseconds to microseconds by default, or leaves nanoseconds under `--nano`. The file can persist stopped traces through configured trace-output actions, but histogram data itself is process-local.

## Dependencies and Integration Points

This file depends on `timerlat.h`, `timerlat_aa.h`, `timerlat_bpf.h`, `common.h`, libtraceevent handlers, tracefs/BPF timerlat support, global CPU state, threshold/end actions, auto-analysis, user/kernel workload setup, cgroup and scheduling configuration, and utility helpers from `utils.c`.

## Risks and Edge Cases

Large `--entries` values can allocate substantial memory because three arrays are allocated for every CPU. `--no-irq` and `--no-thread` together are rejected because no kernel contexts remain. `--no-index` without `--with-zeros` is rejected because sparse rows become ambiguous. BPF mode is downgraded to mixed mode when trace-output or auto-analysis is needed. Missing samples from tracefs buffer overflow are only reported after printing and can skew distributions.

## Test Signals

Useful tests include argument validation for bucket and entry bounds, `--nano` unit conversion, `--no-*` option combinations, tracefs event handling with synthetic `context` values, BPF map pull correctness for histogram/summary/overflow values, threshold action restart behavior, and runtime smoke tests that confirm per-CPU IRQ/thread/user columns appear when timerlat data is generated.
