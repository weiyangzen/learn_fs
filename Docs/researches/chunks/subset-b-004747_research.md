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
