# Research: subset-b-004833

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac80211.c

## Purpose
This file is the main mac80211 integration layer for Intel iwlwifi MVM when the legacy/non-MLD operation table is selected. It advertises hardware and wiphy capabilities, registers `iwl_mvm_hw_ops`, and implements most mac80211 callbacks for transmit, interface lifetime, channel contexts, station state transitions, scan, remain-on-channel, keys, AP/IBSS operation, power-save interactions, channel switch, statistics, FTM/PMSR, suspend hooks, and debug-trigger callbacks. It also contains common helpers used by the MLD operation table, so it is not purely legacy; functions such as station-state common flow, AP/IBSS common stop/start pieces, channel-context switching common code, HE/EHT station packet-extension parsing, multicast filter handling, and ROC common flow are shared by `mld-mac80211.c`.

## Important APIs, Types, And Functions
The central exported object is `const struct ieee80211_ops iwl_mvm_hw_ops`, wiring mac80211 callbacks to `iwl_mvm_mac_tx`, `iwl_mvm_mac_wake_tx_queue`, `iwl_mvm_mac_start`, `iwl_mvm_mac_stop`, `iwl_mvm_mac_add_interface`, `iwl_mvm_mac_remove_interface`, `iwl_mvm_bss_info_changed`, `iwl_mvm_mac_sta_state`, `iwl_mvm_mac_set_key`, channel-context callbacks, AP/IBSS callbacks, CSA/TDLS callbacks, survey/statistics callbacks, PMSR/FTM callbacks, and optional PM/debugfs callbacks.

Registration is driven by `iwl_mvm_mac_setup_register()`, which fills `ieee80211_hw` and `wiphy` capabilities from NVM, firmware TLVs, module parameters, transport limits, and regulatory support. It sets flags such as MLO support, fast-xmit, A-MPDU, power save, reorder buffer, checksum features, supported ciphers, WoWLAN, FTM/PMSR capabilities, TDLS, scan limits, bands, interface combinations, and per-object private data sizes.

Key runtime functions include `iwl_mvm_mac_start()`/`__iwl_mvm_mac_start()` and `iwl_mvm_mac_stop()`/`__iwl_mvm_mac_stop()` for firmware lifecycle; `iwl_mvm_restart_cleanup()` and `iwl_mvm_mac_reconfig_complete()` for hardware restart recovery; `iwl_mvm_mac_add_interface()` and `iwl_mvm_mac_remove_interface()` for MAC context and vif state; `iwl_mvm_mac_sta_state_common()` plus non-MLD callback bindings for station transitions; `__iwl_mvm_mac_set_key()` for hardware crypto setup; `iwl_mvm_add_chanctx()`, `iwl_mvm_assign_vif_chanctx()`, and `iwl_mvm_switch_vif_chanctx_common()` for PHY/channel binding; and `iwl_mvm_roc_common()` for remain-on-channel setup shared with MLD.

## Control Flow
Probe/registration calls `iwl_mvm_mac_setup_register()`, which advertises capabilities before `ieee80211_register_hw()`. When mac80211 starts the device, `iwl_mvm_mac_start()` takes `mvm->mutex`, optionally retries timeouts, obtains MEI ownership, handles fast resume, converts restart request flags into in-restart state, cleans internal state, then calls `iwl_mvm_up()`. Stop clears firmware-running state early, flushes async workers and ROC paths, cancels delayed work, then stops or fast-suspends the device and purges async handlers.

TX enters through `iwl_mvm_mac_tx()` for direct frames or `iwl_mvm_mac_wake_tx_queue()`/`iwl_mvm_mac_itxq_xmit()` for iTXQ-driven queues. The code drops RF-killed/offchannel-invalid frames, translates MLD management addresses when needed, treats most management frames as non-station broadcast, and calls station or non-station TX helpers. Wake queue uses `tx_request` atomic state to serialize dequeuing and schedules `add_stream_wk` for not-yet-ready station queues.

Interface addition initializes `iwl_mvm_vif`, allocates a MAC context, publishes `vif_id_to_mac`, delays AP/IBSS firmware upload until start_ap/join_ibss, and for station/P2P/monitor contexts sends MAC context, power, beacon-filter, TCM, MEI, and debugfs setup. AP/IBSS start sends the beacon template and MAC context in firmware-version-dependent order, binds the vif, adds broadcast/multicast internal stations, applies early keys, updates power/quotas/coex, and starts FTM responder if needed. Removal reverses debugfs, MEI, beacon filter ownership, MAC context, station allocations, and RCU pointers.

