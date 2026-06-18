<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c

## Purpose
Implements netdev-family packet forwarding and duplication helpers for nftables, plus flow-offload action construction for fwd/dup netdev expressions.

## Important APIs, Types, and Functions
Exports `nf_fwd_netdev_egress()`, `nf_dup_netdev_egress()`, and `nft_fwd_dup_netdev_offload()`. Internal `nf_do_netdev_egress()` handles recursion limiting, optional MAC header push for ingress-origin packets, device assignment, timestamp clearing, and `dev_queue_xmit()`.

## Control Flow
Forwarding looks up the output interface by index under RCU; missing devices consume/free the original skb. Duplication looks up the device, clones the skb with `GFP_ATOMIC`, and transmits only the clone. Egress preparation pushes the MAC header back when duplicating/forwarding from netdev ingress and a MAC header is available. Offload obtains a device reference and appends a flow action entry with the requested action ID.

## State and Persistence
No persistent module state is stored. It mutates skb device/header/timestamp state and uses per-CPU netfilter duplicate recursion state. Offload entries hold device references later released by flow-rule destruction.

## Dependencies and Integration Points
Depends on nftables netdev packet info, nf_tables offload, flow action entries, netdevice lookup/transmit, and `nf_get_nf_dup_skb_recursion()`. Called by `nft_dup_netdev.c` and `nft_fwd_netdev.c`.

## Risks
Recursion limit enforcement prevents loops but drops skbs when exceeded. Forward consumes the original skb, while dup must not. MAC header push requires headroom and may fail. Offload must not leak device references on later failure paths.

## Test Signals
Test nft netdev dup and fwd rules on ingress and egress hooks, missing output interface behavior, recursive dup/fwd loops, insufficient headroom, cloned skb delivery, hardware/software offload setup, and device ref cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_dup_netdev.c -->
