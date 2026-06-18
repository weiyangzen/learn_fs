# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_obj_id.c

## Purpose
This serial selftest validates kernel object ID enumeration and info retrieval for BPF programs, maps, and links. It loads two identical raw tracepoint programs, records their map/program/link info, and confirms get-by-id and get-next-id APIs expose consistent metadata.

## Important APIs, Types, And Functions
The entry point is `serial_test_bpf_obj_id()`. It uses `bpf_prog_test_load()`, `bpf_find_map()`, `bpf_map_update_elem()`, `bpf_object__find_program_by_name()`, `bpf_program__attach()`, `bpf_map_get_info_by_fd()`, `bpf_prog_get_info_by_fd()`, `bpf_link_get_info_by_fd()`, `bpf_prog_get_next_id()`, `bpf_map_get_next_id()`, `bpf_link_get_next_id()`, and get-FD-by-ID variants for prog/map/link.

## Control Flow
The test first verifies ID zero cannot be resolved for program, map, or link. It then loads `test_obj_id.bpf.o` twice, updates each map with a magic value, attaches each raw tracepoint program, and records map, program, and link metadata. It enumerates all program IDs, finds the two loaded programs, checks a negative `EFAULT` case for missing `map_ids`, and compares retrieved info. It repeats analogous enumeration and comparison for maps and links.

## State And Persistence Behavior
State consists of two loaded BPF objects, two program FDs, two map FDs, two BPF links, captured `bpf_*_info` structures, instruction buffers, map ID buffers, and a magic array value. No bpffs pinning is used. All links are destroyed and objects closed in the `done` cleanup loop.

## Dependencies And Integration Points
It depends on `test_obj_id.bpf.o`, raw tracepoint support, JIT status exposed in `env.jit_enabled`, kernel object ID APIs, and stable metadata fields such as names, UID, load time, map IDs, and raw tracepoint name.

## Risks And Edge Cases
ID enumeration is global and can race with other BPF objects disappearing, so the code tolerates `ENOENT` for objects in the "dead row." Load time comparison allows a 60-second window. JIT instruction assertions are conditional on `env.jit_enabled`.

## Test Signals
Passing signals are `ENOENT` for ID zero, correct map/program/link metadata lengths and fields, nonzero translated instructions, expected JIT data when JIT is enabled, correct created UID and load time, matching map IDs and magic values, raw tracepoint link info for `sys_enter`, and finding both loaded objects during enumeration.
