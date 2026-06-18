# sources/distributed-fs/ceph-client/include/net/udp_tunnel.h

## Purpose

`udp_tunnel.h` defines kernel UDP tunnel socket creation, receive callbacks, transmit helpers, GSO/offload handling, destination lookup, metadata construction, GRO registration, and NIC UDP tunnel port offload notification APIs.

## Important APIs, types, and functions

Key types include `struct udp_port_cfg`, callback typedefs for encap receive/error/GRO/destroy, `struct udp_tunnel_sock_cfg`, `enum udp_parsable_tunnel_type`, `struct udp_tunnel_info`, `struct udp_tunnel_nic_info`, `struct udp_tunnel_nic_shared`, and `struct udp_tunnel_nic_ops`. Important functions and helpers include `udp_sock_create4()`, `udp_sock_create6()`, `udp_sock_create()`, `setup_udp_tunnel_sock()`, `udp_tunnel_xmit_skb()`, `udp_tunnel6_xmit_skb()`, `udp_tunnel_handle_partial()`, `udp_tunnel_set_inner_protocol()`, `udp_tunnel_sock_release()`, `udp_tunnel_dst_lookup()`, `udp_tunnel6_dst_lookup()`, `udp_tun_rx_dst()`, `udp_tunnel_handle_offloads()`, `udp_tunnel_cleanup_gro()`, `udp_tunnel_encap_enable()`, and the `udp_tunnel_nic_*` helpers.

## Control flow

Tunnel drivers create AF_INET or AF_INET6 UDP sockets with `udp_port_cfg`, install callbacks with `setup_udp_tunnel_sock()`, and enable encapsulation dispatch. On transmit they perform route lookup, set UDP/IP encapsulation headers, handle offloads, and send through IPv4 or IPv6. On receive, the UDP layer calls encap/GRO callbacks based on the socket configuration. NIC offload management notifies devices about parsable tunnel ports through add/delete/reset/dump helpers under RTNL or device-specific locks.

## State and persistence behavior

Socket state stores encap type, callback pointers, and user data in `udp_sock`. Tunnel port offload state persists in netdevice UDP tunnel tables managed by the udp_tunnel module and optionally shared across devices. Static keys in UDP/UDPv6 persist while tunnel sockets are active. Destination caches may persist route lookup results.

## Dependencies and integration points

It depends on IP tunnel metadata, UDP core, IPv6 conditionally, netdevice notifier chains, dst cache, GRO, and NIC feature flags. It integrates with VXLAN, Geneve, VXLAN-GPE, XFRM UDP encapsulation, NIC RX tunnel port offloads, and tunnel metadata destinations.

## Risks and test signals

Risks include family mismatch in socket creation, checksum policy errors for IPv6 zero checksums, partial GSO flag stripping mistakes, overriding inner protocol for nested tunnels, best-effort NIC port notifications being treated as authoritative, and lock ordering around shared NIC tables. Tests should cover IPv4/IPv6 tunnel creation, callback install/destroy, encapsulated transmit with and without checksums, nested partial offload, GRO lookup cleanup, NIC port add/delete/reset, shared table bounds, and `!CONFIG_NET_UDP_TUNNEL` stubs.
