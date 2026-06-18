# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_core.c

## Purpose
This file provides common IPv4 UDP tunnel helpers for kernel tunnel drivers. It creates/binds/connects kernel UDP sockets, installs encapsulation callbacks, notifies NICs about tunnel ports, transmits UDP-encapsulated packets, releases tunnel sockets, builds tunnel receive metadata, and performs IPv4 route lookup for tunnel egress.

## Important APIs, Types, and Functions
Key exports are `udp_sock_create4()`, `setup_udp_tunnel_sock()`, `udp_tunnel_push_rx_port()`, `udp_tunnel_drop_rx_port()`, `udp_tunnel_notify_add_rx_port()`, `udp_tunnel_notify_del_rx_port()`, `udp_tunnel_xmit_skb()`, `udp_tunnel_sock_release()`, `udp_tun_rx_dst()`, and `udp_tunnel_dst_lookup()`. It uses `struct udp_port_cfg`, `struct udp_tunnel_sock_cfg`, `struct udp_tunnel_info`, `struct ip_tunnel_key`, `struct metadata_dst`, and `struct dst_cache`.

## Control Flow
Socket creation allocates a kernel AF_INET datagram socket, optionally binds to an interface, binds local address/port, optionally connects a peer, and sets transmit checksum policy. Setup clears multicast loopback, enables checksum conversion, stores user data and encap/GRO callbacks in `udp_sock`, enables UDP tunnel encap, registers GRO receive type, and adds the socket to fast GRO lookup if it is a wildcard kernel listener. Transmit prepends a UDP header, sets checksum via `udp_set_csum()`, clears IP options, and delegates to `iptunnel_xmit()`.

## State and Persistence Behavior
Persistent state lives on the kernel socket: user data, encap receive/error/destroy callbacks, GRO callbacks, encap type, checksum conversion, and global tunnel encap/GRO references. Route cache entries may persist in `dst_cache`. Release clears user data under RCU before shutdown and `sock_release()`.

## Dependencies and Integration Points
This file integrates tunnel drivers with UDP core, UDP tunnel NIC offload, IPv4 routing, dst metadata, ip tunnel transmit, checksum helpers, RCU socket user data, RTNL-protected netdevice iteration, and optional destination cache.

## Risks
Incorrect callback installation or release ordering can leave stale tunnel state reachable by receive paths. Wildcard GRO lookup is only valid for unconnected/unbound-device kernel sockets. Route lookup must reject circular routes back to the tunnel device. Checksum policy mismatches can break tunnel interoperability.

## Test Signals
Test tunnel socket create error unwinding, bind-ifindex, connected and unconnected sockets, setup/release under RCU readers, NIC add/drop notifications, `udp_tunnel_xmit_skb()` checksums, metadata source/destination ports, dst cache hits, no-route and circular-route errors.
