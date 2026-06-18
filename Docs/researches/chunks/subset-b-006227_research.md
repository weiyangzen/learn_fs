# sources/distributed-fs/ceph-client/net/mac80211/mlme.c lines 1-8936

## Scope

This chunk covers the first 8,936 lines of `net/mac80211/mlme.c`, the managed station MLME implementation for mac80211. It starts at the file header and includes connection capability selection, association request construction, channel switch handling, power-save control, WMM/QoS handling, authentication and association response processing, beacon/probe response processing, MLO link reconfiguration/removal, advertised and negotiated TTLM handling, queued management-frame dispatch, retry timers, connection probing, and the beginning of the PM quiesce function. Later public cfg80211 auth/assoc/disassoc entry points and the rest of PM/EPCS/ML-reconfiguration helpers are outside this chunk.

## Purpose

This code is the station-side control plane for joining and maintaining infrastructure BSS connections. It translates cfg80211 scan/auth/assoc state, AP beacon/probe/association elements, local hardware capabilities, regulatory constraints, and driver callback results into mac80211 station state, channel contexts, per-link BSS configuration, power-save behavior, and cfg80211/user-visible MLME events.

The chunk is especially responsible for:

- Determining the usable connection mode and bandwidth from legacy, HT, VHT, HE, EHT, UHR, S1G, and 6 GHz operation elements.
- Building association and reassociation requests, including per-link MLO STA profiles, capability IEs, WMM/U-APSD, FILS encryption, EHT/UHR, and regulatory connectivity elements.
- Applying association success state to one or more links and station records.
- Maintaining an associated station by processing beacons, probe responses, CSA/ECSA, power constraints, WMM changes, TWT support, MLO reconfiguration, and TTLM changes.
- Detecting loss of connectivity with beacon timers, connection-idle timers, AP probes, nullfunc ACK feedback, and driver loss notifications.
- Cleaning up auth, assoc, and associated state on failures, deauth, disassoc, CSA failure, or link invalidation.

## Important Constants and Module Parameters

- `IEEE80211_AUTH_TIMEOUT*`, `IEEE80211_ASSOC_TIMEOUT*`, `IEEE80211_AUTH_MAX_TRIES`, and `IEEE80211_ASSOC_MAX_TRIES` define retry windows and retry limits for authentication and association state machines.
- `IEEE80211_CONNECTION_IDLE_TIME` defines how long an associated station can be idle before the stack probes the AP.
- `IEEE80211_ADV_TTLM_SAFETY_BUFFER_MS` and `IEEE80211_ADV_TTLM_ST_UNDERFLOW` control advertised TTLM switch scheduling.
- `IEEE80211_NEG_TTLM_REQ_TIMEOUT` bounds negotiated TTLM request/response waiting.
- Module parameters:
  - `max_nullfunc_tries`: nullfunc retries before disconnecting when TX ACK status is available.
  - `max_probe_tries`: probe-request retries before disconnecting otherwise.
  - `beacon_loss_count`: beacon intervals before beacon loss is declared.
  - `probe_wait_ms`: wait time after each AP probe.

## Key Types and State Containers

- `struct ieee80211_sub_if_data`: interface-level state. This chunk heavily uses `sdata->u.mgd`, `sdata->vif.cfg`, `sdata->vif.bss_conf`, `sdata->link[]`, and `sdata->deflink`.
- `struct ieee80211_if_managed`: managed-station state, including `auth_data`, `assoc_data`, association flag, monitor timers, power-save flags, TSPEC state, RSSI thresholds, probe counters, MLO reconf/TTLM/EPCS state, and cached association request IEs.
- `struct ieee80211_link_data`: per-link state for MLO and the default non-MLO link. The code updates `link->conf`, `link->u.mgd.conn`, `link->u.mgd.bssid`, CSA state, beacon CRC/signals, WMM tracking, DTIM, power limits, and channel reservation/use.
- `struct ieee80211_mgd_auth_data`: in-progress authentication state, including AP address, BSS reference, algorithm, transaction, retry/timeout state, and algorithm-specific data.
- `struct ieee80211_mgd_assoc_data`: in-progress association state, including per-link BSSes, addresses, IEs, selected link, mode/bandwidth, FILS keys, WMM/U-APSD flags, previous AP, and retry/timeout fields.
- `struct sta_info` and `struct link_sta_info`: AP peer state and per-link peer capabilities. Association success moves them through `IEEE80211_STA_AUTH`, `IEEE80211_STA_ASSOC`, and sometimes `IEEE80211_STA_AUTHORIZED`.
- `struct ieee80211_chan_req` and `struct cfg80211_chan_def`: selected operating channel and AP-wide wider-bandwidth/OFDMA channel description.
- `struct ieee80211_conn_settings`: local/AP negotiated connection mode and bandwidth limit.
- `struct ieee802_11_elems`: parsed management-frame elements used throughout channel selection, association response validation, beacon tracking, CSA, WMM, TTLM, and MLO parsing.

