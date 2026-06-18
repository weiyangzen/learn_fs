# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c

Research item: `subset-b-006814` ordinal `52`. Source size: 10880 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_l4lb.c_research.md`.

## Purpose
The program parses Ethernet/IP/TCP/UDP/ICMP traffic, looks up VIP/backend maps, updates per-CPU stats, and rewrites or redirects packets in TC/XDP style paths. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tc`
- BPF helpers/macros used: `bpf_helpers`, `bpf_endian`, `bpf_map_lookup_elem`, `bpf_tunnel_key`, `bpf_ntohs`, `bpf_skb_set_tunnel_key`, `bpf_redirect`, `bpf_htons`
- Declared maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`
- Key local types: `struct packet_description`, `struct ctl_value`, `struct vip_meta`, `struct real_definition`, `struct vip_stats`, `struct eth_hdr`, `struct vip`, `struct icmp6hdr`, `struct ipv6hdr`, `struct icmphdr`, `struct iphdr`, `struct udphdr`, `struct tcphdr`, `struct __sk_buff`, and 2 more.
- Main functions/subprograms: `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`

## Control Flow
Entry programs are attached through `tc`. Control is organized around `rol32`, `jhash`, `__jhash_nwords`, `jhash_2words`, `get_packet_hash`, `get_packet_dst`, `parse_icmpv6`, `parse_icmp`, `parse_udp`, `parse_tcp`, `process_packet`, `balancer_ingress`. Runtime lookups and shared state flow through declared BPF maps before the program returns an attach-specific verdict. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Maps: `vip_map: BPF_MAP_TYPE_HASH, max MAX_VIPS, key struct vip, value struct vip_meta`, `ch_rings: BPF_MAP_TYPE_ARRAY, max CH_RINGS_SIZE, key __u32, value __u32`, `reals: BPF_MAP_TYPE_ARRAY, max MAX_REALS, key __u32, value struct real_definition`, `stats: BPF_MAP_TYPE_PERCPU_ARRAY, max MAX_VIPS, key __u32, value struct vip_stats`, `ctl_array: BPF_MAP_TYPE_ARRAY, max CTL_MAP_SIZE, key __u32, value struct ctl_value`. Global data/control fields include `_license`. Persistence is mostly map lookup/result state rather than durable filesystem or kernel object state.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `stddef.h`, `stdbool.h`, `string.h`, `linux/pkt_cls.h`, `linux/bpf.h`, `linux/in.h`, `linux/if_ether.h`, `linux/ip.h`, `linux/ipv6.h`, `linux/icmp.h`, `linux/icmpv6.h`, `linux/tcp.h`, and 3 more..
Local test dependencies: `test_iptunnel_common.h`
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Bounds checks, endian conversion, checksum updates, dynptr handling, and map value layout are the main compatibility risks.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_l4lb.c` is a test fixture for packet parser and L4 load-balancer selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `#include <bpf/bpf_endian.h>` | `__uint(type, BPF_MAP_TYPE_HASH);` | `} vip_map SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_ARRAY);` | `} ch_rings SEC(".maps");` | `} reals SEC(".maps");` | `__uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);` | `} stats SEC(".maps");` | `} ctl_array SEC(".maps");` | and 18 more marker lines
