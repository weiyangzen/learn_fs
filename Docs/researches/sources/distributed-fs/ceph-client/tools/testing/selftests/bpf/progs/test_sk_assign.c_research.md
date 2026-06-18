# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c

Research item: `subset-b-006814` ordinal `115`. Source size: 4562 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sk_assign.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `maps`, `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_misc`, `bpf_elf_map`, `bpf_sock_tuple`, `bpf_htons`, `bpf_sock`, `bpf_sk_lookup_udp`, `bpf_map_lookup_elem`, `bpf_sk_assign`, `bpf_sk_release`, `bpf_skc_lookup_tcp`, `bpf_sk_assign_test`
- Declared maps: `server_map: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value __u64`
- Key local types: `struct bpf_elf_map`, `struct bpf_sock_tuple`, `struct __sk_buff`, `struct ethhdr`, `struct iphdr`, `struct ipv6hdr`, `struct bpf_sock`
- Main functions/subprograms: `get_tuple`, `handle_udp`, `handle_tcp`, `bpf_sk_assign_test`

## Control Flow
Entry programs are attached through `maps`, `tc`. Control is organized around `get_tuple`, `handle_udp`, `handle_tcp`, `bpf_sk_assign_test`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `server_map: BPF_MAP_TYPE_SOCKMAP, max 1, key int, value __u64`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state. Socket references acquired from maps or helpers are explicitly released to satisfy verifier lifetime rules.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/in.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/pkt_cls.h`, `linux/tcp.h`, `sys/socket.h`, `bpf/bpf_helpers.h`, and 1 more..
Local test dependencies: `bpf_misc.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_sk_assign.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `#include "bpf_misc.h"` | `__uint(type, BPF_MAP_TYPE_SOCKMAP);` | `} server_map SEC(".maps");` | `/* Must match struct bpf_elf_map layout from iproute2 */` | `} server_map SEC("maps") = {` | `.type = BPF_MAP_TYPE_SOCKMAP,` | `char _license[] SEC("license") = "GPL";` | `static inline struct bpf_sock_tuple *` | and 23 more marker lines
