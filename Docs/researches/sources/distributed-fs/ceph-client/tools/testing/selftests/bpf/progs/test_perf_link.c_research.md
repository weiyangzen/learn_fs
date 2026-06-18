# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c

Research item: `subset-b-006814` ordinal `87`. Source size: 311 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_perf_link.c_research.md`.

## Purpose
The code attaches to perf or trace events and reports counters/samples through perf buffer or link infrastructure. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_tracing`
- Declared maps: None visible in this compact source.
- Key local types: `struct pt_regs`
- Main functions/subprograms: `handler`

## Control Flow
Entry programs are attached through `perf_event`. Control is organized around `handler`.

## State And Persistence Behavior
Global data/control fields include `run_cnt`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`, `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Test results depend on perf event availability, CPU context, stack/sample flags, and link detach semantics.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_perf_link.c` is a test fixture for perf-event BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_tracing.h>` | `SEC("perf_event")` | `char _license[] SEC("license") = "GPL";`
