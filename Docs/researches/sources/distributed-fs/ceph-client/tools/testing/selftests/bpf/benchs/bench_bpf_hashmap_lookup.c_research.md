# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_lookup.c

## Purpose

This module benchmarks BPF hash map lookup throughput across configurable key size, map flags, entry count, and loop count.

## Important APIs, Types, and Functions

CLI options control `key_size`, `map_flags`, `max_entries`, `nr_entries`, and `nr_loops`. Important helpers are `validate()`, `producer()`, `patch_key()`, `setup()`, `events_from_time()`, `compute_events()`, and `hashmap_report_final()`. It exports `bench_bpf_hashmap_lookup`.

## Control Flow and Data Flow

Setup configures map dimensions and flags before load, initializes a deterministic key template for keys larger than four bytes, loads the skeleton, fills `nr_entries` keys, and attaches the benchmark program. Producers trigger via `getpgid`. The BPF side stores timing samples per CPU; final reporting converts time samples to million lookups per second and prints mean/stddev.

## State and Persistence Behavior

Map contents, key template, and per-CPU timing samples are process-local skeleton state. There is no persistent storage.

## Dependencies and Integration Points

It depends on `bpf_hashmap_lookup.skel.h`, libbpf map mutators, endian-aware key patching, and the benchmark runner's quiet/affinity modes.

## Risks and Edge Cases

`nr_entries` must not exceed `max_entries`; `nr_loops` is capped by the kernel loop bound. `ctx.skel->bss->nr_loops` is integer-divided by entries, so total work can be lower than requested. `compute_events()` scans only 32 timing samples per CPU.

## Test Signals

Expected final output prints per-CPU lookup throughput, or a single numeric quiet result when affinity pins execution.
