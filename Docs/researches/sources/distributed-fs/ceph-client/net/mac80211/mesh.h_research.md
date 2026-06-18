# sources/distributed-fs/ceph-client/net/mac80211/mesh.h

## Purpose
`mesh.h` is the internal mac80211 mesh contract for the files that implement IEEE 802.11s mesh routing, peer links, mesh power save, synchronization, and fast transmit caching. It defines the shared state carried in mesh path objects, recent multicast cache entries, fast-xmit cache entries, and the cross-file APIs used by `mesh.c`, TX/RX paths, cfg80211 operations, and per-feature modules such as HWMP, path tables, plinks, power-save, and TSF sync.

## Important APIs, Types, and Functions
The central type is `struct mesh_path`, keyed by `dst` and optionally `mpp`, with RCU linkage (`rhash`, `walk_list`, `gate_list`), next-hop `sta_info`, a discovery timer, queued frames, HWMP sequence/metric/hop/lifetime fields, route flags, root/gate markers, RANN state, and `path_change_count`/`fast_tx_check`. `enum mesh_path_flags` encodes whether a path is active, resolving, sequence-valid, fixed, resolved, queued for PREQ, or deleted. `struct ieee80211_mesh_fast_tx_key` and `struct ieee80211_mesh_fast_tx` describe the cached fast-xmit mesh header state for local, proxied, and forwarded data. `struct rmc_entry` and `struct mesh_rmc` provide recent multicast cache declarations.

The header declares the mesh path API: `mesh_nexthop_lookup()`, `mesh_nexthop_resolve()`, `mesh_path_start_discovery()`, lookup/add/delete helpers, gate helpers, path expiration, pending-frame helpers, HWMP receive/error/root transmit entry points, and fast-xmit cache lookup/cache/flush/gc helpers. Peer-link declarations include `mesh_neighbour_update()`, `mesh_peer_accepts_plinks()`, plink state transitions (`mesh_plink_open()`, `mesh_plink_deactivate()`, `mesh_plink_block()`), the timer, RX handler, and STA cleanup. Power-save declarations expose local/peer PM updates, frame flag stamping, receive-side power-mode tracking, MPSP trigger processing, and beacon-driven frame release. Synchronization is represented by `ieee80211_mesh_sync_ops_get()` and `mesh_sync_adjust_tsf()`.

Inline helpers update established-peer counts and beacon state (`mesh_plink_inc_estab_count()`, `mesh_plink_dec_estab_count()`), compute remaining plink capacity, test HWMP path-selection mode, and activate a path by setting `MESH_PATH_ACTIVE | MESH_PATH_RESOLVED`.

## Control Flow, State, and Persistence
This header does not execute behavior itself, but it fixes the state transitions used by the implementation files. Mesh paths live in per-interface tables and are RCU-protected, while mutable path state is protected by `state_lock`. Unresolved traffic is persisted transiently in `frame_queue` until HWMP resolves the path, sends it via a gate, or discards it. Fast-xmit entries mirror active paths and must be invalidated whenever path, MPP, next-hop, or address state changes. Deferred work flags in `enum mesh_deferred_task_flags` allow timers, beacon updates, root announcements, PREQ processing, and TSF drift correction to be shifted to the mesh work item.

## Dependencies and Integration
The header depends on `linux/types.h`, `linux/jhash.h`, `ieee80211_i.h`, rhashtable-compatible layout, `sta_info`, `ieee80211_sub_if_data`, skb queues, timers, RCU, cfg80211/nl80211 mesh constants, and mac80211 TX/RX internals. It is consumed by `mesh.c`, `mesh_hwmp.c`, `mesh_pathtbl.c`, `mesh_plink.c`, `mesh_ps.c`, `mesh_sync.c`, and generic TX/RX/status/cfg paths. `CONFIG_MAC80211_MESH` gates selected exported helpers and turns mesh path selection into no-ops when mesh support is disabled.

## Risks
The main risks are concurrency and lifetime mistakes around RCU path/STA references, lock ordering across `state_lock`, per-table walk/gate locks, and skb queue locks, plus stale fast-xmit cache entries after path changes. The fixed limits (`MESH_MAX_PLINKS`, `MESH_MAX_MPATHS`, `MESH_FRAME_QUEUE_LEN`, fast-tx cache thresholds, and RMC sizing) are important denial-of-service and memory-pressure boundaries. Callers must respect comments that identify RCU read-side requirements and state-lock requirements; otherwise path deletion, next-hop replacement, or pending-frame flushing can race with TX/RX.

## Test Signals
Useful signals are mesh KUnit or hwsim cases that create and expire paths, force PREQ retries, flush paths by next-hop/interface, toggle fixed paths, verify gate fallback, exercise MPP/proxy lookups, and confirm fast-xmit cache invalidation. Plink tests should verify established-count updates and BSS_CHANGED flags. Power-save tests should assert FC/QoS PM bit stamping for unicast, multicast, peer, and non-peer modes.
