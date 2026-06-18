# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004734`: lines 1-9717, `Docs/researches/chunks/subset-b-004734_research.md`
- `subset-b-004735`: lines 9718-10896, `Docs/researches/chunks/subset-b-004735_research.md`

## Chunk Research

### subset-b-004734: lines 1-9717

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

### subset-b-004735: lines 9718-10896

# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mac.c lines 9718-10896

## Scope

This chunk covers the end of ath11k's mac80211-facing MAC implementation. It starts inside `ath11k_mac_op_remain_on_channel()` after ROC scan state has been moved to `ATH11K_SCAN_STARTING`, then covers station add/remove/state transitions, the `ieee80211_ops` callback table, supported-channel/rate setup, interface-combination and extended-capability advertisement, MAC registration/unregistration, per-radio allocation/destruction, and STA keepalive programming.

The code is the bridge between mac80211/cfg80211 abstractions and ath11k's firmware, WMI, peer table, datapath, regulatory, debugfs, and WoW subsystems. Most functions in this range either publish device capabilities to `struct wiphy`/`struct ieee80211_hw` or translate mac80211 lifecycle callbacks into ath11k state and firmware commands.

## Purpose

The covered code has four main responsibilities:

- Implement remain-on-channel by using the firmware scan engine as an off-channel dwell mechanism.
- Maintain peer and station lifetime across mac80211 station-state transitions.
- Advertise ath11k radio capabilities and operation callbacks during hardware registration.
- Allocate, initialize, unregister, and destroy per-radio `struct ath11k` objects and their mac80211 `struct ieee80211_hw` containers.

This chunk is not the whole MAC layer. It depends heavily on earlier functions in the same file for scan finish/abort, peer association, vdev start/stop, capability population, TX/RX helpers, debugfs, regulatory handling, and WMI command wrappers.

## Important APIs, Types, and Functions

### Remain-on-channel

`ath11k_mac_op_remain_on_channel()` builds a one-channel `struct scan_req_params` and calls `ath11k_start_scan()` using `ATH11K_SCAN_ID`. It stores ROC state in `ar->scan`, including `is_roc`, `vdev_id`, `roc_freq`, and `roc_notify`, under `ar->data_lock`, while the outer operation is serialized by `ar->conf_mutex`.

Important behavior:

- Only `ATH11K_SCAN_IDLE` may transition into a ROC request; starting/running/aborting scans return `-EBUSY`.
- The channel list is dynamically allocated, populated with `chan->center_freq`, and freed before returning because firmware owns the submitted request data after `ath11k_start_scan()`.
- Active/passive dwell and maximum scan time use twice `wiphy->max_remain_on_channel_duration`; `burst_duration` uses the caller's requested duration.
- The function waits up to `3 * HZ` for `ar->scan.on_channel`. If the firmware never reports on-channel, it attempts `ath11k_scan_stop()` and returns `-ETIMEDOUT`.
- On success it schedules `ar->scan.timeout` for the requested duration.

`ath11k_mac_op_cancel_remain_on_channel()` appears just before the mapped range and is referenced through `ath11k_ops`; it clears `roc_notify`, aborts scan state, drops the config mutex, then cancels the timeout work synchronously.

### Station and peer lifecycle

`ath11k_mac_station_add()` is called with `ar->conf_mutex` held. It increments station accounting with `ath11k_mac_inc_num_stations()`, optionally reinstalls group keys on the first station after a firmware group-key race window, allocates per-station RX stats, creates a firmware/software peer through `ath11k_peer_create()`, optionally allocates extended TX stats when debugfs asks for them, configures mesh 4-address peer mode, sets up datapath peer resources with `ath11k_dp_peer_setup()`, optionally starts a delayed vdev for non-AP vdevs, and initializes EWMA RSSI.

Failure unwinding is staged in reverse order: free TX stats, delete the peer, free RX stats, decrement station counters. This matters because station count and peer visibility affect capacity limits and later cleanup paths.

