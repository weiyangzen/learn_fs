<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c

## Purpose

BPF benchmark or verifier fixture for loop/map behavior, focusing on helper bounds, callback execution, map update/lookup cost, and stack safety.

## Important APIs, Types, and Functions

- BPF sections: `license`, `.maps`
- Maps: `hash_map_bench`
- Important functions/callbacks: `loop_update_callback`, `benchmark`
- BPF helpers/kfunc-like calls: `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_update_elem`
- Mutable globals/test result fields: `nr_loops`

## Control Flow and Data Flow

Control flow is selftest-oriented: userspace loads the object, attaches the declared BPF programs, drives kernel events, and checks globals/maps for expected observations.

## State and Persistence Behavior

BPF maps persist across program invocations while the object is loaded: `hash_map_bench` Globals are used as userspace-visible configuration/results: `nr_loops`

## Dependencies and Integration Points

Includes `vmlinux.h`, `bpf/bpf_helpers.h`, `bpf_misc.h`.

## Risks and Edge Cases

Verifier compatibility, BTF layout drift, and architecture-specific helper availability are the main risks for this selftest fixture. Helper availability and license restrictions matter for `bpf_get_smp_processor_id`, `bpf_ktime_get_ns`, `bpf_loop`, `bpf_map_update_elem`.

## Test Signals

Load/attach success and verifier log expectations are primary signals. Userspace should read globals such as `nr_loops` to confirm the exercised path ran. Map contents/counts for `hash_map_bench` provide state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/bpf_hashmap_full_update_bench.c -->
