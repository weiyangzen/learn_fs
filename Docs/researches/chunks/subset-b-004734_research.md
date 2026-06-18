# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.c lines 1-9717

## Scope

This chunk covers the first 9,717 lines of the ath11k mac80211 integration file. It includes channel/rate tables, mac80211 operation callbacks through the start of remain-on-channel support, WMI vdev and peer orchestration, monitor mode, beacon/MBSSID/EMA handling, scan and 11d flow, key installation, station association and rate-control updates, TX and management TX routing, HT/VHT/HE capability construction, channel-context start/stop/restart, 6 GHz TPC handling, bitrate-mask programming, survey/statistics reporting, IPv6/ARP/GTK offload state capture, and BIOS SAR configuration.

The final registration, `ieee80211_ops` table, station add/remove state machine tail, hardware registration, and cleanup functions begin after this chunk. This report therefore treats those as cross-chunk integration points rather than complete local definitions.

## Purpose

`mac.c` is the main bridge between Linux mac80211/cfg80211 and ath11k firmware/data-path internals. In this range it translates mac80211 callbacks and station/vif/channel state into WMI commands, DP TX/RX configuration, firmware object lifecycles, and driver-private state updates. The central runtime objects are `struct ath11k`, `struct ath11k_base`, `struct ath11k_vif`, `struct ath11k_sta`, firmware `peer_assoc_params`, `vdev_create_params`, and mac80211 `ieee80211_hw`, `ieee80211_vif`, `ieee80211_sta`, and channel-context structures.

## Important APIs, Types, And Functions

