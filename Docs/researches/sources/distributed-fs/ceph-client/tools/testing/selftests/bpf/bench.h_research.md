# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/bench.h

## Purpose

This header defines the common ABI for BPF benchmark modules and the runner.

## Important APIs, Types, and Functions

Important types are `struct cpu_set`, `struct env`, `struct basic_stats`, `struct bench_res`, `struct bench`, and cacheline-aligned `struct counter`. It declares global `env` and `bench`, libbpf setup, shared reporting functions, grace-period statistics helpers, and relaxed atomic helpers `atomic_inc()`, `atomic_add()`, and `atomic_swap()`.

## Control Flow and Data Flow

Benchmark modules populate a `const struct bench` with callbacks. Producers update counters or trigger BPF programs; the runner calls `measure()` once per interval to fill `bench_res`; report helpers consume those deltas.

## State and Persistence Behavior

The header defines no storage except through external declarations. Atomic helpers operate on caller-owned counters and intentionally use relaxed ordering for throughput measurement.

## Dependencies and Integration Points

It integrates libbpf, BPF syscall wrappers, math/time/syscall headers, and all `benchs/` modules.

## Risks and Edge Cases

`bench_res` is a shared catch-all structure, so fields have benchmark-specific meanings. Relaxed atomics are correct for approximate benchmark counters but not for synchronization. The aligned `counter` type helps avoid false sharing only when arrays are allocated naturally.

## Test Signals

Successful compilation of all benchmark modules and sensible output from shared reporting functions validate the contract.