Station transitions are centralized in `iwl_mvm_mac_sta_state_common()`. NOTEXIST->NONE validates beacon interval/TDLS constraints, calls callback `add_sta`, initializes rates, and records AP sta. AUTH->ASSOC updates HE/link support and firmware station data. ASSOC->AUTHORIZED enables beacon filtering, marks authorized state, informs MEI, and updates station MFP/rate state. Reverse transitions disable beacon filtering, stop session protection, remove station state, and handle TDLS tid reservation/unreservation.

## State And Persistence
Persistent state is rooted in `struct iwl_mvm`: firmware status bits, `phy_ctxts`, scan status, multicast filter command, firmware key tables, RCU station maps, time-event lists, add-stream queue list, power/coex state, beacon-filter ownership, MEI/CSME pointers, statistics accumulators, and restart flags. Per-vif state lives in `struct iwl_mvm_vif` and per-link `struct iwl_mvm_vif_link_info`: MAC id/color, link ids, PHY context, AP station id, broadcast/multicast station objects, beacon stats, queue parameters, beacon-filter state, early AP keys, CSA flags, and probe response data. Per-station state in `struct iwl_mvm_sta` tracks link station objects, tx queues, aggregation state, pairwise cipher, PN tracking, authorization, sleep state, and firmware station ids.

Most hardware state is non-persistent across firmware reset and must be replayed through mac80211 restart callbacks. The file explicitly preserves accumulated beacon/radio counters, skips reprogramming invalid keys during restart, restores MU groups, clears firmware-only maps, resets PHY contexts, and wakes queues. Key and station RCU maps are carefully invalidated in pre-RCU removal and restart cleanup.

## Dependencies And Integration Points
This file is tightly integrated with Linux mac80211/cfg80211, the iwlwifi transport, firmware command APIs, NVM parsing, regulatory/LAR, MEI coexistence, scan, power, Bluetooth coexistence, time events, beacon filtering, TDLS, FTM/PMSR, debug triggers, D3/WoWLAN, TX/RX queue synchronization, and MVM station/MAC context helpers in adjacent files. Firmware capability checks select command versions and feature exposure throughout; transport properties select checksum, DMA, TX API, RX API, and device-family-specific behavior.

## Risks
The largest risks are ordering and lifetime bugs: MAC context, binding, beacon template, internal stations, queues, power updates, and quotas must be sequenced exactly as firmware expects, with device-family and firmware-version exceptions. Restart paths must not leak stale station ids, key indexes, PHY references, RCU pointers, or delayed work. Key handling has complex fallback behavior: failures can intentionally return success for old TX APIs but not new TX APIs; WEP and AP early keys have special handling; PN tracking allocations must be undone on failure. Channel switch and ROC paths depend on time-event cleanup and correct TX blocking/unblocking. Shared helpers used by MLD must remain compatible with both operation tables.

## Test Signals
Useful signals are successful `ieee80211_register_hw()` and interface creation across station, AP, P2P client/GO/device, monitor, and IBSS modes; association/disassociation with HE/EHT, beacon filtering, UAPSD, TDLS, and MFP; AP start/stop with beacon protection and early keys; firmware restart recovery with preserved counters and replayed keys/stations; channel context add/change/switch, CSA, ROC, scan/sched-scan cancellation races, and multicast filter updates. Lockdep, KASAN, RCU diagnostics, DMA debugging, firmware assert/recovery tests, and mac80211 hwsim-style callback coverage are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-key.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-key.c

## Purpose
Implements security key programming for the newer MLD firmware security command path. It translates mac80211 key configuration into `SEC_KEY_CMD` add/remove commands, chooses the firmware station mask that should own each key, builds firmware key flags for cipher, multicast, MFP, key size, and SPP A-MSDU, and handles AP-link/client-link group key corner cases.

## Important APIs, Types, And Functions
`iwl_mvm_get_sec_sta_mask()` selects target firmware station ids for pairwise, GTK, IGTK, BIGTK, AP, and station modes. `iwl_mvm_get_sec_flags()` converts `ieee80211_key_conf` cipher and flags to `IWL_SEC_KEY_FLAG_*` bits. `iwl_mvm_mld_send_key()` constructs the ADD flavor of `struct iwl_sec_key_cmd`, including WEP key offset quirks, TKIP MIC keys, TX PN, and duplicate WEP unicast/multicast programming. `iwl_mvm_sec_key_add()` is the public add helper used by `mac80211.c` when `SEC_KEY_CMD` exists. `iwl_mvm_sec_key_del()`, `iwl_mvm_sec_key_del_pasn()`, and private delete helpers send REMOVE commands. `iwl_mvm_sec_key_remove_ap()` iterates mac80211 keys to asynchronously remove AP group keys for a link.

