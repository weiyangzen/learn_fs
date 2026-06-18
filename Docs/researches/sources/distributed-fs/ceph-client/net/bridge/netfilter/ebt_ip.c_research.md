# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip.c

## Purpose
Implements the legacy ebtables `ip` match for IPv4 TOS, source/destination addresses, L4 protocol, TCP/UDP-like port ranges, ICMP type/code ranges, and IGMP type ranges.

## Important APIs, Types, And Functions
The module provides `ebt_ip_mt`, `ebt_ip_mt_check`, `xt_match ebt_ip_mt_reg`, and a local `union pkthdr` for minimal L4 field reads.

## Control Flow
At runtime it safely reads the IPv4 header, checks requested L3 fields, then if protocol-dependent fields are requested it rejects non-initial fragments and reads a small L4 header at `ihl * 4` to evaluate port or ICMP/IGMP ranges. Checkentry requires ethproto IPv4, validates masks, enforces valid protocol dependencies for ports/ICMP/IGMP, and checks range ordering.

## State And Persistence Behavior
No mutable state exists. Match criteria are stored in each rule's `struct ebt_ip_info`.

## Dependencies And Integration Points
Depends on IP protocol constants, `skb_header_pointer`, ebtables rule metadata, and xtables match registration. It complements the bridge ethproto basic match in `ebtables.c`.

## Risks And Test Signals
Risks include fragmented packet behavior, short IHL/payload reads, protocol/range validation, and inversion semantics. Tests should cover each field, all supported transport protocols, non-first fragments, invalid protocol dependencies, reversed ranges, and truncated IPv4/L4 headers.