- Static band/rate definitions: `ath11k_2ghz_channels`, `ath11k_5ghz_channels`, `ath11k_6ghz_channels`, `ath11k_legacy_rates`, `ath11k_phymodes`, and `ath11k_mac_mon_status_filter_default` advertise supported channels/rates and default monitor-status TLV filtering.
- Rate and PHY conversion helpers: `ath11k_mac_phy_he_ru_to_nl80211_he_ru_alloc()`, `ath11k_mac_he_ru_tones_to_nl80211_he_ru_alloc()`, `ath11k_mac_he_gi_to_nl80211_he_gi()`, `ath11k_mac_bw_to_mac80211_bw()`, `ath11k_mac_mac80211_bw_to_ath11k_bw()`, `ath11k_mac_hw_ratecode_to_legacy_rate()`, and legacy bitrate-to-WMI helpers convert between firmware encodings and mac80211 rate metadata.
- VIF/radio lookup helpers: `ath11k_mac_get_arvif()`, `ath11k_mac_get_arvif_by_vdev_id()`, `ath11k_mac_get_ar_by_vdev_id()`, `ath11k_mac_get_ar_by_pdev_id()`, `ath11k_mac_get_vif_up()`, and target pdev lookup helpers map WMI vdev/pdev IDs back to active mac80211 objects.
- Monitor mode lifecycle: `ath11k_mac_monitor_vdev_create/delete/start/stop()`, `ath11k_mac_monitor_start/stop()`, `ath11k_mac_config_mon_status_default()`, and `ath11k_mac_op_config()` allocate an internal monitor vdev, start it on an active channel, configure HTT monitor status rings, and tear it down.
- Beacon and MBSSID handling: `ath11k_mac_setup_bcn_tmpl()`, `ath11k_mac_setup_bcn_tmpl_mbssid()`, `ath11k_mac_setup_bcn_tmpl_ema()`, `ath11k_mac_set_vif_params()`, `ath11k_mac_set_nontx_vif_params()`, `ath11k_control_beaconing()`, `ath11k_mac_bcn_tx_event()`, and beacon miss/loss handlers build and submit firmware beacon templates, track RSN/WPA/P2P IEs, manage transmitted/non-transmitted BSSID profiles, and signal color-change completion.
- Peer association builders: `ath11k_peer_assoc_prepare()` and its `*_h_basic`, `*_h_crypto`, `*_h_rates`, `*_h_ht`, `*_h_vht`, `*_h_he`, `*_h_he_6ghz`, `*_h_smps`, `*_h_qos`, and `*_h_phymode` helpers translate station capabilities and bitrate masks into WMI peer association fields.
- BSS and scan callbacks: `ath11k_mac_op_bss_info_changed()`, `ath11k_bss_assoc()`, `ath11k_bss_disassoc()`, `ath11k_mac_op_hw_scan()`, `ath11k_mac_op_cancel_hw_scan()`, `ath11k_scan_abort()`, `ath11k_scan_stop()`, `ath11k_start_scan()`, and `__ath11k_mac_scan_finish()` synchronize association, beacon, TWT, OBSS PD, BSS color, FILS, ARP offload, and scan state.
- Key/security functions: `ath11k_mac_op_set_key()`, `ath11k_install_key()`, `ath11k_clear_peer_keys()`, and `ath11k_set_group_keys()` map mac80211 key operations to WMI key install/delete commands and local `ath11k_peer` key slots.
- Station/rate-control functions: `ath11k_station_assoc()`, `ath11k_station_disassoc()`, fixed-rate helpers for HT/VHT/HE peers, `ath11k_sta_rc_update_wk()`, `ath11k_mac_op_sta_rc_update()`, `ath11k_mac_op_sta_set_txpwr()`, and `ath11k_mac_op_sta_set_4addr()` update peer association, bandwidth, NSS, SMPS, fixed-rate, 4-address, and per-station power settings.
- Queue/WMM/capability functions: `ath11k_mac_op_conf_tx()`, `ath11k_mac_op_conf_tx_mu_edca()`, `ath11k_conf_tx_uapsd()`, `ath11k_create_ht_cap()`, `ath11k_create_vht_cap()`, `ath11k_mac_setup_ht_vht_cap()`, `ath11k_mac_copy_he_cap()`, `ath11k_mac_setup_he_cap()`, and beamforming/PPE helpers build advertised HT/VHT/HE/6 GHz capabilities and configure WMM/UAPSD.
- TX path functions: `ath11k_mac_op_tx()`, `ath11k_mac_mgmt_tx()`, `ath11k_mgmt_over_wmi_tx_work()`, `ath11k_mac_mgmt_tx_wmi()`, `ath11k_mac_drain_tx()`, and `ath11k_mac_wait_tx_complete()` route data frames to DP TX, route management frames through queued WMI TX, track pending management IDs/DMA, and flush queues.
- Device/vdev lifecycle callbacks: `ath11k_mac_op_start()`, `ath11k_mac_op_stop()`, `ath11k_mac_op_add_interface()`, `ath11k_mac_op_remove_interface()`, `ath11k_mac_vdev_start_restart()`, `ath11k_mac_vdev_stop()`, and channel-context callbacks create/delete/start/stop vdevs, allocate AP self-peers, maintain `free_vdev_map`, and control active pdev exposure.
- Regulatory and 6 GHz power: `ath11k_mac_11d_scan_start/stop/stop_all()`, `ath11k_mac_parse_tx_pwr_env()`, `ath11k_mac_fill_reg_tpc_info()`, and helper frequency/power functions derive 6 GHz TPC/EIRP/PSD power arrays from TPE IE, channel width, local regulatory rules, AP power type, and firmware reported power.
- Bitrate mask and survey/statistics: `ath11k_mac_op_set_bitrate_mask()`, helper validators/range checkers, `ath11k_mac_op_get_survey()`, `ath11k_mac_op_sta_statistics()`, and RSSI chain helpers expose rate constraints and station/survey data to cfg80211/mac80211.
- Offload/configuration hooks: `ath11k_mac_op_ipv6_changed()`, `ath11k_mac_op_set_rekey_data()`, `ath11k_mac_op_set_bios_sar_specs()`, `ath11k_mac_op_update_vif_offload()`, RTS/fragment threshold callbacks, and the start of remain-on-channel callbacks cache offload state and push firmware parameters.

## Control Flow