## Control Flow
On key add, `__iwl_mvm_mac_set_key()` in `mac80211.c` calls `iwl_mvm_sec_key_add()` when firmware exposes `SEC_KEY_CMD`. The add path computes the station mask and flags, removes any old IGTK tracked on the same link, sends the add command, records the active IGTK pointer if relevant, and sets `hw_key_idx` to a non-invalid dummy value because this API does not allocate legacy hardware key indexes. Delete follows the same mask/flag computation, clears tracked IGTK state, sends remove, and sends a second WEP remove with toggled multicast flag when required. AP key removal during link teardown walks mac80211 keys and skips pairwise keys, already-invalid keys, and keys for other links.

## State And Persistence
The file persists little state directly. It updates per-link `mvmvif->link[link_id]->igtk` for active IGTK/BIGTK-like management protection keys and uses `keyconf->hw_key_idx` as a validity marker for mac80211/restart flows. The firmware stores actual key material and station-mask association. The add command seeds firmware TX PN from `keyconf->tx_pn`; RX PN tracking for pairwise data keys is still allocated by the common key path in `mac80211.c`.

## Dependencies And Integration Points
Depends on mac80211 key semantics, MVM vif/link/station mapping, `iwl_mvm_sta_fw_id_mask()` from `mld-sta.c`, firmware `SEC_KEY_CMD` structures in `fw/api/datapath.h`, and MVM command submission. It is selected by the common key callback in `mac80211.c` based on firmware command version, so old and new key APIs coexist.

## Risks
The target station mask is the highest-risk part: AP group keys must land on bcast or mcast internal stations by key index, client group keys may need the AP station without a mac80211 `sta`, and removal may happen after the AP station pointer has already been cleared. A zero station mask is rejected, so link teardown ordering can surface as key removal failures. IGTK pointer replacement is stateful and must stay synchronized with firmware deletion. WEP double-programming/removal can leave asymmetric state if the second command fails. Async AP key removal marks keys invalid after best-effort command submission, so firmware failure is not strongly recovered here.

## Test Signals
Exercise WPA2/WPA3 pairwise keys, GTK rekey, IGTK/BIGTK installation and replacement, beacon protection, AP group keys, station group keys with and without `sta`, PASN key delete, WEP compatibility, and link teardown after AP station removal. Firmware logs should show successful `SEC_KEY_CMD` add/remove; mac80211 should not repeatedly try to remove already-invalid keys. Restart tests should verify dummy `hw_key_idx` and IGTK tracking do not cause duplicate stale keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac.c

## Purpose
Builds and sends MLD firmware MAC context commands. It is the MLD replacement for legacy MAC context command construction: given a mac80211 vif, it fills `MAC_CONFIG_CMD` for station, AP/GO, monitor, P2P device, and IBSS contexts, including MLD address, MAC type, filter flags, association state, HE/EHT support, P2P CT window, TWT policy, and NIC ACK policy.

## Important APIs, Types, And Functions
The main public helpers are `iwl_mvm_mld_mac_ctxt_add()`, `iwl_mvm_mld_mac_ctxt_changed()`, and `iwl_mvm_mld_mac_ctxt_remove()`. Internally, `iwl_mvm_mld_mac_ctxt_cmd_common()` fills shared `struct iwl_mac_config_cmd_v3` fields and scans all active `vif->link_conf[]` entries to set HE/EHT support. Type-specific builders are `iwl_mvm_mld_mac_ctxt_cmd_sta()`, `iwl_mvm_mld_mac_ctxt_cmd_listener()`, `iwl_mvm_mld_mac_ctxt_cmd_ibss()`, `iwl_mvm_mld_mac_ctxt_cmd_p2p_device()`, and `iwl_mvm_mld_mac_ctxt_cmd_ap_go()`. `iwl_mvm_mld_mac_ctx_send()` dispatches by interface type, and `iwl_mvm_mld_mac_ctxt_send_cmd()` wraps command submission and error logging.

