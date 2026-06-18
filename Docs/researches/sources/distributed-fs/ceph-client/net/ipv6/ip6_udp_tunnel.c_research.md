# sources/distributed-fs/ceph-client/net/ipv6/ip6_udp_tunnel.c

## Purpose
This file provides small shared helpers for IPv6 UDP-based tunnel drivers. It creates kernel UDP/IPv6 sockets, builds IPv6/UDP tunnel headers around an skb, and performs route lookup with optional dst-cache support for tunnel endpoints.

## Important APIs, Types, And Functions
Exported APIs are `udp_sock_create6()`, `udp_tunnel6_xmit_skb()`, and `udp_tunnel6_dst_lookup()`. They operate on `struct udp_port_cfg`, `struct socket`, `struct dst_entry`, `struct ip_tunnel_key`, `struct dst_cache`, IPv6 addresses, and UDP source/destination ports.

`udp_sock_create6()` supports v6-only mode, binding to an interface index, binding to local IPv6 address/port, optional connected peer address/port, and toggling UDPv6 checksum behavior. `udp_tunnel6_xmit_skb()` pushes `struct udphdr` and `struct ipv6hdr`, computes UDPv6 checksum with `udp6_set_csum()`, and sends via `ip6tunnel_xmit()`. `udp_tunnel6_dst_lookup()` constructs `flowi6` from tunnel key, ports, mark, traffic class, label, and output interface, then calls `ip6_dst_lookup_flow()`.

## Control Flow
Socket creation allocates an AF_INET6 datagram kernel socket, applies optional `IPV6_V6ONLY` and bind-to-index constraints, binds the local endpoint, optionally connects the peer endpoint, sets no-checksum tx/rx flags according to configuration, and returns the socket. All failure paths shut down and release the partially created socket and clear the caller's pointer.

Transmit assumes the caller already has route and headroom. It prepends UDP, assigns ports and length, attaches the dst to the skb, computes checksum or no-checksum state, prepends IPv6, fills flow label, payload length, next header, hop limit, and addresses, and hands off to the generic IPv6 tunnel transmit helper.

Route lookup first tries `dst_cache_get_ip6()` when a cache is supplied. On miss it initializes `flowi6`, performs XFRM-aware IPv6 dst lookup using the supplied socket, maps route failures to `-ENETUNREACH`, rejects circular routes where the dst device is the tunnel device, stores the selected source in both dst cache and caller storage, and returns a held dst.

## State And Persistence
The helpers own no persistent global state. Socket state is held by the caller after successful creation. The dst lookup helper may update a caller-provided `dst_cache` and writes the selected source address through `saddr`. Checksumming flags are stored on the UDP socket.

## Dependencies And Integration Points
This file is a library for drivers such as VXLAN, GENEVE, GUE, or other UDP tunnel users. It depends on kernel socket APIs, UDP tunnel configuration, IPv6 route/XFRM lookup, IPv6 checksum helpers, `ip6tunnel_xmit()`, and optional `CONFIG_DST_CACHE`.

## Risks And Edge Cases
UDPv6 checksum disabling is protocol-sensitive; many deployments require IPv6 UDP checksums except for explicitly permitted tunnel modes. Route lookup returns `-ENETUNREACH` for any `ip6_dst_lookup_flow()` error, losing more specific errno. Circular-route detection is only `dst_dev(dst) == dev`; more complex recursive tunnel loops rely on upper layers. The xmit helper does not validate headroom or skb writability.

## Test Signals
Test socket creation with local-only and connected peer configs, v6-only sockets, bind-ifindex failures, checksum on/off settings, route lookup cache hit/miss, no-route and circular-route failures, selected source address caching, and transmit packet capture validating IPv6 payload length, UDP length/checksum, flow label, hop limit, and source/destination ports.
