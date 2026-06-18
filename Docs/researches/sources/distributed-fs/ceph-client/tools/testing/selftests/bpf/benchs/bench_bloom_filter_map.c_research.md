# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bloom_filter_map.c

## Purpose

This benchmark module measures BPF bloom filter map lookup/update, bloom-assisted hashmap lookup, plain hashmap lookup, and false-positive behavior.

## Important APIs, Types, and Functions

State lives in `ctx` with skeleton, map FDs, condition variable, and population cursor. CLI args set `nr_entries`, `nr_hash_funcs`, and `value_size`. Important functions are `validate()`, `producer()`, `map_prepare_thread()`, `populate_maps()`, `check_args()`, `setup_skeleton()`, per-benchmark setup functions, and `measure()`. It exports five `struct bench` instances.

## Control Flow and Data Flow

Setup opens the skeleton, resizes maps and key/value sizes, sets bloom hash function count, loads BPF, populates maps with random values from concurrent threads, fills random lookup data, and attaches the selected BPF program. Producers repeatedly call `getpgid` to trigger attached programs. `measure()` reads per-CPU BSS stats and reports deltas for hits, drops, and false hits.

## State and Persistence Behavior

Map contents and per-CPU counters live for the benchmark process. `ctx.next_map_idx` coordinates concurrent map population; `map_done` only signals first completing thread, so all workers are expected to finish by exhausting the shared index quickly enough for this setup pattern.

## Dependencies and Integration Points

It depends on `bloom_filter_bench.skel.h`, libbpf map resizing APIs, `bpf_map_update_elem()`, `getrandom`, syscall-triggered BPF attachment, and the runner's reporting helpers.

## Risks and Edge Cases

Small `value_size` can make requested unique entries impossible, so `check_args()` rejects it. Hashmap population retries on `EEXIST`. The condition variable does not join all population threads, making `map_prepare_err` and map completeness sensitive to thread timing. False-positive percentages depend on random data and bloom parameters.

## Test Signals

Useful signals are stable hit/drop rates for lookup/update benches, false-positive percentages for `bloom-false-positive`, and setup failures for invalid map sizing, random generation, or skeleton attach.
