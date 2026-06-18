<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_hwmp.c -->
# sources/distributed-fs/ceph-client/net/mac80211/mesh_hwmp.c

## Purpose
`mesh_hwmp.c` implements Hybrid Wireless Mesh Protocol path selection for mac80211 mesh interfaces. It builds and receives PREQ, PREP, PERR, and RANN action frames; updates mesh path routing information from those frames; computes airtime metrics; queues and retries path discovery; resolves next hops for outbound mesh data; handles path-error propagation; and emits proactive root/gate advertisements.

## Important APIs, Types, and Functions
`mesh_path_sel_frame_tx()` serializes HWMP management IEs for PREQ, PREP, and RANN into mesh action frames and transmits them. `mesh_path_error_tx()` builds a deferred PERR frame and queues it through `ieee80211_add_pending_skb()` to avoid driver-lock deadlocks in the TX path. `ieee80211s_update_metric()` updates EWMA delivery failure and rate state on TX status and calls `mesh_plink_broken()` when link failure exceeds `LINK_FAIL_THRESH`. `airtime_link_metric_get()` computes the HWMP airtime metric from expected throughput or fallback EWMA rate/failure data, returning `MAX_METRIC` for non-established links or unusable rates.

Receive-side processing starts at `mesh_rx_path_sel_frame()`, which validates that the sender is an established mesh peer, parses action-frame elements, enforces supported IE lengths, and dispatches to `hwmp_preq_frame_process()`, `hwmp_prep_frame_process()`, `hwmp_perr_frame_process()`, or `hwmp_rann_frame_process()`. `hwmp_route_info_get()` is the key route-update routine: it learns or updates routes to the HWMP originator and transmitter, compares sequence numbers and metrics, assigns next hops, activates paths, refreshes expiration, resets failure EWMA, flushes stale fast-tx state when next hop changes, and transmits queued frames.

Path discovery uses `mesh_queue_preq()` to rate-limit and deduplicate per-destination PREQs in `ifmsh->preq_queue`; `mesh_path_start_discovery()` pops that queue, updates local sequence and PREQ IDs, sends a PREQ, and arms the per-path discovery timer. `mesh_nexthop_resolve()` handles outbound frames by trying `mesh_nexthop_lookup()`, creating a path and queuing PREQ discovery when needed, and buffering up to `MESH_FRAME_QUEUE_LEN` frames. `mesh_path_timer()` retries unresolved paths with exponential timeout until `dot11MeshHWMPmaxPREQretries`, then tries mesh gates or flushes pending frames. `mesh_path_tx_root_frame()` emits proactive RANN or PREQ root announcements based on `dot11MeshHWMPRootMode`.

## Control Flow, State, and Persistence
The normal outbound path is: TX path calls `mesh_nexthop_resolve()`, `mesh_nexthop_lookup()` finds an active `mesh_path` and stamps RA/TA plus MPS flags, or a new unresolved path is created and traffic is queued. HWMP discovery is scheduled through the interface work item or `mesh_path_timer`. PREQ/PREP reception updates the reverse route to the originator/transmitter and may generate a PREP, forward a PREQ/PREP, or activate the target route and drain queued frames. PERR reception deactivates affected paths if the error came from the current next hop and forwards the error when mesh forwarding is enabled. RANN reception records root/gate candidates, schedules root refresh PREQs, and forwards RANNs while TTL permits.

Persistent state is per-interface and per-path: local sequence number `ifmsh->sn`, `preq_id`, `last_preq`, `last_sn_update`, `next_perr`, PREQ queue length, mesh stats, path flags, destination sequence numbers, metrics, hop counts, lifetimes, RANN sender/metric, root/gate status, discovery retry/timeout, and queued skbs. All path mutations are synchronized with RCU and `mpath->state_lock`; the PREQ queue uses `mesh_preq_queue_lock`.

## Dependencies and Integration
This file depends on path-table helpers from `mesh_pathtbl.c`, peer-link state from `sta_info`, power-save flag stamping from `mesh_ps.c`, work/timer setup in `mesh.c`, TX status callbacks, `wme.h`, rhashtable-backed path lookup, unaligned little-endian accessors, cfg80211 bitrate helpers, and driver TX APIs. RX integration is through mesh action frame handling in `mesh.c`; TX integration is through `tx.c` next-hop resolution and fast-xmit cache population.

