# sources/distributed-fs/ceph-client/net/batman-adv/send.h

## Purpose
Declares batman-adv transmit and forwarding-queue helpers. It is the shared contract for modules that need to send prepared packets, encapsulate payloads for unicast/4-address forwarding, queue broadcasts, or purge delayed forwarding packets.

## Important APIs And Types
The header declares forwarding packet lifecycle functions (`batadv_forw_packet_alloc`, `batadv_forw_packet_free`, `batadv_forw_packet_steal`, `batadv_forw_packet_ogmv1_queue`, `batadv_forw_packet_is_rebroadcast`), raw send helpers (`batadv_send_skb_packet`, `batadv_send_broadcast_skb`, `batadv_send_unicast_skb`, `batadv_send_skb_to_orig`), broadcast queue helpers (`batadv_forw_bcast_packet`, `batadv_send_bcast_packet`, `batadv_purge_outstanding_packets`), and unicast encapsulation/lookup helpers (`batadv_send_skb_prepare_unicast_4addr`, `batadv_send_skb_unicast`, `batadv_send_skb_via_tt_generic`, `batadv_send_skb_via_gw`). Inline wrappers `batadv_send_skb_via_tt` and `batadv_send_skb_via_tt_4addr` bind common packet type/subtype values.

## Control Flow
The inline wrappers simply forward to `batadv_send_skb_via_tt_generic` with `BATADV_UNICAST` or `BATADV_UNICAST_4ADDR`. All other behavior is implemented in `send.c`; the header documents lookup-by-TT and encapsulate-then-send semantics.

## State And Persistence
The header owns no state. It exposes APIs that operate on skbs, forwarding packet objects, hard-interface/originator/neighbor refcounted structures, and queue locks.

## Dependencies And Integration Points
Includes `main.h`, kernel skb/spinlock/compiler/types headers, and `uapi/linux/batadv_packet.h` for packet constants. It is consumed by routing, TVLV, ICMP/TP meter, fragmentation, and upper transmit paths.

## Risks
The public API encodes skb ownership implicitly: most send helpers consume skbs. Misunderstanding the inline wrappers can lead to wrong packet subtype or stale destination hints. Signature changes have broad impact because send helpers sit on hot data and control paths.

## Test Signals
Compilation catches signature drift. Packet-level tests should exercise both inline wrappers, especially 4-address subtype propagation and TT lookup with and without `dst_hint`.
