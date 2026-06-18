# sources/distributed-fs/ceph-client/net/mac80211/mlme.c lines 8937-11322

## Scope

This chunk covers the managed station MLME path from the tail of suspend quiesce handling through station restart/setup, authentication and association entry points, local deauth/disassoc/stop paths, CQM RSSI/beacon notifications, Multi-Link Operation (MLO) link reconfiguration request/response handling, and EPCS enable/teardown handling.

The range starts inside `ieee80211_mgd_quiesce()`: the function header and initial local variables are just before this chunk, but the covered lines include the critical suspend race workaround that explicitly aborts in-progress authentication or association and deauthenticates again if an association completed during suspend.

## Purpose

`net/mac80211/mlme.c` implements managed-mode station MLME for mac80211. In this chunk, it:

- Keeps station state coherent across suspend/resume and hardware restart, including driver-requested post-resume disconnects.
- Initializes per-interface and per-link work items, timers, SMPS state, link addresses, channel-switch work, and TDLS teardown state.
- Prepares AP station/link state before authentication or association, including MLO link creation, BSSID/timing setup, channel context preparation, and scan cancellation.
- Implements cfg80211-facing authentication, association, deauthentication, and disassociation hooks for station interfaces.
- Converts cfg80211 auth/assoc requests into mac80211 internal `auth_data`, `assoc_data`, link settings, U-APSD/MFP/RRM/control-port flags, and transmitted management frames.
- Validates and executes MLO association link reconfiguration: building protected EHT action frames, pre-removing requested links, adding accepted links after AP response, and notifying cfg80211/driver state changes.
- Handles EPCS enable/disable action frames, including per-link WMM parameter updates carried in ML EPCS elements.

Although this source tree is under a Ceph client snapshot, this file is generic Linux wireless station infrastructure. It does not implement CephFS behavior directly.

## Important APIs, Types, And Functions

Station lifecycle and setup:

- `ieee80211_mgd_quiesce()` tail aborts in-flight auth/assoc during suspend and handles an association-completed-during-suspend race by calling `ieee80211_mgd_deauth()` when not using WoWLAN.
- `ieee80211_sta_restart()` consumes `IEEE80211_SDATA_DISCONNECT_RESUME` and `IEEE80211_SDATA_DISCONNECT_HW_RESTART`, reporting connection loss if the driver requested a disconnect.
- `ieee80211_sta_setup_sdata()` initializes managed-interface work items and timers: monitor, beacon loss, CSA drop, TDLS peer deletion, ML reconf, TTL mapping, TSpec, negotiation timeout, and teardown work.
- `ieee80211_mgd_setup_link()` initializes per-link managed state, SMPS defaults, CSA switch work, transmit power envelope state, and per-link local address selection.
- `ieee80211_mgd_stop_link()` and `ieee80211_mgd_stop()` cancel link/interface work, destroy pending auth/assoc state, clear TDLS teardown SKBs, free association request IEs, and delete the station timer.

Connection preparation and CSA filtering:

- `ieee80211_prep_connection()` is the shared setup routine for auth/assoc. It validates MLO versus non-MLO inputs, creates or reuses the AP `sta_info`, allocates MLO link state with `ieee80211_vif_set_links()`, configures link STA parameters, copies BSSID/timing from the BSS, runs `ieee80211_prep_channel()`, notifies drivers of BSSID/basic-rate/beacon interval changes, inserts the AP station, and cancels scans.
- `ieee80211_mgd_csa_present()` and `ieee80211_mgd_csa_in_process()` reject auth/assoc while a BSS advertises an active CSA/ECSA move. They ignore zero-count switch elements and no-op non-blocking switches to the current channel.
- `ieee80211_parse_cfg_selectors()` records userspace-provided BSS membership selectors and defaults to SAE H2E support for backward compatibility when selectors are absent.

Authentication and association:

- `ieee80211_mgd_auth()` maps nl80211 auth types to WLAN auth algorithms, rejects unsupported/FIPS-disallowed modes, allocates `struct ieee80211_mgd_auth_data`, preserves continuation state for SAE/EPPKE exchanges, disconnects from a current AP if necessary, sets `vif.cfg.ap_addr`, derives connection mode, prepares the connection, and transmits auth frames through `ieee80211_auth()`.
- `ieee80211_setup_assoc_link()` copies per-link STA-profile elements, resets beacon/DTIM tracking, reads DTIM and MBSSID/EMA data from BSS IEs, logs corrupt BSS data, and selects SMPS mode.
- `ieee80211_mgd_get_ap_ht_vht_capa()` validates required HT operation and VHT capability elements for the selected connection mode and stores AP HT/VHT data in association state.
- `ieee80211_mgd_assoc_bss_has_mld_ext_capa_ops()` scans the AP's Basic Multi-Link element to decide whether extended MLD capabilities may be sent without triggering broken APs.
- `ieee80211_mgd_assoc()` builds `struct ieee80211_mgd_assoc_data` for single-link or MLO association, validates SSID and BSS capabilities, handles existing connections, sets HT/VHT/S1G capability overrides, copies FILS KEK/nonces, selects U-APSD/MFP/RRM/control-port policy, prepares all requested MLO links, starts association timeout handling, optionally waits for a DTIM beacon, queues the MLME timer, and releases matching auth state once association starts.
- `ieee80211_mgd_deauth()` and `ieee80211_mgd_disassoc()` implement local abort/disconnect paths for auth, assoc, and connected states and report disconnect frames to cfg80211.

CQM notifications:

- `ieee80211_cqm_rssi_notify()` and `ieee80211_cqm_beacon_loss_notify()` are exported driver APIs that trace and forward connection-quality events to cfg80211.
- `ieee80211_enable_rssi_reports()` / `ieee80211_disable_rssi_reports()` store scaled RSSI thresholds in managed-interface state for later averaging logic.

MLO reconfiguration and EPCS:

- `ieee80211_process_ml_reconf_resp()` validates protected EHT link reconfiguration responses by MLD state, minimum action size, dialog token, expected link mask, status array length, duplicate/unexpected links, and group-key-data presence. It disconnects on inconsistent responses.
- `ieee80211_build_ml_reconf_req()` constructs a protected EHT link reconfiguration request SKB with a Reconfiguration Multi-Link element, common MLD fields, optional EML/MLD/ext-MLD capability fields, per-STA profiles for added/deleted links, WMM info, fragmented elements, and `IEEE80211_TX_CTL_REQ_TX_STATUS`.
- `ieee80211_mgd_assoc_ml_reconf()` is the cfg80211-requested MLO reconfiguration entry point. It validates MLD and AP support, rejects concurrent operations, prepares added-link association data, verifies EHT/WMM/U-APSD/channel compatibility, changes active links if removals would remove the current active set, builds and transmits the request, pre-removes requested links locally, and starts a short response timeout.
- `ieee80211_mgd_epcs_supp()` requires MLO and per-link `epcs_support` before EPCS operations.
- `ieee80211_mgd_set_epcs()` sends EPCS enable request or teardown action frames and tracks a pending EPCS dialog token.
- `ieee80211_ml_epcs()` parses ML EPCS per-STA profiles, defragments subelements, parses per-link elements, and applies WMM/MU-EDCA updates with `ieee80211_sta_wmm_params()`.
- `ieee80211_process_epcs_ena_resp()` validates dialog token/status, parses EPCS response IEs, applies ML EPCS updates, and marks EPCS enabled.
- `ieee80211_process_epcs_teardown()` accepts AP teardown only when MLO EPCS is enabled and clears EPCS state.

## Control Flow

Suspend quiesce first handles pending connection attempts: if `auth_data` or `assoc_data` exists, mac80211 sends a local deauth frame, destroys pending state, and reports the transmitted MLME frame to cfg80211. It then covers the race where an association response arrives during suspend after cfg80211's disconnect check but before RX frame dropping; if now associated and not in WoWLAN, it constructs a deauth request and runs the normal managed deauth path.

