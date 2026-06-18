# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c

Research item: `subset-b-006814` ordinal `98`. Source size: 561 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_ptr_untrusted.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `lsm.s/bpf`, `raw_tracepoint`
- BPF helpers/macros used: `bpf_tracing`, `bpf_attr`, `bpf_copy_from_user`
- Declared maps: None visible in this compact source.
- Key local types: None visible in this compact source.
- Main functions/subprograms: `BPF_PROG`

## Control Flow
Entry programs are attached through `lsm.s/bpf`, `raw_tracepoint`. Control is organized around `BPF_PROG`.

## State And Persistence Behavior
Global data/control fields include `tp_name`, `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_tracing.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_ptr_untrusted.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_tracing.h>` | `SEC("lsm.s/bpf")` | `int BPF_PROG(lsm_run, int cmd, union bpf_attr *attr, unsigned int size, bool kernel)` | `bpf_copy_from_user(tp_name, sizeof(tp_name) - 1,` | `SEC("raw_tracepoint")` | `char _license[] SEC("license") = "GPL";`
