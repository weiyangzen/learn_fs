<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c

## Purpose

In-place TC tunnel encapsulation and decapsulation coverage for IPv4/IPv6, IPIP, GRE, UDP, MPLS, Ethernet-over-UDP, VXLAN, SIT, and ip6 tunnels. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 702 source lines. BPF sections: `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_compiler`, `bpf_endian`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_ntohs`, `bpf_skb_adjust_room`, `bpf_skb_load_bytes`, `bpf_skb_store_bytes`, `bpf_tracing_net`. Important C functions and entry points include `__encap_ipip_none`, `__encap_gre_none`, `__encap_gre_mpls`, `__encap_gre_eth`, `__encap_udp_none`, `__encap_udp_mpls`, `__encap_udp_eth`, `__encap_vxlan_eth`, `__encap_sit_none`, `__encap_ip6tnl_none`, `__encap_ipip6_none`, `__encap_ip6gre_none`, `__encap_ip6gre_mpls`, `__encap_ip6gre_eth`, `__encap_ip6udp_none`, `__encap_ip6udp_mpls`, `__encap_ip6udp_eth`, `__encap_ip6vxlan_eth`. Notable globals or configuration/result fields include `int __encap_ipip_none(struct __sk_buff *skb)`; `int __encap_gre_none(struct __sk_buff *skb)`; `int __encap_gre_mpls(struct __sk_buff *skb)`; `int __encap_gre_eth(struct __sk_buff *skb)`; `int __encap_udp_none(struct __sk_buff *skb)`; `int __encap_udp_mpls(struct __sk_buff *skb)`; `int __encap_udp_eth(struct __sk_buff *skb)`; `int __encap_vxlan_eth(struct __sk_buff *skb)`.

## Control Flow

Shared encap helpers load inner headers, filter TCP destination port 8000, compute outer header size and flags, call `bpf_skb_adjust_room`, write outer headers and optional L2/VXLAN/MPLS data; `decap_f` removes the matching outer headers.

## State And Persistence Behavior

No maps; packet contents are the state under test. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Room-adjust flags encode L3/L4/L2 metadata and are easy to regress; pointer invalidation after `bpf_skb_adjust_room` requires helper-based stores. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run all section variants with matching packets and inspect encapsulated/decapsulated headers and TC return codes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_tunnel.c -->