## Important APIs and Functions

### Timer and Monitor Helpers

- `run_again()` updates the shared managed timer only if the new timeout is earlier or the timer is not pending. This multiplexes auth, assoc, and AP-probe retry timing.
- `ieee80211_sta_reset_beacon_monitor()` arms `bcn_mon_timer` unless beacon filtering or driver connection monitoring is active.
- `ieee80211_sta_reset_conn_monitor()` arms `conn_mon_timer`, resets probe counters, and skips when not associated or hardware monitors the connection.
- `ieee80211_sta_bcn_mon_timer()`, `ieee80211_sta_conn_mon_timer()`, `ieee80211_sta_monitor_work()`, and `ieee80211_sta_work()` form the connection-health state machine.

### Channel and Mode Determination

- `ieee80211_determine_ap_chan()` derives the AP's effective mode and chandef from operation elements. It handles S1G, 6 GHz HE/EHT, HT/VHT compatibility, EHT puncturing, and UHR NPCA validation. It downgrades mode on bad or missing operation information rather than blindly using advertised capabilities.
- `ieee80211_determine_chan_mode()` parses BSS IEs repeatedly until the requested `conn->mode` matches what can actually be used, checks required basic rates and BSS membership selectors, applies regulatory and hardware restrictions, validates mandatory MCS/NSS support, and returns parsed elements with `chanreq` and `ap_chandef` populated.
- `ieee80211_config_bw()` re-evaluates AP bandwidth/mode from association responses, ML reconfiguration responses, beacons, or action frames. It updates HT operation mode, 6 GHz TPE data, and channel context state or rejects incompatible AP changes.
- `ieee80211_prep_channel()` wraps channel determination, 6 GHz power/TPE setup, max RX-chain estimation, and `ieee80211_link_use_channel()` with fallback bandwidth downgrades.

### Capability and Rate Validation

- `ieee80211_verify_sta_ht_mcs_support()`, `ieee80211_verify_sta_vht_mcs_support()`, `ieee80211_verify_peer_he_mcs_support()`, `ieee80211_verify_sta_he_mcs_support()`, and `ieee80211_verify_sta_eht_mcs_support()` validate AP requirements against local and peer capabilities. Several checks are relaxed outside `STRICT` mode for interoperability with known broken APs.
- `ieee80211_get_rates()` converts supported-rate elements into supported/basic rate bitmaps, records unknown membership selectors, tracks whether rates exceed 11 Mbit, and finds the minimum rate fallback.
- `ieee80211_mgd_setup_link_sta()` initializes per-link AP station rate masks, basic rates, and 11g operating mode from scan BSS rate data.
- `ieee80211_max_rx_chains()` estimates required RX chains from HT, VHT, and HE capability IEs.

### TPE and Channel Width Helpers

- `ieee80211_chandef_usable()` wraps cfg80211 usability and adds local puncturing restrictions.
- `ieee80211_chandef_num_subchans()`, `ieee80211_chandef_num_widths()`, `ieee80211_calc_chandef_subchan_offset()`, `ieee80211_rearrange_tpe_psd()`, and `ieee80211_rearrange_tpe()` are KUnit-visible helpers for mapping transmit power envelope data from AP channel layout to the downgraded or actually used channel layout.
- `ieee80211_set_chanreq_ap()` records AP-wide EHT wider-bandwidth information in `chanreq->ap` unless disabled by driver flags.

### Association Request Construction