Station setup is mostly initialization. Interface setup wires work items and timers to their handlers and copies default power-save/U-APSD values from wdev/hardware. Link setup binds `conf->bssid` to managed BSSID storage, initializes SMPS based on dynamic-SMPS support, initializes CSA work, clears TPE, and chooses the link address from pending association data, pending reconfiguration data, or a random address.

Authentication starts at cfg80211's `auth` operation, which calls `ieee80211_mgd_auth()` through `net/mac80211/cfg.c`. The function validates the auth type, rejects association overlap, rejects APs currently switching channels, allocates and fills `auth_data`, merges auth payload and IEs, stores crypto key material for shared-key auth, and detects continuation of an existing auth exchange. It then replaces old auth data, may mark the station authenticated for continuation cases, disconnects any current association, derives station mode, calls `ieee80211_prep_connection()`, and transmits the auth frame. On failure it clears BSSID/channel state for non-MLO and frees auth data.

Association follows the cfg80211 `assoc` operation into `ieee80211_mgd_assoc()`. It allocates a single flexible `assoc_data` block large enough for common IEs and per-link elements, reads SSID from BSS IEs under RCU, records AP MLD or BSSID address, optionally suppresses ext-MLD capability transmission for compatibility, and disconnects an existing association. For MLO, it validates all requested links, requires WMM and EHT, rejects S1G and disabled HT/VHT/HE/EHT flags, assigns per-link local addresses, derives per-link connection modes, and captures AP HT/VHT capabilities. For non-MLO, it configures link 0 with the interface address, WMM/S1G state, 6 GHz restrictions, connection mode, and AP capability snapshots. The function then refuses incomplete auth or another pending assoc, installs IEs/FILS data, configures U-APSD/MFP/RRM/control-port state, stores `ifmgd->assoc_data`, pre-validates non-association MLO links, stores SSID and AP address in `vif.cfg`, prepares the connection, optionally waits for beacon/DTIM, schedules the association timeout, and destroys matched auth state.

Local deauth and disassoc are address-matched state machines. Deauth can abort pending auth, abort pending assoc, or deauthenticate an established association; each successful path sends or suppresses the frame according to local-state-change policy and calls `ieee80211_report_disconnect()`. Disassoc only applies to an established association with matching AP address.

MLO reconfiguration request flow starts at cfg80211's `assoc_ml_reconf` operation. Added links are validated and stored in temporary association-style data but are not made valid yet. Removed links are handled earlier: active links are adjusted so at least one non-dormant valid link remains, then after the request SKB is built the removed links are dropped from `vif.valid_links`, station link state is removed, and cfg80211/driver notifications are emitted. The request is transmitted, reconfiguration state records added/removed masks and temporary data, and a delayed timeout work item will disconnect if no valid response arrives.

MLO reconfiguration response flow validates the AP response against the pending dialog token and exact changed-link mask. Failure to remove an already-removed link is fatal. Failure to add a link just clears that link from the added mask. For successful additions, the code requires group key data for userspace processing, allocates station link state, enables the new valid links, configures each accepted link from the BSS and response profile, activates the station link, marks the link associated, notifies driver changes, recalculates SMPS/powersave, reports completion to cfg80211, frees temporary add-link data, and resets reconfiguration state. Malformed or inconsistent responses disconnect the station.

EPCS enable flow sends a protected EHT action frame with a new dialog token, then `ieee80211_process_epcs_ena_resp()` accepts only a matching token, or a constrained unsolicited token-zero notification when EPCS is already enabled and status is success. Successful responses parse action-frame IEs, apply per-link WMM/MU-EDCA changes from the ML EPCS element, and mark EPCS enabled. EPCS disable/teardown clears local state immediately for local requests or in response to AP teardown.

## State And Persistence Behavior

All state in this chunk is in-memory kernel networking state. There is no filesystem or disk persistence.

Key persistent-in-memory fields include:

