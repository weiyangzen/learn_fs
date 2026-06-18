# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.c lines 1-9394

## Scope

This chunk covers the first 9,394 lines of `drivers/net/wireless/ath/ath12k/mac.c`. The file continues after this range; APIs that begin near the end, such as `ath12k_mac_add_p2p_noa_ie()`, are only partially visible here and should be reconciled with later chunk reports.

## Purpose

This section of `mac.c` is the ath12k driver's main mac80211 integration layer for channel/rate capability advertisement, vdev lifecycle, beaconing, BSS configuration, scanning, key installation, station state transitions, MLO link management, per-peer rate control updates, TX queue configuration, PHY capability construction, and management-frame TX over WMI. It translates Linux `mac80211`/`cfg80211` objects (`ieee80211_hw`, `ieee80211_vif`, `ieee80211_bss_conf`, `ieee80211_sta`, `ieee80211_link_sta`, `cfg80211_chan_def`) into ath12k firmware WMI commands and datapath peer state.

## Static Tables And Conversions

- Channel tables define 2.4 GHz, 5 GHz, and 6 GHz channels with default power and antenna values via `CHAN2G`, `CHAN5G`, and `CHAN6G`.
- `ath12k_legacy_rates` maps CCK/OFDM legacy bitrates to ath12k hardware rate codes, with aliases for 2 GHz and 5 GHz rate sets.
- `ath12k_phymodes` maps `nl80211` band plus channel width to firmware `enum wmi_phy_mode`, including EHT 20/40/80/160/320 modes.
- `ath12k_mac_mon_status_filter_default` configures monitor status TLV filters for MPDU/PPDU status and management/control/data packet filters.
- Exported conversion helpers include `ath12k_mac_he_convert_tones_to_ru_tones()`, `ath12k_mac_eht_gi_to_nl80211_eht_gi()`, `ath12k_mac_eht_ru_tones_to_nl80211_eht_ru_alloc()`, `ath12k_mac_bw_to_mac80211_bw()`, and `ath12k_mac_hw_ratecode_to_legacy_rate()`.
- NSS/MCS helpers (`ath12k_mac_max_*_nss()`, `ath12k_mac_max_eht_mcs_nss()`) compute maximum supported spatial streams from bitrate masks or EHT MCS/NSS structures.

## Core Object Lookup And State Mapping

- Link-aware helpers use RCU or wiphy-protected dereferences to resolve `ath12k_vif`/`ath12k_link_vif` and `ath12k_sta`/`ath12k_link_sta`:
  - `ath12k_mac_get_link_bss_conf()`, `ath12k_mac_get_link_sta()`, and `ath12k_mac_vif_link_chan()` read mac80211 link state.
  - `ath12k_mac_get_arvif()`, `ath12k_mac_get_arvif_by_vdev_id()`, `ath12k_mac_get_ar_by_vdev_id()`, `ath12k_mac_get_ar_by_pdev_id()`, `ath12k_get_ar_by_vif()`, and channel-context helpers map firmware vdev/pdev/radio identifiers to driver objects.
  - `ath12k_mac_get_tx_arvif()` and `ath12k_mac_get_tx_bssid()` support MBSSID/non-transmitted profile handling.
- Radio/pdev selection handles split PHY and single-pdev devices. `ath12k_mac_get_target_pdev_id()` selects a firmware pdev based on active vif channel band when firmware exposes one Linux radio but multiple firmware pdevs.
- Persistent driver state updated in this chunk includes `ar->allocated_vdev_map`, `ar->num_started_vdevs`, `ar->num_created_vdevs`, `ar->num_peers`, `ar->num_stations`, `arvif->is_created`, `arvif->is_started`, `arvif->is_up`, `ahvif->links_map`, `ahsta->links_map`, cached link config, key cache entries, and rate-control shadow fields on `ath12k_link_sta`.

## Vdev, Monitor, Beacon, And BSS Control Flow