- `ieee80211_add_ht_ie()`, `ieee80211_add_vht_ie()`, `ieee80211_put_he_cap()`, `ieee80211_put_eht_cap()`, and `ieee80211_put_uhr_cap()` emit local capabilities while respecting AP capability, bandwidth limits, SMPS, and MU-MIMO ownership.
- `ieee80211_add_before_ht_elems()`, `ieee80211_add_before_vht_elems()`, `ieee80211_add_before_he_elems()`, and `ieee80211_add_before_reg_conn()` preserve ordering of user-provided IEs around generated capability IEs.
- `ieee80211_add_link_elems()` builds the per-link body of an association request. It adds rates, power capability, supported channels, HT/VHT/HE/EHT/UHR/S1G elements, 6 GHz regulatory connectivity, vendor elements, and records which elements are present for MLO non-inheritance.
- `ieee80211_assoc_add_ml_elem()` emits the EHT Multi-Link element for MLD station association, including common MLD data and per-STA profiles for non-association links.
- `ieee80211_add_non_inheritance_elem()` records elements inherited by the outer association request but absent from per-STA MLO profiles.
- `ieee80211_send_assoc()` allocates the association or reassociation frame, builds SSID and link elements, adds WMM and FILS encryption if needed, caches request IEs in `ifmgd->assoc_req_ies`, prepares driver TX, sets encryption/status flags, and transmits.

### Management Frame Transmission

- `ieee80211_send_pspoll()`, `ieee80211_send_nullfunc()`, and `ieee80211_send_4addr_nullfunc()` send control/data null frames used for power-save signaling, AP probing, and 4-address mode notification.
- `ieee80211_mlme_send_probe_req()` and `ieee80211_mgd_probe_ap_send()` send AP liveness probes, choosing nullfunc when ACK status is reliable and probe requests otherwise.
- `ieee80211_send_neg_ttlm_req()`, `ieee80211_send_neg_ttlm_res()`, and `ieee80211_send_teardown_neg_ttlm()` send protected EHT TTLM action frames.

### Channel Switch Handling

- `ieee80211_sta_process_chanswitch()` is the core CSA/ECSA processor. It parses CSA elements, handles protected action, unprotected action, beacon, and cross-link sources differently, validates channel compatibility, tears down TDLS peers, reserves channel context, blocks queues for quiet mode, starts cfg80211 channel-switch notifications, invokes driver callbacks, or schedules software completion.
- `ieee80211_csa_switch_work()` completes a channel switch after driver or software scheduling, handles inactive links specially, applies TPE immediately after 6 GHz switch, and resets monitors when all links were switching.
- `ieee80211_chswitch_post_beacon()` finalizes CSA after the first post-switch beacon and calls driver post-switch hooks.
- `ieee80211_chswitch_done()` is exported for drivers to report CSA completion and queue the switch worker.
- `ieee80211_sta_abort_chanswitch()`, `ieee80211_sta_csa_rnr_iter()`, `ieee80211_sta_other_link_csa_disappeared()`, and `ieee80211_mgd_check_cross_link_csa()` support abort/completion detection from RNR and MLO per-STA profiles.

### Power, Power Save, and QoS

- `ieee80211_find_80211h_pwr_constr()`, `ieee80211_find_cisco_dtpc()`, and `ieee80211_handle_pwr_constr()` derive AP-requested TX power limits from Country/Power Constraint and Cisco DTPC IEs and trigger TX power recalculation.
- `ieee80211_enable_ps()`, `ieee80211_change_ps()`, `ieee80211_powersave_allowed()`, `ieee80211_recalc_ps()`, `ieee80211_recalc_ps_vif()`, `ieee80211_dynamic_ps_disable_work()`, `ieee80211_dynamic_ps_enable_work()`, and `ieee80211_dynamic_ps_timer()` manage stack- and driver-visible power-save transitions.
- `_ieee80211_sta_wmm_params()` parses WMM and MU-EDCA parameters, validates all ACs, applies regulatory limits, and stores per-link TX queue settings.
- `ieee80211_sta_wmm_params()` applies WMM parsing results through `drv_conf_tx()` and enables QoS.
- `__ieee80211_sta_handle_tspec_ac_params()`, `ieee80211_sta_handle_tspec_ac_params()`, and `ieee80211_sta_tx_wmm_ac_notify()` enforce admitted TX time by temporarily downgrading AC parameters when TSPEC time slices are consumed.
- `ieee80211_mgd_set_link_qos_params()` pushes per-link AC parameters to the driver.

