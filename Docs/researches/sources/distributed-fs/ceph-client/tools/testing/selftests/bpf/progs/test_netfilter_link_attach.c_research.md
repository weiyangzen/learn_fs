# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c

Research item: `subset-b-006814` ordinal `78`. Source size: 247 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_netfilter_link_attach.c_research.md`.

## Purpose
The file contains a compact eBPF program or header used by user-space selftests to validate a specific verifier, helper, map, attach, or libbpf behavior. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `netfilter`
- BPF helpers/macros used: `bpf_helpers`, `bpf_nf_ctx`
- Declared maps: None visible in this compact source.
- Key local types: `struct bpf_nf_ctx`
- Main functions/subprograms: `nf_link_attach_test`

## Control Flow
Entry programs are attached through `netfilter`. Control is organized around `nf_link_attach_test`.

## State And Persistence Behavior
Global data/control fields include `_license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `bpf/bpf_helpers.h`.
Local test dependencies: `vmlinux.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Most risk comes from verifier log sensitivity, kernel feature gating, and tight coupling to the corresponding selftest harness.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_netfilter_link_attach.c` is a test fixture for targeted BPF selftest program. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `SEC("netfilter")` | `int nf_link_attach_test(struct bpf_nf_ctx *ctx)` | `char _license[] SEC("license") = "GPL";`