## Control Flow
Add validates that the MAC is not already uploaded, sends an ADD command with association forced off, restores last non-QoS sequence state for D3 resume cases, and marks `mvmvif->uploaded`. Change validates the context is uploaded and sends MODIFY with optional `force_assoc_off`, which is used by common station/channel-switch flows to temporarily suppress association state. Remove sends a minimal REMOVE command with id/color and clears `uploaded` only after firmware accepts it.

For station contexts, the builder accepts group frames, sets P2P CT window when needed, marks association and AID unless forced off, applies high-priority coexistence policy before authorization, accepts beacons while unassociated, accepts P2P probe requests when requested, and adds TWT policy when HE is enabled. Monitor contexts use promiscuous/control/management/beacon/probe/group filters. P2P device contexts use extended discovery capability and accept control/management frames. AP/GO contexts delegate filter flag construction to common AP helper logic.

## State And Persistence
The file mutates only the per-vif `uploaded` flag directly, but commands serialize persistent firmware MAC context state keyed by `mvmvif->id`. It reads vif association, AID, P2P, HE/EHT, probe request registration, and authorization state. HE/EHT flags are aggregated from current link configurations, so MLD link state in mac80211 drives firmware MAC-level capabilities.

## Dependencies And Integration Points
Depends on `mvm.h`, mac80211 vif/link structures, firmware `MAC_CONFIG_CMD` versions, common helper functions from the legacy MAC context implementation, module parameters disabling 11ax/11be, and MVM command submission. It is called by `mld-mac80211.c` for MLD mac80211 callbacks and by common station-state code through a callback table.

## Risks
Firmware command version handling is strict: versions above 3 warn and return without filling the command, so future API changes require updates here. MAC type support is limited to known interface types; unsupported types return `-EOPNOTSUPP`. HE/EHT capability aggregation runs under RCU and assumes link configuration is coherent with vif lifetime. Incorrect `force_assoc_off` use can leave firmware accepting or rejecting frames with the wrong association state. The `uploaded` flag must match firmware state; failed add/remove paths need callers to unwind link and vif state correctly.

## Test Signals
Create and remove station, AP/GO, P2P device, monitor, and IBSS interfaces under MLD firmware. Validate association transitions update MAC_CONFIG_CMD fields, P2P probe request filtering works, AP/GO filter flags accept the expected management frames, and HE/EHT capability exposure follows active links and module disables. Restart and D3 resume should verify `uploaded` state and sequence restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac80211.c

## Purpose
Provides the MLD-specific mac80211 operation table `iwl_mvm_mld_hw_ops`. It reuses many common callbacks from `mac80211.c` but replaces interface, link, station, channel-context, AP/IBSS, remain-on-channel, per-link BSS change, and QoS handling with link-aware firmware flows using MLD MAC/link/station commands.

## Important APIs, Types, And Functions
`iwl_mvm_mld_hw_ops` is the exported ops table. MLD-specific callbacks include `iwl_mvm_mld_mac_add_interface()`, `iwl_mvm_mld_mac_remove_interface()`, `iwl_mvm_mld_assign_vif_chanctx()`, `iwl_mvm_mld_unassign_vif_chanctx()`, `iwl_mvm_mld_switch_vif_chanctx()`, `iwl_mvm_mld_start_ap()`/`stop_ap()`, `iwl_mvm_mld_start_ibss()`/`stop_ibss()`, `iwl_mvm_mld_mac_sta_state()`, `iwl_mvm_mld_link_info_changed()`, `iwl_mvm_mld_vif_cfg_changed()`, `iwl_mvm_mld_mac_conf_tx()`, and `iwl_mvm_mld_roc()`. It also implements `iwl_mvm_send_ap_tx_power_constraint_cmd()` for 6 GHz AP/client TPE constraints and uses common operation callback structs for station-state, channel switching, and ROC.

## Control Flow
Interface add initializes `mvmvif`, allocates a MAC context id, publishes `vif_id_to_mac`, sends MLD MAC context ADD, disables beacon filtering, chooses beacon-filter ownership for a station vif, attaches deflink as link 0, adds the initial firmware link, updates power, adds TCM/debugfs/MEI state, and enables monitor FCS handling when relevant. Removal flushes P2P ROC state, removes TCM/debugfs/MEI state, updates power, removes or disables the firmware link, removes the MAC context, clears RCU mappings/probe response data, and clears monitor FCS state.

