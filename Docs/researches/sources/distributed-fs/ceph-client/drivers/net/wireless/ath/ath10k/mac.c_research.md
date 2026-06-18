# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004719`: lines 1-10094, `Docs/researches/chunks/subset-b-004719_research.md`
- `subset-b-004720`: lines 10095-10380, `Docs/researches/chunks/subset-b-004720_research.md`

## Chunk Research

### subset-b-004719: lines 1-10094

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.c lines 1-10094

## Scope

This chunk covers the ath10k mac80211/cfg80211 integration layer from the top of `mac.c` through the early `ath10k_mac_register()` capability setup. It includes rate tables, SAR capability declarations, crypto/key handling, channel/vdev/monitor/radar lifecycle, beacon and probe-response template programming, station association state, regulatory updates, TX and scan paths, mac80211 operation callbacks, TID/rate-control configuration, channel-context handling, station statistics, interface-combination tables, ACPI WRDD regulatory hints, and the start of wireless hardware registration.

The source file is executable driver code, not a generated ABI header. Most behavior is host-side orchestration around firmware WMI/HTT commands and mac80211 callbacks, with local state in `struct ath10k`, `struct ath10k_vif`, `struct ath10k_sta`, and `struct ath10k_peer`. The requested range stops at line 10094, immediately after setting core wiphy feature flags; the remainder of `ath10k_mac_register()` and `ath10k_mac_unregister()` are outside this chunk and should be reconciled by a later/adjacent chunk.

## Purpose

`mac.c` is the central bridge between the Linux 802.11 stack and ath10k firmware. It translates mac80211 operations into WMI control commands and HTT data-path submissions, maintains host mirrors of firmware resources, and exposes device capabilities to cfg80211.

The covered code is responsible for:

- exposing 2.4 GHz and 5 GHz rates/channels, HT/VHT capabilities, SAR ranges, interface modes, and mac80211 operation callbacks;
- creating, starting, stopping, restarting, and deleting firmware virtual devices (`vdevs`) for STA/AP/IBSS/mesh/P2P/monitor roles;
- creating/deleting firmware peers and associating them with mac80211 station state, rate capabilities, QoS, SMPS, TDLS, WEP/static-key state, and per-TID policy;
- sending data, management, and off-channel frames through the correct HTT or WMI path for firmware revision and frame mode;
- managing scans and remain-on-channel operations through a shared WMI scan state machine;
- updating regulatory/channel lists, DFS/radar CAC monitor state, channel contexts, BSS survey data, and transmit power/SAR constraints.

## Important APIs, Types, and Data

### Rates, Channels, and Capabilities

The file starts with legacy rate tables (`ath10k_rates`, `ath10k_rates_rev2`) and helpers for CCK/OFDM mapping: `ath10k_mac_bitrate_is_cck()`, `ath10k_mac_bitrate_to_rate()`, `ath10k_mac_hw_rate_to_idx()`, `ath10k_mac_bitrate_to_idx()`, and `ath10k_mac_get_rate_hw_value()` around lines 36-179. These convert between mac80211 bitrate indexes and WMI/firmware rate encodings.

HT/VHT support is derived from firmware capability fields in `ath10k_get_ht_cap()`, `ath10k_create_vht_cap()`, and `ath10k_mac_setup_ht_vht_cap()` around lines 4860-5035. The code adjusts beamforming, STBC, LDPC, MCS maps, 160/80+80 highest-rate hints, and chainmask-dependent NSS. Static channel arrays (`ath10k_2ghz_channels`, `ath10k_5ghz_channels`) and interface-combination tables appear near lines 9532-9838.

SAR support is declared by `ath10k_sar_freq_ranges` and `ath10k_sar_capa` near lines 88-97, then applied through `ath10k_mac_set_sar_specs()` and `ath10k_mac_set_sar_power()` around lines 3021-3083.

### Crypto and Peer Key State

The crypto section maps mac80211 ciphers to WMI key ciphers in `ath10k_send_key()` and waits for firmware completion in `ath10k_install_key()` around lines 239-332. `ath10k_set_key()` around lines 6560-6713 is the mac80211 callback. It selects peer address, handles software-only BIP ciphers, validates key indexes, caches WEP keys, installs/deletes firmware keys, records `peer->keys[]`, and authorizes TDLS/pairwise peers after key installation.

Static WEP receives special handling: `ath10k_install_peer_wep_keys()`, `ath10k_clear_peer_keys()`, `ath10k_clear_vdev_key()`, `ath10k_mac_vif_update_wep_key()`, and `ath10k_set_default_unicast_key()` maintain both vdev-level and peer-level WEP key mirrors. The code installs WEP as pairwise and/or group depending on AP/IBSS/STA semantics and uses `def_keyid` WMI vdev parameters as a firmware workaround.

### Vdev, Interface, Beacon, and Monitor Lifecycle

General vdev synchronization uses `ath10k_vdev_setup_sync()` and `ath10k_vdev_delete_sync()` around lines 1017-1052, waiting on WMI completion objects unless crash/restart state short-circuits. `ath10k_vdev_start_restart()`, `ath10k_vdev_start()`, `ath10k_vdev_restart()`, and `ath10k_vdev_stop()` build WMI channel arguments, issue start/restart/stop commands, update `num_started_vdevs`, and recalculate radar state.

