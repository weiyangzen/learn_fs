
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_proto.c

Purpose: Implements packet-header manipulation for NAT across IPv4, IPv6, TCP, UDP, SCTP, ICMP, ICMPv6, and GRE, plus family-specific NAT hook wrappers and registration helpers.

Important APIs and functions: `nf_nat_manip_pkt()` is the core exported manipulator used by NAT core. `nf_nat_csum_recalc()` supports helper payload rewrites. `nf_nat_icmp_reply_translation()` and `nf_nat_icmpv6_reply_translation()` translate outer and embedded packets in related error messages. Exported registration helpers are `nf_nat_ipv4_register_fn()`, `nf_nat_ipv4_unregister_fn()`, `nf_nat_ipv6_register_fn()`, `nf_nat_ipv6_unregister_fn()`, and inet variants when enabled.

Control flow: Protocol-specific functions ensure skb writability, update address/port/id fields, and adjust checksums. `nf_nat_manip_pkt()` inverts the opposite conntrack tuple to produce the target tuple and dispatches to IPv4 or IPv6 manipulation. IPv4 and IPv6 hook wrappers handle related ICMP errors before calling `nf_nat_inet_fn()`, drop stale dst after DNAT, reroute local output when destination changes, orphan early-demux sockets when local-in source/port changes, and redo xfrm lookup when NAT changes flow keys.

State and persistence: The file has static hook operation arrays for IPv4 and IPv6. Runtime state is in conntrack and skb headers; no local mutable persistent data.

Dependencies and integration: Called by `nf_nat_core.c`, OVS/TC NAT support, helpers needing checksum recalculation, and family NAT registration paths. Depends on conntrack tuples, IPv4/IPv6 routing, xfrm, checksum APIs, SCTP checksum support, GRE/PPTP types, and netfilter hook priorities.

Risks: This is a high-risk packet rewrite layer. Risks include checksum correctness for partial and complete checksums, inner ICMP translation bounds, IPv6 extension header parsing, fragments with unavailable L4 headers, GRE version behavior, SCTP checksum recomputation, route/xfrm refresh after NAT, socket early-demux invalidation, and family registration mismatches. Test signals include every supported L4 protocol, IPv4/IPv6 SNAT/DNAT in each hook, ICMP error translation, fragmented IPv6, local output reroute, xfrm policy lookup after NAT, and helper-driven checksum recalculation.