- `ath12k_mac_vdev_setup_sync()` waits for firmware vdev start/stop completion and returns timeout/shutdown/status errors.
- Monitor vdev flow:
  - `ath12k_mac_monitor_vdev_start()` builds a WMI vdev-start request from a channel definition, waits for setup completion, then sends vdev-up.
  - `ath12k_mac_monitor_vdev_stop()` stops/down's the monitor vdev.
  - `ath12k_mac_monitor_vdev_delete()`, `ath12k_mac_monitor_start()`, and `ath12k_mac_monitor_stop()` manage monitor creation state, HTT monitor-ring filter programming, and started-vdev counts.
- Normal vdev stop is handled by `ath12k_mac_vdev_stop()`, which sends WMI stop, waits for setup sync, decrements `num_started_vdevs`, and clears CAC state when needed.
- Beacon setup:
  - `ath12k_mac_setup_bcn_tmpl()` obtains mac80211 beacon templates, handles transmitted/non-transmitted MBSSID profiles, extracts RSN/WPA/security and beacon-protection flags, handles P2P GO IE offload/removal, and sends `ath12k_wmi_bcn_tmpl()`.
  - `ath12k_mac_setup_bcn_tmpl_ema()` sends EMA beacon template series from mac80211.
  - `ath12k_control_beaconing()` sends WMI vdev down/up and sets bssid/aid/tx-bssid fields around beacon enable state.
  - `ath12k_mac_bcn_tx_event()` drives color-change countdown and beacon template refresh from beacon TX work.
- `ath12k_mac_bss_info_changed()` is the major BSS change dispatcher for beacon interval/template/DTIM, SSID, BSSID, beacon enable, HE/EHT TXBF config, ERP CTS/slot/preamble, association/disassociation, TX power recalc, multicast/basic rates, TWT, OBSS PD/spatial reuse, BSS color, FILS discovery, and STA power-save setup.
- `ath12k_mac_op_link_info_changed()` caches BSS changes when a link vdev does not yet exist and replays them later through the vdev setup path outside this chunk.

## Peer Association Pipeline

`ath12k_peer_assoc_prepare()` builds a `struct ath12k_wmi_peer_assoc_arg` by composing many focused helpers before `ath12k_wmi_send_peer_assoc_cmd()` is issued by station/AP association paths.

- Basic and crypto setup:
  - `ath12k_peer_assoc_h_basic()` fills peer MAC, vdev id, AID, listen interval, auth flag, and assoc capability.
  - `ath12k_peer_assoc_h_crypto()` infers 4-way/2-way handshake and PMF needs from beacon template flags, cfg80211 BSS IEs, and STA MFP state.
- Rate/capability setup:
  - `ath12k_peer_assoc_h_rates()` intersects peer supported legacy rates with `arvif->bitrate_mask`.
  - `ath12k_peer_assoc_h_ht()`, `_vht()`, `_he()`, `_he_6ghz()`, and `_eht()` translate mac80211 peer capabilities, local bitrate masks, bandwidth, NSS, PPE thresholds, AMPDU limits, TWT, puncturing, and MCS/NSS maps into WMI peer-association fields.
  - `ath12k_peer_assoc_h_phymode()` chooses the highest applicable WMI PHY mode, preferring EHT, then HE, VHT, HT, and finally legacy modes by band.
  - Fixed-rate helpers later reuse these masks to set peer-specific VHT/HE/EHT fixed rates when exactly one MCS is selected.
- QoS, SMPS, MLO:
  - `ath12k_peer_assoc_h_qos()` and `ath12k_peer_assoc_qos_ap()` set WME/UAPSD flags and AP power-save peer params.
  - `ath12k_peer_assoc_h_smps()` maps HT/6 GHz SMPS state through `ath12k_smps_map`.
  - `ath12k_peer_assoc_h_mlo()` fills WMI MLO parameters including MLD address, ML peer id, logical link index, assoc/primary UMAC flags, and partner link metadata for already started partner links.

