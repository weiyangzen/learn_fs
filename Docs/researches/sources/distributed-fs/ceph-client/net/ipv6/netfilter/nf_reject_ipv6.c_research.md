# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_reject_ipv6.c

Purpose: Provides the IPv6 reject core used by iptables/nftables to synthesize TCP resets and ICMPv6 destination-unreachable packets for rejected traffic.

Important APIs, types, and functions: Exported functions include `nf_reject_skb_v6_tcp_reset()`, `nf_reject_skb_v6_unreach()`, `nf_send_reset6()`, and `nf_send_unreach6()`. Internal helpers validate IPv6 headers, locate/check TCP headers, verify checksums, construct IPv6/TCP/ICMPv6 headers, detect ICMPv6 unreachable loops, fill dsts, and handle bridged RST transmission.

Control flow: Reset generation validates the original IPv6 packet, extracts a non-RST TCP header through extension headers, verifies TCP checksum, builds a reversed IPv6 header, creates a minimal RST header with correct sequence/ack logic, attaches conntrack, marks the original conntrack closing, routes/xfrm-lookups output, and transmits via `ip6_local_out()` or direct bridge xmit when bridge netfilter metadata exists. Unreachable generation avoids replying to an unreachable, clips quoted payload to the IPv6 minimum MTU budget, verifies checksum, builds ICMPv6, computes the checksum, and either returns the skb or sends through `icmpv6_send()`.

State and persistence: No durable state. It mutates generated skbs, may attach conntrack from the original packet, and sets conntrack closing state for TCP resets. It also may temporarily attach a dst to an input skb before calling `icmpv6_send()`.

Dependencies and integration: Depends on IPv6 route/xfrm, checksum helpers, ICMPv6, TCP header parsing, bridge netfilter, conntrack helpers, security flow classification, and reject expression/target modules.

Risks and test signals: Risks include responding to malformed extension-header chains, bad checksum acceptance, RST sequence correctness, bridge MAC header correctness, and route/xfrm failure leaks. Tests should cover TCP SYN/data/RST input, ICMP unreachable suppression, fragmented/non-first packets, extension headers, bridged traffic, local-output rejects, xfrm policy routes, and invalid checksums.
