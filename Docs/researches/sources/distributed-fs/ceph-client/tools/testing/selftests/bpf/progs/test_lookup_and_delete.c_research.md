# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c

Research item: `subset-b-006814` ordinal `62`. Source size: 547 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_lookup_and_delete.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getpgid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_lookup_and_delete_test`, `bpf_get_current_pid_tgid`, `bpf_map_update_elem`
- Declared maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key __u64, value __u64`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `bpf_lookup_and_delete_test`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getpgid`. Control is organized around `bpf_lookup_and_delete_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `hash_map: BPF_MAP_TYPE_HASH, max 2, key __u64, value __u64`. Global data/control fields include `set_pid`, `set_key`, `set_value`, `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_lookup_and_delete.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} hash_map SEC(".maps");` | `SEC("tp/syscalls/sys_enter_getpgid")` | `int bpf_lookup_and_delete_test(const void *ctx)` | `if (set_pid == bpf_get_current_pid_tgid() >> 32)` | `bpf_map_update_elem(&hash_map, &set_key, &set_value, BPF_NOEXIST);` | `char _license[] SEC("license") = "GPL";`