## Association, Station, And MLO State

- STA-mode BSS association uses `ath12k_bss_assoc()`: it finds the AP STA/link, prepares peer assoc, recalculates HE TXBF mode, sends WMI peer assoc, waits for confirmation, sets peer SMPS, sends vdev-up with MBSSID fields, marks `arvif->is_up`, authorizes an already datapath-authorized BSS peer, sends OBSS PD config, and stops 11d scan offload where applicable.
- AP/mesh/adhoc station association uses `ath12k_mac_station_assoc()`: it sends peer assoc, waits for completion, stores bandwidth state, optionally sets fixed VHT/HE/EHT peer rates, configures SMPS, updates legacy-station RTS/CTS protection, and applies UAPSD AP PS params.
- Station lifecycle:
  - `ath12k_mac_station_add()` increments counts, updates the link-sta rhash, creates firmware and datapath peers, sets mesh 4addr if needed, and starts delayed vdevs where required.
  - `ath12k_mac_station_remove()` cancels rate-update work, disassociates/stops STA vdevs, deletes datapath/firmware peer state for non-MLO peers, updates rhashes, and unassigns link STA objects.
  - `ath12k_mac_station_authorize()` and `_unauthorize()` mirror authorization into datapath peer state and WMI peer params; unauthorize also clears keys before mac80211 frees them.
  - `ath12k_mac_handle_link_sta_state()` translates mac80211 station-state transitions to add, remove, assoc, authorize, unauthorize, and disassoc operations.
- `ath12k_mac_op_sta_state()` is the exported mac80211 station-state callback. It creates the common `ath12k_dp_peer`, allocates ML peer IDs, assigns the default link STA, activates selected MLO links before STA association, applies transitions to each valid link, updates active-link state after authorization, and deletes ML/common peers on final removal.
- MLO link selection uses firmware DBS/SBS capability and frequency range tables:
  - `ath12k_mac_freqs_on_same_mac()`, `ath12k_mac_are_sbs_chan()`, and `ath12k_mac_are_dbs_chan()` classify candidate link frequencies.
  - `ath12k_mac_select_links()` keeps the assoc link active and chooses a partner link, preferring SBS then DBS.
  - `ath12k_mac_mlo_sta_update_link_active()` and `ath12k_mac_mlo_sta_set_link_active()` build WMI bitmaps to force inactive links when two links land on the same hardware MAC.
- `ath12k_mac_op_change_sta_links()` allocates and adds newly active MLO link STAs. Link removal is intentionally deferred to full ML STA deletion because firmware lacks per-link STA removal support in this path.

## Scan Flow

- `ath12k_mac_select_scan_device()` picks a radio for a scan channel by frequency and radio range.
- `ath12k_mac_op_hw_scan()` may split one mac80211 scan request across underlying radios; for each radio it calls `ath12k_mac_initiate_hw_scan()`.
- `ath12k_mac_initiate_hw_scan()` chooses an existing link vdev on the target radio or a scan-only link id, creates/recreates a scan vdev when needed, transitions `ar->scan.state` from idle to starting, builds a WMI scan request including SSIDs, extra IEs, and channel list, starts firmware scan, schedules timeout work, and starts 11d scan tracking if required.
- Completion/abort paths are guarded by `ar->data_lock`: `__ath12k_mac_scan_finish()`, `ath12k_scan_stop()`, `ath12k_scan_abort()`, `ath12k_scan_timeout_work()`, and `ath12k_scan_vdev_clean_work()` complete mac80211 scan once all radios finish, delete temporary scan vdevs, and reset scan/ROC state.

## Key Management And Security State