Channel assignment maps mac80211 chanctx private id to an MVM PHY context, sets the per-link `phy_ctxt`, sends a link update first with PHY context id, then activates the link if mac80211 marks it active. Station links also send 6 GHz AP TX power constraints, while monitor links add a sniffer station. Unassignment deactivates the firmware link, removes sniffer stations, optionally blocks AP TX during channel switch, and cleans the PHY pointer unless the switch flow intentionally keeps firmware state for CSA. The switch callback reuses the common swap/reassign code from `mac80211.c` with MLD assign/unassign functions.

AP/IBSS start sends TPE constraints for AP, beacon template, non-active link parameters, multicast station, broadcast station, common AP/IBSS state, P2P device MAC updates, coex updates, TDLS teardown for DCM, and FTM responder restart. Stop removes common AP/IBSS state, P2P updates, responder state, bcast/mcast stations, and power state. Station state transitions delegate to common `iwl_mvm_mac_sta_state_common()` but use MLD add/update/remove station and MAC context callbacks.

MLD separates per-link changes from per-vif changes. `link_info_changed` updates link active state during link switch, QoS, ERP slot/rates, HE/EHT/puncturing, MAC context, BSSID, common station BSS behavior, AP beacon templates, and TX power. `vif_cfg_changed` handles association-level state, statistics, periodic system stats for link selection, power, session protection, disassociation cleanup, multicast, SMPS workaround, and idle scan stop.

## State And Persistence
Persistent state spans per-vif `link[]` entries with firmware link ids, active flags, PHY contexts, queue parameters, bcast/mcast/sniffer stations, AP station ids, BSSID, and beacon stats. It updates `mvm->vif_id_to_mac`, `bf_allowed_vif`, `p2p_device_vif`, `monitor_on`, hardware FCS flag, CSME/MEI netdev state, and periodic statistics requests. Firmware state includes MAC contexts, link contexts, station contexts, TPE constraints, beacon templates, and internal stations. Restart flows rely on common counters and status bits from `mac80211.c` plus MLD station/link reallocation.

## Dependencies And Integration Points
Depends on the common mac80211 callbacks and helper APIs in `mac80211.c`, MLD MAC command helpers from `mld-mac.c`, station helpers from `mld-sta.c`, link helpers declared in `mvm.h`, firmware MAC/link/PHY/data-path commands, cfg80211/mac80211 MLO link APIs, FTM, scan, power, BT coexistence, MEI, debugfs, and time-event/ROC code.

## Risks
MLD correctness depends on keeping mac80211 active-link state, MVM per-link state, and firmware link context state synchronized. Error unwinds in interface add and AP start must remove MAC/link/beacon-filter state in the right order. Link switching deliberately keeps or clears PHY/link state depending on CSA mode, making regressions easy. Some code has FIXME notes for per-link FTM responder and misbehaving AP handling. Periodic statistics are enabled for associated MLD station operation and must be disabled on disassociation. Monitor mode toggles the shared RX_INCLUDES_FCS hardware flag and must be paired with removal.

## Test Signals
Test MLD station association with multiple links, link activation/deactivation, link switch/CSA, 6 GHz TPE constraints, HE/EHT QoS and puncturing updates, AP/GO start/stop, P2P device ROC, monitor mode, and firmware restart. Signals include correct `MAC_CONFIG_CMD`, link update, station config, bcast/mcast station add/remove, periodic statistics toggling, preserved beacon counters, and absence of stale `vif_id_to_mac` or link pointers under RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-sta.c

## Purpose
Implements MLD firmware station management for iwlwifi MVM. It handles firmware station ids for peer links and internal stations, sends `STA_CONFIG_CMD`, removes stations with `STA_REMOVE_CMD`, creates and destroys TVQM queues, allocates per-link `iwl_mvm_link_sta` objects, restores station state after restart, and provides MLD variants of broadcast, multicast, sniffer, auxiliary, peer add/update/remove, and TX disable helpers.

