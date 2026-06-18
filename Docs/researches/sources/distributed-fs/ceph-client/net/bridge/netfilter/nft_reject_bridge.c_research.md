# sources/distributed-fs/ceph-client/net/bridge/netfilter/nft_reject_bridge.c

## Purpose
Implements the nftables bridge-family `reject` expression, generating IPv4/IPv6 TCP resets or ICMP unreachable replies at bridge prerouting/local-in while ultimately dropping the original packet.

## Important APIs, Types, And Functions
Important functions are `nft_reject_bridge_eval`, `nft_reject_bridge_validate`, `nft_reject_br_push_etherhdr`, `nft_reject_br_send_v4_tcp_reset`, `nft_reject_br_send_v4_unreach`, `nft_reject_br_send_v6_tcp_reset`, and `nft_reject_br_send_v6_unreach`. The expression uses common `nft_reject_init`/`dump` helpers.

## Control Flow
Evaluation ignores broadcast/multicast destinations, then dispatches on Ethernet protocol and reject type. It asks IPv4/IPv6 reject helpers to build the L3 response, pushes a reversed Ethernet header and VLAN tag from the original skb, forwards the generated skb through the ingress bridge port, and sets the original verdict to `NF_DROP`. Validation allows only bridge prerouting and local-in chains.

## State And Persistence Behavior
No persistent state is kept. The expression emits response packets as side effects and drops the triggering skb.

## Dependencies And Integration Points
Depends on nftables core, common reject helpers, IPv4/IPv6 reject code, bridge forwarding `br_forward`, bridge-port lookup, VLAN accelerated tag helpers, and NF_BR hook validation.

## Risks And Test Signals
Risks include using the wrong egress device for bridge-generated replies, missing VLAN preservation, emitting rejects for multicast/broadcast, and hook validation errors. Tests should cover IPv4/IPv6 TCP reset, ICMP/ICMPv6 unreachable, ICMPx mapping, VLAN-tagged packets, broadcast/multicast no-reply drop, unsupported ethproto drop, and invalid hook rejection.
