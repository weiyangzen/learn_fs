# sources/distributed-fs/ceph-client/net/ipv4/xfrm4_input.c

## Purpose
This file contains IPv4-specific XFRM/IPsec input finishing and ESP-in-UDP decapsulation support. It restores IPv4 transport headers after transform processing, reinjects packets through prerouting or GRO paths, and handles NAT-T keepalive/IKE/ESP distinction for UDP encapsulated ESP.

## Important APIs, Types, and Functions
Key functions are `xfrm4_transport_finish()`, `xfrm4_udp_encap_rcv()`, `xfrm4_gro_udp_encap_rcv()`, and `xfrm4_rcv()`. Internals include `xfrm4_rcv_encap_finish()`, `__xfrm4_udp_encap_rcv()`, `xfrm_trans_queue()`, `xfrm4_rcv_encap()`, `xfrm4_rcv_spi()`, and callbacks from UDP encap sockets.

## Control Flow
For transformed transport packets, `xfrm4_transport_finish()` restores the original protocol, updates total length/checksum, and either returns a protocol resubmit value, rebuilds MAC headers for GRO offload, or passes through IPv4 prerouting before `dst_input()`. UDP encap receive checks socket encap type, pulls enough bytes to inspect NAT-T payload, drops one-byte keepalives, passes IKE/non-ESP marker packets back to UDP, strips UDP/non-ESP marker bytes for ESP, and invokes XFRM input.

## State and Persistence Behavior
The file mostly mutates transient skb state: IP protocol, total length, transport offset, MAC/network headers, XFRM skb control blocks, and GRO control fields. Persistent socket state is read from `udp_sock->encap_type`.

## Dependencies and Integration Points
It integrates UDP encap sockets, XFRM core input, IPv4 routing, netfilter prerouting, ESP net offload GRO callbacks, skb offload metadata, and ICMP/error behavior from surrounding XFRM protocol code.

## Risks
Offset and length handling are critical; stripping the wrong bytes corrupts ESP or exposes IKE packets to XFRM. GRO paths must preserve full L2 headers for VLAN reinjection. Keepalive and non-ESP marker classification must remain compatible with NAT-T.

## Test Signals
Test ESP-in-UDP keepalive drop, IKE pass-through, ESP with and without non-ESP marker, malformed short skb, GRO ESP-in-UDP aggregation, async transport finish, netfilter-enabled and disabled builds, and VLAN/L2 header preservation.