- `sdata->u.mgd.auth_data` and `assoc_data`, which represent pending authentication and association transactions and own copied request IEs, FILS material, BSS references, per-link settings, timeouts, AP address, and link-local addresses until success, abort, timeout, or stop.
- `sdata->u.mgd.reconf`, which persists an in-flight MLO reconfiguration's dialog token, added/removed masks, temporary add-link data, and delayed timeout work.
- `sdata->u.mgd.epcs`, which stores whether EPCS is enabled and whether an enable request dialog token is pending.
- `sdata->vif.valid_links`, `active_links`, `dormant_links`, `vif.cfg.ap_addr`, `vif.cfg.ssid`, per-link `link->conf`, and AP `sta_info`/`link_sta_info`, which are updated during connection setup, association, and MLO reconfiguration.
- Managed-interface flags for U-APSD, MFP, RRM, control-port behavior, RSSI thresholds, power-save defaults, multicast sequence state, and TDLS teardown SKB ownership.

RCU protects BSS IE access and station/link dereferences in multiple places. The wiphy mutex is expected for most public cfg80211-facing entry points, with explicit `lockdep_assert_wiphy()` calls in several routines. Work and timer state persists across asynchronous MLME operations until canceled by stop, disconnect, timeout, or link removal.

The connection-preparation path is careful about partial state. On errors it releases channel context, destroys temporary station state, clears valid links for failed MLO setup, zeroes BSSID for non-MLO, and frees auth/assoc/reconf temporary data. Some state is intentionally changed before frame exchange: MLO link removals are applied locally before the AP response to prevent transmission over links the AP is expected to remove.

## Dependencies And Integration Points

This chunk depends on mac80211 core types such as `struct ieee80211_sub_if_data`, `struct ieee80211_if_managed`, `struct ieee80211_link_data`, `struct ieee80211_local`, `struct sta_info`, `struct link_sta_info`, `struct ieee80211_mgd_auth_data`, `struct ieee80211_mgd_assoc_data`, and `struct ieee80211_conn_settings`.

It integrates with cfg80211 through:

- `net/mac80211/cfg.c` operations: `auth`, `assoc`, `deauth`, `disassoc`, `assoc_ml_reconf`, and `set_epcs` delegate into functions in this chunk.
- cfg80211 BSS objects and IEs (`struct cfg80211_bss`, `cfg80211_bss_ies`, `cfg80211_find_elem()`, `ieee80211_bss_get_elem()`), BSS references, and cfg80211 notifications such as `cfg80211_tx_mlme_mgmt()`, `cfg80211_cqm_rssi_notify()`, `cfg80211_cqm_beacon_loss_notify()`, `cfg80211_links_removed()`, and `cfg80211_mlo_reconf_add_done()`.
- nl80211 request structures and feature flags for auth algorithms, association flags, MLO link reconfiguration, EPCS, bands, iftypes, and CQM events.

It integrates with drivers through mac80211 notifications and callbacks:

- `drv_mgd_prepare_tx()` / `drv_mgd_complete_tx()` bracket local auth/assoc abort deauth frames.
- `ieee80211_link_info_change_notify()` and `ieee80211_vif_cfg_change_notify()` notify BSSID, rates, beacon interval, QoS, and valid-link changes.
- `ieee80211_set_active_links()`, `ieee80211_vif_set_links()`, `ieee80211_link_release_channel()`, and `ieee80211_prep_channel()` manage link and channel context visible to drivers.

It integrates with RX action-frame dispatch in `net/mac80211/iface.c`, which calls `ieee80211_process_ml_reconf_resp()`, `ieee80211_process_epcs_ena_resp()`, and `ieee80211_process_epcs_teardown()` for protected EHT station action frames.

It also depends on shared MLME helpers outside this chunk for frame construction/transmission, association response parsing, station state transitions, power-save recalculation, SMPS recalculation, HT/VHT/HE/EHT mode determination, EPCS state changes, element fragmentation/defragmentation, and WMM parameter application.

## Risks And Edge Cases

Suspend/resume races are explicitly called out in the code. cfg80211 cannot abort every in-progress auth/assoc attempt during suspend, so mac80211 sends deauth and destroys pending state itself. The additional post-check for a newly associated station prevents a channel-context leak into driver suspend removal.

MLO state transitions are fragile because `vif.valid_links`, `active_links`, station link allocation, channel contexts, and cfg80211 notifications must remain consistent. Error paths that miss `ieee80211_vif_set_links(..., 0, 0)`, channel release, or station-link cleanup can leave stale links or driver-visible state.

