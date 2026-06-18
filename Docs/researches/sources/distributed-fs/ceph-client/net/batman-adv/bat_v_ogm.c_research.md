# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.c

## Purpose
`bat_v_ogm.c` implements BATMAN V OGMv2 generation, aggregation, receive processing, throughput metric propagation, route updates, forwarding, and per-mesh OGMv2 resource management.

## Important APIs and Functions
- `batadv_v_ogm_orig_get`: retrieve or create originator entries.
- Mesh lifecycle: `batadv_v_ogm_init` and `batadv_v_ogm_free`.
- Interface lifecycle: `batadv_v_ogm_iface_enable`, `batadv_v_ogm_iface_disable`, `batadv_v_ogm_primary_iface_set`.
- Timers/work: `batadv_v_ogm_start_timer`, `batadv_v_ogm_send`, `batadv_v_ogm_aggr_work`, and queue timer helpers.
- Aggregation: `batadv_v_ogm_queue_on_if`, `batadv_v_ogm_aggr_send`, `batadv_v_ogm_aggr_list_free`, `batadv_v_ogm_len`, and `batadv_v_ogm_aggr_packet`.
- Routing: `batadv_v_forward_penalty`, `batadv_v_ogm_metric_update`, `batadv_v_ogm_route_update`, `batadv_v_ogm_forward`, and `batadv_v_ogm_process`.
- `batadv_v_ogm_packet_recv`: registered packet handler for OGM2.

## Control Flow
Mesh init allocates an OGM2 template with max throughput, TTL, version, random sequence number, delayed work, and mutex. Periodic send commits TT changes, appends TVLVs, stamps seqno/tvlv length, clones the skb to active lower interfaces, suppresses pointless broadcasts, and queues or sends per aggregation policy. Aggregation queues are flushed periodically or when a new packet would exceed MTU/aggregation byte limits. Receive validates algorithm and management packet shape, drops self-sourced frames, unpacks aggregates, and processes each OGM. Processing requires prior ELP neighbor discovery, creates originator/neighbor records, clamps advertised path throughput to the one-hop ELP throughput, updates default and per-outgoing-interface metrics, processes TVLVs for new default-table OGMs, updates routes when the neighbor is better or sufficiently newer, and forwards only from the best next hop.

## State and Persistence
State persists in the per-mesh OGM buffer/length/seqno/work/mutex, per-hard-interface aggregation queues and lengths, originator ifinfo last real/forwarded seqnos and TTL, neighbor ifinfo throughput and last seqno, hardif-neighbor ELP throughput, and route table next-hop selections.

## Dependencies and Integration
Depends on ELP-discovered hardif neighbors, originator hash, route update helpers, hard-interface broadcast suppression, TT/TVLV subsystems, workqueues, skb aggregation, RCU/krefs, and BATMAN V algorithm registration in `bat_v.c`.

## Risks and Test Signals
Risks include accepting OGMs before ELP state exists, aggregation length parsing, mutable skb data during per-aggregate processing, sequence reboot protection, forwarding loops, best-next-hop strictness, throughput unit/penalty errors, and cleanup of delayed work/queued skbs. Test signals include OGM2 send cadence, aggregation enabled/disabled, TVLV propagation, route convergence by throughput, suppression cases from `batadv_hardif_no_broadcast`, ELP-missing OGM drops, old/restarted sequence injection, and mesh/interface teardown with no delayed work leaks.
