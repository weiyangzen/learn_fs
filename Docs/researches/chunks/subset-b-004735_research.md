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