Startup begins in `ath11k_mac_op_start()`. It drains pending TX, transitions `ar->state` from `OFF` or `RESTARTING` to `ON`/`RESTARTED`, programs pdev parameters for PMF QoS, dynamic bandwidth, probe-request OUI, ARP AC override, DFS offload, PPDU stats, mesh multicast, antenna chain masks, regulatory channel lists, monitor status filters, LRO hash seed, and optional idle power save. It resets runtime counters and publishes the active pdev through RCU.

VIF creation flows through `ath11k_mac_op_add_interface()`. The callback reserves a free vdev ID from `ab->free_vdev_map`, initializes `ath11k_vif`, default bitrate masks, work items, queues, vdev type/subtype, MBSSID create parameters, and firmware vdev state. AP vdevs create a self-peer and set kickout/keepalive thresholds; STA vdevs program default power-save parameters and may enter 11d preparation; monitor vdevs set monitor flags. On failure it unwinds peer/vdev/list state under `conf_mutex` and `data_lock`.

Channel assignment starts vdevs. `ath11k_mac_op_assign_vif_chanctx()` handles delayed-start hardware, monitor vdev start, normal `ath11k_mac_vdev_start()`, and optional internal monitor start. `ath11k_mac_vdev_start_restart()` composes `wmi_vdev_start_req_arg` from the channel definition, beacon interval/DTIM, AP SSID/radar/regdomain fields, MBSSID fields, and chain preferences, waits for `vdev_setup_done`, optionally sends 6 GHz TPC power, increments started-vdev counters, sets CAC state, and configures VHT TXBF. Change/switch channel-context paths restart or stop/start active vdevs, refresh beacon templates, bring AP vdevs back up, and restart the internal monitor vdev.

Association uses the peer association builder. For AP-side station association, `ath11k_station_assoc()` prepares and sends WMI peer assoc, waits on `peer_assoc_done`, applies fixed-rate overrides if a single HT/VHT/HE rate is configured, configures SMPS, updates legacy station RTS/CTS mode, and applies AP UAPSD parameters. For STA-side association, `ath11k_bss_assoc()` finds the AP station, prepares peer params, recalculates STA HE TXBF, sends peer assoc, brings the vdev up with the AP BSSID/AID, optionally authorizes the BSS peer, sends OBSS PD and DTIM policy, and stops 11d scans.

`ath11k_mac_op_bss_info_changed()` is a large event dispatcher for mac80211 BSS changes. It sets beacon interval, beacon template and staggered mode, DTIM, SSID, BSSID, beacon enabled/up/down state, ERP CTS/slot/preamble, association/disassociation, TX power, STA power save, multicast/basic rates, TWT enable/disable, HE OBSS PD, BSS color collision/change config, FTM responder, FILS/unsolicited probe response templates, and ARP offload cache.

Scanning is a state machine guarded by `data_lock` and `conf_mutex`. `ath11k_mac_op_hw_scan()` transitions from `ATH11K_SCAN_IDLE` to `STARTING`, allocates a WMI scan request, copies SSIDs/IEs/channel list/random MAC/dwell time, starts optional 11d activity, calls `ath11k_start_scan()`, and arms a timeout worker. Completion or abort converges through `__ath11k_mac_scan_finish()`, which reports scan completion or remain-on-channel expiration, clears scan channel/ROC fields, cancels timeout, and completes waiters.

TX control splits management frames and data frames. `ath11k_mac_op_tx()` records VIF/cipher metadata in `ATH11K_SKB_CB`; non-HW-encap management frames are queued to `wmi_mgmt_tx_queue`, counted in `num_pending_mgmt_tx`, and later DMA-mapped/sent with WMI from auxiliary work. Data and HW-encap frames are passed to `ath11k_dp_tx()`. Management TX completion uses an IDR keyed by firmware buffer ID, unmaps DMA, frees SKBs through mac80211, and wakes `txmgmt_empty_waitq` when the count drains.

Teardown reverses those lifecycles. `ath11k_mac_op_stop()` drains TX, disables monitor-status RX filters, marks the radio off, cancels scan/channel/regulatory/11d work, frees queued stats/channel-update entries, removes the active pdev pointer, synchronizes RCU, and clears pending management count. `ath11k_mac_op_remove_interface()` cancels vif work, stops spectral and 11d, deletes AP self-peer, deletes vdevs, handles monitor-vdev flags, removes the VIF from `arvifs`, cleans peers and pending TX references, and recalculates txpower.

