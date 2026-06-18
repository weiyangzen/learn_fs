<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h

## Purpose
`nf_dup_netdev.h` declares netdev-family packet duplicate/forward helpers, recursion tracking, and nftables flow offload support for dup/fwd actions.

## Important APIs, types, and functions
It declares `nf_dup_netdev_egress`, `nf_fwd_netdev_egress`, `NF_RECURSION_LIMIT`, `nf_get_nf_dup_skb_recursion`, and `nft_fwd_dup_netdev_offload`.

## Control flow
Netdev nftables actions duplicate or forward packets to an output ifindex while recursion tracking prevents repeated reinjection loops. Non-RT builds store recursion counters in per-CPU softnet data; PREEMPT_RT uses current task net-xmit state.

## State and persistence
State is the recursion counter in softnet or task net_xmit state. Flow offload state is built in nft flow rule structures.

## Dependencies and integration points
It depends on nftables packet info, netdevice, scheduler/current task state, PREEMPT_RT configuration, and flow offload types. It integrates netdev ingress/egress nftables actions with packet transmission and hardware offload.

## Risks and test signals
Risks include recursion-limit bypass, PREEMPT_RT storage differences, skb ownership after egress, offload action mismatch, and ifindex validation. Tests should cover nested dup/fwd rules, RT and non-RT builds, invalid oif, flow offload generation, and loop prevention.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h` completely for this pass (29 lines, 753 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_dup_netdev.h -->
