# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpftool_maps_access.c

## Purpose
This selftest validates bpftool access to BPF maps under BPF LSM/security policy. It checks read, BTF dump, write, delete, iterator access, nested map creation, and BTF listing for protected and unprotected maps, both by name and by pinned path.

## Important APIs, Types, And Functions
Important structures and helpers include `enum map_protection`, `struct test_desc`, `general_setup()`, `general_cleanup()`, `update_test_desc()`, `test_setup()`, `test_cleanup()`, `lookup_map_value()`, `read_map_btf_data()`, `write_map_value()`, `delete_map_value()`, `iterate_on_map_values()`, `create_inner_map()`, `create_outer_map()`, `add_outer_map_entry()`, `test_basic_access()`, `test_create_nested_maps()`, `test_btf_list()`, and `test_bpftool_maps_access()`. It uses `run_bpftool_command()`, `security_bpf_map` skeleton attach, bpffs pinning, and shell `cat` for pinned iterators.

## Control Flow
`general_setup()` loads and attaches the security skeleton, initializes protected and unprotected maps, enables protection in a status map, and creates `/sys/fs/bpf/test_bpftool_map`. Each table-driven subtest resolves the skeleton map, optionally pins it, builds a bpftool handle, checks lookup and BTF dump succeed, and checks write/delete either fail or succeed according to protection. It restores deleted values when needed. Iterator access pins `bpf_iter_map_elem.bpf.o` and reads the iterator file. Additional subtests create hash-of-maps nested maps through bpftool and run `btf list`.

## State And Persistence Behavior
The test temporarily creates a bpffs directory, optional map pins, iterator pins, and nested map pins. It also keeps security policy in loaded BPF LSM programs and skeleton maps. Cleanup unpins maps, unlinks iterator and nested-map pins, removes the directory, and destroys the skeleton.

## Dependencies And Integration Points
It depends on bpftool helper wrappers, bpffs, BPF LSM/security programs in `security_bpf_map`, `bpf_iter_map_elem.bpf.o`, map-in-map support, and bpftool command syntax for map lookup/update/delete, BTF dump, iter pin, map create, and BTF list.

## Risks And Edge Cases
Assertions around `write_must_fail` invert bpftool return status intentionally: protected maps should make update/delete fail while lookup/BTF/iteration remain allowed. Fixed bpffs paths can collide with stale state. `iterate_on_map_values()` uses `snprintf(cmd, MAP_NAME_MAX_LEN, "cat %s", iter_pin_path)`, so command length is capped by map-name size rather than full command size.

## Test Signals
Passing signals include successful security skeleton attach, successful initial map seeding, lookup/BTF dump success for all handles, expected write/delete success or failure based on protection, successful map iterator pin/read, nested outer map accepting two entries but rejecting a third, and successful `bpftool btf list`.
