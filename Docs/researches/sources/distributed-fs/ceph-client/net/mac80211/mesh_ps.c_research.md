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
