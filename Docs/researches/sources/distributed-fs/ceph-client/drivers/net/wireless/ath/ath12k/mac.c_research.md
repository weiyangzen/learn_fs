# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004746`: lines 1-9394, `Docs/researches/chunks/subset-b-004746_research.md`
- `subset-b-004747`: lines 9395-15241, `Docs/researches/chunks/subset-b-004747_research.md`

## Chunk Research

### subset-b-004746: lines 1-9394

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

### subset-b-004747: lines 9395-15241

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mac.c lines 9395-15241

## Scope

This chunk covers the late `ath12k/mac.c` mac80211 integration code. It starts at the tail of P2P Notice-of-Absence IE insertion, then covers MLO transmit-link address translation, MAC start/stop, rfkill configuration, vdev creation/deletion, interface/channel-context operations, 6 GHz transmit-power-control derivation, bitrate-mask and rate-parameter handling, recovery completion, survey and station statistics, remain-on-channel, channel/rate registration, interface-combination construction, wiphy registration/unregistration, MLO setup/teardown, and hardware allocation/destruction.

The code is executable driver orchestration. It maintains host-side mirrors of firmware objects (`pdev`, `vdev`, peers, DP peers, scan vdevs, MLO links) and translates mac80211/cfg80211 callbacks into WMI, HTT, DP, and regulatory commands.

## Purpose

The covered code completes the ath12k MAC layer by handling:

- per-link transmit address selection for MLO and non-MLO stations;
- radio start/stop sequencing and monitor-status RXDMA filter programming;
- firmware vdev create/delete, including AP self-peers, DP peers, vdev stats IDs, offload encap/decap, STA power-save defaults, monitor vdev bookkeeping, and deferred MLD/link assignment;
- channel-context assignment, unassignment, channel-width/radar/puncturing updates, CSA-safe vdev restart, and remain-on-channel scans;
- 6 GHz TPE/TPC power calculation and WMI TPC programming inputs;
- RTS/fragment/flush callbacks, bitrate masks, fixed-rate or autorate GI/LTF/NSS/LDPC parameters, and peer rate-control refresh;
- exposed station/survey statistics and recovery completion behavior;
- registration-time construction of channels, bands, capabilities, interface combinations, cipher suites, sched-scan/WoW support, MLO capability flags, and mac80211 hardware objects.

## Important APIs, Types, and Functions

