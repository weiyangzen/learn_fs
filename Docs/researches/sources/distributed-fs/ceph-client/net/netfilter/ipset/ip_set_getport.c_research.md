# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_getport.c

## Purpose

`ip_set_getport.c` provides shared helpers for extracting layer-4 port-like values from IPv4 and IPv6 skbs for IP set packet-path matching. It handles non-linear skbs through `skb_header_pointer` and exports IPv4 and IPv6 helpers to set-type modules.

## Important APIs

The internal `get_port` handles TCP, SCTP, UDP, UDPLITE, ICMP, and ICMPv6. For TCP/SCTP/UDP/UDPLITE it returns the selected source or destination port. For ICMP and ICMPv6 it synthesizes a 16-bit value from type and code. It also returns the protocol through `proto`.

`ip_set_get_ip4_port` extracts the IPv4 header, computes the transport offset, rejects invalid protocol values and transport fragments with nonzero offset for protocols where the L4 header is unavailable, and then calls `get_port`. `ip_set_get_ip6_port`, compiled when `CONFIG_IP6_NF_IPTABLES` is enabled, uses `ipv6_skip_exthdr` to locate the final header, rejects non-initial fragments, and calls `get_port`.

## Control Flow And State

Both exported functions are read-only packet parsers. They return `true` when the protocol can be represented and the needed header bytes are available, otherwise `false`. No state is stored and no skb data is modified.

## Dependencies And Integration

The file depends on IPv4/IPv6 headers, ICMP/ICMPv6, SCTP, UDP/TCP header definitions, `skb_header_pointer`, and IPv6 extension-header parsing. It is built into the `ip_set` core module by the ipset Makefile and used by port-bearing set types, including `bitmap:port` in this subset.

## Risks

Fragment and non-linear skb handling are the main risks. Returning a port for a non-initial fragment would allow false matches, while failing to use `skb_header_pointer` would break non-linear skbs. IPv6 extension parsing must reject invalid offsets and fragmented packets where the L4 header is not available. Consumers may further filter accepted protocols, so helper behavior should remain protocol-general.

## Test Signals

Packet tests should cover linear and non-linear skbs, IPv4 fragments with offset zero and nonzero, IPv6 extension headers and fragments, TCP/UDP/SCTP/UDPLITE source and destination extraction, ICMP type/code extraction, unsupported protocols, truncated headers, and builds with and without IPv6 iptables support.