## Risks
Sequence-number comparisons and metric freshness rules are subtle, especially around wraparound, reboot-like jumps (`MAX_SANE_SN_DELTA`), fixed paths, and equal-sequence metric changes. The implementation intentionally supports only one destination and no address-extension variants for some HWMP IEs, so interoperability with more complex HWMP frames is limited. Concurrency risks include path deletion while discovery timers or queued PREQs are active, next-hop STA lifetime under RCU, stale fast-tx entries after route changes, and rate-limited PERR loss under rapid link failures. Queue limits prevent unbounded memory growth but can drop older unresolved traffic.

## Test Signals
High-value tests should cover PREQ/PREP route learning, duplicate or stale sequence rejection, better-metric route replacement, target replies, proactive root modes, RANN gate recording, PERR invalidation and propagation, TTL drops, discovery retry/backoff, gate fallback after discovery failure, nolearn direct-neighbor routing, and fast-xmit cache flushing after next-hop changes. TX-status tests should verify EWMA failure threshold behavior and airtime metric fallback for missing expected throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_hwmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_pathtbl.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_pathtbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_plink.c -->
# sources/distributed-fs/ceph-client/net/mac80211/mesh_plink.c

## Purpose
`mesh_plink.c` implements mesh peer-link management for kernel-managed MPM. It discovers or updates mesh neighbors from beacons/probe responses, allocates `sta_info` entries, sends mesh peering OPEN/CONFIRM/CLOSE action frames, runs the peer-link finite state machine, handles retry/confirm/holding timers, updates peer capabilities and protection modes, and flushes paths when an established link is lost.

## Important APIs, Types, and Functions
`mesh_neighbour_update()` is called from beacon/probe processing to get or allocate a mesh STA, refresh capabilities, record gate connectivity, optionally auto-open peer links, and release power-save-buffered frames. `mesh_rx_plink_frame()` parses self-protected peering action frames and delegates to `mesh_process_plink_frame()`. `mesh_plink_get_event()` maps frame type, local mesh compatibility, peer IDs, free capacity, and current STA state to FSM events. `mesh_plink_fsm()` performs state transitions across LISTEN, OPN_SNT, OPN_RCVD, CNF_RCVD, ESTAB, HOLDING, and BLOCKED and schedules any response action frame.

`mesh_plink_frame_tx()` builds OPEN/CONFIRM/CLOSE action frames with supported rates, RSN, mesh ID/configuration, HT/VHT/HE/EHT capabilities and operations, vendor IEs, AID, peering protocol, LLID/PLID, and close reason. `mesh_plink_open()`, `mesh_plink_deactivate()`, and `mesh_plink_block()` expose local control operations. `mesh_plink_timer()` handles retry, confirm, and holding timeouts. `mesh_sta_info_init()` imports rates and HT/VHT/HE/EHT capability data into `sta_info` and updates rate control. `mesh_set_short_slot_time()` and `mesh_set_ht_prot_mode()` recompute BSS protection parameters from all established peers.

## Control Flow, State, and Persistence
Neighbor state lives in `sta->mesh`: plink state, LLID/PLID, reason, retries, timers, peer AID, processed-beacon flag, power-save modes, and capability-derived fields in `sta->deflink`. New peers are either reported to userspace when `user_mpm` or authenticated mesh security is active, or allocated in-kernel with an AID, WME enabled, and AUTH/ASSOC/AUTHORIZED pre-states. Automatic peering starts from `mesh_neighbour_update()` when the peer accepts plinks, local plinks are available, auto-open is configured, and RSSI threshold passes.

The FSM sends OPEN and CONFIRM exchanges, establishes the link on valid confirm/open sequences, updates established peer counts and BSS_CHANGED flags, sets mesh power-save state, and flushes mesh paths by next hop when a peer closes or is deactivated. Timers retry OPEN with randomized backoff, close on confirm timeout or max retries, then return to LISTEN after holding timeout. User-managed MPM bypasses kernel RX handling and STA allocation for peering frames.

## Dependencies and Integration
This file depends on `ieee80211_i.h`, rate control, mesh IE builders from `mesh.c`, path flushing from `mesh_pathtbl.c`, mesh power-save helpers from `mesh_ps.c`, cfg80211 peer-candidate notifications, local STA lists, hwsim/driver RX status for signal, and BSS change notification through `ieee80211_mbss_info_change_notify()`. It is invoked from mesh beacon/probe receive and mesh action receive paths, and it drives route validity because only established plinks are accepted by HWMP.