- `ath12k_mac_op_set_key()` handles mac80211 key install/remove. It rejects IGTK offload, bounds WMI key index, applies pairwise keys across all active links for MLO STAs, caches keys for not-yet-created link vdevs, and otherwise delegates to `ath12k_mac_set_key()`.
- `ath12k_install_key()` maps Linux ciphers to WMI ciphers, sets management-IV generation flags for CCMP/GCMP, handles raw-mode IV/tailroom flags, works around STA group-key-before-pairwise firmware ordering by caching GTK, sends `ath12k_wmi_vdev_install_key()`, waits for completion, and updates pairwise/group key ordering state.
- `ath12k_mac_set_key()` verifies peer existence, chooses peer address, sets WMI pairwise/group flags, installs/removes firmware key, configures datapath PN replay detection, and updates `dp_peer->keys`, unicast/multicast key indexes, encryption types, and STA PN type.
- `ath12k_clear_peer_keys()` snapshots peer key pointers under datapath lock, clears peer references, and removes keys from firmware during deauthorization/removal to avoid stale mac80211 key pointers.

## Rate Control, TX Queue, TX Power, And Capability Advertisement

- `ath12k_sta_rc_update_wk()` consumes rate-control deltas staged by `ath12k_mac_op_link_sta_rc_update()`. It updates peer bandwidth, phymode, NSS, SMPS, and supported rates. Bandwidth upgrades send phymode then width, while downgrades send width then phymode to avoid firmware crashes.
- Fixed peer-rate functions set `WMI_PEER_PARAM_FIXED_RATE` for single selected VHT/HE/EHT MCS masks; otherwise peer-assoc is rerun and fixed rate is cleared.
- `ath12k_mac_op_get_txpower()` fetches cached or fresh firmware pdev stats for channel TX power, with fallback to `vif->bss_conf.txpower`.
- `ath12k_mac_conf_tx()` and `ath12k_mac_op_conf_tx()` update WMM AC parameters and STA UAPSD state, caching config for links whose vdev is not created yet.
- Capability construction:
  - `ath12k_create_ht_cap()`, `ath12k_create_vht_cap()`, `ath12k_mac_copy_he_cap()`, and `ath12k_mac_copy_eht_cap()` build mac80211 HT/VHT/HE/EHT capability structures from firmware pdev/band caps and configured chain masks.
  - Mesh filters strip unsupported HE/EHT features for mesh iftype.
  - 6 GHz HE capability, HE/EHT MCS/NSS maps, and PPE thresholds are converted from firmware format into ieee80211 structures.
  - `__ath12k_set_antenna()` updates configured chain masks, sends WMI pdev chain mask params when hardware is on/restarted, refreshes NSS counts, and rebuilds advertised capabilities.

## Management TX Over WMI

- `ath12k_mac_mgmt_tx()` is an exported enqueue path. It refuses crash-flush state, applies probe-response backpressure, enforces queue length, increments `num_pending_mgmt_tx`, and queues `wmi_mgmt_tx_work`.
- `ath12k_mgmt_over_wmi_tx_work()` validates the stored vif/link, finds the link vdev, optionally fills driver-owned action-frame fields, and sends via `ath12k_mac_mgmt_tx_wmi()`. Invalid or inactive vdev cases drop and complete the skb.
- `ath12k_mac_mgmt_tx_wmi()` allocates an IDR buffer id, appends protected management MIC tailroom when needed, DMA maps the skb, and sends WMI management TX. Failures unwind IDR and DMA state.
- `ath12k_mac_tx_mgmt_free()`, `ath12k_mac_tx_mgmt_pending_free()`, `ath12k_mac_vif_txmgmt_idr_remove()`, and `ath12k_mgmt_over_wmi_tx_purge()` clean pending WMI management frames and wake waiters when the pending count reaches zero.
- `ath12k_mac_mgmt_action_frame_fill_elem_data()` fills Radio Measurement link-measurement request/report TX power fields, accounting for protected management frame IV offsets and software-crypto cases.

## Dependencies And Integration Points

