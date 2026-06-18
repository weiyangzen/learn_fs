# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_map_in_map.c

## Purpose
This file validates BTF-declared map-in-map definitions, including array-of-maps, hash-of-maps, dynamic inner maps, and rejection of incompatible inner map sizes for sockmap-like nesting.

## APIs, Types, and Functions
It uses the generated `test_btf_map_in_map.skel.h` skeleton, `bpf_map__fd`, `bpf_map_get_info_by_fd`, `bpf_map_update_elem`, `bpf_map_lookup_elem`, and skeleton open/load/attach/destroy helpers. `bpf_map_id` reads map IDs for identity checks.

## Control Flow
`test_lookup_update` opens and attaches the skeleton, retrieves inner and outer map FDs, updates outer maps to point at different inner maps, changes `skel->bss->input`, sleeps briefly to let the attached program run, and checks values written into the selected inner maps. It then repeatedly swaps inner map FDs and verifies map IDs are obtainable. `test_diff_size` attempts to insert an incompatible inner sock array into an outer map and expects failure. `test_btf_map_in_map` runs both subtests.

## State, Dependencies, and Integration
State lives in kernel BPF maps and skeleton BSS during the test and is destroyed with the skeleton. Integration is through BPF object metadata generated from the companion program and libbpf's map-in-map creation logic.

## Risks and Test Signals
The important signals are correct map update routing, expected inner-map values, successful map info lookup, and rejection of size-mismatched inner maps. Races are minimized with `usleep`, but scheduling or attach failures can still make this environment-sensitive.