## Risks
Peer-link correctness is sensitive to ID matching, races between timers and state transitions, and the nonstandard handling that accepts CLOSE on established links without strict LLID/PLID checks to avoid livelock. Capability updates are intentionally frozen once an established peer has processed a beacon, so dynamic capability changes may not take effect until re-peering. STA allocation and insertion drop/reacquire RCU, which makes cleanup on insertion failure important. BSS protection mode recomputation scans all peers and must stay synchronized with plink state changes. Security/user-MPM modes change who owns STA allocation and peering policy, so mixed handling can be fragile.

## Test Signals
Useful tests include full OPEN/CONFIRM establishment in both initiator and responder roles, rejection for mesh ID/config mismatch, capacity exhaustion, RSSI threshold rejection, CLOSE handling from every state, retry and confirm timeout behavior, holding-to-listen reset, blocked peers, user-MPM bypass, AID allocation exhaustion, path flush after ESTAB teardown, BSS_CHANGED flag changes, HT protection recalculation, and short-slot changes as peers join/leave.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_plink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_ps.c -->
# sources/distributed-fs/ceph-client/net/mac80211/mesh_ps.c

## Purpose
`mesh_ps.c` implements IEEE 802.11s mesh power-save state tracking and mesh peer service period behavior. It stamps outgoing frames with local peer or non-peer power mode, learns peer power mode from received frames, controls per-STA PS buffering, sends QoS Null frames to announce mode changes or trigger service periods, and releases buffered frames when peers indicate availability.

## Important APIs, Types, and Functions
`ieee80211_mps_local_status_update()` derives the interface non-peer power mode from current peering state and established peers' local PM settings, updates `nonpeer_pm`, light/deep-sleep peer counters, and returns `BSS_CHANGED_BEACON` when beacon state changes. `ieee80211_mps_set_sta_local_pm()` updates the local peer-specific mode for a STA, announces changes using `mps_qos_null_tx()` when the link is established, and recomputes non-peer state. `ieee80211_mps_set_frame_flags()` writes PM and mesh PS level bits into 802.11 frame control and QoS control fields for management, multicast, and peer-specific QoS data.

Receive-side state is handled by `ieee80211_mps_rx_h_sta_process()`, which calls `mps_set_sta_peer_pm()` for individually addressed QoS data/null frames and `mps_set_sta_nonpeer_pm()` otherwise. `ieee80211_mps_sta_status_update()` chooses whether to buffer traffic for a STA based on peer or non-peer PM and toggles `WLAN_STA_PS_STA`. MPSP behavior is implemented by `mpsp_trigger_send()`, `mpsp_qos_null_append()`, `mps_frame_deliver()`, and `ieee80211_mpsp_trigger_process()`. `ieee80211_mps_frame_release()` responds to TIM/awake-window information from beacons or probe responses by triggering a service period or sending one frame to non-peers.

## Control Flow, State, and Persistence
Local state is stored per interface in `ifmsh->nonpeer_pm`, `ps_peers_light_sleep`, `ps_peers_deep_sleep`, and `ifmsh->ps`; per-peer state is stored in `sta->mesh->local_pm`, `peer_pm`, `nonpeer_pm`, MPSP owner/recipient flags, and normal mac80211 PS queues (`ps_tx_buf`, `tx_filtered`). During plink setup the non-peer PM is forced active. Once links are established, any light/deep local peer mode makes non-peer mode deep sleep; otherwise it follows the configured mesh power mode.

Outgoing frames get PM bits according to peer-specific mode for established unicast QoS traffic, or interface non-peer mode for multicast/management/non-peer frames. Incoming QoS data updates the peer's advertised mode from FC.PM and QoS mesh PS level bits, then may start/end an MPSP. When a service period is active, buffered frames are moved from PS queues to a local pending queue, MoreData and EOSP are set on the appropriate frames, and a QoS Null is appended if the last released frame cannot carry EOSP.

## Dependencies and Integration
The file depends on mesh address construction from `mesh.c`, WME/QoS helpers, `sta_info` PS buffering, TX status callbacks (`status.c` calls `ieee80211_mpsp_trigger_process()` for transmitted QoS frames), RX handlers (`rx.c` calls `ieee80211_mps_rx_h_sta_process()`), cfg80211 power-mode changes, plink state transitions, and mac80211 pending TX/TIM recalculation. It is tightly coupled to header bit definitions for FC PM, QoS EOSP, RSPI, and mesh PS level.