`ath10k_add_interface()` around lines 5556-5919 maps mac80211 interface types to WMI vdev type/subtype, allocates vdev IDs from `free_vdev_map`, initializes `struct ath10k_vif`, sets TX queues to the vdev ID, allocates long-lived beacon buffers for AP/IBSS/mesh, creates WMI vdevs and AP/IBSS self-peers, configures keepalive, NSS, power-save parameters, TX beamforming, RTS threshold, TX power, FTM responder, and monitor state. `ath10k_remove_interface()` around lines 5929-6037 tears these down, deletes peers/vdevs, cleans beacon DMA memory late, clears stale peer-map references, unlocks TX queues, and recalculates monitor and TX power.

Beacon offload handling is centered on `ath10k_mac_setup_bcn_tmpl()`, `ath10k_mac_setup_prb_tmpl()`, `ath10k_control_beaconing()`, and `ath10k_mac_vif_fix_hidden_ssid()` around lines 1589-1854. The code obtains templates from mac80211, optionally splits P2P IEs into firmware-managed WMI state, removes duplicate vendor IEs, restarts AP vdevs for hidden SSID correctness, and frees/unmaps beacon SKBs and persistent beacon buffers under `data_lock`.

Monitor support uses a separate monitor vdev when needed by promisc filters, mesh broadcast limitations, or DFS CAC. `ath10k_monitor_recalc()` decides whether to create/start/stop/delete monitor vdevs, and `ath10k_start_cac()`, `ath10k_stop_cac()`, and `ath10k_recalc_radar_detection()` use monitor state for radar/CAC when DFS is enabled.

### Station, Association, TDLS, TID, and Rate Control

Peer creation/deletion is managed by `ath10k_peer_create()`, `ath10k_peer_delete()`, `ath10k_peer_cleanup()`, and `ath10k_peer_cleanup_all()` around lines 735-917. Host state includes `ar->peers`, `ar->peer_map[]`, `ar->num_peers`, `ar->num_stations`, peer station/vif pointers, and peer key arrays. Several cleanup paths intentionally scan for stale peer-map references because firmware events may be missing or delayed.

Association helpers (`ath10k_peer_assoc_h_basic()`, `_crypto()`, `_rates()`, `_ht()`, `_vht()`, `_qos()`, `_phymode()`) populate `struct wmi_peer_assoc_complete_arg` from mac80211 station capabilities, local bitrate masks, QoS/UAPSD state, SMPS, VHT NSS, and firmware peer flags. `ath10k_bss_assoc()` handles STA association to an AP, while `ath10k_station_assoc()` handles AP/mesh/IBSS/TDLS peers. `ath10k_sta_state()` maps mac80211 station state transitions to peer creation, TDLS firmware state, association, disassociation, peer deletion, debug TX stats allocation, and TXQ cleanup.

Per-TID configuration support is implemented in `ath10k_mac_parse_tid_config()`, `ath10k_mac_set_tid_config()`, `ath10k_mac_reset_tid_config()`, `ath10k_sta_tid_cfg_wk()`, `ath10k_mac_op_set_tid_config()`, and `ath10k_mac_op_reset_tid_config()` around lines 6915-7479 and 9401-9470. VIF-level defaults are cached in `arvif` arrays and asynchronously pushed to stations unless station-specific overrides exist. No-ACK, retry count, AMPDU, fixed/limited rate, and RTS/CTS controls interact; no-ACK suppresses aggregation/rate/retry settings in several branches.

Bitrate-mask handling is split between vdev fixed-rate parameters and station updates. `ath10k_mac_op_set_bitrate_mask()` validates single-rate/single-NSS masks, handles firmware's limited VHT MCS-mask expression, optionally uses peer fixed rate for single VHT rates, updates `arvif->bitrate_mask`, and queues station re-association/rate-update work.

### TX, Scan, and Channel Context Paths

Transmit handling chooses an HTT/WMI path with `ath10k_mac_tx_h_get_txmode()` and `ath10k_mac_tx_h_get_txpath()` around lines 3737-4017. Data can be native Wi-Fi, Ethernet, raw, or management mode. The code works around firmware-specific NullFunc status issues, TDLS key selection bugs, raw-mode requirements, and WMI management TX availability. `ath10k_mac_tx()` consumes SKBs, transforms headers, queues off-channel frames when needed, and submits via HTT or WMI. TXQ push mode uses `ath10k_mac_tx_push_txq()`, `ath10k_mac_schedule_txq()`, and `ath10k_mac_tx_push_pending()` with pending-count accounting, per-TXQ airtime estimates, and mac80211 TXQ scheduling.

Off-channel and WMI management work queues (`ath10k_offchan_tx_work()`, `ath10k_mgmt_over_wmi_tx_work()`) serialize special transmissions. Off-channel TX may create a temporary peer on the scan vdev for older firmware, waits for completion, and deletes the temporary peer afterward. WMI management TX may DMA-map management frames by reference if firmware advertises that feature.

