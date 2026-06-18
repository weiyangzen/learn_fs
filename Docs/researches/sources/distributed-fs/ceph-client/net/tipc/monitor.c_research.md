# sources/distributed-fs/ceph-client/net/tipc/monitor.c

## Purpose

`monitor.c` implements TIPC's scalable peer monitoring. Instead of every node actively probing every peer in large clusters, it maintains a circular monitor list, assigns domain heads, exchanges compact domain records in link STATE messages, detects suspected lost members from peer reports, and tells links when to monitor, probe, or reset.

## Important APIs, Types, and Functions

`struct tipc_mon_domain` is the on-wire/local domain record containing length, generation, acknowledged generation, member count, up bitmap, and member addresses. `struct tipc_peer` tracks a peer's address, domain, hash/list links, applied domain count, down count, and role flags. `struct tipc_monitor` owns peer hash buckets, peer count, self peer, rwlock, cached outgoing domain record, list/domain generations, net namespace, and timer.

Public functions include `tipc_mon_create()`, `tipc_mon_delete()`, `tipc_mon_peer_up()`, `tipc_mon_peer_down()`, `tipc_mon_remove_peer()`, `tipc_mon_prep()`, `tipc_mon_rcv()`, `tipc_mon_get_state()`, `tipc_mon_reinit_self()`, and netlink threshold/dump helpers. Internal helpers handle endian conversion, domain sizing, peer lookup/list traversal, domain application, lost-member identification, local-domain updates, neighbor updates, and role assignment.

## Control Flow

Creation allocates a monitor per bearer, creates the self peer/domain, starts a randomized periodic timer, and stores the monitor in `tipc_net->monitors[bearer_id]`. Peer up inserts or finds a peer, marks it up, updates local domain if the affected head is self, and reassigns roles. Peer down removes domain state, marks the peer down, identifies potentially lost members if the peer was a head, updates affected domains, and reassigns roles. Removal deletes the peer and may revert all domains when cluster size falls below threshold.

STATE-message send calls `tipc_mon_prep()`. If monitoring is inactive it sends an invalid zero-length record. If the peer has acked the current domain generation it sends a dummy ack-only record; otherwise it copies the cached full domain and sets `ack_gen`. STATE-message receive calls `tipc_mon_rcv()`, validates record length/count/generation, synchronizes per-link monitor state, stores the peer's domain, applies it to the local monitor list, identifies lost members, and reassigns roles. Links call `tipc_mon_get_state()` to decide whether to monitor, probe, or reset.

## State and Persistence Behavior

All state is per net namespace and bearer in memory. The monitor list is a circular ascending list anchored at self plus hash buckets for lookup. Generations `list_gen` and `dom_gen` let link-local `struct tipc_mon_state` cache decisions. Peer `down_cnt` accumulates reports until `MAX_PEER_DOWN_EVENTS` triggers reset. The timer periodically corrects self domain size when peer count changes.

## Dependencies and Integration Points

The file depends on generic netlink, TIPC core/address/bearer/netlink helpers, timers, rwlocks, hlist/list APIs, and link STATE-message storage. It integrates tightly with `link.c`: link protocol embeds monitor records via `tipc_mon_prep()`, consumes peer records via `tipc_mon_rcv()`, and queries state through `tipc_mon_get_state()`. Netlink monitor commands expose threshold, monitor, and peer details.

## Risks and Edge Cases

Domain record validation is critical because records arrive from peers. Role assignment depends on sorted circular list invariants; insertion/removal bugs can misassign heads or skip local monitoring. Endian conversion must match the on-wire record. Threshold transitions between full-mesh and active monitoring must free or recreate peer domains carefully. `down_cnt` false positives can reset healthy links if duplicate/stale domain records are mishandled.

## Test Signals

Test clusters below and above monitor threshold, peer up/down churn, bearer deletion, node address reinitialization, malformed domain lengths/counts, generation duplicate handling, probe/reset escalation after repeated down reports, and netlink monitor/peer dumps. STATE packet captures should show dummy ack-only records after peer acknowledgement and full records on generation changes.
