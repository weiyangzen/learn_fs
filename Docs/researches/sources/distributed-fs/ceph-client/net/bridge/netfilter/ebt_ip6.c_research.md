# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_ip6.c

## Purpose
Implements the legacy ebtables `ip6` match for IPv6 traffic class, masked source/destination addresses, next header protocol, TCP/UDP-like port ranges, and ICMPv6 type/code ranges.

## Important APIs, Types, And Functions
Important routines are `ebt_ip6_mt`, `ebt_ip6_mt_check`, and `xt_match ebt_ip6_mt_reg`, using `struct ebt_ip6_info` and `ipv6_skip_exthdr`.

## Control Flow
The match reads the IPv6 header, evaluates traffic class and masked addresses, then follows extension headers to locate the effective next header and L4 offset. If L4 fields are requested, it reads a compact port/ICMP header and applies range and inversion checks. Checkentry enforces IPv6 ethproto, mask bounds, transport-protocol requirements, ICMPv6 requirements, and range ordering.

## State And Persistence Behavior
The module keeps no runtime mutable state beyond registration. Per-rule criteria are immutable.

## Dependencies And Integration Points
Depends on IPv6 header helpers, dsfield helpers, ebtables UAPI, and xtables. It is built only when bridge ebtables and IPv6 support are enabled.

## Risks And Test Signals
Risks include extension-header skip failures, fragmented IPv6 behavior, truncated L4 reads, and invalid protocol/range combinations. Tests should cover extension headers, ports, ICMPv6, masked addresses, traffic class, inversions, bad ranges, and invalid ethproto rejection.