Scanning and remain-on-channel share `ar->scan` state and WMI scan commands. `ath10k_hw_scan()` initializes `ATH10K_SCAN_STARTING`, builds `wmi_start_scan_arg`, copies SSIDs/IE/channels/random MAC, computes timeout, starts scan, and schedules a timeout worker. `ath10k_remain_on_channel()` starts a single-channel passive scan with ROC flags and waits for `scan.on_channel`. `ath10k_scan_stop()`, `ath10k_scan_abort()`, `__ath10k_scan_finish()`, and `ath10k_scan_timeout_work()` handle completion, abort, timeout cleanup, mac80211 callbacks, and off-channel TX purge.

Channel context callbacks (`ath10k_mac_op_add_chanctx()`, `remove_chanctx()`, `change_chanctx()`, `assign_vif_chanctx()`, `unassign_vif_chanctx()`, `switch_vif_chanctx()`) around lines 8703-9120 keep `ar->rx_channel` optimized for single-channel operation, start/stop vdevs as contexts are assigned/unassigned, and perform channel switches by downing affected vdevs, updating `rx_channel`, reinstalling beacon/probe templates, restarting vdevs, and bringing them back up.

### Registration and mac80211 Ops

`ath10k_ops` around lines 9472-9530 is the main integration surface for mac80211. It wires callbacks for TX, TXQ wake, start/stop/config, add/remove interface, BSS changes, coverage class, scanning, keys, station state, TX power, WMM/UAPSD, remain-on-channel, thresholds, flush, antenna, restart completion, survey, bitrate mask, rate-control updates, TSF offset, AMPDU policy, ethtool stats, channel contexts, station pre-RCU removal, station statistics, TID config, testmode, WoW suspend/resume, debugfs station setup, and SAR.

`ath10k_mac_create()`/`ath10k_mac_destroy()` allocate/free `ieee80211_hw` with a per-instance copy of `ath10k_ops`, allowing registration to disable unsupported callbacks later. `ath10k_mac_register()` begins by validating/generating the MAC address, copying channel arrays into `ar->mac.sbands`, setting bands/rates, reading OF frequency limits, setting HT/VHT caps, exposing interface modes/P2P support, and enabling mac80211 hardware flags such as signal reporting, power save, MFP, TX ACK status, rate control, AP link PS, spectrum management, fast TX, connection monitor, per-station GTK, monitor vif, channel-context STA CSA, queue control, TX fragmentation, low-ACK reporting, SW crypto control, and `NL80211_FEATURE_STATIC_SMPS`.

## Control Flow

The main runtime flow starts when mac80211 calls `.start`. `ath10k_start()` drains any old TX work, transitions device state, powers up HIF, starts core firmware, configures rfkill, PMF QoS, dynamic bandwidth, probe-request OUI, adaptive QCS/CCA, burst/idle PS, antenna masks, ARP AC override, ANI, peer-stat period, BT coexistence, optional BB timing from device tree, regulatory state, spectral scanning, thermal throttling, and radar confirmation. Failure paths unwind core/HIF and restore state to OFF.

Interface bring-up is: mac80211 `.add_interface` creates a WMI vdev and host `arvif`, `.assign_vif_chanctx` starts that vdev on a channel, BSS changes install beacon/probe templates and bring AP/IBSS vdevs up, or STA association calls `ath10k_bss_assoc()` to WMI-associate the AP peer and bring the STA vdev up. Station transitions create firmware peers before association and delete them after disassociation/removal.

Transmit flow is: mac80211 calls `.tx` or `.wake_tx_queue`; ath10k fills SKB control metadata, picks frame mode and path, increments HTT pending counters where needed, transforms headers for native-wifi or Ethernet firmware expectations, optionally queues off-channel frames, then submits to HTT data TX, HTT management TX, or WMI management TX. Completion events elsewhere decrement pending counters and wake waiters/queues.

Scan flow is: check no active TDLS peer on the vif, transition `ar->scan.state` from IDLE to STARTING, issue WMI start scan, wait for scan-start event, then rely on firmware scan completion or timeout/abort cleanup to call mac80211 scan/ROC completion APIs and reset state.

Channel switch flow is: stop monitor if active, bring relevant vdevs down, update the host RX-channel shortcut, reinstall firmware offload templates, WMI restart each vdev on the new channel definition, WMI up each vdev again, then recalculate monitor/radar handling.

Device stop/restart flow drains TX, halts firmware unless already in restart handling, finishes scans, cleans peers/beacons/radar state, stops core/HIF, cancels workers, and later `ath10k_reconfig_complete()` moves RESTARTED back to ON and wakes queues.

## State and Persistence Behavior

Persistent host state is concentrated in `struct ath10k` and per-vif/per-station private structures:

- `ar->state`, `dev_flags`, `free_vdev_map`, `num_started_vdevs`, `num_peers`, `num_stations`, `max_*` limits, `tx_paused`, scan state, monitor flags, regulatory state, tx power/SAR limits, `rx_channel`, peer maps, and survey/statistic caches;
- `arvif->vdev_id`, WMI type/subtype, `is_started`, `is_up`, `bssid`, `aid`, beacon/SSID/DTIM settings, power-save/UAPSD settings, WEP key cache, bitrate/TID config arrays, no-ack/retry/AMPDU/rate/RTSCTS caches, txpower, and beacon DMA buffer state;
- `arsta->arvif`, peer ID, pending RC/TID work, per-station TID overrides, peer stats, last rate, tx retry/failure stats, and cached unicast cipher;
- `peer->vif`, `peer->sta`, `peer->keys[]`, `peer_ids`, `removed`, and list/map membership.

