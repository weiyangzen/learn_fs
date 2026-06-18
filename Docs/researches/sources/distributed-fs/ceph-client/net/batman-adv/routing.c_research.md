# sources/distributed-fs/ceph-client/net/batman-adv/routing.c

## Purpose
Implements the receive-side routing logic for batman-adv packets after a hard interface has accepted a frame. It validates packet shapes, updates originator routes, selects next hops, handles ICMP echo/TTL/throughput-meter traffic, forwards or decapsulates unicast, TVLV, fragment, broadcast, and multicast packets, and coordinates with translation-table, DAT, BLA, fragmentation, and multicast subsystems before handing payloads to the mesh interface.

## Important APIs And Functions
Public entry points are `batadv_update_route`, `batadv_window_protected`, `batadv_check_management_packet`, `batadv_recv_icmp_packet`, `batadv_recv_unicast_packet`, `batadv_recv_unicast_tvlv`, `batadv_recv_unhandled_unicast_packet`, `batadv_recv_frag_packet`, `batadv_recv_bcast_packet`, optional `batadv_recv_mcast_packet`, and `batadv_find_router`. Internal helpers include `_batadv_update_route`, `batadv_recv_my_icmp_packet`, `batadv_recv_icmp_ttl_exceeded`, `batadv_check_unicast_packet`, `batadv_last_bonding_get`, `batadv_last_bonding_replace`, `batadv_route_unicast_packet`, `batadv_reroute_unicast_packet`, and `batadv_check_unicast_ttvn`.

## Control Flow
Route updates replace an originator's per-interface router under `orig_node->neigh_list_lock`, take a reference on the new neighbor, drop the old router after the RCU pointer swap, and delete global TT entries when a route disappears. Router selection starts with `batadv_orig_router_get`; if bonding is enabled for first-hop traffic it rotates among similar-or-better per-interface candidates using `orig_node->last_bonding_candidate`.

ICMP receive validates unicast Ethernet addressing and local destination, appends record-route data when present, locally answers echo requests, dispatches `BATADV_TP` packets to `batadv_tp_meter_recv`, generates TTL exceeded responses for traceroute-style echo requests, or decrements TTL and forwards through `batadv_send_skb_to_orig`. Unicast receive verifies the local outer destination, checks and possibly repairs stale TTVN state through the translation table, drops BLA backbone duplicates, lets DAT snoop ARP/DHCP, and finally either delivers with `batadv_interface_rx` or forwards. Fragment receive may forward oversized fragments, buffer/merge fragments, and re-enter `batadv_batman_skb_recv` for assembled packets. Broadcast receive enforces broadcast outer destination, rejects self-originated traffic, applies duplicate and reset-window checks, queues rebroadcast, filters BLA backbone traffic, then snoops DAT and delivers locally. Multicast receive parses TVLV payload, lets multicast TVLV handlers decide forwarding/local delivery, and accounts multicast counters.

## State And Persistence
State is volatile kernel state: originator router RCU pointers, neighbor/originator refcounts, bonding candidate pointers, broadcast sequence windows, per-originator reset timestamps, packet counters, and skb contents. The file does not persist to disk. It mutates skb headers in place after `skb_cow`/linearization, updates checksums for TTVN rerouting, decrements TTLs, and consumes or frees skbs according to kernel ownership conventions.

## Dependencies And Integration Points
Depends on `originator`, `send`, `translation-table`, `fragmentation`, `distributed-arp-table`, `bridge_loop_avoidance`, `tp_meter`, `tvlv`, `mesh-interface`, `hard-interface`, `bitarray`, and batman-adv algorithm callbacks. It is the receive integration point between lower hard-interface packet demux and upper mesh-interface delivery. It also drives route cleanup in TT on route deletion and uses DAT/BLA decisions to suppress duplicate or bridged traffic.

## Risks
Correctness depends on strict skb ownership: most forwarding helpers consume the skb, while local error exits must free it exactly once. Stale TTVN repair can misroute if TT state is inconsistent or if checksum adjustment is missed after header edits. Bonding candidate rotation touches RCU-protected ifinfo/router objects and is refcount-sensitive. Broadcast duplicate protection depends on sequence arithmetic and reset windows. Several handlers linearize packets and may drop under memory pressure. TTL-exceeded return-code translation appears easy to misread because transmit and receive status constants differ.

## Test Signals
Best signals are kernel build coverage across `CONFIG_BATMAN_ADV_MCAST`, packet-injection tests for malformed headers, self-originated broadcasts, TTL expiry, TTVN mismatch rerouting, roaming clients, DAT/BLA filtering, fragment merge/forward cases, and bonding path selection. Runtime counters (`BATADV_CNT_FORWARD`, broadcast, fragment, multicast counters) plus batman-adv debug logs can validate forwarding decisions in integration tests.