## Risks
Incorrect PM/QoS bit handling can deadlock buffered traffic, leave peers asleep, or prematurely end service periods. MPSP state spans RX, TX status, and buffered queue release, so lost TX status or unacked trigger frames can leave owner/recipient flags inconsistent. The code intentionally ignores awake-window duration and uses QoS Null triggers, which may under-model timing-sensitive peers. Queue accounting must keep `local->total_ps_buffered`, TIM recalculation, `WLAN_STA_PS_STA`, and `num_sta_ps` consistent. Frame flag stamping requires a non-NULL STA for unicast QoS data, and the WARN path signals misuse by callers.

## Test Signals
Tests should cover local power-mode transitions during peering and established links, beacon-change return values, outgoing FC/QoS bits for active/light/deep modes, peer-mode learning from received QoS frames, non-peer mode learning from management/multicast frames, PS buffering enable/disable, MPSP owner/recipient flag transitions for RSPI/EOSP on RX and TX status, delivery of all or one buffered frame, QoS Null append behavior, TIM/awake-window gating, and wakeup delivery when a peer returns active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_sync.c -->
# sources/distributed-fs/ceph-client/net/mac80211/mesh_sync.c

## Purpose
`mesh_sync.c` implements the mesh synchronization method registry and the neighbor-offset synchronization method for mac80211 mesh interfaces. Its job is to measure TSF offset and clock drift from neighbor beacons, choose a stable offset setpoint, schedule deferred TSF adjustment work, and apply TSF corrections through driver operations.

## Important APIs, Types, and Functions
`struct sync_method` maps an IEEE 802.11 mesh sync method ID to `struct ieee80211_mesh_sync_ops`. The only registered method here is `IEEE80211_SYNC_METHOD_NEIGHBOR_OFFSET`, with `mesh_sync_offset_rx_bcn_presp()` as the beacon/probe-response receive hook and `mesh_sync_offset_adjust_tsf()` as the beacon-adjust hook. `ieee80211_mesh_sync_ops_get()` returns the ops for a configured method or `NULL`.

`mesh_sync_offset_rx_bcn_presp()` ignores non-beacon frames, obtains the receive timestamp either from hardware RX timestamp calculation or current TSF, looks up the transmitting STA, skips peers currently advertising TBTT adjustment, computes `sta->mesh->t_offset`, initializes or validates `t_offset_setpoint`, and updates `ifmsh->sync_offset_clockdrift_max` when drift is within the allowed jump threshold. `mesh_sync_offset_adjust_tsf()` compares the maximum drift against `TOFFSET_MINIMUM_ADJUSTMENT` and sets `MESH_WORK_DRIFT_ADJUST` for deferred correction. `mesh_sync_adjust_tsf()` consumes `sync_offset_clockdrift_max`, applies a bounded negative TSF delta, and uses `drv_offset_tsf()` when available or falls back to get/set TSF.

## Control Flow, State, and Persistence
The receive path records per-STA timing state: `t_offset`, `t_offset_setpoint`, and `WLAN_STA_TOFFSET_KNOWN`. The interface aggregates the largest observed positive clock drift in `ifmsh->sync_offset_clockdrift_max`, protected by `sync_offset_lock`. Beacon generation or mesh housekeeping calls the sync adjust op; if enough drift exists, a deferred work flag is set because driver TSF setters may block. The actual adjustment later subtracts either the whole maximum drift, if below a small beacon-interval fraction, or a fractional beacon interval to avoid overcorrection.

## Dependencies and Integration
This file depends on `ieee80211_i.h`, `mesh.h`, driver TSF operations in `driver-ops.h`, RX timestamp helpers, mesh config IE capability bits, STA mesh timing fields, mesh work scheduling via `wrkq_flags`, and method selection during mesh startup in `mesh.c`. It integrates with beacon/probe response processing and with the mesh work item that handles `MESH_WORK_DRIFT_ADJUST`.

## Risks
Synchronization is sensitive to timestamp quality. Without hardware RX timestamps, current TSF is only an approximation. Large offset jumps clear the known setpoint to handle peer restart/reset, but repeated noisy timestamps may prevent convergence. Only beacons are used despite the generic hook name, and TODO comments note missing support for non-peer non-MBSS neighbors. Driver TSF operations may have latency, so the margin and fractional adjustment constants are heuristic and can under- or over-correct on unusual hardware.

## Test Signals
Tests should validate method lookup, ignoring non-beacons, skipping peers with TBTT-adjusting capability, setpoint initialization, drift accumulation under `sync_offset_lock`, large-jump invalidation, minimum-adjustment filtering, deferred work flag setting, and both `offset_tsf` and get/set TSF adjustment paths. Hwsim-style tests can simulate two mesh peers with controlled timestamp drift and verify convergence without repeated large corrections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh_sync.c -->
