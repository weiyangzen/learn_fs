
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_data_init.c

## Purpose

`global_data_init.c` verifies `bpf_map__set_initial_value()` for internal global data maps before object load and rejects wrong-size or post-load initial-value changes.

## Important APIs, Types, and Functions

It opens `test_global_data.bpf.o`, finds the `.rodata` internal map, uses `bpf_map__value_size()`, `bpf_map__set_initial_value()`, `bpf_object__load()`, and `bpf_map_lookup_elem()`.

## Control Flow and Data Flow

The test allocates a zeroed buffer matching `.rodata`, checks that `sz - 1` is rejected, sets the full-size value, loads the object, reads map element zero, compares bytes, then tries to set a new initial value after load and expects failure.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the pre-load internal map initial-value buffer and loaded `.rodata` map. Dependencies are libbpf object open/load and internal map support. Integration is libbpf initial data override semantics. Risks include paired object layout changes and allocation failure. Test signals are wrong-size rejection, successful full-size override, byte-for-byte map match after load, and post-load rejection.
