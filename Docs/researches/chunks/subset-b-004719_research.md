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
