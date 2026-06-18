<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c

## Purpose
`xt_pkttype.c` implements matching on skb packet type, such as host, broadcast, multicast, or otherhost.

## Important APIs, Types, and Functions
`pkttype_mt()` consumes `struct xt_pkttype_info` and compares against `skb->pkt_type`, with special handling for loopback broadcast/multicast presentation. `pkttype_mt_reg` registers the protocol-unspecified match.

## Control Flow, State, and Persistence
Each packet path reads `skb->pkt_type`, normalizes loopback behavior where needed, compares it with the configured packet type, and applies inversion. No state is persisted.

## Dependencies and Integration Points
It depends on skb link-layer classification assigned by drivers or receive paths. The match is usable across IPv4 and IPv6 because packet type is not IP-family-specific.

## Risks and Test Signals
Risks include driver differences in `pkt_type`, loopback behavior, VLAN/bridge transformations, and local-output skbs without meaningful ingress packet type. Tests should cover host, broadcast, multicast, otherhost, inversion, loopback broadcast/multicast, bridged traffic, and IPv4/IPv6 rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_pkttype.c -->
