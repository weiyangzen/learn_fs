<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h

## Purpose
`br_netfilter.h` exposes bridge netfilter helpers for attaching bridge skb extension state, protocol/header adjustment, hook threshold continuation, fake routing table lookup, pre-routing setup, and optional IPv6 bridge validation.

## Important APIs, types, and functions
It defines `nf_bridge_alloc`, `nf_bridge_update_protocol`, `br_nf_hook_thresh`, `nf_bridge_encap_header_len`, `nf_bridge_push_encap_header`, `br_nf_pre_routing_finish_bridge`, `bridge_parent_rtable`, `setup_pre_routing`, and IPv6 enabled/stub helpers.

## Control flow
Bridge netfilter paths allocate skb extension metadata, adjust encapsulation headers before/after L3 netfilter processing, continue hooks at a threshold, and use the bridge fake rtable for routing interactions. IPv6 bridge pre-routing validation is conditional on CONFIG_IPV6.

## State and persistence
State is attached to skb extensions and bridge port/bridge structures; no persistent state is defined here.

## Dependencies and integration points
It depends on bridge private headers, netfilter hook state, skb extensions, IPv6 optional support, and route table types. It integrates bridge forwarding with L3 netfilter.

## Risks and test signals
Risks include skb extension allocation failure, incorrect encap header push/pull, direct inclusion of bridge private internals, IPv6-disabled behavior, and bridge port RCU lifetime. Tests should cover IPv4/IPv6 bridged netfilter, VLAN/PPPoE encapsulation lengths, pre-routing finish, and CONFIG_BRIDGE_NETFILTER off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h` completely for this pass (77 lines, 1904 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/br_netfilter.h -->
