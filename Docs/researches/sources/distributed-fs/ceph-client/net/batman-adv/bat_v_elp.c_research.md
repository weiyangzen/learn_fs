# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.c

## Purpose
`bat_v_elp.c` implements BATMAN V Echo Location Protocol. ELP discovers one-hop neighbors, sends periodic broadcast probes, optionally sends WiFi unicast probes to feed rate control, and updates per-neighbor throughput estimates used by OGMv2 routing.

## Important APIs, Types, and Functions
- `struct batadv_v_metric_queue_entry`: temporary list item for neighbor throughput updates outside RCU.
- `batadv_v_elp_iface_enable` / `batadv_v_elp_iface_disable`: allocate/free the per-interface ELP skb and start/cancel periodic work.
- `batadv_v_elp_iface_activate` and `batadv_v_elp_primary_iface_set`: keep ELP originator MAC aligned with the primary interface.
- `batadv_v_elp_periodic_work`: sends broadcast ELPs, probes neighbors, queues metric updates, and reschedules itself.
- `batadv_v_elp_get_throughput`: obtains throughput from user override, cfg80211 station data, ethtool link settings, or default fallback.
- `batadv_v_elp_packet_recv`: validates incoming ELPs and updates neighbor state via `batadv_v_elp_neigh_update`.

## Control Flow
Interface enable allocates an ELP template skb, randomizes ELP seqno, initializes duplex/default-warning flags, and starts a jittered periodic timer. The periodic worker skips inactive/removing/deactivating interfaces, clones and broadcasts the ELP skb with current seqno/interval, increments seqno, probes WiFi neighbors if recent unicast traffic is insufficient, then updates throughput metrics outside RCU because cfg80211/ethtool paths may sleep. Receive handling drops malformed/self/wrong-algorithm packets, requires a selected primary interface, creates/updates originator, neighbor, and hardif-neighbor records, and ignores old ELP seqnos unless the peer appears restarted.

## State and Persistence
State persists in per-hard-interface ELP skb, ELP seqno, interval, flags (`FULL_DUPLEX`, default-warning), neighbor latest seqno/interval, neighbor `last_seen`, and EWMA throughput.

## Dependencies and Integration
Integrates with BATMAN V OGM originator creation, hard-interface neighbor tables, cfg80211, ethtool, RTNL locking, workqueues, send helpers, route/originator state, and debug logging.

## Risks and Test Signals
Risks include RTNL deadlock avoidance (`rtnl_trylock`), stale/missing throughput data, default throughput warning behavior, WiFi probe allocation, RCU-to-sleeping context handoff, and old sequence acceptance after restart. Test signals include ELP broadcast cadence, neighbor discovery before OGM acceptance, throughput override, cfg80211 expected throughput path, ethtool full/half-duplex detection, default fallback warning once per enable, and cleanup canceling delayed work and freeing skb.