Firmware state persists separately in WMI objects: vdevs, peers, peer association state, keys, scan operations, channel lists, pdev/vdev parameters, beacon/probe templates, per-peer/per-TID config, rfkill, ANI, TXBF, BT coexistence, and pktlog/peer stats. The host generally treats firmware as authoritative for command completion but keeps local mirrors for fast lookup and teardown recovery.

Locking is intentional and mixed: `conf_mutex` serializes sleeping WMI/mac80211 lifecycle operations; `data_lock` protects peer maps, scan state, beacon pointers, stats, and `rx_channel`; `htt.tx_lock` protects TX pending/paused state; workqueues are used to avoid sleeping under atomic mac80211 callbacks or RCU sections.

## Dependencies and Integration Points

This file depends on Linux mac80211/cfg80211 APIs for `ieee80211_ops`, `ieee80211_hw`, `ieee80211_vif`, station state, TXQ scheduling, scan/ROC callbacks, channel contexts, rate masks, BSS info, regulatory requests, SAR specs, and survey/station info.

Internal ath10k dependencies include:

- `mac.h` for ath10k MAC declarations, private driver structures, and helper prototypes;
- `core.h` for `struct ath10k`, firmware feature flags, hw params, device state, channel counts, and restart/core APIs;
- `wmi.h`, `wmi-tlv.h`, and `wmi-ops.h` for WMI command arguments, service bits, pdev/vdev/peer params, scan commands, vdev/peer/key lifecycle, regulatory, rfkill, TDLS, stats, and TID configuration;
- `htt.h` and `txrx.h` for HTT TX modes, pending counters, TX queues, peer IDs, and TX completion state;
- `debug.h`, `testmode.h`, `wow.h`, and `leds.h` for stats/debugfs/testmode/WoW callback integration and ancillary device features;
- common Atheros regulatory helpers (`ath_reg_notifier_apply`, `ath_regd_init`, `ath_regd_find_country_by_name`) and optional DFS detector hooks.

Firmware capability bits drive many branches. Examples include WMI services for beacon offload, WMI management TX, sync delete commands, STA keepalive, TX mode dynamic, peer TID config, extended peer TID config, TDLS, mesh 11s, SAR, BSS channel info, PNO/sched scan registration later in the function, and per-chip feature bits such as raw mode, no P2P, no PS, peer fixed rate, MFP support, BT coexistence, and restart-disconnect behavior.

## Risks and Edge Cases

- Vdev/peer accounting must stay consistent with firmware events. The code has multiple stale-peer cleanup paths, which indicates real firmware/event-loss risk; incorrect `num_peers` or `peer_map` updates can block new interfaces or leave dangling station references.
- WEP handling is intricate and firmware-specific. Static WEP keys may be installed as both pairwise and group, copied to peers after association, cleared incrementally without holding `data_lock` across sleeping calls, and reselected through `def_keyid`.
- Scan state is shared between ordinary scans and ROC. Missing firmware completion events are handled by timeout/cleanup, but wrong state transitions can double-complete mac80211 scan/ROC notifications or leave off-channel TX queued.
- Monitor vdev creation is a workaround for filters, mesh broadcast, and DFS CAC. It is intentionally stopped around association and channel switching because some firmware revisions crash with monitor vdev combinations.
- Beacon offload has DMA lifetime risk. The code allocates per-vif coherent buffers for AP/IBSS/mesh because firmware may reuse beacon memory without host-visible completion; freeing or reusing buffers too early can leak or transmit stale memory.
- TX path selection is firmware-version-sensitive. NullFunc management TX, TDLS Ethernet mode, raw-mode software crypto, WMI management-by-reference, and off-channel temporary peers are all compatibility workarounds.
- Per-TID config interactions are easy to regress. No-ACK suppresses retry/AMPDU/rate changes, VIF-level config is later replayed to stations, and station-specific overrides must win over VIF defaults.
- Rate-mask support is constrained by firmware. Arbitrary VHT masks are rejected unless peer fixed-rate support can cover a single VHT rate; HT/VHT NSS validation must match peer capabilities.
- `ath10k_mac_update_rx_channel()` optimizes for single-channel operation and falls back to NULL in multi-channel cases; receive status code must handle NULL correctly.
- Regulatory and DFS behavior relies on both cfg80211 state and firmware channel lists. DFS radar channels are forced passive for scanning because firmware may otherwise actively probe radar channels.
- Several operations are intentionally best-effort or tolerate `-EOPNOTSUPP`. Treating those as hard failures in future edits could break older firmware branches.
- The requested chunk ends inside `ath10k_mac_register()`, so any final conclusions about registration error paths, remaining feature flags, cipher suite counts, regulatory init, and unregister cleanup require the tail chunk.

## Test and Validation Signals

Useful validation for this chunk is mostly integration and regression oriented:

