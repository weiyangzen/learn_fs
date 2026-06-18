
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/inner_array_lookup.c

## Purpose

`inner_array_lookup.c` validates lookup and update behavior for an inner array map referenced by the loaded BPF program.

## Important APIs, Types, and Functions

The harness uses `inner_array_lookup.skel.h`, skeleton attach, `bpf_map__fd()`, `bpf_map_update_elem()`, and `bpf_map_lookup_elem()`.

## Control Flow and Data Flow

After load and attach, the test writes value 1 at key 3 of `inner_map1`. The attached BPF probe is expected to observe/update that slot, so the host reads key 3 back and asserts value 2.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the inner array map contents and attached probe link. Dependencies are array-in-array map handling and the paired BPF trigger path. Integration is inner map lookup from BPF. Risks include missing trigger if attach point does not fire promptly. Test signal is key 3 value changed to 2.
