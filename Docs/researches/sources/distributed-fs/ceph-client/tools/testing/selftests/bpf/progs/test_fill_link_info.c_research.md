# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c

Research item: `subset-b-006814` ordinal `13`. Source size: 1078 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_fill_link_info.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `kprobe`, `uprobe`, `tracepoint`, `perf_event`, `kprobe.multi`, `uprobe.multi`
- BPF helpers/macros used: `bpf_tracing`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `unused`, `BPF_PROG`, `event_run`

## Control Flow
Entry programs are attached through `kprobe`, `uprobe`, `tracepoint`, `perf_event`, `kprobe.multi`, `uprobe.multi`. Control is organized around `unused`, `BPF_PROG`, `event_run`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_tracing.h`, `stdbool.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_fill_link_info.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `SEC("kprobe")` | `SEC("uprobe")` | `SEC("tracepoint")` | `SEC("perf_event")` | `SEC("kprobe.multi")` | `SEC("uprobe.multi")` | `char _license[] SEC("license") = "GPL";`
