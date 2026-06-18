# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_count.c

## Purpose

This module provides pure userspace counting baselines for the benchmark framework: one contended global counter and one per-producer local counter.

## Important APIs, Types, and Functions

`count_global_ctx` contains a single aligned counter. `count_local_ctx` contains an allocated array of counters. Producer and measurement functions are `count_global_producer()`, `count_global_measure()`, `count_local_setup()`, `count_local_producer()`, and `count_local_measure()`. It exports `bench_count_global` and `bench_count_local`.

## Control Flow and Data Flow

Producers spin forever incrementing either one shared counter or their own slot. Measurement swaps counters to zero and reports deltas through the generic hits/drops reporting path.

## State and Persistence Behavior

Counters are process memory only. Local counters are allocated once based on producer count and never freed because the process exits after the run.

## Dependencies and Integration Points

It depends only on `bench.h` relaxed atomic helpers and the runner's thread management/reporting.

## Risks and Edge Cases

The global baseline measures atomic contention as much as loop overhead. The local baseline depends on producer index matching array bounds. Producers never terminate.

## Test Signals

`count-local` should scale better with producers than `count-global`; both are useful smoke tests for the runner without requiring BPF support.