- build coverage for ath10k with `CONFIG_ATH10K`, `CONFIG_MAC80211`, mesh, DFS-certified, PM/WoW, debugfs, and testmode options varied;
- mac80211 smoke tests for start/stop, add/remove STA/AP/mesh/IBSS/P2P/monitor interfaces, channel assignment/unassignment, channel switch, and firmware restart recovery;
- association tests for STA-to-AP, AP station add/remove, TDLS peer lifecycle, legacy non-WMM station handling, SMPS/NSS/bandwidth RC updates, and peer cleanup after failed WMI commands;
- crypto tests for CCMP/TKIP/GCMP/CCMP-256 hardware ciphers, software-only BIP ciphers, raw-mode software crypto, static WEP STA/AP/IBSS, default WEP key changes, and key deletion on missing peers;
- scan/ROC tests covering active/passive scans, random MAC scan, scan duration timeouts, abort races, TDLS-busy rejection, remain-on-channel expiry/cancel, and off-channel management TX completion;
- TX tests for direct TX and TXQ push mode, management-over-WMI, management-by-reference DMA mapping, off-channel temporary-peer TX, raw/native-wifi/Ethernet encapsulation, P2P NoA IE injection, no-ack TID TX flags, and queue pause/unpause;
- regulatory/DFS tests for reg notifier channel-list updates, DFS CAC monitor start/stop, radar-detected fallback on CAC start failure, passive scanning on radar channels, and WRDD ACPI regulatory hints;
- feature/capability tests for antenna chainmask changes, HT/VHT capability derivation, SAR limits under connected/disconnected state, per-vif TX power minimum selection, bitrate-mask rejection/fixed-rate application, and per-TID set/reset behavior;
- fault-injection tests for WMI command failures and missing completions: vdev start/stop/delete, peer create/delete, scan start/stop, key install, beacon/probe template install, peer stats request, BSS survey request, and pktlog enable.

## Cross-Chunk Notes

This chunk is the primary body of `ath10k/mac.c`, but it is not the entire file. Lines after 10094 continue `ath10k_mac_register()` with additional wiphy features, sched-scan and WoW setup, interface-combination selection, SAR assignment, regulatory init, cipher-suite exposure, `ieee80211_register_hw()`, error cleanup, and `ath10k_mac_unregister()`. The merge lane should combine this chunk with the tail chunk before producing a final per-file report and should keep the report aligned under the source tree path `drivers/net/wireless/ath/ath10k/mac.c`.

### subset-b-004720: lines 10095-10380

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.c lines 10095-10380

## Scope And Purpose

This chunk is the final registration and unregister section of the ath10k mac80211 glue in `mac.c`. It completes `ath10k_mac_register()` by advertising firmware- and hardware-dependent `wiphy`/`ieee80211_hw` capabilities to cfg80211/mac80211, deriving regulatory state, registering the device with mac80211, and defining the unwind path for late registration failures. It also contains `ath10k_mac_unregister()`, the matching teardown entry point used by the core unregister path.

The code is not a packet-processing path. Its main job is to translate already-discovered ath10k state (`struct ath10k`, firmware feature bits, WMI service map, hardware parameters, channel/rate allocations prepared earlier in `ath10k_mac_register()`) into the public Linux wireless capability surface. After `ieee80211_register_hw()`, userspace and mac80211 can create interfaces, schedule scans, use WoWLAN, TDLS, airtime fairness, TID configuration, regulatory hints, and other features according to these advertised flags.

## Important APIs, Types, And Constants

- `int ath10k_mac_register(struct ath10k *ar)` is the registration function being completed. Earlier lines allocate 2 GHz/5 GHz channel arrays, fill supported bands, set base interface modes, antenna masks, and core `ieee80211_hw` flags. This chunk finishes feature advertisement and calls `ieee80211_register_hw()`.
- `void ath10k_mac_unregister(struct ath10k *ar)` is the public teardown function declared in `mac.h` and called from `core.c` both on registration unwind and normal core unregister.
- `struct ath10k` carries the persistent driver state: `ar->hw` points to `struct ieee80211_hw`; `ar->hw->wiphy` is the cfg80211-visible radio; `ar->wmi.svc_map` and `ar->running_fw->fw_file` describe firmware services/version; `ar->hw_params` contains chip-family capabilities; `ar->mac.sbands[]` owns dynamically duplicated channel arrays.
- `struct ath10k_vif`, `struct ath10k_sta`, and `struct ath10k_txq` are exposed to mac80211 by setting `ar->hw->vif_data_size`, `sta_data_size`, and `txq_data_size`. This lets mac80211 allocate driver-private storage for each virtual interface, station, and TXQ.
- cfg80211/mac80211 flags used here include `WIPHY_FLAG_IBSS_RSN`, `WIPHY_FLAG_AP_PROBE_RESP_OFFLOAD`, `WIPHY_FLAG_SUPPORTS_TDLS`, `WIPHY_FLAG_HAS_REMAIN_ON_CHANNEL`, `WIPHY_FLAG_HAS_CHANNEL_SWITCH`, `WIPHY_FLAG_AP_UAPSD`, `NL80211_FEATURE_*`, `NL80211_EXT_FEATURE_*`, and `ieee80211_hw_set()` capability bits.
- WMI service bits gate firmware-dependent features: `WMI_SERVICE_NLO`, `BEACON_OFFLOAD`, `TDLS`, `TDLS_EXPLICIT_MODE_ONLY`, `TDLS_WIDER_BANDWIDTH`, `TDLS_UAPSD_BUFFER_STA`, `TX_DATA_ACK_RSSI`, `HTT_MGMT_TX_COMP_VALID_FLAGS`, `REPORT_AIRTIME`, `RTT_RESPONDER_ROLE`, `TX_PWR_PER_PEER`, `PEER_TID_CONFIGS_SUPPORT`, `EXT_PEER_TID_CONFIGS_SUPPORT`, `ADAPTIVE_OCS`, `VDEV_DIFFERENT_BEACON_INTERVAL_SUPPORT`, `SPOOF_MAC_SUPPORT`, and `PER_PACKET_SW_ENCRYPT`.
- The interface-combination tables selected here (`ath10k_if_comb`, `ath10k_tlv_if_comb`, `ath10k_tlv_qcs_if_comb`, `ath10k_10x_if_comb`, `ath10k_10_4_if_comb`, `ath10k_10_4_bcn_int_if_comb`) are defined just above this chunk and constrain how many station/AP/P2P/mesh/IBSS virtual interfaces mac80211 may create.
- `ath10k_wow_init()`, `dfs_pattern_detector_init()`, `ath10k_mac_init_rd()`, `ath_regd_init()`, `ieee80211_register_hw()`, `regulatory_hint()`, and `ieee80211_unregister_hw()` are the major external calls in this chunk.

