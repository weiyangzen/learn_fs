# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h

Research item: `subset-b-006814` ordinal `134`. Source size: 8877 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_kern.h_research.md`.

## Purpose
The program validates socket map update, stream parser/verdict, skb verdict, ktls/listen behavior, or per-socket storage interactions. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sockops`, `sk_msg`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_printk`, `bpf_prog1`, `bpf_map_lookup_elem`, `bpf_prog2`, `bpf_sk_redirect_map`, `bpf_sk_redirect_hash`, `bpf_write_pass`, `bpf_skb_pull_data`, `bpf_prog3`, `bpf_skb_adjust_room`, `bpf_sockmap`, `bpf_sock_ops`, `bpf_sock_map_update`, and 14 more.
- Declared maps: `sock_map: TEST_MAP_TYPE, max 20`, `sock_map_txmsg: TEST_MAP_TYPE, max 20`, `sock_map_redir: TEST_MAP_TYPE, max 20`, `sock_apply_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_cork_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_bytes: BPF_MAP_TYPE_ARRAY, max 6, key int, value int`, `sock_redir_flags: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_skb_opts: BPF_MAP_TYPE_ARRAY, max 3, key int, value int`, `tls_sock_map: TEST_MAP_TYPE, max 20`
- Key local types: `struct __sk_buff`, `struct bpf_sock_ops`, `struct sk_msg_md`
- Main functions/subprograms: `bpf_prog1`, `bpf_prog2`, `bpf_write_pass`, `bpf_prog3`, `bpf_sockmap`, `bpf_prog4`, `bpf_prog6`, `bpf_prog8`, `bpf_prog9`, `bpf_prog10`

## Control Flow
Entry programs are attached through `sk_skb/stream_parser`, `sk_skb/stream_verdict`, `sockops`, `sk_msg`. Control is organized around `bpf_prog1`, `bpf_prog2`, `bpf_write_pass`, `bpf_prog3`, `bpf_sockmap`, `bpf_prog4`, `bpf_prog6`, `bpf_prog8`, `bpf_prog9`, `bpf_prog10`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `sock_map: TEST_MAP_TYPE, max 20`, `sock_map_txmsg: TEST_MAP_TYPE, max 20`, `sock_map_redir: TEST_MAP_TYPE, max 20`, `sock_apply_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_cork_bytes: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_bytes: BPF_MAP_TYPE_ARRAY, max 6, key int, value int`, `sock_redir_flags: BPF_MAP_TYPE_ARRAY, max 1, key int, value int`, `sock_skb_opts: BPF_MAP_TYPE_ARRAY, max 3, key int, value int`, and 1 more.. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/in.h`, `linux/udp.h`, `linux/tcp.h`, `linux/pkt_cls.h`, `sys/socket.h`, and 2 more..
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Socket lifetime, reference release, redirect return codes, map compatibility, and attach-type restrictions are the primary risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sockmap_kern.h` is a test fixture for sockmap/sockhash and socket storage BPF selftest. Test signals are: trace output helps diagnose unexpected helper return values.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `* The bpf_printk is verbose and prints information as connections` | `} sock_map SEC(".maps");` | `} sock_map_txmsg SEC(".maps");` | `} sock_map_redir SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} sock_apply_bytes SEC(".maps");` | `} sock_cork_bytes SEC(".maps");` | and 55 more marker lines
