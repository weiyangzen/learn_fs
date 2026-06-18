# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_hashmap_full_update.c

## Purpose

This benchmark measures BPF hash map update behavior when the map is already full.

## Important APIs, Types, and Functions

The module uses `bpf_hashmap_full_update_bench.skel.h`, `MAX_LOOP_NUM`, `validate()`, `producer()`, `setup()`, and `hashmap_report_final()`. It exports `bench_bpf_hashmap_full_update`.

## Control Flow and Data Flow

Setup loads and attaches the skeleton, sets BSS `nr_loops`, fills every entry in `hash_map_bench`, and producers repeatedly trigger the attached BPF program through `getpgid`. Measurement is empty during the run; final reporting reads per-CPU BSS elapsed times and computes events per second from loop count over recorded time.

## State and Persistence Behavior

The full hash map and per-CPU timing arrays live in the BPF skeleton during the process. No persistent state is written.

## Dependencies and Integration Points

It integrates the benchmark runner, libbpf skeleton generation, BPF map update syscall wrapper, and the BPF program that records per-CPU timing.

## Risks and Edge Cases

The benchmark intentionally relies on a full map, so map prefill failures would distort results but are not individually checked. No progress is printed until final reporting. The per-CPU report skips CPUs with zero time.

## Test Signals

A successful final report prints `hash_map_full_perf` events per second for CPUs that executed the benchmark.