## Registration Control Flow

The chunk starts by adding remaining wireless capability advertisements:

1. IBSS RSN is always advertised at this point with `WIPHY_FLAG_IBSS_RSN`.
2. Dynamic SMPS is advertised if `ar->ht_cap_info` contains `WMI_HT_CAP_DYNAMIC_SMPS`.
3. AMPDU aggregation and hardware TX AMPDU setup are advertised if HT is enabled in `ar->ht_cap_info`.
4. Scan limits are set to `WLAN_SCAN_PARAMS_MAX_SSID` and `WLAN_SCAN_PARAMS_MAX_IE_LEN`.
5. Scheduled scan and network-detect scan limits are filled only if firmware advertises `WMI_SERVICE_NLO`; this also advertises random MAC support for network detection.

It then binds mac80211-private allocation sizes for VIF/STA/TXQ state and sets `ATH10K_MAX_HW_LISTEN_INTERVAL`. Beacon/probe-response, TDLS, Ethernet TX encapsulation offload, remain-on-channel, channel switch, AP U-APSD, AP scan, and AP channel-width-change support are all added by directly updating `wiphy` flags/features or `ieee80211_hw` flags.

The call to `ath10k_wow_init(ar)` is the first fallible call in this chunk. It is conditional internally: if the firmware image lacks `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, it returns success without enabling WoWLAN. If the feature bit is present but `WMI_SERVICE_WOW` is missing, it warns and fails with `-EINVAL`. On success it may add network-detect support when `WMI_SERVICE_NLO` is present, sets `ar->hw->wiphy->wowlan`, and marks the device wakeup-capable.

After WoWLAN, the code publishes extended capabilities. Some are unconditional within this driver version (`VHT_IBSS`, `SET_SCAN_DWELL`, `AQL`, `CQM_RSSI_LIST` later), while others depend on hardware parameters or WMI service bits:

- multicast frame registration depends on `ar->hw_params.mcast_frame_registration`;
- ACK signal reporting depends on either TX data ACK RSSI service or valid HTT management TX completion flags;
- airtime fairness depends on peer stats being enabled or firmware airtime reporting support;
- FTM responder, per-station TX power, and TID configuration depend on their matching WMI services.

For TID configuration, support is advertised per VIF and copied to per-peer support. Base attributes include no-ack, short/long retry counts, AMPDU control, TX rate, and TX rate type. Extended peer TID config support adds RTS/CTS control. If firmware lacks the base service, `ar->ops->set_tid_config` is nulled before registration so mac80211 never calls the operation.

Queue state is then declared. The driver sets `ar->hw->queues` to `IEEE80211_MAX_QUEUES`, with a comment that low-latency hardware queues are firmware-managed. The off-channel TX hardware queue is set to `IEEE80211_MAX_QUEUES - 1` because ath10k uses vdev IDs as hardware queue numbers and wants the off-channel queue outside the reachable vdev ID range.

The firmware WMI operation version drives interface-combination selection:

- `ATH10K_FW_WMI_OP_VERSION_MAIN` uses `ath10k_if_comb` and enables IBSS.
- `ATH10K_FW_WMI_OP_VERSION_TLV` uses either `ath10k_tlv_qcs_if_comb` when adaptive OCS is available, or `ath10k_tlv_if_comb` otherwise, and enables IBSS.
- `ATH10K_FW_WMI_OP_VERSION_10_1`, `10_2`, and `10_2_4` use `ath10k_10x_if_comb`.
- `ATH10K_FW_WMI_OP_VERSION_10_4` starts with `ath10k_10_4_if_comb`, but switches to `ath10k_10_4_bcn_int_if_comb` if firmware supports different beacon intervals per vdev.
- unset or max sentinel values trigger `WARN_ON(1)`, set `ret = -EINVAL`, and unwind.

The rest of registration is late capability and subsystem setup. Dynamic SAR support attaches `ath10k_sar_capa`; non-raw mode enables `NETIF_F_HW_CSUM`; DFS certified builds initialize a DFS pattern detector and keep going with only a warning if detector allocation fails. Regulatory state is derived through `ath10k_mac_init_rd()` and registered with `ath_regd_init()`. `set_coverage_class` is disabled in the copied `ieee80211_ops` table when the chipset has no hardware operation for it.

Cipher suites are exposed through a static `cipher_suites[]` table defined at the top of `ath10k_mac_register()`. The number of advertised ciphers is taken from `ar->hw_params.n_cipher_suites`, because older QCA988x/QCA6174-family chips only support the first eight entries while some later variants support the GCMP and CCMP-256 entries too. Invalid zero or too-large values are logged and coerced to eight suites.

Finally, `ar->hw->weight_multiplier` is set to `ATH10K_AIRTIME_WEIGHT_MULTIPLIER`, and `ieee80211_register_hw(ar->hw)` publishes the device. After successful mac80211 registration, the code conditionally adds AP VLAN support for firmware with per-packet software encryption, then sends a regulatory hint if both the copied world regdomain and active regulatory state are non-world domains.

## Error And Unregister Flow

The function uses three local unwind labels:

- `err_unregister` calls `ieee80211_unregister_hw(ar->hw)` and then falls through to DFS/channel cleanup. This is reached if `regulatory_hint()` fails after mac80211 registration.
- `err_dfs_detector_exit` exits the DFS detector when `CONFIG_ATH10K_DFS_CERTIFIED` is enabled and `ar->dfs_detector` is non-NULL. This handles failures after DFS initialization but before successful registration, and also the `ieee80211_register_hw()` failure case.
- `err_free` releases the dynamically duplicated 2 GHz and 5 GHz channel arrays and clears the device association with `SET_IEEE80211_DEV(ar->hw, NULL)`.

`ath10k_mac_unregister()` mirrors the successful-registration cleanup in a simpler order: unregister from mac80211, exit DFS detector if present, free both supported-band channel arrays, and clear the `ieee80211_hw` device pointer.

The wider integration in `core.c` depends on this ordering. Normal `ath10k_core_unregister()` calls `ath10k_mac_unregister()` before testmode cleanup, firmware file release, and debug unregister, and specifically before HTC/HIF shutdown so mac80211 callbacks can still submit firmware commands during unregister. Registration unwind in core also calls `ath10k_mac_unregister()` after coredump/debug/spectral/thermal/LED setup failures.

## State And Persistence Behavior

Most state in this chunk is configuration state persisted in `ar->hw`, `ar->hw->wiphy`, and driver-owned `ar` fields for the lifetime of the registered radio:

- The cfg80211-visible capability set is persisted in `wiphy` flags, feature bitmasks, extended features, interface modes, interface combinations, scan limits, scheduled-scan limits, cipher suite pointers, SAR capability pointer, and regulatory structures.
- The mac80211-private allocation contract is persisted through `vif_data_size`, `sta_data_size`, and `txq_data_size`; changing these after registration would corrupt callback expectations.
- The driver operation table (`ar->ops`) is a copied `ieee80211_ops` table. This chunk mutates it before registration by nulling unsupported callbacks (`set_tid_config`, `set_coverage_class`) so mac80211 sees only operations that the current firmware/hardware can satisfy.
- WoWLAN initialization writes `ar->wow.wowlan_support`, assigns `wiphy->wowlan`, and marks the parent device wakeup-capable. That state outlives the register call and is consumed by suspend/resume paths.
- DFS detector state is held in `ar->dfs_detector` and must be explicitly exited on unregister or failed registration after initialization.
- Regulatory state is stored in `ar->ath_common.regulatory` and associated with the `wiphy`; the later `regulatory_hint()` may trigger cfg80211 regulatory processing after the hardware is registered.
- The supported-band channel arrays were allocated earlier with `kmemdup()` and are freed here on all late failures and normal unregister.

The code does not persist state to disk or firmware NVRAM. It does, however, define the live kernel/userspace contract for the radio until unregister, and that contract controls which userspace operations cfg80211 will allow.

## Dependencies And Integration Points

This chunk is tightly integrated with mac80211 and cfg80211. `ieee80211_register_hw()` is the publication boundary: every flag and pointer must be valid before that call because mac80211 and userspace can observe the device afterward. `ieee80211_unregister_hw()` is the inverse boundary that stops mac80211 use before lower driver resources disappear.

Firmware discovery is another central dependency. `ar->wmi.svc_map`, `ar->ht_cap_info`, `ar->running_fw->fw_file.wmi_op_version`, and `ar->running_fw->fw_file.fw_features` come from earlier firmware/service-ready processing. Incorrect service bits would cause this chunk to over-advertise unsupported nl80211 features or hide working ones.

Hardware parameter tables in `core.c` feed `ar->hw_params` values such as `n_cipher_suites`, `dynamic_sar_support`, `mcast_frame_registration`, and `hw_ops->set_coverage_class`. This chunk trusts those tables, except for range-checking `n_cipher_suites`.

The DFS integration depends on `CONFIG_ATH10K_DFS_CERTIFIED` and the common ath DFS detector API. Regulatory integration depends on the ath common regulatory helpers (`ath10k_mac_init_rd()`, `ath_regd_init()`, `ath10k_reg_notifier()`, `ath_is_world_regd()`, and `regulatory_hint()`).

The source path is under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/`, so it is a copied Linux wireless driver source inside the broader `learn_fs` tree. The code does not directly interact with Ceph filesystem logic, but any build that includes this tree relies on these registration flags for ath10k wireless device behavior.

