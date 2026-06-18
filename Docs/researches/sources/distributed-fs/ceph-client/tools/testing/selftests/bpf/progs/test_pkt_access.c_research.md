# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c

Research item: `subset-b-006814` ordinal `93`. Source size: 3791 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_pkt_access.c_research.md`.

## Purpose
The program reads packet data or skb context fields and validates verifier range tracking while parsing TCP/IP headers and options. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_htons`
- Declared maps: None visible in this compact source.
- Key local types: `struct __sk_buff`, `struct tcphdr`, `struct ethhdr`, `struct ipv6hdr`, `struct iphdr`
- Main functions/subprograms: `test_pkt_access_subprog1`, `test_pkt_access_subprog2`, `get_skb_len`, `get_constant`, `get_skb_ifindex`, `test_pkt_access_subprog3`, `test_pkt_write_access_subprog`, `test_pkt_access`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `test_pkt_access_subprog1`, `test_pkt_access_subprog2`, `get_skb_len`, `get_constant`, `get_skb_ifindex`, `test_pkt_access_subprog3`, `test_pkt_write_access_subprog`, `test_pkt_access`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/in.h`, `linux/tcp.h`, `linux/pkt_cls.h`, `bpf/bpf_helpers.h`, `bpf/bpf_endian.h`.
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Packet boundary checks, dynptr slice validity, checksum/endian handling, and context-field writability are the main risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_pkt_access.c` is a test fixture for packet/skb metadata and TCP parsing selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `SEC("tc")` | `return TC_ACT_SHOT;` | `if (eth->h_proto == bpf_htons(ETH_P_IP)) {` | `} else if (eth->h_proto == bpf_htons(ETH_P_IPV6)) {` | `return TC_ACT_OK;` | `return TC_ACT_UNSPEC;`