### Association and Authentication RX

- `ieee80211_rx_mgmt_auth()` validates authentication frames against in-progress auth state, handles shared-key challenges, SAE retry/confirm behavior, IEEE 802.1X encapsulated-auth success, cfg80211 notifications, driver TX completion, and transition to `IEEE80211_STA_AUTH`.
- `ieee80211_rx_mgmt_assoc_resp()` validates assoc/reassoc response source and length, decrypts FILS responses, parses elements, handles comeback, validates MLO Basic Multi-Link element, commits AID, calls `ieee80211_assoc_success()`, reports status to drivers and cfg80211, and destroys assoc state.
- `ieee80211_assoc_success()` performs the multi-step commit: allocate MLO link STA state, parse TTLM in assoc response, set valid/dormant links, initialize DTIM/beacon data, prep non-association link channels, initialize rates/capabilities per link, activate links, initialize rate control, set MFP/control-port state, move station state, set 4addr mode, call `ieee80211_set_associated()`, optionally send 4addr nullfunc, and start monitors.
- `ieee80211_assoc_config_link()` parses link-specific association response data, fills peer HT/VHT/HE/EHT/UHR/S1G capabilities, updates TWT/EPCS/BSS-color/UORA/nontransmitted BSS/WMM/max-idle/assoc capability state, and applies AP bandwidth checks.

### Deauth, Disassoc, and Disconnect

- `ieee80211_set_disassoc()` is the central associated-state teardown path. It optionally transmits deauth/disassoc, disables power save, flushes queues, removes AP and TDLS STA state, resets BSS config, WMM, TSPEC, timers, channel contexts, CSA flags, power/TPE, TTLM, MLO reconf, link masks, EPCS state, and userspace membership selectors.
- `ieee80211_report_disconnect()` reports TX/RX MLME management events to cfg80211 and drivers.
- `__ieee80211_disconnect()` unlinks BSS records on connection loss, calls disassociation teardown, clears CSA flags, and reports disconnect.
- `ieee80211_beacon_loss()`, `ieee80211_connection_loss()`, and `ieee80211_disconnect()` are exported driver-facing APIs that schedule disconnect/probe work.
- `ieee80211_rx_mgmt_deauth()` and `ieee80211_rx_mgmt_disassoc()` process AP-originated and TDLS-originated disconnect frames.
- `ieee80211_destroy_auth_data()` and `ieee80211_destroy_assoc_data()` release in-progress connection state and BSS references, destroy temporary STA state, cancel timers, notify cfg80211 of failures, and reset link masks on unsuccessful auth/assoc.

### Beacon, Probe, and BSS Tracking

- `ieee80211_rx_bss_info()` updates cfg80211/mac80211 BSS cache from received management frames.
- `ieee80211_rx_mgmt_probe_resp()` accepts directed probe responses and 6 GHz broadcast probe responses, updates BSS info, and cancels AP probing when the current AP responds.
- `ieee80211_handle_beacon_sig()` tracks EWMA beacon signal and emits RSSI/CQM events after enough samples.
- `ieee80211_rx_mgmt_beacon()` is the main associated beacon processor. It validates BSSID/frequency, supports pre-association beacon wait, tracks signal and timers, handles TIM/PS-Poll/nullfunc behavior, P2P NoA, beacon timing, CRC-based beacon filtering, BSS cache, CSA, cross-link CSA, MLO BSS parameter change counts, WMM changes, first-beacon DTIM state, ERP capability changes, TWT recalculation, AP bandwidth changes, opmode notifications, power constraints, ML reconfiguration, advertised TTLM, and link change notifications.
- `ieee80211_rx_our_beacon()` handles transmitted BSSID matching for nontransmitted MBSSID profiles.
- `ieee80211_mgd_ssid_mismatch()` detects decrypted beacons from the associated BSSID that advertise a mismatching non-hidden SSID and forces disconnect.
- `ieee80211_rx_beacon_freq_valid()` accepts normal beacon frequency matches and the S1G 2 MHz primary sibling case.

### MLO Reconfiguration and TTLM