## Risks And Edge Cases

The highest-risk behavior is capability over-advertisement. Many flags are gated by WMI services or hardware parameters; if those inputs are wrong, cfg80211/mac80211 may expose operations that later firmware callbacks cannot execute. Risky examples include TDLS wider bandwidth, per-peer TID configuration, FTM responder, per-station TX power, ACK signal reporting, AP VLAN software interface support, and AP probe-response offload.

The AP VLAN feature is added after `ieee80211_register_hw()`. That is notable because most public `wiphy` capability setup happens before registration. If mac80211/cfg80211 expects interface mode and software-iftype masks to be complete at registration time, this ordering could be subtle. It is presumably intentional for firmware with per-packet software encryption, but any future rework should verify the timing.

Unwind must remain aligned with allocation order. Channel arrays are always freed at `err_free`, including when only one band was allocated; `kfree(NULL)` makes that safe. DFS detector exit is guarded by both config and non-NULL detector checks. A future added resource between these blocks must be placed into the correct unwind label or normal unregister will leak or double-free it.

The invalid WMI operation version path frees channel arrays and clears `SET_IEEE80211_DEV`, but does not unregister mac80211 because the hardware has not yet been registered. That separation is important: using `err_unregister` before successful `ieee80211_register_hw()` would be wrong.