- `ath12k_mlo_mcast_update_tx_link_address()` and `ath12k_mac_get_tx_link()` rewrite 802.11 header addresses under RCU for MLO/non-MLO transmit paths. Ethernet-encap frames are left for firmware translation; non-MLO clients use the station default link; ML data/encap frames go to the associated primary link while ML management frames may be translated to a requested link's `link_sta` and `bss_conf` addresses.
- `ath12k_mac_drain_tx()`, `ath12k_mac_start()`, `ath12k_mac_op_start()`, `ath12k_mac_stop()`, and `ath12k_mac_op_stop()` are the core runtime lifecycle. They drain RCU TX paths and WMI management work, set pdev parameters, request PPDU stats, configure monitor status rings, reset counters/maps, publish or clear `ab->pdevs_active[]`, cancel work, purge queued regulatory/channel updates, and move `ath12k_hw::state`.
- `ath12k_mac_rfkill_config()` and `ath12k_mac_rfkill_enable_radio()` encode hardware rfkill GPIO/level policy into `WMI_PDEV_PARAM_HW_RFKILL_CONFIG` and `WMI_PDEV_PARAM_RFKILL_ENABLE`.
- `ath12k_mac_get_vdev_stats_id()`, `ath12k_mac_setup_vdev_params_mbssid()`, and `ath12k_mac_setup_vdev_create_arg()` allocate vdev stats IDs and construct WMI vdev create arguments, including MBSSID/EMA flags, per-band chain counts, and MLD address data for ML vifs.
- `ath12k_mac_update_vif_offload()` and `ath12k_mac_op_update_vif_offload()` map mac80211 offload flags to firmware TX encap/RX decap modes, falling back to raw or native-WiFi as appropriate.
- `ath12k_mac_11d_scan_start()`, `ath12k_mac_11d_scan_stop()`, and `ath12k_mac_11d_scan_stop_all()` drive firmware 11d offload scans only when regulatory state is not user-set and no AP vdev is active.
- `ath12k_mac_vdev_create()` and `ath12k_mac_vdev_delete()` own the firmware vdev lifecycle: vdev ID allocation, queue mapping, WMI create/delete, `ar->arvifs` list membership, AP peer creation/deletion, optional DP peer creation, STA power-save defaults, monitor state, txpower/RTS setup, DP TX attach, IDR cleanup, DP bank-profile release, and host accounting.
- `ath12k_mac_assign_vif_to_vdev()`, `ath12k_mac_op_add_interface()`, and `ath12k_mac_op_remove_interface()` implement deferred vdev creation. `add_interface()` initializes `ath12k_vif` and queue defaults but waits for scan or channel assignment to bind a link to a radio.
- `ath12k_mac_op_add_chanctx()`, `ath12k_mac_op_remove_chanctx()`, `ath12k_mac_vdev_start_restart()`, `ath12k_mac_update_vif_chan()`, `ath12k_mac_op_change_chanctx()`, `ath12k_mac_op_assign_vif_chanctx()`, `ath12k_mac_op_unassign_vif_chanctx()`, and `ath12k_mac_op_switch_vif_chanctx()` translate mac80211 channel contexts into WMI vdev start/restart/stop/up operations.
- `ath12k_mac_fill_reg_tpc_info()` and helpers derive 6 GHz TPC data from channel width, PSD/EIRP regulatory data, TPE elements, power reduction, firmware max allowed power, AP/client power mode, and per-20/40/80/160/320 MHz subchannel limits.
- `ath12k_mac_op_set_rts_threshold()`, `ath12k_mac_op_set_frag_threshold()`, `ath12k_mac_flush()`, `ath12k_mac_wait_tx_complete()`, and `ath12k_mac_op_flush()` expose mac80211 threshold and queue-drain callbacks. Fragmentation is deliberately rejected because known firmware cannot preserve software-fragment semantics.
- `ath12k_mac_op_set_bitrate_mask()` and its helpers validate legacy/HT/VHT/HE/EHT masks, choose fixed-rate versus NSS/rate-control refresh, disable stale peer fixed-rate state, and program WMI vdev NSS, LDPC, SGI, HE/EHT LTF, and autorate GI/LTF parameters.
- `ath12k_mac_op_reconfig_complete()` completes restart recovery, restores current country where needed, updates reset counters/completions, and triggers reconnect for STA vdevs that were up before recovery.
- `ath12k_mac_op_get_survey()`, `ath12k_mac_op_sta_statistics()`, and `ath12k_mac_op_link_sta_statistics()` expose BSS channel survey and station/link metrics from WMI stats and DP peer rate/RSSI/retry accounting.
- `ath12k_mac_op_remain_on_channel()` and `ath12k_mac_op_cancel_remain_on_channel()` create or reuse a scan vdev, start a passive single-channel scan, wait for on-channel notification, and cleanly abort/cancel timeout work.
- `ath12k_mac_setup_channels_rates()`, `ath12k_mac_update_freq_range()`, `ath12k_mac_update_ch_list()`, and `ath12k_mac_update_band()` allocate per-radio supported bands/rates, apply firmware regulatory frequency limits, and merge split-MAC channels into a shared wiphy band.
- `ath12k_mac_setup_iface_combinations()` and helpers build per-radio and global interface-combination limits, including STA/AP/mesh/P2P constraints and multi-radio `wiphy_radio` frequency ranges.
- `ath12k_mac_hw_register()`, `ath12k_mac_register()`, `ath12k_mac_hw_unregister()`, and `ath12k_mac_unregister()` expose ath12k hardware to mac80211 and clean it up. Registration sets wiphy flags/features, cipher suites, queues, offload support, MLO support, sched-scan limits, WoW, regulatory state, debugfs, and error-path cleanup.
- `ath12k_mac_setup()`, `ath12k_mac_hw_allocate()`, `ath12k_mac_allocate()`, `ath12k_mac_destroy()`, and `ath12k_mac_hw_destroy()` allocate `ieee80211_hw`/`ath12k_hw`, bind pdevs to radios, initialize locks/work/completions/lists, preallocate DP resources, and free those mappings.
- `ath12k_mac_mlo_setup()` and `ath12k_mac_mlo_teardown()` send group-wide MLO setup/teardown WMI commands for partner hardware links, skipping teardown during recovery.

