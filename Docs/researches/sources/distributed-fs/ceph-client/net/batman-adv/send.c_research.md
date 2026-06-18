# sources/distributed-fs/ceph-client/net/batman-adv/send.c

## Purpose
Implements the transmit and forwarding queue side of batman-adv. It wraps payloads in batman-adv headers, resolves next hops through originator or translation-table state, sends prepared packets on hard interfaces, fragments oversized unicast traffic, queues delayed broadcast/OGMv1 forwarding packets, retransmits broadcasts, and purges outstanding work during interface or mesh teardown.

## Important APIs And Functions
Transmit APIs include `batadv_send_skb_packet`, `batadv_send_broadcast_skb`, `batadv_send_unicast_skb`, `batadv_send_skb_to_orig`, `batadv_send_skb_prepare_unicast_4addr`, `batadv_send_skb_unicast`, `batadv_send_skb_via_tt_generic`, and `batadv_send_skb_via_gw`. Queue APIs include `batadv_forw_packet_alloc`, `batadv_forw_packet_free`, `batadv_forw_packet_steal`, `batadv_forw_packet_ogmv1_queue`, `batadv_forw_bcast_packet`, `batadv_send_bcast_packet`, `batadv_forw_packet_is_rebroadcast`, and `batadv_purge_outstanding_packets`. Internal queue helpers manage forwarding lists and delayed work.

## Control Flow
Prepared packets go through `batadv_send_skb_packet`, which verifies active/up hard interface state, pushes an Ethernet header, fills source/destination/protocol, sets skb device/protocol metadata, and calls `dev_queue_xmit`. Unicast sending uses `batadv_find_router`; if fragmentation is enabled and the skb exceeds the next-hop MTU, it delegates to `batadv_frag_send_packet`, otherwise it sends to the selected neighbor. Higher-level payload APIs push `BATADV_UNICAST` or `BATADV_UNICAST_4ADDR` headers, set destination originator and TTVN, optionally lower TTVN for roaming clients, and then route to the originator.

Broadcast forwarding clones the skb per outgoing hard interface, suppresses unnecessary rebroadcasts based on neighbor/originator topology, sends immediately when possible, and queues remaining retransmissions on `bat_priv->forw_bcast_list`. Delayed work clones the saved skb, transmits it, decrements `num_bcasts`, requeues while broadcasts remain, or steals and frees the forwarding packet. Purge logic atomically steals matching broadcast and OGMv1 forwarding packets from global lists, cancels delayed work synchronously, and frees claimed packets.

## State And Persistence
State is in-memory only: queued `batadv_forw_packet` objects, delayed-work items, `bcast_queue_left`/`batman_queue_left` capacity counters, per-skb broadcast counters, interface refcounts, and optional BATMAN_V last-unicast timestamps for hardif neighbors. The file follows a consume-on-send pattern: most send helpers consume the skb regardless of success, and queued forwarding packets own their skb until freed.

## Dependencies And Integration Points
Depends on `routing` for next-hop selection, `translation-table` for client lookup and roaming flags, `gateway_client` for gateway forwarding, `fragmentation`, `distributed-arp-table`, `originator`, `hard-interface`, `mesh-interface`, and the batman-adv event workqueue. It is used by receive forwarding, upper-layer mesh-interface transmit paths, TVLV unicast sending, ICMP/TP meter replies, and broadcast flood handling.

## Risks
Skb ownership and clone semantics are the highest risk: callers must not touch skbs after helpers consume or queue them, and cloned broadcast skbs may make original data non-writable. Forwarding packet stealing prevents requeue-after-free races but relies on correct list lock use and `cleanup_list` markers. Queue capacity must be restored exactly once. Broadcast suppression depends on hard-interface neighbor topology and can cause under-flooding if topology state is stale. Purge sleeps through `cancel_delayed_work_sync`, so callers must not hold incompatible locks.

## Test Signals
Useful tests include skb ownership/failure injection around headroom expansion, inactive/down hard-interface sends, unicast fragmentation threshold behavior, TT and gateway lookup failure, broadcast queue saturation, delayed retransmission counts, DAT drop behavior in queued broadcasts, and purge during active delayed work. Counters, debug logs, and lockdep/KASAN are important runtime signals.