`ar->ops` mutation is permanent for the lifetime of this allocated hardware object. Since `ath10k_core_create()` allocates a private copy of `ath10k_ops`, this is safe per device, but it means callbacks disabled during registration are not restored later if firmware mode or service information changes.

DFS detector initialization failure is warning-only. Registration can continue without `ar->dfs_detector`, so radar/CAC behavior in DFS-certified builds must tolerate a missing detector. Conversely, unregister must tolerate a stale non-NULL pointer only if the detector's `exit()` semantics are single-use; the current code does not clear `ar->dfs_detector` after exit.

The cipher-suite fallback silently mutates `ar->hw_params.n_cipher_suites` to eight after logging. That protects registration from bad table data, but it also hides the original invalid value for later diagnostics and may under-advertise on affected hardware.

The regulatory hint happens after mac80211 registration. If `regulatory_hint()` fails, the code unregisters hardware and tears down DFS/channel resources. Tests need to cover that late failure because it exercises the full registered-hardware unwind path.

## Test Signals

Useful test and review signals for this chunk include:

- Boot/register tests for representative firmware operation versions: MAIN, TLV without adaptive OCS, TLV with adaptive OCS, 10.1/10.2/10.2.4, 10.4 without different beacon interval support, and 10.4 with different beacon interval support. Each should verify advertised interface combinations and IBSS availability.
- Capability matrix tests or debug dumps comparing WMI service bits to visible nl80211/mac80211 features: NLO scheduled scan and network-detect random MAC, beacon/probe-response offload, TDLS and wider bandwidth, TDLS buffer STA, ACK signal support, airtime fairness, FTM responder, station TX power, TID config, scan random MAC, and AP VLAN software interface support.
- Negative registration tests for unsupported/sentinel WMI op versions, `ath10k_wow_init()` failure, `ath_regd_init()` failure, `ieee80211_register_hw()` failure, and `regulatory_hint()` failure. The expected signal is that channel arrays are freed, DFS detector exit runs only when initialized, and `SET_IEEE80211_DEV` is cleared.
- WoWLAN tests for firmware with no WoWLAN feature bit, firmware with WoWLAN feature but missing `WMI_SERVICE_WOW`, and firmware with WoWLAN plus NLO. These should verify `wiphy->wowlan`, wakeup capability, and network-detect limits.
- Cipher-suite tests for hardware parameter values 8, 11, 0, and greater than `ARRAY_SIZE(cipher_suites)`, checking that older chips do not advertise unsupported GCMP/CCMP-256 ciphers and invalid values fall back to eight.
- DFS-certified build tests ensuring registration succeeds when `dfs_pattern_detector_init()` returns NULL and unregister does not call through a NULL detector; a detector-present path should verify exactly one exit on normal unregister and on late registration failure.
- Regulatory tests that exercise WRDD/eeprom-derived regulatory state in the preceding helper, `ath_regd_init()`, world versus non-world domains, successful and failed `regulatory_hint()`, and the resulting unregister path.
- mac80211 private-data tests or compile-time checks verifying `vif_data_size`, `sta_data_size`, and `txq_data_size` match the driver-private structs used by callbacks.
- Core unregister ordering tests or audits should preserve the documented sequence from `core.c`: unregister mac80211 before stopping HTC/HIF, because mac80211 unregister may still need firmware-command callbacks to succeed.

For the research pipeline, the key artifact signal is that this chunk document is source-tree-aligned at `Docs/researches/chunks/subset-b-004720_research.md` and only covers `mac.c` lines 10095-10380. The later merge lane should reconcile it with earlier `ath10k_mac_register()` chunks that cover channel allocation, base hardware flags, and the helper definitions above this range.