## Control Flow

Start flow is `ath12k_mac_op_start()` -> `ath12k_drain_tx()` -> hardware-state transition under `ah->hw_mutex` -> per-radio `ath12k_mac_start()`. Each radio programs pdev defaults, DFS phyerr offload, PPDU stats, mesh multicast, antenna masks, channel list, monitor RX filters, LRO hash configuration, optional idle power save, and finally publishes the pdev in `ab->pdevs_active[]`. On partial failure, earlier radios are stopped.

Stop flow is `ath12k_mac_op_stop()` -> drain TX -> set `ATH12K_HW_STATE_OFF` -> per-radio `ath12k_mac_stop()`. Stop disables monitor RX filtering, clears CAC, cancels scan/regulatory/rfkill/11d work, frees PPDU stats and queued channel-list updates, clears active pdev RCU pointers, synchronizes RCU, and resets pending management TX accounting.

Interface flow is intentionally deferred. `ath12k_mac_op_add_interface()` initializes `ath12k_vif` and determines WMI type/subtype but does not necessarily create a firmware vdev. Later `assign_vif_chanctx()`, `remain_on_channel()`, or scan paths assign a link vif to a radio and call `ath12k_mac_vdev_create()`. This is required for multi-radio wiphys and MLDs because the target radio is not always known at add-interface time.

Vdev create flow allocates a vdev ID from `ab->free_vdev_map`, fills WMI arguments, sends `ath12k_wmi_vdev_create()`, adds the arvif to `ar->arvifs`, programs encap/decap offload and NSS, initializes DP link-vif IDs, creates AP self peers and optional DP peers, configures STA power-save defaults or monitor flags, recalculates txpower, programs RTS threshold, and attaches DP TX. Error paths unwind peer, DP peer, WMI vdev, maps, stats ID, list membership, and monitor flags.

Channel-context flow starts or restarts the vdev on `ctx->def`, downgrades EHT phymode if the iftype lacks EHT capability, supplies MBSSID/MLO partner arguments, marks DFS CAC when applicable, sends 6 GHz TPC power after start, and configures TX beamforming. Channel-width/radar/puncturing changes iterate active interfaces on the affected radio, restart/up vdevs, update peer puncturing width for STA vdevs, and defer AP `vdev_up` during CSA until new beacon templates are available.

Bitrate-mask flow first identifies whether the mask represents one legacy rate, a single NSS across HT/VHT/HE/EHT, or more complex fixed/range settings. It rejects unsupported SGI and unsupported multiple arbitrary MCS values, validates fixed HE/VHT/EHT NSS compatibility against peers, updates `arvif->bitrate_mask`, queues station rate-control work, disables old peer fixed rates, and then programs vdev rate/NSS/GI/LTF/LDPC parameters.

Registration flow is group-oriented. `ath12k_mac_allocate()` groups pdevs into one wiphy when MLO is capable, otherwise one radio per wiphy. `ath12k_mac_hw_register()` then sets up all radios in an `ath12k_hw`, merges supported bands into `wiphy->bands`, builds interface combinations, sets feature flags, initializes regulatory/WoW/debugfs state, registers with mac80211, and applies initial regulatory updates. Unregistration reverses debugfs/stats, unregisters mac80211, frees channel arrays, and releases interface-combination allocations.

## State and Persistence Behavior

Long-lived state is split across:

- `struct ath12k_hw`: `state`, `hw_mutex`, radio array, DP peer list, and the mac80211 `ieee80211_hw` object.
- `struct ath12k`: pdev/radio identity, WMI pointer, chain masks, vdev/peer counters, `allocated_vdev_map`, monitor vdev state, scan state, 11d state, regulatory update work/queues, survey/RSSI state, management TX IDR/queue, completions, and `arvifs` list.
- `struct ath12k_vif` and `struct ath12k_link_vif`: vdev type/subtype, link map, vdev ID, BSSID, txpower, bitrate mask, rekey data, MBSSID/MLO/link state, cached configuration, DP link-vif data, and vdev started/up/created flags.
- `struct ath12k_sta` and `struct ath12k_link_sta`: per-link station identity, rate-control update work, RSSI/beacon stats, and link mapping used by MLO TX translation and statistics.
- `struct ath12k_base` / `ath12k_hw_group`: global vdev maps, vdev stats ID map, regulatory frequency ranges, hardware params/service bits, MLO group topology, reset/recovery counters, and active pdev RCU table.

Firmware-persistent state includes WMI pdev params, vdevs, peers, AP self-peers, MBSSID/EMA mode, MLO setup groups, scan/ROC operations, TPC power tables, rate/NSS/GI/LTF params, rfkill config, 11d scans, monitor-status filters, and sched-scan/WoW support.

Locking is explicit. mac80211 callbacks assert `lockdep_assert_wiphy()`. Hardware start/stop also require `ah->hw_mutex`. RCU protects `vif->link_conf[]`, `sta->link[]`, and `ab->pdevs_active[]`. `ar->data_lock` protects lists, scan/rx-channel state, and queued regulatory updates. DP locks protect TX descriptors and DP peer lists. Completion objects synchronize vdev delete/setup, MLO setup, scan, survey, peer/key operations, and regulatory/current-country updates.

## Dependencies and Integration Points

This code integrates with mac80211/cfg80211 through `ieee80211_hw`, `wiphy`, `ieee80211_vif`, `ieee80211_bss_conf`, `ieee80211_sta`, channel contexts, scan/ROC callbacks, survey/statistics structures, bitrate masks, interface combinations, wiphy radio ranges, and registration/unregistration APIs.

Internal ath12k dependencies include WMI command helpers for pdev/vdev/peer/scan/MLO/rfkill/TPC/11d/current-country operations, HTT/DP helpers for RX filter setup, PPDU stats, TX flushing, DP peer creation/deletion, DP link-vif setup, peer rate/RSSI stats, firmware stats requests, regulatory helpers, WoW setup, debugfs, and hardware-group mapping.

Firmware capability and hardware-parameter bits heavily shape behavior. Important gates include `WMI_TLV_SERVICE_MBSS_PARAM_IN_VDEV_START_SUPPORT`, `WMI_TLV_SERVICE_11D_OFFLOAD`, `WMI_TLV_SERVICE_ETH_OFFLOAD`, `WMI_TLV_SERVICE_BSS_CHANNEL_INFO_64`, `WMI_TLV_SERVICE_BSS_COLOR_OFFLOAD`, `WMI_TLV_SERVICE_BEACON_PROTECTION_SUPPORT`, `WMI_TLV_SERVICE_NLO`, `WMI_TLV_SERVICE_STA_KEEP_ALIVE`, `WMI_TLV_SERVICE_HW_DB2DBM_CONVERSION_SUPPORT`, plus `hw_params` such as `rxdma1_enable`, `num_rxdma_per_pdev`, `idle_ps`, `supports_monitor`, `single_pdev_only`, `vdev_start_delay`, `current_cc_support`, and `supports_dynamic_smps_6ghz`.

## Risks and Edge Cases

