# sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.c

## Purpose
`bat_iv_ogm.c` implements the BATMAN IV routing algorithm. It generates and forwards OGMv1 packets, computes transmission quality (TQ), maintains sequence-number windows, updates originator routes, provides neighbor/originator/gateway netlink dumps, and registers the `BATMAN_IV` algorithm.

## Important APIs, Types, and Functions
- `enum batadv_dup_status`: classifies OGM sequence handling as no duplicate, originator duplicate, neighbor duplicate, or protected.
- Interface ops: `batadv_iv_ogm_iface_enable`, `batadv_iv_ogm_iface_disable`, `batadv_iv_ogm_iface_update_mac`, `batadv_iv_ogm_primary_iface_set`, and `batadv_iv_iface_enabled`.
- OGM scheduling/forwarding: `batadv_iv_ogm_schedule_buff`, `batadv_iv_ogm_queue_add`, aggregation helpers, `batadv_iv_send_outstanding_bat_ogm_packet`, and `batadv_iv_ogm_receive`.
- Metric/routing: `batadv_iv_ogm_update_seqnos`, `batadv_iv_ogm_calc_tq`, `batadv_iv_ogm_orig_update`, and `batadv_iv_ogm_process_per_outif`.
- Netlink/gateway callbacks: neighbor/originator dump functions, `batadv_iv_gw_get_best_gw_node`, `batadv_iv_gw_is_eligible`, and `batadv_iv_gw_dump`.
- `batadv_iv_init`: registers the OGM packet handler and the algorithm ops.

## Control Flow
Enabling a hard interface allocates an OGM template, randomizes its sequence number, and initializes packet fields. The enabled callback starts periodic OGM scheduling. Primary-interface OGMs commit TT changes, append TVLVs, increment seqno, slide own broadcast windows, and queue cloned packets to all active lower interfaces; secondary OGMs are sent only on their own interface. Received OGM aggregates are unpacked and processed first for the default originator table and then for each active outgoing interface. Processing rejects self/echo/not-best packets, updates duplicate windows, computes bidirectional TQ from own rebroadcast counts and neighbor receive counts, updates routes when a neighbor is better, handles TVLVs, and forwards eligible packets with TTL and hop penalty adjustments.

## State and Persistence
State persists in per-hard-interface `bat_iv` OGM buffers, sequence atomics, mutexes, forward queues, per-originator `bat_iv` counters, per-originator-interface broadcast windows and last seqno/TTL, per-neighbor-interface TQ ring buffers and averages, gateway selection class, and the global receive handler/algorithm registration.

## Dependencies and Integration
Integrates with originator hash management, route updates, hard-interface state, `bitarray.c` sequence windows, send/forward queues, TVLV and translation-table code, gateway client code, generic netlink, workqueues, RCU, krefs, and debug logging.

## Risks and Test Signals
Risks include sequence-window protection around reboots, aggregation bounds, skb clone/copy ownership, route flapping from TQ ties, lock ordering across RCU/spinlocks/mutexes, forwarding loops, and per-interface state cleanup. Test signals include OGM send/receive counters, route convergence in multi-hop topologies, duplicate/reordered/old sequence injection, TVLV propagation, gateway reselection by TQ, aggregation on/off, interface activation/removal, and netlink dumps for neighbors/originators/gateways under small skb cursors.
