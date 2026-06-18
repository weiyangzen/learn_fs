# sources/distributed-fs/ceph-client/include/linux/ip.h

## Purpose
`ip.h` supplies kernel IPv4 header accessors layered over `sk_buff` network and transport offsets, plus helpers for total length handling in normal packets and TCP GSO packets.

## Important APIs, types, and functions
Important helpers are `ip_hdr`, `inner_ip_hdr`, `ipip_hdr`, `ip_transport_len`, `iph_totlen`, `skb_ip_totlen`, `IP_MAX_MTU`, and `iph_set_totlen`.

## Control flow
Consumers read the IPv4 header from the skb network header, inner network header, or transport header for IP-in-IP. Length helpers decode `iph->tot_len`; for TCP GSO with a zero field they infer the effective length from `skb->len` and network offset. `iph_set_totlen` writes zero for packets exceeding the 16-bit IPv4 total length field.

## State and persistence
The header has no state. It reads and mutates only packet header fields in caller-owned skbs.

## Dependencies and integration points
It depends on `skbuff.h`, endian conversion via UAPI IP definitions, and GSO helpers. It is used across IPv4 routing, tunnels, offload, filtering, and transport code.

## Risks and test signals
Risks include stale skb header offsets, jumbo/GSO length interpretation, and misuse on non-IPv4 packets. Tests should include encapsulated packets, TCP GSO with zero total length, maximum MTU boundaries, and tunnel transport header access.
