
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/global_map_resize.c

## Purpose

`global_map_resize.c` tests resizing libbpf global datasec maps before load for `.bss` and custom `.data`, and verifies BTF metadata handling for invalid resize layouts.

## Important APIs, Types, and Functions

The test uses `test_global_map_resize.skel.h`, `bpf_map__set_value_size()`, `bpf_map__value_size()`, `bpf_map__initial_value()`, BTF key/value type queries, skeleton attach, and syscall triggers (`getpid`, `getuid`) for attached programs.

## Control Flow and Data Flow

The BSS subtest opens the skeleton, seeds one element, resizes `.bss` to include a large trailing array, resizes a percpu data map, refreshes the initial-value pointer, fills new elements, sets rodata lengths/PID, loads/attaches, triggers, and checks sum. The data subtest mirrors this for `.data.custom`. The invalid subtest resizes maps whose BTF cannot remain valid and asserts resize succeeds while BTF IDs are cleared.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is pre-load skeleton global-data memory, resized map definitions, BTF metadata, and post-trigger BSS sum. Dependencies include libbpf support for datasec resizing and kernel support for attached syscall probes. Integration is libbpf map sizing, initial-value preservation, and BTF invalidation policy. Risks are page-size dependence, struct layout assumptions, and stale skeleton pointers after resize. Test signals are preserved first element, sum equals computed array length, percpu resize success, and BTF IDs cleared for invalid layouts.