`ath11k_mac_station_remove()` mirrors the add path. For delayed-start non-AP vdevs it may stop the vdev early, then performs datapath peer cleanup, deletes the peer, decrements station counters, and frees TX/RX stats. Peer deletion failures are logged and returned, but local stat pointers are still cleared after the delete attempt.

`ath11k_mac_op_sta_state()` is the mac80211 `sta_state` callback. It handles these transitions:

- `NOTEXIST -> NONE`: zeroes `struct ath11k_sta`, binds it to `arvif`, initializes PS state and work items, then calls `ath11k_mac_station_add()`.
- `NONE -> NOTEXIST`: cancels station work before taking `conf_mutex`, calls `ath11k_mac_station_remove()`, then defensively checks the peer hash/list and removes a lingering peer whose `peer->sta` still matches the mac80211 station. It also decrements CFR peer accounting.
- `AUTH -> ASSOC` for AP, mesh, and ad-hoc vifs: calls `ath11k_station_assoc()` and snapshots WMI bandwidth in `arsta->bw` and `bw_prev` under `ar->data_lock`.
- `ASSOC -> AUTHORIZED`: marks the peer authorized under `ab->base_lock`; for STA mode with an up vdev, sends `WMI_PEER_AUTHORIZE`. For 6 GHz STA operation with CC extension support, it also refreshes the regulatory channel list based on AP power type.
- `AUTHORIZED -> ASSOC`: clears local peer authorization.
- `ASSOC -> AUTH` for AP, mesh, and ad-hoc vifs: calls `ath11k_station_disassoc()`.

The state callback uses `ar->conf_mutex` for high-level serialization, `ab->base_lock` for peer table mutation, `ab->tbl_mtx_lock` around peer rhash/list repair, and `ar->data_lock` for station bandwidth state.

### mac80211 operations table

`ath11k_ops` is the `struct ieee80211_ops` table passed to `ieee80211_alloc_hw()`. The table binds the driver into mac80211 for TX, interface add/remove, configuration, scanning, key management, station state and rate-control updates, queue configuration, antenna selection, AMPDU, channel contexts, bitrate masks, survey and station stats, flush, SAR, remain-on-channel, and optional testmode, PM/WoW, debugfs, and IPv6 neighbor offload callbacks.

This table is the primary integration point from mac80211 into the functions spread across `mac.c`; many callbacks referenced here are implemented outside this chunk.

### Channel, rate, address, and interface advertisement

`ath11k_mac_update_ch_list()` disables channels outside firmware/board regulatory frequency limits by setting `IEEE80211_CHAN_DISABLED`.

`ath11k_get_phy_id()` maps WMI 2 GHz/5 GHz band capability flags to per-band `phy_id` fields in `struct ath11k_pdev_cap`; unsupported input logs and returns 0.

`ath11k_mac_setup_channels_rates()` allocates per-radio copies of static 2 GHz, 5 GHz, and 6 GHz channel arrays, fills `ar->mac.sbands[]`, and publishes them through `wiphy->bands[]`. It chooses 6 GHz support when the 5 GHz regulatory high channel reaches `ATH11K_MIN_6G_FREQ`, marks `ar->supports_6ghz`, and uses OFDM rates for 5/6 GHz and CCK/OFDM rates for 2 GHz. On single-pdev hardware it may use band-specific phy regulatory capabilities instead of the current pdev index.

`ath11k_mac_setup_mac_address_list()` publishes additional locally administered MAC addresses when `support_dual_stations` is enabled, using `hw_params.num_vdevs` as the address count.

`ath11k_mac_setup_iface_combinations()` builds cfg80211 interface-combination limits. The base combination allows one STA plus up to sixteen AP/mesh-style interfaces on one channel. Dual-station hardware gets a second combination allowing two STA interfaces and two channels. P2P support adds P2P client/GO to the AP limit bucket and one P2P device limit.

