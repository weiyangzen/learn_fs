# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c

Research item: `subset-b-006814` ordinal `94`. Source size: 1127 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_md_access.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`
- Main functions/subprograms: `test_pkt_md_access`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `test_pkt_md_access`. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/pkt_cls.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pkt_md_access.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `return TC_ACT_SHOT;				\` | `SEC("tc")` | `return TC_ACT_OK;`
