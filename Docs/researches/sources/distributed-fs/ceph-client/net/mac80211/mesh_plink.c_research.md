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
