# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c

Research item: `subset-b-006814` ordinal `84`. Source size: 841 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pe_preserve_elems.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `raw_tp/sched_switch`, `raw_tp/task_rename`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`, `bpf_perf_event_value`, `bpf_perf_event_read_value`
- Declared maps: `array_1: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`, `array_2: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`
- Key local types: `struct bpf_perf_event_value`
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `raw_tp/sched_switch`, `raw_tp/task_rename`. Control is organized around `BPF_PROG`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict.

## State And Persistence Behavior
Maps: `array_1: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`, `array_2: BPF_MAP_TYPE_PERF_EVENT_ARRAY, max 1, key int, value int`. Global data/control fields include `LICENSE`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `linux/bpf.h`, `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pe_preserve_elems.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `__uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);` | `} array_1 SEC(".maps");` | `} array_2 SEC(".maps");` | `SEC("raw_tp/sched_switch")` | `struct bpf_perf_event_value val;` | `return bpf_perf_event_read_value(&array_1, 0, &val, sizeof(val));` | `SEC("raw_tp/task_rename")` | `return bpf_perf_event_read_value(&array_2, 0, &val, sizeof(val));` | and 1 more marker lines
