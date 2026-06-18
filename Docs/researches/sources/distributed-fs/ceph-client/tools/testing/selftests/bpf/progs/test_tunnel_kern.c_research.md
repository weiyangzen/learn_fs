<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c

## Purpose

Broad tunnel-helper test covering GRE, ERSPAN, VXLAN, Geneve, IPIP, FOU/GUE, IPv6 tunnel metadata, FOU kfuncs, and XFRM state lookup from TC and XDP. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 1026 source lines. BPF sections: `.maps`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `tc`, `xdp`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`. Important helper/kfunc surface: `bpf_core_enum_value`, `bpf_core_read`, `bpf_csum_diff`, `bpf_dynptr`, `bpf_dynptr_from_xdp`, `bpf_dynptr_slice`, `bpf_endian`, `bpf_fou_encap`, `bpf_fou_encap___local`, `bpf_fou_encap_type___local`, `bpf_helpers`, `bpf_htonl`, `bpf_htons`, `bpf_kfuncs`, `bpf_l3_csum_replace`, `bpf_map_lookup_elem`, `bpf_ntohl`, `bpf_ntohs`, `bpf_printk`, `bpf_skb_change_type`, `bpf_skb_get_fou_encap`, `bpf_skb_get_tunnel_key`, `bpf_skb_get_tunnel_opt`, `bpf_skb_get_xfrm_state`, `bpf_skb_set_fou_encap`, `bpf_skb_set_tunnel_key`, `bpf_skb_set_tunnel_opt`, `bpf_skb_store_bytes`, .... Important C functions and entry points include `bpf_skb_set_fou_encap`, `bpf_skb_get_fou_encap`, `bpf_xdp_xfrm_state_release`, `gre_set_tunnel`, `gre_set_tunnel_no_key`, `gre_get_tunnel`, `ip6gretap_set_tunnel`, `ip6gretap_get_tunnel`, `erspan_set_tunnel`, `erspan_get_tunnel`, `ip4ip6erspan_set_tunnel`, `ip4ip6erspan_get_tunnel`, `vxlan_set_tunnel_dst`, `vxlan_set_tunnel_src`, `vxlan_get_tunnel_src`, `veth_set_outer_dst`, `ip6vxlan_set_tunnel_dst`, `ip6vxlan_set_tunnel_src`. Notable globals or configuration/result fields include `int bpf_skb_set_fou_encap(struct __sk_buff *skb_ctx,`; `int bpf_skb_get_fou_encap(struct __sk_buff *skb_ctx,`; `int gre_set_tunnel(struct __sk_buff *skb)`; `int gre_set_tunnel_no_key(struct __sk_buff *skb)`; `int gre_get_tunnel(struct __sk_buff *skb)`; `int ip6gretap_set_tunnel(struct __sk_buff *skb)`; `int ip6gretap_get_tunnel(struct __sk_buff *skb)`; `int erspan_set_tunnel(struct __sk_buff *skb)`.

## Control Flow

TC setters populate `bpf_tunnel_key` and protocol-specific option structures, call set/get tunnel helpers, patch outer IP destination and checksum when needed, and verify tunnel flags. XFRM programs read skb or XDP ESP state, including dynptr packet parsing and kfunc reference release.

## State And Persistence Behavior

`local_ip_map` supplies dynamic local/remote IPs; globals such as `xfrm_reqid`, `xfrm_spi`, `xfrm_remote_ip`, and `xfrm_replay_window` expose XFRM results. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tunnel metadata layout, byte order, CORE bitfield access, kfunc availability, and reference release are high-risk integration points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run each TC section in its tunnel topology and validate helper return codes, metadata, rewritten headers, and XFRM globals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tunnel_kern.c -->
