# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c

Research item: `subset-b-006814` ordinal `72`. Source size: 1719 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_lookup_percpu_elem.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tp/syscalls/sys_enter_getuid`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_percpu_elem`, `bpf_get_current_pid_tgid`, `bpf_loop`
- Declared maps: `percpu_array_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64`, `percpu_hash_map: BPF_MAP_TYPE_PERCPU_HASH, max 1, key __u64, value __u64`, `percpu_lru_hash_map: BPF_MAP_TYPE_LRU_PERCPU_HASH, max 1, key __u64, value __u64`
- Key local types: `struct read_percpu_elem_ctx`
- Main functions/subprograms: `read_percpu_elem_callback`, `sysenter_getuid`

## Control Flow
Entry programs are attached through `tp/syscalls/sys_enter_getuid`. Control is organized around `read_percpu_elem_callback`, `sysenter_getuid`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use. The control flow includes helper-mediated dispatch or bounded looping, so the verifier must preserve state across helper boundaries.

## State And Persistence Behavior
Maps: `percpu_array_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64`, `percpu_hash_map: BPF_MAP_TYPE_PERCPU_HASH, max 1, key __u64, value __u64`, `percpu_lru_hash_map: BPF_MAP_TYPE_LRU_PERCPU_HASH, max 1, key __u64, value __u64`. Global data/control fields include `percpu_array_elem_sum`, `percpu_hash_elem_sum`, `percpu_lru_hash_elem_sum`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_lookup_percpu_elem.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} percpu_array_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_HASH);` | `} percpu_hash_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_LRU_PERCPU_HASH);` | `} percpu_lru_hash_map SEC(".maps");` | `value = bpf_map_lookup_percpu_elem(ctx->map, &key, index);` | `SEC("tp/syscalls/sys_enter_getuid")` | `if (my_pid != (bpf_get_current_pid_tgid() >> 32))` | and 2 more marker lines