- `ieee80211_ml_reconfiguration()` parses ML reconfiguration elements in beacons, identifies links to remove, computes removal delays from beacon intervals, and schedules `ml_reconf_work`.
- `ieee80211_ml_reconf_work()` applies pending link removals, ensures at least one valid/non-dormant link remains, adjusts active/valid/dormant links, removes station link state, notifies cfg80211 and drivers, or disconnects on invalid results.
- `ieee80211_parse_adv_t2l()` validates AP-advertised TID-to-link mapping: direction must be both, all TIDs must be mapped to the same nonzero link set, and switch/duration fields are parsed.
- `ieee80211_process_adv_ttlm()` handles advertised TTLM in beacons. It cancels or reverts mappings when TTLM disappears, schedules future switches from partial TSF with a safety buffer, or disconnects on invalid maps.
- `ieee80211_ttlm_set_links()` applies active/dormant/suspended link masks, clears negotiated TTLM if superseded, notifies BSS changes, and disconnects if link state cannot be set.
- `ieee80211_apply_neg_ttlm()`, `ieee80211_req_neg_ttlm()`, `ieee80211_parse_neg_ttlm()`, `ieee80211_process_neg_ttlm_req()`, `ieee80211_process_neg_ttlm_res()`, and `ieee80211_process_ttlm_teardown()` implement negotiated TTLM request, response, acceptance, timeout, teardown, and driver validation behavior.

### Queued RX and Work State Machine

- `ieee80211_sta_rx_queued_ext()` dispatches S1G beacon extension frames.
- `ieee80211_sta_rx_queued_mgmt()` dispatches queued management frames by subtype, including beacon, probe response, auth, deauth, disassoc, assoc response, and CSA action frames.
- `ieee80211_mgd_conn_tx_status()` stores MLME connection frame TX status and queues station work.
- `ieee80211_sta_work()` handles TX status side effects, auth/assoc retry timeouts, association comeback timing, and AP probe retry/disconnect behavior.
- `ieee80211_restart_sta_timer()` restarts probing after station timer disruption.

## Control Flow

### Capability Selection Before Association

1. Local mode is initially determined by `ieee80211_determine_our_sta_mode()` based on band, WMM, crypto, request flags, and local HT/VHT/HE/EHT/UHR capabilities.
2. For each target BSS, `ieee80211_determine_chan_mode()` parses AP IEs and calls `ieee80211_determine_ap_chan()` to find the AP mode/chandef.
3. If AP mode is below the requested local mode, the parser reruns with the lower mode, because element parsing itself depends on the target mode.
4. The selected channel is downgraded as needed for regulatory restrictions, bandwidth limits, unsupported HE/EHT/UHR, mandatory MCS/NSS requirements, unknown BSS membership selectors, and driver puncturing restrictions.
5. `ieee80211_prep_channel()` applies the resulting channel request to the link, downgrading again if channel context sharing fails.

### Association Request Flow

1. `ieee80211_do_assoc()` increments retries and calls `ieee80211_send_assoc()`.
2. `ieee80211_send_assoc()` sizes and allocates the skb, fills the management header, SSID, link capabilities, optional MLO Multi-Link element, WMM info, custom IEs, vendor IEs, and FILS encryption.
3. The request IEs are cached in `ifmgd->assoc_req_ies` for cfg80211 response reporting.
4. The driver is given `drv_mgd_prepare_tx()` and the frame is transmitted with TX status requested when supported.
5. `ieee80211_sta_work()` updates association timeout after TX status; an ACK shortens the wait for a response, while a failed TX forces immediate retry.

### Authentication Flow

1. `ieee80211_auth()` sends the next auth transaction and arms a timeout.
2. `ieee80211_rx_mgmt_auth()` accepts only frames matching the in-progress AP and algorithm/transaction constraints.
3. Failed SAE anti-clog/H2E/SAE-PK statuses may hand control back to userspace and extend timeout.
4. Shared-key authentication sends a challenge response and waits for transaction 4.
5. Successful auth marks the AP STA authenticated and waits for association.
6. Timeout or retry exhaustion destroys auth state, unlinks likely stale BSS data, notifies cfg80211, and reports a driver event.

### Association Response Flow