- Linux wireless stack: mac80211/cfg80211 channel contexts, link-specific bss/sta objects, scan callbacks, station-state machine, beacon template APIs, TX queue config, bitrate masks, and ML active-link APIs.
- Firmware/WMI: vdev start/stop/up/down/delete, peer create/delete/assoc/params, pdev params, scan start/stop, beacon templates, FILS/probe response templates, OBSS PD/SRG config, BSS color, TWT enable/disable, stats request, key install, management TX, MLO link active commands.
- Datapath: `dp_lock`, `dp_hw->peer_lock`, `ath12k_dp_peer_create/delete/setup`, `ath12k_dp_link_peer_find_by_vdev_and_addr()`, PN replay config, encryption type mapping, RX peer TID cleanup, and peer rhashes.
- Internal synchronization uses wiphy lock assertions for mac80211 callbacks, RCU for link object dereferences, spinlocks for datapath and scan/mgmt state, completions for WMI command confirmation, delayed work and `wiphy_work` for async scan, beacon, rate-control, and management TX processing.

## Risks And Edge Cases

- Many paths rely on lock context (`lockdep_assert_wiphy`, RCU, `data_lock`, `dp_lock`). Missing the expected context can produce stale link pointers or inconsistent peer/key state.
- Several firmware workarounds are order-sensitive: group key caching until pairwise key, peer bandwidth downgrade ordering, 160 MHz NSS ratio overrides, VHT MCS 10/11 masking, and scan cleanup when firmware drops completion events.
- MLO handling is complex and partly constrained by firmware: per-link STA removal is not supported here, active-link selection is limited for multi-device cases, and link/partner metadata depends on started vdev state.
- Scan splitting across multiple radios treats mac80211's request as a single scan and aborts all created scan vdevs if any radio scan fails; cleanup bugs could leak scan link ids or leave scan state non-idle.
- Beacon/MBSSID security inference depends on beacon template contents, non-inheritance elements, and EMA/non-EMA paths. Incorrect parsing can misprogram RSN/WPA flags or beacon protection.
- `ath12k_mac_op_set_key()` returns success after iterating MLO links even if a middle link failed in the loop; it breaks but then returns `0` in the visible code. This is worth review because partial key install across links can desynchronize security state.
- `ath12k_mac_set_hemcsmap()` uses `cap->tx_chain_mask_shift` for some RX map tests visible in this chunk; confirm against later/current upstream code whether that is intentional or should use `rx_chain_mask_shift`.
- The chunk ends while `ath12k_mac_add_p2p_noa_ie()` is still open; P2P NoA handling and later op registration/recovery paths require later chunk reconciliation.

## Test Signals

- mac80211 interface lifecycle tests: add/remove AP, STA, mesh, and MLO vifs; change links; verify vdev create/start/stop/delete counts and firmware command order.
- Association tests: WPA/WPA2/WPA3, open BSS, PMF, MBSSID/EMA, 6 GHz, HE/EHT, MLO multi-link association, roaming between split PHY radios, and legacy non-WME stations.
- Key tests: pairwise-before-group and group-before-pairwise ordering, MLO pairwise key fanout, key removal on deauth, PN replay offload state, IGTK host fallback, raw-mode IV/tailroom behavior.
- Scan tests: single-radio and split-radio scan requests, scan abort, timeout, scan while vdev exists on another radio, 11d interaction, and cleanup of temporary scan links.
- Rate/power tests: fixed VHT/HE/EHT masks, bandwidth upgrade/downgrade RC updates, SMPS changes, TX power stats fallback during CAC or firmware down, antenna chain mask changes and capability refresh.
- Beacon/BSS tests: AP beacon enable/disable, beacon template refresh, CSA/color-change countdown, FILS discovery/unsolicited broadcast probe response, P2P GO beacon IE offload, OBSS PD and BSS color config.
- Management TX tests: queue saturation, probe-response drop threshold, DMA/IDR cleanup on WMI failure, protected action-frame TX power field filling, and pending management frame purge during stop/remove.
