# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_tunnel.c

## Purpose
This module implements the IPv4 IPIP XFRM tunnel type and registers IPv4 tunnel handlers for XFRM tunnel-mode packets. It supports IPsec tunnel transformations that encapsulate IPv4 in IPv4.

## Important APIs, Types, and Functions
Important functions are `ipip_init_state()`, `ipip_output()`, `ipip_xfrm_rcv()`, `xfrm_tunnel_rcv()`, `ipip_init()`, and `ipip_fini()`. Key objects are `ipip_type`, `xfrm_tunnel_handler`, and, when IPv6 is enabled, `xfrm64_tunnel_handler`.

## Control Flow
Module init registers the IPIP XFRM type for `AF_INET`, then registers an IPv4 tunnel handler and optionally an AF_INET6 tunnel handler. State initialization rejects non-tunnel mode and rejects UDP or other encapsulation because this IPIP type supplies its own IPv4 tunnel header. Output pushes the skb back to the network header; input returns the inner IPv4 protocol. Tunnel receive calls `xfrm4_rcv_spi()` using the source address as SPI-like tunnel selector.

## State and Persistence Behavior
Persistent state consists of registered XFRM type and tunnel handler records. Individual XFRM states get `props.header_len = sizeof(struct iphdr)` during init. There is no per-state private allocation.

## Dependencies and Integration Points
It integrates with XFRM type registration, IPv4 tunnel handler registration, module aliasing for XFRM type autoload, and optional IPv6-family tunnel handler registration for IPv6 interop paths.

## Risks
Allowing non-tunnel or encapsulated states would create invalid header expectations. Init failure unwinding must unregister earlier handlers. Receive selector behavior depends on source address matching the XFRM tunnel lookup contract.

## Test Signals
Test module load/unload, tunnel-mode IPIP state creation, rejection of transport-mode and encap states, IPv4-in-IPv4 tunnel packet receive, optional AF_INET6 handler registration, and failure unwinding if handler registration fails.
