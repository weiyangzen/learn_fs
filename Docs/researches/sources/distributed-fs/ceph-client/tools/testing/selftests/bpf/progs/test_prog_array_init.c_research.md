# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c

Research item: `subset-b-006814` ordinal `97`. Source size: 693 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_prog_array_init.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sys_enter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_get_current_pid_tgid`, `bpf_tail_call`
- Declared maps: `prog_array_init: BPF_MAP_TYPE_PROG_ARRAY, max 2`
- Key local types: None visible in this compact source.
- Main functions/subprograms: `tailcall_1`, `entry`

## Control Flow
Entry programs are attached through `raw_tp/sys_enter`. Control is organized around `tailcall_1`, `entry`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use. The control flow includes helper-mediated dispatch or bounded looping, so the verifier must preserve state across helper boundaries.

## State And Persistence Behavior
Maps: `prog_array_init: BPF_MAP_TYPE_PROG_ARRAY, max 2`. Global data/control fields include `value`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_prog_array_init.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("raw_tp/sys_enter")` | `__uint(type, BPF_MAP_TYPE_PROG_ARRAY);` | `} prog_array_init SEC(".maps") = {` | `pid_t pid = bpf_get_current_pid_tgid() >> 32;` | `bpf_tail_call(ctx, &prog_array_init, 1);`