1. `ieee80211_rx_mgmt_assoc_resp()` validates AP source, frame length, FILS protection, status, AID, and MLO Basic Multi-Link consistency.
2. Temporary rejection with comeback schedules a later retry rather than destroying assoc state.
3. On success, `ieee80211_assoc_success()` validates and commits all requested links.
4. Per-link `ieee80211_assoc_config_link()` configures capabilities and BSS state; rejected non-association links are removed.
5. Station state advances to associated and possibly authorized, BSS/link changes are notified, carrier is enabled, power-save state is recalculated, and health monitors are armed.
6. The assoc data object is destroyed with `ASSOC_SUCCESS` or failure status, and cfg80211 receives the response with per-link statuses and request IEs.

### Associated Beacon Flow

1. `ieee80211_sta_rx_queued_mgmt()` dispatches beacons to `ieee80211_rx_mgmt_beacon()` with the correct link from RX status.
2. The beacon is accepted only if BSSID and RX frequency match the associated link, including MBSSID and S1G exceptions.
3. Signal averages and AP-probe state are updated; beacon monitor is pushed out.
4. Relevant IEs are parsed with a CRC filter so unchanged beacons skip heavy processing.
5. Changed beacons update BSS cache, CSA, cross-link CSA, MLO BSS change count, WMM/QoS, DTIM, ERP, TWT, bandwidth, opmode, power constraints, ML reconfiguration, and advertised TTLM.
6. Accumulated `BSS_CHANGED_*` bits are sent to the driver through `ieee80211_link_info_change_notify()`.

### Channel Switch Flow

1. CSA can arrive in beacons, protected action frames, public/unprotected action frames, or another link's MLO per-STA profile.
2. Unprotected action frames are not trusted for switching; they may only block TX for quiet mode while waiting for a beacon.
3. Protected/beacon CSA validates band, channel usability, same-channel behavior, channel context support, and driver pre-switch acceptance.
4. The code reserves a channel context, sets CSA flags, blocks queues if requested, notifies cfg80211 start, and either delegates to the driver or schedules software completion.
5. Driver completion calls `ieee80211_chswitch_done()`; `ieee80211_csa_switch_work()` finishes reservation and waits for the first post-switch beacon.
6. `ieee80211_chswitch_post_beacon()` clears CSA state, unblocks queues, calls driver post-switch, and notifies cfg80211.
7. Any incompatible or failed step queues `csa_connection_drop_work`, which disconnects.

### Connection Loss Flow

1. Beacon loss, driver connection loss, connection idle, nullfunc/probe failures, or driver-requested disconnect all converge on AP probing or disconnect work.
2. `ieee80211_mgd_probe_ap()` marks connection polling active, disables power save if needed, and sends a nullfunc or probe request.
3. Beacon/probe response or nullfunc ACK resets the AP probe state.
4. Repeated nullfunc failures or probe timeouts call `ieee80211_sta_connection_lost()`, which tears down association and reports disconnect.

## State and Persistence Behavior

This chunk does not persist data to disk; persistence is in kernel memory, timers, RCU-protected BSS/STA objects, and driver/cfg80211 notifications.

Important retained state includes:

- `ifmgd->auth_data` and `ifmgd->assoc_data`: own BSS references and temporary STA/channel state while authentication or association is active.
- `ifmgd->associated`: gates most managed-station behavior and is cleared only through teardown paths.
- `ifmgd->assoc_req_ies`: cached request IEs for cfg80211 association response reporting.
- `ifmgd->flags`: bitfield for U-APSD, MFP, RRM, control port, connection polling, and nullfunc ACK state.
- `ifmgd->probe_send_count`, `ifmgd->nullfunc_failed`, and `ifmgd->probe_timeout`: liveness-probe retry state.
- `ifmgd->timer`, `bcn_mon_timer`, and `conn_mon_timer`: in-memory scheduling state for auth/assoc/probe/beacon/idle monitoring.
- `link->conf`: driver-facing per-link BSS configuration, including channel request, beacon/DTIM timing, QoS, TPE, TWT, EPCS support, power limits, CQM, MLO counters, and CSA flags.
- `link->u.mgd`: per-link private state for AP BSSID, connection mode, beacon CRC/signal tracking, WMM parameter-set tracking, CSA state, DTIM period, and disable-WMM-tracking guard.
- `sdata->vif.valid_links`, `active_links`, `dormant_links`, `suspended_links`, and `neg_ttlm`: MLO link-set state visible to drivers.
- `sdata->u.mgd.ttlm_info` and `sdata->u.mgd.removed_links`: pending advertised TTLM and ML-reconfiguration state.