- The chunk has many cross-object accounting invariants: `free_vdev_map`, `allocated_vdev_map`, `free_vdev_stats_id_map`, `num_created_vdevs`, `num_started_vdevs`, AP self-peers, DP peers, and `ar->arvifs` must unwind consistently on every failure path.
- Deferred vdev creation means configuration can arrive before firmware vdev existence. The cache flush path must replay queued TX/BSS/key configuration exactly once when a link is finally created.
- MLO address translation is sensitive to RCU validity of `bss_conf` and `link_sta`; wrong link choice or missing translation can transmit frames with MLD addresses where link addresses are required.
- Channel switching and CSA paths must avoid stale beacon templates. This code explicitly skips `vdev_up` for AP CSA until beacon contents are updated later.
- 6 GHz TPC math mixes PSD/EIRP regulatory values, TPE values, local power constraint, firmware max power, and idle-PS behavior. Off-by-one channel center-frequency calculations or incorrect PSD/EIRP conversion can violate regulatory limits.
- `ath12k_mac_validate_fixed_rate_settings()` scans DP peers by link ID and may reject or warn on missing link station state. Fixed-rate behavior across legacy/HT/VHT/HE/EHT remains constrained by firmware command expressiveness.
- Monitor support is advertised as `NO_VIRTUAL_MONITOR` while an internal monitor vdev may still be created; user-visible monitor mode may be briefly enabled until after `ieee80211_register_hw()` when unsupported hardware clears it.
- `ath12k_mac_update_band()` assumes same-index channel arrays when merging split MAC bands. Any upstream channel table shape change can break the enabled/disabled merge assumption.
- Error unwind in MLO setup uses loop indexes from nested loops; partial setup teardown must be reviewed carefully if group/radio iteration changes.
- Recovery completion triggers STA disconnects for PN safety. Changes here affect user-visible reconnection behavior after firmware restart.
- Fragmentation is deliberately unsupported. Enabling it without firmware support would produce unreassemblable frames because firmware clears the "more fragments" bit.

## Test and Validation Signals

Useful validation for this chunk should include:

- build coverage with mac80211, cfg80211, mesh, WoW, debugfs, 6 GHz, MLO, monitor support, and raw/Ethernet offload options varied;
- start/stop/restart tests for single-radio, multi-radio, and MLO-capable groups, including partial WMI failure injection and recovery completion;
- add/remove interface tests for STA, AP, mesh, monitor, P2P client/GO/device, MLD links, scan-created vdevs, and channel reassignment across radios;
- vdev failure-path tests for WMI create/delete timeout, AP peer create/delete failure, DP peer failure, NSS/RTS/txpower programming failure, and stats-ID/vdev-map cleanup;
- 11d/regulatory tests covering user-set regdom, AP-active suppression, 11d scan start/stop, current country restore, split-MAC band merging, disabled-channel handling, and cfg80211 regulatory hints after registration;
- channel-context tests for assign/unassign, same-radio switch, cross-radio switch rejection, width/radar/puncturing updates, DFS CAC flag handling, CSA beacon-template deferral, and monitor restart after channel changes;
- 6 GHz TPC tests for PSD and non-PSD channels, TPE present/absent, LPI AP mode, STA client power types, 20/40/80/160/320 MHz widths, local power constraints, and idle-PS firmware max-power comparison;
- bitrate-mask tests for single legacy rates, single NSS masks, unsupported forced SGI, invalid VHT/HE/EHT multi-MCS masks, peer NSS incompatibility, GI/LTF fixed and autorate modes, and peer fixed-rate disable/reassociation work;
- ROC/scan tests for scan-vdev reuse, cross-radio scan-vdev recreation, on-channel timeout, cancel path, timeout work, and remove-interface while scan abort is in progress;
- statistics tests for survey while scanning, disabled channel survey, BSS channel info timeout, DB2DBM conversion, per-chain RSSI stats, link station stats, retry/failure counters, and fallback to firmware beacon RSSI;
- registration/unregistration tests for interface combinations, `wiphy->radio` ranges, monitor-disabled race, cipher suite exposure, sched-scan limits, MLO capability flags, WoW initialization failure, and all cleanup labels.

## Cross-Chunk Notes

Earlier chunks define most helpers used here: beacon/probe template handling, key install, peer association, scan completion, TX submission, station state, capability construction, and rate-count helpers. This chunk supplies the late lifecycle, registration, and allocation machinery that ties those helpers into mac80211. The merge lane should keep this report under the source-tree-aligned path for `drivers/net/wireless/ath/ath12k/mac.c` and combine it with earlier chunks before drawing file-wide conclusions.