`ath11k_iftypes_ext_capa` and the backing byte arrays advertise extended capabilities globally, and per STA/AP iftype, including extended channel switching, multi-BSSID support, operating-mode notification, TWT requester/responder, and EMA support for AP mode.

### Registration and teardown

`__ath11k_mac_register()` configures one radio before calling `ieee80211_register_hw()`. It updates pdev capabilities, sets permanent MAC/device pointers, sets up channels/rates, reads OF frequency limits, fills HT/VHT/HE capabilities, sets interface combinations, then populates `struct ieee80211_hw` and `wiphy` flags/features/limits.

Notable advertised features include signal reporting in dBm, PS/dynamic PS, MFP, TX ACK status, driver rate control, AP link PS, spectrum management, connection monitor, per-STA GTK, monitor vif desire, channel context CSA, queue control, TX fragmentation, low ACK reports, Ethernet encap/decap offload when frame mode permits, AMPDU/AMSDU aggregation when HT or 6 GHz is available, static/dynamic SMPS, remain-on-channel, channel switch, AP U-APSD, AP channel-width change, AP scan, TX power insertion, random MAC scan support, scheduled scan/NLO limits, WoW init, ACK signal support, CQM RSSI list, STA TX power, BSS color, cipher suites, iftype extended capabilities, 6 GHz FILS discovery and unsolicited broadcast probe response, scan dwell setting, FTM responder support, MBSSID/EMA limits, regulatory initialization, software crypto control/fast xmit outside raw mode, and BIOS SAR capability when firmware/hw supports it.

After successful `ieee80211_register_hw()`, monitor mode may be removed from `interface_modes` if hardware does not support monitor. The function then applies regulatory data with `ath11k_regd_update()`, optionally sets the current country code, and registers debugfs. Error paths unregister hw as needed and free interface combinations and channel arrays.

`ath11k_mac_register()` operates at `struct ath11k_base` scope. It skips work if already registered, initializes channel-counter frequency and the free-vdev bitmap, initializes the peer rhash table, derives per-radio MAC addresses from pdev-specific addresses, device-tree/device MAC, or base MAC plus radio index, initializes TX management IDR state, calls `__ath11k_mac_register()` for each radio, and initializes the TX management empty waitqueue after successful registration. On partial failure it unregisters already registered radios and destroys the peer hash table.

`__ath11k_mac_unregister()` cancels regulatory/channel work, unregisters from mac80211, frees pending management TX IDR entries, destroys the IDR, frees channel arrays, interface combination limits, addresses, and clears the hw device pointer.

`ath11k_mac_unregister()` applies that per radio and then destroys the global peer rhash table.

`ath11k_mac_allocate()` allocates `struct ieee80211_hw` with `ath11k_ops` for each radio, wires `ar`, `ab`, `pdev`, `pdev_idx`, `lmac_id`, and WMI pointers, attaches WMI pdev state, caches chain masks/counts, installs the back-pointer in `pdev->ar`, and initializes locks, lists, completions, delayed work, work items, skb queues, monitor state, 11d scan state, and firmware stats.

`ath11k_mac_destroy()` frees firmware stats, frees each `ieee80211_hw`, and clears `pdev->ar`.

### STA keepalive

`ath11k_mac_vif_set_keepalive()` requires `ar->conf_mutex`, no-ops for non-STA vdevs or firmware without `WMI_TLV_SERVICE_STA_KEEP_ALIVE`, builds `struct wmi_sta_keepalive_arg`, and sends it through `ath11k_wmi_sta_keepalive()`.

## Control Flow

The runtime control flow has two major entry families:

