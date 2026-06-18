# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_htab_mem.c

## Purpose

This benchmark measures hash map memory behavior and operation rate under overwrite, batch add/delete, and synchronized add/delete-on-different-CPU use cases.

## Important APIs, Types, and Functions

It defines `struct htab_mem_use_case`, global `ctx`, CLI args `value_size`, `use_case`, and `preallocated`, and functions for argument parsing, validation, barrier setup/teardown, use-case lookup, skeleton setup, add/delete producer loops, memory cgroup file reading, measurement, progress, and final reporting. It exports `bench_htab_mem`.

## Control Flow and Data Flow

Setup chooses the use case, optionally creates per-pair pthread barriers, joins a memory cgroup, opens the skeleton, sets hash value size and max entries, toggles preallocation, enables selected BPF programs by name, loads and attaches. Producers either repeatedly trigger add/overwrite work or synchronize paired add/delete threads through barriers. Measurement drains BPF operation count and reads `memory.current`; final reporting also reads `memory.peak`.

## State and Persistence Behavior

State includes the BPF hash map, cgroup membership, barrier objects, BPF BSS counters, and memory cgroup accounting. Final reporting closes the cgroup FD and cleans up the cgroup environment.

## Dependencies and Integration Points

It depends on `htab_mem_bench.skel.h`, cgroup helper APIs, libbpf map mutators, pthread barriers, cgroup v2 memory files, and syscall triggers.

## Risks and Edge Cases

`add_del_on_diff_cpu` requires an even producer count. On cgroup v1 or missing memory files, memory reads become zero. Cleanup is mainly on setup failure or final reporting, so abnormal exits can leave transient cgroup state. The preallocation flag clears `BPF_F_NO_PREALLOC`, so semantics depend on skeleton defaults.

## Test Signals

Progress should show per-producer kops/sec and memory MiB. Final output reports mean/stddev memory and peak memory for the selected use case.
