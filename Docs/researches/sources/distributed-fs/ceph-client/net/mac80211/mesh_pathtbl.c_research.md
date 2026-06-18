# sources/distributed-fs/ceph-client/net/mac80211/mesh_pathtbl.c

## Purpose
`mesh_pathtbl.c` owns the persistent path-storage layer for mac80211 mesh routing. It implements mesh path and mesh portal/proxy path tables, known-gate lists, pending-frame queues, path add/delete/flush/expire operations, gate fallback for unresolved traffic, link-break handling, fixed next-hop paths, and the mesh fast-xmit cache.

## Important APIs, Types, and Functions
`mesh_table_init()` and `mesh_table_free()` initialize and destroy `struct mesh_table` rhashtables and RCU walk/gate lists. `mesh_path_new()` allocates a `struct mesh_path` with its skb queue, timer, state lock, broadcast RANN sender, and initial expiration. Public lookup helpers (`mesh_path_lookup()`, `mpp_path_lookup()`, `mesh_path_lookup_by_idx()`, `mpp_path_lookup_by_idx()`) use rhashtable or walk-list lookup and lazily clear `MESH_PATH_ACTIVE` if a path has expired.

`mesh_path_add()` inserts unicast non-local destinations into the mesh path table with `MESH_MAX_MPATHS` accounting, while `mpp_path_add()` inserts proxy/portal paths and flushes fast-xmit cache entries for the destination. `mesh_path_del()`, `mesh_path_flush_by_nexthop()`, `mesh_path_flush_by_iface()`, and `mesh_path_expire()` remove paths and free them through `mesh_path_free_rcu()`. `mesh_path_assign_nexthop()` sets the next-hop STA under RCU and rewrites queued frame headers. `mesh_path_fix_nexthop()` creates a fixed active route and drains pending frames.

Gate handling is provided by `mesh_path_add_gate()`, `mesh_gate_del()`, `mesh_gate_num()`, `mesh_path_send_to_gates()`, `mesh_path_move_to_queue()`, and `prepare_for_gate()`. These functions record active mesh gates, add address extension fields when sending unresolved traffic through a gate, and move/copy queued frames to gate paths. `mesh_plink_broken()` deactivates all active non-fixed paths using a failed peer as next hop and emits PERRs.

Fast-xmit support uses `mesh_fast_tx_init()`, `mesh_fast_tx_get()`, `mesh_fast_tx_cache()`, `mesh_fast_tx_gc()`, `mesh_fast_tx_flush_mpath()`, `mesh_fast_tx_flush_sta()`, and `mesh_fast_tx_flush_addr()`. Entries cache full 802.11, mesh, RFC1042, key, and offset metadata keyed by destination/type and are RCU-freed.

## Control Flow, State, and Persistence
Path tables are per mesh interface: `mesh_paths` for normal mesh destinations and `mpp_paths` for portal/proxy destinations. Each table has an rhashtable for keyed lookup plus a walk list for indexed dumps and bulk flushes. Paths persist until explicit deletion, interface teardown, next-hop flush, or expiration after inactive unresolved/non-fixed state exceeds `MESH_PATH_EXPIRE`. `mesh_path_free_rcu()` marks paths resolving/deleted, removes gate state, shuts down the discovery timer, decrements counters, flushes queued traffic and PREQs, and frees via RCU.

Pending data frames are stored in `mpath->frame_queue` while HWMP resolves the route. When a route becomes active, `mesh_path_tx_pending()` hands those skbs back to local pending TX. If route discovery fails and gates exist, `mesh_path_send_to_gates()` rewrites mesh headers and sends via active gates; otherwise `mesh_path_flush_pending()` discards frames and removes queued PREQ nodes for the destination. Fast-xmit entries persist independently but are invalidated on path, mpp, address, or STA changes.

## Dependencies and Integration
The file depends on Linux rhashtable, RCU, hlist/list primitives, skb queues, spinlocks, timers, random/slab helpers, `sta_info`, mesh power-save frame flag stamping, HWMP timer callbacks, and mac80211 pending TX APIs. HWMP calls into this file for path lookup/update, pending queue drain, gate fallback, and link-break propagation. TX/RX fast paths use the fast-tx cache, while cfg80211 path dump/delete operations depend on lookup-by-index and generation counters.

## Risks
The biggest risks are lifetime races between rhashtable removal, RCU readers, timers, queued PREQs, and next-hop STA destruction. `mesh_path_add()` increments `mpaths` before allocation/insert but only decrements during RCU free, so error and duplicate paths must be audited carefully. Gate redirection rewrites skb headers and adds mesh address extensions, making headroom and existing AE handling important. Fast-xmit cache validity depends on complete flushing after path, MPP, key, or next-hop changes; missed invalidations can send stale headers. The implementation uses lock nesting across table walk locks, path state locks, gate locks, cache locks, and skb queue locks, so lock ordering regressions are high risk.

## Test Signals
Tests should exercise duplicate add behavior, local/multicast rejection, path expiration, deletion while frames and PREQs are queued, fixed nexthop activation, next-hop flush on plink teardown, mpp proxy flush, gate add/delete counts, gate fallback with one and multiple gates, pending-frame drain/discard accounting, and fast-tx cache insert/replace/gc/flush paths. Concurrency tests with hwsim route churn and peer removal are especially valuable.
