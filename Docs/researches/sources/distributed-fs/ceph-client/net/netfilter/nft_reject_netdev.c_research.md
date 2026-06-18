
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c

## Purpose

`nft_reject_netdev.c` implements reject support for netdev ingress. Because netdev hooks operate before normal IP stack output context, it builds reject packets with nf_reject helpers, adds an Ethernet header, queues them on the ingress device, and drops the original packet.

## Important APIs, Types, and Functions

`nft_reject_queue_xmit()` creates the L2 header with swapped old Ethernet addresses and calls `dev_queue_xmit()`. Family helpers wrap `nf_reject_skb_v4_tcp_reset()`, `nf_reject_skb_v4_unreach()`, `nf_reject_skb_v6_tcp_reset()`, and `nf_reject_skb_v6_unreach()`. `nft_reject_netdev_eval()` dispatches by Ethernet protocol and reject type.

## Control Flow

Evaluation ignores broadcast and multicast destination frames and simply drops them. For IPv4 and IPv6 unicast frames it generates ICMP unreachable, TCP reset, or ICMPX-mapped unreachable as requested. Unsupported EtherTypes fall through to drop without a generated response. Validation restricts the expression to `NF_NETDEV_INGRESS`.

## State and Persistence Behavior

There is no dynamic persistent state. The expression stores reject type/code. Response skbs are transient and immediately transmitted; the original skb receives an `NF_DROP` verdict.

## Dependencies and Integration Points

Dependencies include Ethernet helpers, netdevice transmit, shared nft reject helpers, nf_reject IPv4/IPv6 skb constructors, and nf_tables netdev family registration.

## Risks and Test Signals

Risks include malformed Ethernet headers, generating replies to multicast/broadcast traffic, wrong ingress device selection, and behavior for non-IP EtherTypes. Test netdev ingress reject rules with IPv4, IPv6, TCP reset, ICMPX codes, multicast/broadcast frames, and packet captures confirming L2 source/destination handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_netdev.c -->
