# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c

Research item: `subset-b-006814` ordinal `15`. Source size: 3092 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_get_stack_rawtp.c_research.md`.

## Purpose
The program exercises map declaration, lookup, update, delete, freezing, resizing, pinning, inner-map, or queue/stack semantics. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tracepoint/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_stack_build_id`, `bpf_get_stack`, `bpf_prog1`, `bpf_map_lookup_elem`, `bpf_get_current_pid_tgid`, `bpf_perf_event_output`
- Declared maps: `perfmap: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 2`, `stackdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct stack_trace_t`, `rawdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64[2 * MAX_STACK_RAWTP]`
- Key local types: `struct stack_trace_t`, `struct bpf_stack_build_id`
- Main functions/subprograms: `bpf_prog1`

## Control Flow
Entry programs are attached through `raw_tracepoint/sys_enter`. Control is organized around `bpf_prog1`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `perfmap: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 2`, `stackdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value struct stack_trace_t`, `rawdata_map: BPF_MAP_TYPE_PERCPU_ARRAY, max 1, key __u32, value __u64[2 * MAX_STACK_RAWTP]`. Global data/control fields include `_license`. The program deliberately persists observations through maps or event buffers for user-space assertions.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Map type restrictions, key/value size, per-CPU layout, lock fields, and libbpf map definition parsing are the main risk points.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_get_stack_rawtp.c` is a test fixture for BPF map operation selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct bpf_stack_build_id user_stack_buildid[MAX_STACK_RAWTP];` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} perfmap SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stackdata_map SEC(".maps");` | `*   usize = bpf_get_stack(ctx, raw_data, max_len, BPF_F_USER_STACK);` | `*   ksize = bpf_get_stack(ctx, raw_data + usize, max_len - usize, 0);` | `} rawdata_map SEC(".maps");` | `SEC("raw_tracepoint/sys_enter")` | and 13 more marker lines
