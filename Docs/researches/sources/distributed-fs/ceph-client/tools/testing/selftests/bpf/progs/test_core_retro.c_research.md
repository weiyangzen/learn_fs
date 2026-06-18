# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c

Research item: `subset-b-006814` ordinal `3`. Source size: 1005 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_retro.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/raw_syscalls/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_core_read`, `bpf_get_current_task`, `bpf_get_current_pid_tgid`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Declared maps: `exp_tgid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `results: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`
- Key local types: `struct task_struct`
- Main functions/subprograms: `handle_sys_enter`

## Control Flow
Entry programs are attached through `tp/raw_syscalls/sys_enter`. Control is organized around `handle_sys_enter`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `exp_tgid_map: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `results: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_core_read.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_core_retro.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_core_read.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} exp_tgid_map SEC(".maps");` | `} results SEC(".maps");` | `SEC("tp/raw_syscalls/sys_enter")` | `struct task_struct *task = (void *)bpf_get_current_task();` | `int real_tgid = bpf_get_current_pid_tgid() >> 32;` | `int *exp_tgid = bpf_map_lookup_elem(&exp_tgid_map, &zero);` | `bpf_map_update_elem(&results, &zero, &tgid, 0);` | and 1 more marker lines