## State And Persistence Behavior

Runtime state is spread across mac80211 objects, ath11k driver objects, firmware vdev/peer objects, and DP rings. Important state in this chunk includes `ar->state`, `ar->monitor_flags`, `ar->allocated_vdev_map`, `ab->free_vdev_map`, `ar->num_created_vdevs`, `ar->num_started_vdevs`, `ar->num_peers`, `ar->num_stations`, `arvif->is_started`, `arvif->is_up`, `arvif->num_stations`, `arvif->bitrate_mask`, `arvif->rsnie_present`, `arvif->wpaie_present`, `arvif->rekey_data`, `arvif->arp_ns_offload`, `arvif->reg_tpc_info`, `ar->scan`, and per-station `ath11k_sta` rate/RSSI/PN fields.

Firmware object state is explicitly created and deleted: vdevs, AP self-peers, station peers, keys, monitor vdevs, scan commands, WMM/WMI vdev parameters, 11d scan state, and stats requests. The driver mirrors enough state locally to avoid duplicate vdev IDs, restore rate parameters after firmware clears them on vdev start, reapply capabilities after antenna changes, and update mac80211 after firmware events.

Persistence is mostly runtime-only. GTK rekey material is cached in memory for offload and cleared on disassociation. ARP/IPv6 neighbor-solicitation offload data is cached in `ath11k_vif` from mac80211/network-device notifications. BIOS SAR programming comes from cfg80211 SAR specs and is pushed to firmware, not stored by this file. Firmware stats, surveys, RSSI, PPDU stats, and scan state are transient and protected with locks/completions.

Concurrency is central. `conf_mutex` serializes most configuration/WMI operations. `data_lock` guards scan state, survey/stat updates, channel update queues, and station rate-change shadow fields. `base_lock` protects peer lists and per-peer key pointers. RCU is used for active pdev pointers and mac80211 channel/VIF iteration. Completions synchronize WMI vdev start/stop/delete, peer assoc, key install, scan start/stop, stats, BSS survey, and 11d scan operations.

## Dependencies And Integration Points

- mac80211/cfg80211: callback signatures, channel contexts, BSS change flags, scan requests, station capabilities, bitrate masks, key operations, survey/station info, beacon template APIs, EMA/MBSSID helpers, ROC callbacks, SAR specs, and IPv6 notifier integration.
- ath11k WMI: all vdev, pdev, peer, key, scan, stats, TWT, FILS, OBSS PD, BSS color, TXBF, 11d, TPC, WMM, SAR, and management TX commands are sent through `ath11k_wmi_*` helpers and firmware-defined enums.
- ath11k DP: data TX (`ath11k_dp_tx()`), RX PN replay offload, RX A-MPDU start/stop, monitor HTT ring configuration, PPDU stats, crypto type mapping, and management protected-frame MIC sizing.
- peer/core/debug modules: peer lookup/create/delete/cleanup, peer TID and fragment cleanup, debug logging/dumps, spectral/CFR hooks, testmode/FTM restrictions, WoW-facing rekey/offload state, and regulatory helpers.
- Linux kernel services: DMA map/unmap, IDR allocation, workqueues, delayed work, timers, completions, RCU, spinlocks, mutexes, sk_buffs, inet6 address lists, and bitfield helpers.
- Regulatory and firmware capability gates: behavior depends on `ab->hw_params`, `wmi_ab.svc_map`, firmware mode, current regulatory info, 6 GHz support, current country support, vdev start delay, idle PS, RAW/Ethernet/NATIVE Wi-Fi frame mode, and hardware crypto availability.

## Risks And Edge Cases