- mac80211 invokes callbacks from `ath11k_ops`, such as remain-on-channel and station-state changes. Those callbacks translate mac80211 state into scan commands, peer commands, datapath setup/cleanup, regulatory refreshes, and local ath11k state transitions.
- ath11k core attach/probe logic invokes `ath11k_mac_allocate()`, then later `ath11k_mac_register()`. Registration builds all mac80211/cfg80211-visible capabilities before exposing the hardware with `ieee80211_register_hw()`. Teardown runs the inverse: unregister from mac80211, cancel work, free allocated cfg80211/mac80211 support structures, destroy peer tracking, then eventually free `ieee80211_hw`.

The registration path is sensitive to ordering. `ath11k_mac_setup_channels_rates()` must run before capability setup and registration because `wiphy->bands[]` is visible to cfg80211. `ieee80211_register_hw()` must happen before regulatory application and debugfs registration, but cleanup must undo registration before freeing memory referenced by wiphy fields.

## State and Persistence Behavior

Persistent software state in this chunk includes:

- `ar->scan`: scan/ROC state, completions, vdev id, ROC frequency, notification flag, and timeout work.
- `arsta`: per-station private state stored in mac80211 station private data, including work items, peer PS state, bandwidth tracking, EWMA RSSI, and allocated TX/RX stats.
- Peer tables: firmware/software peer lifetime is tracked through `ath11k_peer_create()`, `ath11k_peer_delete()`, datapath setup/cleanup, and the defensive peer rhash/list repair path.
- `ar->mac.sbands[]` and `wiphy->bands[]`: dynamically allocated channel arrays published for cfg80211/mac80211 use until unregister/error cleanup.
- `wiphy` capability state: interface modes, interface combinations, addresses, cipher suites, flags, features, ext features, scan limits, SAR capability, MBSSID/EMA limits, and iftype extended capabilities.
- Per-radio lifecycle state: locks, completions, work items, queues, monitor flags, 11d scan id/completion, TX management IDR, and firmware stats.
- Base-level state: `ab->free_vdev_map`, `ab->cc_freq_hz`, peer rhash table, and per-radio MAC addresses.

Firmware-visible persistent state is updated through WMI and peer/datapath calls: ROC scans, peer creation/deletion, peer authorization, mesh 4addr peer parameters, delayed vdev start/stop, regulatory channel list handling, country-code setting, WoW initialization, BIOS SAR capability exposure, and STA keepalive commands.

## Dependencies and Integration Points

This chunk depends on Linux wireless core APIs:

- mac80211: `struct ieee80211_ops`, `ieee80211_alloc_hw()`, `ieee80211_register_hw()`, `ieee80211_unregister_hw()`, `ieee80211_hw_set()`, station state machine, channel contexts, workqueue helpers, and private vif/sta data sizing.
- cfg80211/wiphy: supported bands, interface combinations, flags/features/ext features, cipher suites, SAR capabilities, channel flags, regulatory power type, OF frequency limits, and P2P/mesh/AP/STA iftypes.

Internal ath11k integration points include:

- WMI scan and peer commands: `ath11k_wmi_start_scan_init()`, `ath11k_start_scan()`, `ath11k_scan_stop()`, `ath11k_wmi_set_peer_param()`, `ath11k_wmi_sta_keepalive()`, WoW init, service bitmaps, and pdev WMI attachment.
- Peer/datapath: `ath11k_peer_create()`, `ath11k_peer_delete()`, peer rhash helpers, `ath11k_dp_peer_setup()`, and `ath11k_dp_peer_cleanup()`.
- Station association and rate control: `ath11k_station_assoc()`, `ath11k_station_disassoc()`, `ath11k_sta_rc_update_wk()`, bandwidth conversion, 4addr work, TX power, and CFR peer accounting.
- Regulatory and 6 GHz support: `ath11k_reg_init()`, `ath11k_regd_update()`, `ath11k_reg_set_cc()`, `ath11k_reg_handle_chan_list()`, `hal_reg_cap[]`, and 6 GHz client power type handling.
- Capability setup: HT/VHT/HE helpers, static channel/rate tables, hardware parameters, target resource macros, and service-map feature gates.
- Debug and management TX: debugfs registration/station stats toggles, TX management IDR cleanup, management-over-WMI work, and firmware stats.

