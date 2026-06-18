# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_pkttype.c

## Purpose
Implements the legacy ebtables `pkttype` match for the skb packet type, such as host, broadcast, multicast, or otherhost.

## Important APIs, Types, And Functions
Core functions are `ebt_pkttype_mt`, `ebt_pkttype_mt_check`, and `xt_match ebt_pkttype_mt_reg`, using `struct ebt_pkttype_info`.

## Control Flow
Runtime matching compares `skb->pkt_type` to the configured value and XORs with the invert flag. Validation only constrains invert to 0 or 1 and intentionally allows any packet-type value.

## State And Persistence Behavior
No mutable state is kept. The match reads packet metadata only.

## Dependencies And Integration Points
Depends on skbuff packet type metadata, ebtables UAPI, and xtables registration. Packet type may be affected by bridge input, DNAT, redirect, or driver classification paths.

## Risks And Test Signals
Risks are minimal but include unexpected pkt_type rewrites before match evaluation. Tests should cover host, broadcast, multicast, otherhost, inversion, and invalid invert values.
