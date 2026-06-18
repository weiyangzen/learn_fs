
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/for_each.c

## Purpose

`for_each.c` validates `bpf_for_each_map_elem()` behavior over hash, array, percpu, and multiple-map cases, plus verifier rejection when callbacks try to mutate map keys.

## Important APIs, Types, and Functions

The harness uses skeletons for hash map iteration, array map iteration, key-write failure, multi-map iteration, and hash modification. It uses `bpf_map__update_elem()`, `bpf_map__lookup_elem()`, `bpf_prog_test_run_opts()`, `bpf_num_possible_cpus()`, and packet input from `network_helpers.h`.

## Control Flow and Data Flow

Each subtest populates maps, runs `test_pkt_access`, and validates BSS counters and map side effects. Hash iteration checks element count, callback return/output, deletion of key 1, and percpu value selection for current CPU. Array iteration sums entries except the last to validate early stop behavior. Multi-map iteration toggles `use_array` to drive array versus hash traversal. Hash-modify exercises iteration while updating/deleting map elements according to the BPF-side program.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is limited to BPF maps and skeleton BSS fields. Dependencies are verifier support for map iteration callbacks, percpu map layout, and test-run support. Integration is the helper contract for callback invocation, early termination, key immutability, and map mutation safety. Risks include CPU-count dependent percpu expectations and verifier message/behavior drift. Test signals are expected sums/counters, failed lookup for deleted hash key, valid current-CPU percpu value, expected load failure for key writes, and correct outputs for array/hash selected paths.
