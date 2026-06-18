# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_reject_ipv4.c

## Purpose
IPv4 reject core used by netfilter front ends to synthesize TCP resets and ICMP destination-unreachable errors. It offers skb-building helpers and direct send helpers.

## Important APIs, types, and functions
Exported APIs are `nf_reject_skb_v4_tcp_reset()`, `nf_reject_skb_v4_unreach()`, `nf_send_reset()`, and `nf_send_unreach()`. Internal helpers validate IPv4 headers, reject ICMP-unreach loops, extract valid TCP headers, build IPv4/TCP headers, and populate missing dst entries.

## Control flow
TCP reset generation validates IPv4/TCP headers, rejects fragments/RST/checksum failures, allocates an skb, reverses addresses/ports, computes seq/ack fields, and marks checksum partial. ICMP unreachable generation rejects non-first fragments and ICMP-unreach loops, trims/pulls the original packet, verifies checksum when needed, embeds bounded original data, and computes ICMP/IP checksums. `nf_send_reset()` additionally routes, suppresses broadcast/multicast, attaches conntrack, marks the original flow closing, and handles bridge-netfilter direct Ethernet output or `ip_local_out()`.

## State and persistence
No durable state. The code mutates skb metadata, may attach conntrack to generated replies, and may set the original conntrack entry closing. It reads namespace default TTL and route/dst metadata.

## Dependencies and integration points
Depends on IPv4 routing, TCP/IP checksum helpers, ICMP, dst/route APIs, netfilter reject checksum utilities, conntrack attachment, and optional bridge netfilter. Used by nftables/xtables reject expressions.

## Risks
Replying to fragments, invalid checksums, broadcast/multicast, or ICMP errors can cause protocol violations or amplification; these are explicitly guarded. Bridge output must build Ethernet headers correctly. `nf_reject_fill_skb_dst()` mutates input skb dst when absent.

## Test signals
Test TCP reset for SYN/established packets, no reset for RST/invalid checksum, ICMP unreachable length and loop suppression, fragments, route-missing cases, broadcast/multicast suppression, bridge netfilter, and nft/iptables reject at different hooks.