Authentication continuation needs exact matching. SAE and EPPKE continuation paths preserve or mark authenticated state under narrow transaction-number conditions. Destroying/reallocating the AP STA on continuation would break multi-frame exchanges.

Association compatibility handling is intentionally conservative. Extended MLD capabilities are only sent in strict mode or when the AP advertised that field because some APs reject frames containing it. Regressions here can cause association failures with otherwise valid APs.

CSA/ECSA filtering prevents connecting to a BSS mid-channel-switch. It treats zero-count or no-op non-blocking switch elements as absent, and has a special path for stuck ECSA in probe responses. Incorrect filtering could either reject usable APs or connect to a moving AP.

U-APSD depends on both driver capability and all relevant BSS/link support. The code disables U-APSD when incompatible with `HW_PS_NULLFUNC_STACK` and rejects MLO added links if U-APSD was already enabled but new links do not all support it.

MLO reconfiguration response parsing is intentionally strict. Unexpected links, duplicate links, absent status entries, invalid group-key-data length, failed removals, or mismatched per-station-profile status disconnect the station rather than trying to recover from inconsistent AP state.

The ML reconf request builder computes SKB size manually before adding nested and fragmentable elements. Any mismatch between size calculation and later `skb_put*()` calls risks memory corruption; added link elements, WMM info, capability fields, and fragmentation overhead are important test targets.

EPCS parsing trusts the action-frame body shape after minimum dispatch checks elsewhere. It reads dialog token and status directly and computes IE length from the received frame length. Short malformed frames should be covered by RX validation and tests because underflow here would be dangerous.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for station mode, MLO/EHT, S1G, PM, FIPS, U-APSD, RRM, MFP, FILS, SAE, EPPKE, and driver combinations with and without dynamic SMPS and connection-monitor offload.
- Suspend/resume tests with auth and assoc in progress, including association response racing with suspend, both with and without WoWLAN. Expected signals are explicit disconnect reports, no lingering channel context, and no post-resume phantom association.
- Auth tests for every mapped nl80211 auth type, FIPS shared-key rejection, SAE/EPPKE continuation, IEEE8021X/EPPKE `epp_peer` marking, cfg80211 BSS ref handling, and abort by local deauth.
- Association tests for single-link 2.4/5/6 GHz and S1G, disabled capability flags, missing SSID, missing HT operation, missing VHT capability, corrupt BSS data logging, FILS KEK/nonces, MFP/RRM/control-port flags, DTIM-before-assoc waiting, and concurrent auth/assoc `-EBUSY` behavior.
- MLO association tests with multiple links, missing WMM, non-EHT links, S1G rejection, per-link local address assignment, per-link element copying, userspace selector effects, and ext-MLD capability compatibility behavior against APs that omit or include the field.
- Local deauth/disassoc tests for pending auth, pending assoc, connected state, wrong BSSID/AP address, and `local_state_change` frame-suppression behavior.
- Work/timer cleanup tests for interface/link stop, including pending monitor/beacon/CSA/TDLS/reconf/TTLM/TSpec work, pending auth/assoc, TDLS teardown SKBs, and association request IE memory.
- CQM tests verifying exported RSSI and beacon-loss notifications reach cfg80211, and RSSI threshold storage uses the expected 16x scaling.
- MLO reconfiguration request tests for add-only, remove-only, add+remove, no remaining valid link, active-link fallback, request SKB contents, TX status flag, timeout disconnect, and cleanup on allocation/channel-prep failures.
- MLO reconfiguration response tests for dialog-token mismatch, short status arrays, duplicate/unexpected/missing links, failed added links, failed removed links, invalid group-key data, rejected station profile despite AP success, successful added-link activation, cfg80211 completion data, and power-save/SMPS recalculation.
- EPCS tests for unsupported non-MLO/per-link state, repeated enable while a dialog is pending, local teardown while pending, matching and mismatched enable responses, unsolicited token-zero responses, malformed ML EPCS elements, WMM/MU-EDCA updates per link, and AP teardown notification.
