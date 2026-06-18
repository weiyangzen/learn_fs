# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c

Research item: `subset-b-006814` ordinal `74`. Source size: 2838 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_migrate_reuseport.c_research.md`.

## Purpose
The code assigns or selects sockets from maps based on tuple fields, exercising `sk_lookup`, `sk_reuseport`, and libbpf attach paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `xdp`, `sk_reuseport/migrate`
- BPF helpers/macros used: `bpf_endian`, `bpf_helpers`, `bpf_ntohs`, `bpf_get_socket_cookie`, `bpf_map_lookup_elem`, `bpf_sk_select_reuseport`
- Declared maps: `reuseport_map: BPF_MAP_TYPE_REUSEPORT_SOCKARRAY, max 256, key int, value __u64`, `migrate_map: BPF_MAP_TYPE_HASH, max 256, key __u64, value int`
- Key local types: `struct xdp_md`, `struct ethhdr`, `struct tcphdr`, `struct iphdr`, `struct ipv6hdr`, `struct sk_reuseport_md`
- Main functions/subprograms: `drop_ack`, `migrate_reuseport`

## Control Flow
Entry programs are attached through `xdp`, `sk_reuseport/migrate`. Control is organized around `drop_ack`, `migrate_reuseport`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Several branches converge through `goto` cleanup paths, which is typical for reference-release or error-return validation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `reuseport_map: BPF_MAP_TYPE_REUSEPORT_SOCKARRAY, max 256, key int, value __u64`, `migrate_map: BPF_MAP_TYPE_HASH, max 256, key __u64, value int`. Global data/control fields include `migrated_at_close`, `migrated_at_close_fastopen`, `migrated_at_send_synack`, `migrated_at_recv_ack`, `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `string.h`, `linux/bpf.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/tcp.h`, `linux/in.h`, `bpf/bpf_endian.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Risks include socket reference handling, host/network byte order, `bpf_sk_assign` flag semantics, and expected errno behavior.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_migrate_reuseport.c` is a test fixture for socket lookup and reuseport BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `*        return SK_PASS without selecting a listener.` | `#include <bpf/bpf_endian.h>` | `#include <bpf/bpf_helpers.h>` | `__uint(type, BPF_MAP_TYPE_REUSEPORT_SOCKARRAY);` | `} reuseport_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} migrate_map SEC(".maps");` | `SEC("xdp")` | `switch (bpf_ntohs(eth->h_proto)) {` | `return XDP_DROP;` | and 8 more marker lines