## Risks

- ROC uses scan state shared with ordinary hardware scan. Incorrect locking or state restoration can strand `ar->scan.state`, lose ROC notifications, or make later scans return `-EBUSY`.
- The ROC timeout waits for firmware on-channel notification. Firmware/event regressions can produce user-visible P2P/off-channel failures and leave abort/timeout work racing with completion.
- Station add/remove unwinding crosses station counters, firmware peers, datapath peers, debugfs stats allocations, and delayed vdev start. A missing unwind step can leak peers, leave stale stats pointers, or desynchronize capacity accounting.
- `ath11k_mac_op_sta_state()` has a deliberate forced peer cleanup path after peer deletion. Changes around peer locking, rhash deletion, or `ar->num_peers` can introduce use-after-free, double-delete, or counter underflow risks.
- The 6 GHz authorization path depends on `vif->bss_conf.power_type`. Treating `IEEE80211_REG_UNSET_AP` as valid or skipping channel-list refresh can expose incorrect 6 GHz regulatory limits.
- Interface-combination structures share one `limits` allocation between combinations. Cleanup assumes `iface_combinations[0].limits` owns the allocation; changing allocation layout requires matching teardown changes.
- Channel arrays are dynamically duplicated into `ar->mac.sbands[]` and exposed through wiphy. Error and unregister paths must free exactly those arrays and must not leave stale `wiphy->bands[]` users after unregister.
- Registration advertises many features based on service bits and hardware params. Over-advertising can cause mac80211/cfg80211 to call unsupported paths; under-advertising can hide working firmware features.
- `ath11k_mac_register()` initializes `txmgmt_empty_waitq` after successful per-radio registration. Code that assumes it exists earlier in the registration sequence would be fragile.
- MAC address derivation increments byte 4 by radio index when no per-pdev address is available. Large radio counts or unusual base addresses could collide unless constrained elsewhere.

## Test and Validation Signals

Useful validation for this chunk should include:

- Build coverage with relevant configs: `CONFIG_PM`, `CONFIG_ATH11K_DEBUGFS`, `CONFIG_IPV6`, `CONFIG_MAC80211_MESH`, testmode, and 6 GHz-capable hardware params.
- Basic probe/remove testing should show successful `ieee80211_register_hw()`, clean unregister, no leaks from channel arrays, interface combinations, address lists, TX management IDR, firmware stats, or peer rhash tables.
- `iw phy`/cfg80211 inspection should verify advertised bands, disabled channel ranges, interface combinations, P2P/mesh modes, cipher suites, scan limits, remain-on-channel duration, ext features, MBSSID/EMA values, SAR capability, and 6 GHz capabilities.
- Remain-on-channel testing with P2P/listen/off-channel action frames should exercise successful on-channel completion, timeout handling, cancellation, concurrent scan rejection, and delayed timeout work cleanup.
- AP, STA, mesh, and ad-hoc station lifecycle tests should cover station add/remove, association/disassociation, authorization/deauthorization, mesh 4addr setting, station counter limits, peer creation/deletion, and datapath setup/cleanup.
- Fault injection on allocation failures in station stats, scan channel list, channel arrays, address lists, and interface combinations should verify cleanup labels and partial-registration rollback.
- 6 GHz STA association should verify AP power type handling, channel-list refresh, and rejection/logging for unset power type.
- Hardware/firmware feature matrix testing should verify service-gated features: random MAC scan, NLO/scheduled scan, WoW, ACK signal, BSS color, RTT/FTM responder, BIOS SAR, STA keepalive, and Ethernet encap/decap offload.
- Locking diagnostics such as lockdep/KASAN/KCSAN are valuable around `conf_mutex`, `data_lock`, `base_lock`, `tbl_mtx_lock`, station work cancellation, and peer cleanup.
