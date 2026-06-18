# sources/distributed-fs/ceph-client/net/ipv4/udp_offload.c

## Purpose
This file implements IPv4 UDP GSO, UFO compatibility, GRO, UDP tunnel segmentation, and UDP tunnel GRO dispatch. It is the offload bridge between the generic skb segmentation/GRO core, UDP sockets, and tunnel protocols such as VXLAN, GENEVE, FoU/GUE, and ESP-in-UDP.

## Important APIs, Types, and Functions
Important APIs include `skb_udp_tunnel_segment()`, `__udp_gso_segment()`, `udp4_ufo_fragment()`, `udp_gro_receive()`, `udp4_gro_receive()`, `udp_gro_complete()`, `udp4_gro_complete()`, `udp_tunnel_update_gro_lookup()`, `udp_tunnel_update_gro_rcv()`, and `udpv4_offload_init()`. State includes `udp_tunnel_gro_types`, static calls, per-net `udp_tunnel_gro`, `NAPI_GRO_CB`, `skb_shinfo()->gso_type`, and UDP socket `gro_receive/gro_complete` callbacks.

## Control Flow
Tunnel GSO temporarily strips the outer UDP/tunnel header, selects an inner segmenter by encapsulation type, segments the inner packet, then rebuilds the outer headers and checksum state on every segment. Plain UDP L4 GSO validates MSS and checksum-start geometry, optionally handles fraglist packets, segments with `skb_segment()`, fixes UDP length/checksum per segment, and preserves socket write accounting. GRO validates UDP checksum, detects tunnel sockets when encap is enabled, either aggregates plain UDP segments or calls a tunnel GRO callback, and completes aggregated packets as UDP L4 GSO or tunnel GSO.

## State and Persistence Behavior
Persistent state is small but global: tunnel GRO callback types and counts, a static call enabled only when exactly one tunnel GRO type exists, and per-net single-socket tunnel lookup hints. Per-packet state is encoded in skb headers, checksum mode, encapsulation flags, GRO control block fields, and GSO metadata.

## Dependencies and Integration Points
The code integrates with `inet_add_offload()`, generic GSO/GRO, net device checksum/offload features, UDP tunnel sockets, XFRM GRO callbacks, IPv6 offload tables for shared helpers, static branches/calls, and NAPI GRO recursion protection.

## Risks
Header offset restoration, checksum adjustment, fraglist geometry, and destructor/write-memory accounting are high-risk. Tunnel GRO callback registration must avoid dangling function pointers and must disable the static call when multiple tunnel types exist. GRO of packets that might actually be tunnels can corrupt inner streams if socket detection is wrong.

## Test Signals
Test UDP_SEGMENT transmit, fraglist GRO/GSO, software fallback when hardware lacks checksum/GSO, UDP tunnels with and without outer checksums, remcsum, IPsec/XFRM interaction, multiple tunnel GRO types, single-socket tunnel lookup updates, malformed UDP lengths, zero checksums, and device feature combinations.
