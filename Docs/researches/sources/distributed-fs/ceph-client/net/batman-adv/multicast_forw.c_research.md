# sources/distributed-fs/ceph-client/net/batman-adv/multicast_forw.c

## Purpose
Implements the batman-adv multicast packet forwarding format. It constructs multicast packets with a tracker TVLV listing destination originators, forwards incoming or locally generated packets per next-hop neighbor, removes destinations already assigned to other copies, and shrinks tracker headers to avoid redundant retransmission.

## APIs, Types, and Functions
Public symbols are `batadv_mcast_forw_tracker_tvlv_handler()`, `batadv_mcast_forw_packet_hdrlen()`, `batadv_mcast_forw_push()`, and `batadv_mcast_forw_mcsend()`. Important internal helpers push padding, destination MACs, TT recipients, want-all recipients, router recipients, tracker TVLV headers, and the outer `struct batadv_mcast_packet`. Forwarding helpers include `batadv_mcast_forw_packet()`, `batadv_mcast_forw_scrub_dests()`, `batadv_mcast_forw_shrink_tracker()`, and the shrink/pack/header-update routines.

## Control Flow
Local encapsulation starts in `batadv_mcast_forw_push()`: it expands skb headroom to fit an IPv6-minimum-MTU multicast packet, remembers the transport header, pushes destination originator MACs from TT and want lists, adjusts two-byte TVLV padding depending on the actual destination count, pushes the multicast tracker TVLV header, and finally pushes the batman-adv multicast packet header. `batadv_mcast_forw_mcsend()` then calls the common forwarding engine with `local_xmit=true`.

`batadv_mcast_forw_packet()` validates the tracker TVLV length, marks the checksum invalid, iterates destination originator addresses, drops zero/multicast invalid entries, records local receive when the destination is one of this node's MACs, resolves each remaining originator to its next-hop neighbor, copies the skb for that neighbor, scrubs the copy so it only contains destinations reachable through that next hop, scrubs the original to prevent duplicate sends, shrinks the copy's tracker TVLV, and sends it via `batadv_send_unicast_skb()`. It returns `NET_RX_SUCCESS` only if the local mesh interface should also receive the decapsulated payload.

## State and Persistence
This file mostly mutates transient skbs. Persistent state is read from TT global entries, multicast want lists in `bat_priv->mcast`, originator routing state, BLA gateway state, and per-mesh counters. It updates multicast TX, local TX, forwarding, and byte counters. No long-lived objects are allocated here besides skb copies.

## Dependencies and Integration
Depends on packet UAPI structures from `batadv_packet.h`, multicast policy from `multicast.c`, originator route lookup, TT global tables, BLA filtering, send helpers, skb headroom/linearization helpers, and Ethernet/VLAN/IP constants. Incoming multicast packets reach this file through the TVLV handler registered by `multicast.c`.

## Risks
The tracker TVLV is variable-length and alignment-sensitive; wrong padding or header-length updates can corrupt the packet. The code assumes the tracker TVLV is linearized and that `skb_network_header()` points at `struct batadv_tvlv_mcast_tracker`. Destination counts can diverge from earlier estimates because BLA suppression and concurrent list changes remove entries. Failure paths must preserve skb ownership and avoid leaving partially pushed headers on success callers. Next-hop grouping by neighbor is routing-state sensitive and may drop stale or unresolved originators.

## Test Signals
Tests should cover header length for odd/even destination counts, padding add/remove after actual destination count changes, U16 destination-count bounds, malformed tracker lengths, zero and multicast destination entries, local receive plus forwarding in the same packet, multiple destinations behind one next hop, destinations behind different next hops, route-missing drops, BLA gateway suppression, MTU/headroom expansion failure, and packet capture confirming shrunk tracker TVLVs on forwarded copies.