- Vdev and peer lifecycles are tightly coupled. Missed error unwinds can leak vdev IDs, leave `allocated_vdev_map` inconsistent with firmware, or leave AP self-peers/keys stale.
- Several code paths rely on firmware events arriving before timeouts. Vdev setup/delete, peer assoc, key install, scan start/stop, firmware stats, and survey requests can stall or return fallback values when firmware drops events.
- `ath11k_mac_op_bss_info_changed()` combines many independent BSS transitions under one callback; ordering between beacon template updates, vdev up/down, color change, HE params, association, and power-save updates is easy to regress.
- MBSSID/EMA handling parses beacon profiles manually and assumes profile layout lengths are sane after outer IE discovery. Malformed templates or mismatched transmitted/non-transmitted VIF relationships can return `-EINVAL` or avoid updating non-TX security flags.
- Fixed-rate and bitrate-mask logic has deliberate limitations: multiple arbitrary VHT/HE MCS values are rejected, single VHT/HE/HT rates become peer fixed-rate overrides, and peer compatibility validation only warns for some incompatibilities.
- Key reinstallation has a firmware race workaround for AP group keys. Changing this flow can reintroduce multicast/broadcast drops during GTK rekey or break open-mode transitions with no stations.
- Monitor mode interacts with channel-context changes and normal vdev starts. Internal monitor vdev start/stop/delete failures can leave flags inconsistent or block monitor status capture.
- 6 GHz TPC/EIRP/PSD calculations depend on channel widths, TPE IE parsing, local regulatory power, `max_allowed_tx_power`, idle-PS behavior, and client power type. Incorrect min/max selection can violate regulatory limits or reduce throughput.
- Management TX uses asynchronous queues, IDR slots, DMA mappings, and a pending-count waitqueue. VIF removal must clear queued references and IDR entries to prevent use-after-free against `skb_cb->vif`.
- The requested chunk ends inside `ath11k_mac_op_remain_on_channel()`, so the ROC start path cannot be fully assessed here. Its state initialization must be reconciled with the continuation in chunk `subset-b-004735`.

## Test Signals

- Build coverage with ath11k enabled, including configurations with and without IPv6, hardware crypto, monitor mode, 6 GHz, BIOS SAR, and firmware capability gates.
- mac80211 operation tests or hardware smoke tests for add/remove interface, AP/STA/P2P/mesh mode creation, channel assignment/unassignment, start/stop, restart recovery, and vdev ID reuse after failures.
- Association tests across HT, VHT, HE, 6 GHz HE, legacy-only, WME/non-WME, UAPSD, SMPS, fixed-rate, and peer bandwidth/NSS changes; verify WMI peer assoc contents and rate-control updates.
- Security tests for pairwise/group key install/delete, unsupported BIP software fallback, AP GTK rekey under traffic, peer deletion with keys installed, and PN replay offload configuration.
- Scan/ROC tests for normal scan, random MAC scan, 6 GHz colocated scan flags, scan timeout/abort, concurrent 11d preparation, cancellation, and scan completion reporting.
- Beacon/AP tests for MBSSID and EMA templates, P2P GO P2P IE offload/removal, BSS color change completion, beacon loss/connection loss work, FILS discovery, unsolicited broadcast probe responses, OBSS PD, and FTM responder toggles.
- TX path tests for management TX queue saturation, probe-response drop threshold, protected action-frame TPC field filling, DMA mapping failure, VIF removal during queued management TX, DP TX failure, and flush wait timeouts.
- Regulatory/power tests for txpower recalculation over multiple vdevs, per-station TX power, antenna chain-mask updates, 6 GHz TPE/PSD/EIRP cases, 11d scan stop/start around AP mode, and BIOS SAR table programming.
- Survey/statistics tests for BSS channel survey request gating, chain RSSI conversion with and without DB-to-dBm firmware support, firmware stats fallback, and station signal average reporting.

## Unresolved Cross-Chunk References

The chunk ends at line 9,717 in the middle of `ath11k_mac_op_remain_on_channel()`. The rest of ROC setup, station add/remove callbacks, `ath11k_mac_op_sta_state()`, the `ieee80211_ops` table, channel/rate setup, interface-combination setup, mac80211 register/unregister, allocation/destruction, and keepalive helper are in the next chunk (`subset-b-004735`). Those later definitions determine exactly which callbacks from this chunk are exposed to mac80211 and complete station lifecycle integration.
