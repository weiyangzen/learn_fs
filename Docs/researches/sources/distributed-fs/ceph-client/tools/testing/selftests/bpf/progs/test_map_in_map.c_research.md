# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c

Research item: `subset-b-006814` ordinal `68`. Source size: 1679 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_map_in_map.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`
- BPF helpers/macros used: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`
- Declared maps: `mim_array: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `mim_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1, key int, value __u32`, `mim_array_pe: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1`, `mim_hash_pe: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`
- Key local types: `struct perf_event_array`, `struct xdp_md`
- Main functions/subprograms: `xdp_mimtest0`

## Control Flow
Entry programs are attached through `xdp`. Control is organized around `xdp_mimtest0`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `mim_array: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1, key __u32, value __u32`, `mim_hash: BPF_MAP_TYPE_HASH_OF_MAPS, max 1, key int, value __u32`, `mim_array_pe: BPF_MAP_TYPE_ARRAY_OF_MAPS, max 1`, `mim_hash_pe: BPF_MAP_TYPE_HASH_OF_MAPS, max 1`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `linux/bpf.h`, `linux/types.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_map_in_map.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_ARRAY_OF_MAPS);` | `} mim_array SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH_OF_MAPS);` | `} mim_hash SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} inner_map0 SEC(".maps");` | `} mim_array_pe SEC(".maps") = {` | `} mim_hash_pe SEC(".maps") = {` | `SEC("xdp")` | and 7 more marker lines