The central teardown path, `ieee80211_set_disassoc()`, aggressively resets all of these categories so later associations do not inherit stale BSS, link, WMM, MU-MIMO, PS, CSA, TTLM, or EPCS state. This is a major safety invariant for this file.

## Dependencies and Integration Points

### mac80211 Internal Dependencies

- `ieee80211_i.h` provides core internal structures and helpers.
- `driver-ops.h` supplies driver callbacks such as `drv_mgd_prepare_tx`, `drv_mgd_complete_tx`, `drv_pre_channel_switch`, `drv_channel_switch`, `drv_post_channel_switch`, `drv_abort_channel_switch`, `drv_conf_tx`, `drv_tx_frames_pending`, `drv_can_neg_ttlm`, and `drv_sta_set_4addr`.
- Rate, STA, channel-context, and BSS helpers include `sta_info_*`, `rate_control_rate_init_all_links`, `ieee80211_link_use_channel`, `ieee80211_link_change_chanreq`, `ieee80211_link_reserve_chanctx`, `ieee80211_link_use_reserved_context`, `ieee80211_teardown_tdls_peers`, and BSS cache update routines.
- IE builders/parsers such as `ieee802_11_parse_elems_full`, `ieee80211_ie_build_ht_cap`, `ieee80211_ie_build_vht_cap`, `ieee80211_put_he_cap`, `ieee80211_put_eht_cap`, and MLE helpers are critical dependencies.
- `fils_aead.h` supplies FILS association request/response encryption/decryption helpers.

### cfg80211 and nl80211 Integration

- cfg80211 BSS references and callbacks are used through `cfg80211_put_bss`, `cfg80211_ref_bss`, `cfg80211_unlink_bss`, `cfg80211_assoc_failure`, `cfg80211_rx_assoc_resp`, `cfg80211_assoc_comeback`, `cfg80211_rx_mlme_mgmt`, `cfg80211_tx_mlme_mgmt`, `cfg80211_ch_switch_started_notify`, `cfg80211_ch_switch_notify`, `cfg80211_cac_event`, `cfg80211_cqm_*_notify`, `cfg80211_epcs_changed`, and `cfg80211_links_removed`.
- nl80211 channel width, band, flags, and CQM/TWT/MLO concepts are used throughout.
- cfg80211 RNR and element helpers are used for MLO cross-link CSA and BSS parameter change count propagation.

### Driver-Facing API Surface in This Chunk

Exported or KUnit-visible functions in this chunk include:

- `ieee80211_sta_reset_beacon_monitor()`
- `ieee80211_sta_reset_conn_monitor()`
- `ieee80211_calc_chandef_subchan_offset()` and `ieee80211_rearrange_tpe_psd()` for KUnit.
- `ieee80211_determine_chan_mode()` for KUnit.
- `ieee80211_send_pspoll()`
- `ieee80211_send_nullfunc()`
- `ieee80211_send_4addr_nullfunc()`
- `ieee80211_chswitch_done()`
- `ieee80211_ap_probereq_get()`
- `ieee80211_beacon_loss()`
- `ieee80211_connection_loss()`
- `ieee80211_disconnect()`
- `ieee80211_req_neg_ttlm()`
- `ieee80211_process_neg_ttlm_req()`
- `ieee80211_process_neg_ttlm_res()`
- `ieee80211_process_ttlm_teardown()`
- `ieee80211_send_teardown_neg_ttlm()`
- `ieee80211_sta_rx_queued_ext()`
- `ieee80211_sta_rx_queued_mgmt()`
- `ieee80211_sta_connection_lost()`
- `ieee80211_mgd_conn_tx_status()`
- `ieee80211_sta_work()`

## Risks and Edge Cases