## Important APIs, Types, And Functions
`iwl_mvm_sta_fw_id_mask()` returns a station mask for key and queue commands. `iwl_mvm_mld_send_sta_cmd()` submits versioned `STA_CONFIG_CMD`. Internal station helpers include `iwl_mvm_mld_add_int_sta_with_queue()`, `iwl_mvm_mld_add_bcast_sta()`, `iwl_mvm_mld_add_mcast_sta()`, `iwl_mvm_mld_add_snif_sta()`, `iwl_mvm_mld_add_aux_sta()`, and matching remove functions. Peer station helpers include `iwl_mvm_mld_alloc_sta_links()`, `iwl_mvm_mld_cfg_sta()`, `iwl_mvm_mld_add_sta()`, `iwl_mvm_mld_update_sta()`, `iwl_mvm_mld_rm_sta()`, and `iwl_mvm_mld_rm_sta_id()`. TX disable APIs are `iwl_mvm_mld_sta_modify_disable_tx()`, `iwl_mvm_mld_sta_modify_disable_tx_ap()`, and `iwl_mvm_mld_modify_all_sta_disable_tx()`.

## Control Flow
Internal station add allocates a driver station id, sends either `AUX_STA_CMD` or `STA_CONFIG_CMD`, then enables a TVQM queue because newer firmware requires stations to exist before queues. On queue-enable failure it removes the firmware station and deallocates driver state. Removal optionally flushes the station, removes the scheduler queue through `SCD_QUEUE_CONFIG_CMD` when required, frees the transport queue, sends `STA_REMOVE_CMD`, and deallocates the internal station.

Peer station add allocates one `iwl_mvm_link_sta` and firmware id per active mac80211 link unless in hardware restart. It initializes common station data with `iwl_mvm_sta_init()`, updates station data, then sends `STA_CONFIG_CMD` for every active link with MLD address, link address, link id, station type, AID, MFP, MIMO/SMPS, A-MPDU density/size, UAPSD, HE packet extension, HTC flags, ACK support, and trigger random allocation. In station-vif mode it records each link's AP station id. Error handling removes firmware stations already added and frees all allocated link objects.

Restart recovery uses `iwl_mvm_alloc_sta_after_restart()` to reconfigure existing link station ids and restore RCU mappings before reallocating queues. Peer removal flushes all active link tids, waits for queues to empty, disables all station queues, calls common station deletion, removes firmware station ids per link, and frees link objects. Removing by id is a lower-level path used when the caller already knows the firmware id.

## State And Persistence
The file owns per-link station mappings: `mvm_sta->link[link_id]`, `mvm->fw_id_to_mac_id[sta_id]`, and `mvm->fw_id_to_link_sta[sta_id]`. It persists internal station ids and queues in vif link state (`bcast_sta`, `mcast_sta`, `mgmt_queue`, `cab_queue`), global MVM state (`aux_sta`, `aux_queue`, `snif_sta`, `snif_queue`, `p2p_dev_queue`), and per-station TID queue ids. Firmware state persists station contexts and queues until explicit removal or restart. `ap_sta_id` in each vif link points to the peer station id used for station-mode AP link operations.

## Dependencies And Integration Points
Depends on mac80211 MLO active-link iteration, MVM station structures in `sta.h`, time-sync indirectly, TVQM queue helpers, transport queue free, firmware `STA_CONFIG_CMD`, `STA_REMOVE_CMD`, `AUX_STA_CMD`, `SCD_QUEUE_CONFIG_CMD`, common rate/AMPDU/HE helpers from `mac80211.c`, and key targeting from `mld-key.c`. It is used by `mld-mac80211.c` station-state, AP/IBSS, monitor, P2P ROC, and CSA/TX-blocking flows.

## Risks
Although `iwl_mvm_sta_fw_id_mask()` accepts a `filter_link_id`, this implementation currently returns only `mvmsta->deflink.sta_id`, so multi-link key/queue mask behavior depends on current firmware expectations and may need expansion. Allocation and RCU publication must stay paired; partially added multi-link stations are carefully unwound, but failures during later per-link removal return only the last remove result. Queue removal ordering is firmware-sensitive, and `sta_remove_requires_queue_remove` changes behavior. Restart recovery assumes old link station ids remain meaningful enough to rebuild firmware and queue state. TX disable helpers use async commands and iterate global station id arrays, so stale mappings would affect unrelated vifs.

## Test Signals
Create/remove MLD peer stations with one and multiple active links, AP and station roles, TDLS rejection paths through common state, restart recovery with queue reallocation, AP/GO bcast/mcast station lifetimes, monitor sniffer station lifetime, P2P/HS20 auxiliary station ROC, queue removal with and without `sta_remove_requires_queue_remove`, and CSA TX disable/enable. Watch firmware logs for `STA_CONFIG_CMD`, `STA_REMOVE_CMD`, queue config errors, empty-queue waits, and RCU/lockdep reports around station removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mld-sta.c -->