- Mode selection is intentionally permissive outside `STRICT` mode. This improves interoperability with broken APs but means spec-invalid APs may be accepted with downgraded capabilities.
- The repeated parse/downgrade loop in `ieee80211_determine_chan_mode()` relies on connection mode monotonically decreasing. Any future mode ordering changes must preserve that invariant.
- CSA handling has security-sensitive branching. Unprotected public action frames may block queues but are not trusted for final switch; beacons/protected frames can trigger real channel changes.
- Channel switch failure sets CSA state before disconnect so teardown knows whether TX was blocked. Incorrect CSA flag reset can leave queues blocked or cause forbidden deauth transmission.
- MLO cross-link CSA uses RNR/per-STA profile inference and has documented timing limitations. It may not perfectly detect bandwidth/puncturing-only CSA aborts.
- Association success is a multi-object commit across `sdata`, `vif`, `sta_info`, per-link state, channel contexts, and cfg80211 BSS references. Partial failure paths must destroy or release all created link/STA/channel state.
- `ieee80211_set_disassoc()` is very broad; changes here can regress roaming latency, AP notification, power-save state, link masks, EPCS/TTLM, or driver BSS notifications.
- Beacon CRC filtering intentionally avoids heavy processing on unchanged beacons, but any newly important IE must be added to `care_about_ies` or otherwise force processing.
- WMM tracking disables itself after invalid AP parameters to avoid oscillating queue settings; this may leave default QoS in place even if later beacons become valid.
- Power save depends on associated/authenticated station state, beacon availability, AP-broken flags, and hardware capability combinations. Incorrect ordering around disassoc or nullfunc ACK status can leave PS enabled at the wrong time.
- TTLM parsing requires valid nonzero maps and valid-link containment. A bad negotiated response currently disconnects rather than attempting recovery.
- `ieee80211_rx_mgmt_beacon()` disconnects on decrypted SSID mismatch, which is correct for security but sensitive to hidden SSID handling and MBSSID profile parsing.
- This chunk ends inside `ieee80211_mgd_quiesce()`. PM quiesce behavior is not fully visible here and must be reconciled with later chunk research.

## Test and Verification Signals

Useful test signals for this chunk include:

- KUnit coverage for `ieee80211_calc_chandef_subchan_offset()`, `ieee80211_rearrange_tpe_psd()`, and `ieee80211_determine_chan_mode()` through their `VISIBLE_IF_MAC80211_KUNIT` exports.
- Association tests that cover mode downgrades: legacy-only, HT, VHT, HE, EHT, UHR, 6 GHz HE/EHT, S1G, disabled HT/VHT/HE/EHT/UHR request flags, WEP/TKIP legacy forcing, and required membership-selector rejection.
- Interoperability tests with APs missing WMM/HT/VHT data in association responses, validating the non-STRICT fallback to beacon/probe response data.
- Negative association tests for missing SuppRates, invalid AID, MLO response without Basic Multi-Link element, AP MLD address mismatch, invalid per-STA profile status, and invalid TTLM in association response.
- Beacon-processing tests for unchanged CRC filtering, WMM parameter changes, invalid WMM fallback, DTIM update, P2P NoA changes, ERP changes, TWT recalculation, power constraint changes, and SSID mismatch disconnect.
- CSA tests for protected action CSA, unprotected action CSA, beacon CSA, same-channel CSA, unsupported channel, different band, inactive-link switch, driver channel-switch success/failure, reservation failure, abort detection, and post-switch beacon completion.
- MLO tests for cross-link CSA, BSS parameter change count propagation, link removal with timeout, no-valid-link disconnect, advertised TTLM scheduled switch, TTLM cancellation, and negotiated TTLM request/response/teardown.
- Power-save tests for single-station eligibility, AP interface disabling PS, dynamic PS with pending TX, PS nullfunc ACK handling, TIM-driven nullfunc/PS-Poll behavior, and disassociation PS cleanup.
- Connection-loss tests for beacon loss, connection idle, nullfunc failure, probe response recovery, probe exhaustion disconnect, driver-requested disconnect, and reconnect flag reporting.
- Teardown regression tests should check that timers are canceled, queues are unblocked, channel contexts released, AP/TDLS STA entries removed, link masks reset, MU-MIMO ownership cleared, WMM defaults restored, TTLM/EPCS cleared, and cfg80211 notifications are emitted exactly once.

## Chunk Boundary Notes

- Lines after 8936 continue `ieee80211_mgd_quiesce()` under `CONFIG_PM`; this chunk only observes its declaration, local variables, lock assertion, and the first auth/assoc-data branch setup.
- Later chunks should reconcile this report with setup/restart functions visible after line 8936, especially initialization of work/timers and cfg80211 entry points for auth, assoc, deauth, disassoc, ML reconfiguration, RSSI reports, and EPCS.
