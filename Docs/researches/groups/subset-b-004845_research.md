# subset-b-004845 research

This grouped report covers the mwifiex firmware ABI, common driver state, initialization, management-IE handling, association/ad-hoc join logic, and main lifecycle paths under `sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex`. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/fw.h

## Purpose
`fw.h` is the mwifiex firmware ABI contract. It defines packed download headers, transmit/receive packet descriptors, command IDs, TLV IDs, event IDs, capability bit helpers, host command payloads, and the top-level `struct host_cmd_ds_command` union used by command preparation and response handling across the driver.

## Important APIs, Types, and Functions
The file is type and macro heavy rather than function based. Core framing types are `struct mwifiex_fw_header`, `struct mwifiex_fw_data`, `struct txpd`, `struct rxpd`, `struct uap_txpd`, `struct uap_rxpd`, `struct mwifiex_ie_types_header`, and `struct host_cmd_ds_gen`. Command payloads include hardware spec, scan, association, ad-hoc start/join, key material v1/v2/WEP, power save, host sleep, WMM status, UAP system config, TDLS, coalesce, GTK rekey, channel report, station configure, packet aggregation, and config-data structures. Important constants include `HostCmd_CMD_*`, `EVENT_*`, `TLV_TYPE_*`, `S_DS_GEN`, `MWIFIEX_AUTO_IDX_MASK`, `MWIFIEX_DELETE_MASK`, `MGMT_MASK_*`, `ISSUPP_*`, `IS_SUPPORT_MULTI_BANDS()`, `HostCmd_SET_SEQ_NO_BSS_INFO()`, and event/BSS extraction macros.

## Control Flow
Runtime control flow in other files is built around these layouts. Firmware download code sends `mwifiex_fw_data` chunks headed by `mwifiex_fw_header`; TX/RX paths prepend or parse `txpd`/`rxpd`; command builders fill `host_cmd_ds_command.command`, `.size`, `.seq_num`, and the relevant `params` union member; response handlers reinterpret the same union with `HostCmd_RET_BIT` response IDs. Scan, join, UAP, power, and key paths append variable TLVs by writing `mwifiex_ie_types_header` followed by packed payload data.

## State and Persistence
The header defines volatile wire state, not persistent storage. State survives only when copied into `mwifiex_adapter` or `mwifiex_private` fields in `main.h`, or when firmware retains configured state. Packed little-endian fields are the source of truth at the firmware boundary, so callers must use `cpu_to_le*()` and `le*_to_cpu()` consistently.

## Dependencies and Integration Points
`fw.h` depends on Linux Ethernet, WLAN, cfg80211, and 802.11 structures pulled through surrounding mwifiex headers. It integrates with `init.c` for firmware download and hardware-spec parsing, `main.c` for sleep-confirm setup and packet paths, `join.c` for association/ad-hoc command construction, `ie.c` for custom management IE TLVs, and command/event handlers throughout the mwifiex directory.

## Risks and Edge Cases
The main risk is binary ABI drift. Many structures are `__packed`, include flexible arrays, or carry explicit comments that fields must not be added, especially `struct adhoc_bss_desc`. Wrong endian conversion, size accounting, or TLV length calculation can corrupt firmware commands. Command union growth must stay within allocated command buffers. Capability macros encode firmware bit positions; changing them without firmware coordination breaks feature gating. Management IE indexes and masks are shared with firmware and must match `ie.c` semantics.

## Test Signals
Useful signals include successful firmware download and `GET_HW_SPEC`, correct command sizes in association, scan, UAP, and power-save commands, event dispatch for all expected `EVENT_*` values, stable key install/remove across key API versions, successful custom IE add/delete, valid sleep-confirm handling, and no firmware rejects caused by malformed TLV lengths or command IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ie.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ie.c

## Purpose
`ie.c` manages custom management information elements for mwifiex AP/UAP operation. It parses cfg80211 beacon data, extracts selected vendor and generic IEs, allocates firmware management-IE indexes, updates the per-interface `priv->mgmt_ie[]` cache, sends UAP custom IE configuration to firmware, and deletes configured IEs during teardown or AP reconfiguration.

## Important APIs, Types, and Functions
Public entry points are `mwifiex_set_mgmt_ies()` and `mwifiex_del_mgmt_ies()`. Internal helpers include `mwifiex_ie_index_used_by_other_intf()`, `mwifiex_ie_get_autoidx()`, `mwifiex_update_autoindex_ies()`, `mwifiex_update_uap_custom_ie()`, `mwifiex_update_vs_ie()`, `mwifiex_set_mgmt_beacon_data_ies()`, and `mwifiex_uap_parse_tail_ies()`. It uses `struct mwifiex_ie`, `struct mwifiex_ie_list`, `struct ieee_types_header`, `struct ieee80211_vendor_ie`, management subtype masks, `MWIFIEX_AUTO_IDX_MASK`, `MWIFIEX_DELETE_MASK`, and `TLV_TYPE_MGMT_IE`.

## Control Flow
`mwifiex_set_mgmt_ies()` first parses beacon tail IEs through `mwifiex_uap_parse_tail_ies()`, then handles beacon/probe/assoc response vendor IEs through `mwifiex_set_mgmt_beacon_data_ies()`. Tail parsing skips IEs generated by firmware or BSS config, skips Microsoft WMM, preserves generic IEs and WPA vendor IE, and pushes them as one custom IE for beacon, probe response, and association response masks. Vendor parsing collects WPS and P2P vendor IEs from cfg80211 beacon/probe/assoc buffers. `mwifiex_update_uap_custom_ie()` packs one or more `mwifiex_ie` records into an `mwifiex_ie_list`; `mwifiex_update_autoindex_ies()` assigns indexes or validates deletes, updates `priv->mgmt_ie[]`, and for UAP sends `HostCmd_CMD_UAP_SYS_CONFIG` with `UAP_CUSTOM_IE_I`.

## State and Persistence
State is in each `mwifiex_private`: `mgmt_ie[]`, `beacon_idx`, `proberesp_idx`, `assocresp_idx`, and `gen_idx`. Indexes are firmware-facing and shared across adapter interfaces, so new indexes cannot be reused if another `priv` has a live IE at the same slot. There is no disk persistence; state is rebuilt from cfg80211 AP settings and cleared by delete paths.

## Dependencies and Integration Points
The file depends on cfg80211 IE scanners, UAP command support, firmware TLV layouts from `fw.h`, and `main.h` private/adapter state. It is driven by AP start/change paths in cfg80211 code and feeds firmware UAP system configuration.

## Risks and Edge Cases
Length validation is critical because all collected IEs share `IEEE_MAX_IE_SIZE`. Auto-indexing can fail when all firmware IE slots are used or when a slot belongs to another interface. Deletion is rejected if the target index is used by another interface. The code intentionally omits firmware-generated IEs; adding skipped IDs blindly can duplicate SSID, rates, country, HT/VHT, WMM, or WPA content. Some helper return values from `mwifiex_update_vs_ie()` are not checked in every call site, so allocation/length failures rely on later state remaining consistent.

## Test Signals
Test AP beacon/probe/assoc response contents with WPS, P2P, WPA, and generic vendor IEs; verify repeated beacon updates reuse or allocate indexes correctly; run multi-interface AP/P2P scenarios to catch index sharing conflicts; validate oversized IE rejection; and confirm `mwifiex_del_mgmt_ies()` removes all firmware custom IEs and resets indexes to `MWIFIEX_AUTO_IDX_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/init.c

## Purpose
`init.c` initializes and shuts down mwifiex adapter/private runtime state, command buffers, work-related locks/lists, firmware defaults, BSS priority tables, wakeup/device-dump support, and the common firmware download sequence.

## Important APIs, Types, and Functions
Exported/common functions are `mwifiex_init_priv()`, `mwifiex_set_trans_start()`, `mwifiex_wake_up_net_dev_queue()`, `mwifiex_stop_net_dev_queue()`, `mwifiex_init_lock_list()`, `mwifiex_init_fw()`, `mwifiex_free_priv()`, `mwifiex_shutdown_drv()`, `mwifiex_dnld_fw()`, and `mwifiex_free_cmd_buffers()`. Internal helpers include `mwifiex_add_bss_prio_tbl()`, `wakeup_timer_fn()`, `fw_dump_work()`, `mwifiex_allocate_adapter()`, `mwifiex_init_adapter()`, `mwifiex_invalidate_lists()`, `mwifiex_adapter_cleanup()`, and `mwifiex_delete_bss_prio_tbl()`.

## Control Flow
Firmware bring-up through `mwifiex_init_fw()` sets hardware status to initializing, allocates command and sleep-confirm buffers, seeds adapter defaults, initializes every `mwifiex_private`, and sends per-interface STA init commands unless manufacturing mode is active. `mwifiex_init_adapter()` prepares sleep-confirm command contents, power-save defaults, scan timing, host-sleep defaults, firmware capability placeholders, interface limits, wakeup timer, and firmware dump work. `mwifiex_init_lock_list()` initializes all adapter/private spinlocks, command/scan queues, RX/TX queues, BSS priority lists, WMM RA lists, BA/reorder lists, station/TDLS lists, and ACK-status IDRs. Shutdown cancels current commands, frees per-priv TX/RX state, drains TX/RX queues, wakes waiters, cancels timers/work, and marks hardware not ready.

## State and Persistence
State is entirely in memory and hardware/firmware. `mwifiex_adapter` holds command queues, power state, scan defaults, firmware capability state, wait queues, sleep confirmation skb, wakeup timer, device dump work, and interface limits. Each `mwifiex_private` holds connection/security/WMM/rate/scan/IE defaults. BSS priority nodes are dynamically allocated and later removed from adapter priority lists.

## Dependencies and Integration Points
The file relies on command allocation helpers, WMM and 11h initialization, bus `if_ops` callbacks, skbuff queues, Linux timers/workqueues, netdev queue APIs, firmware request/download paths, and command/event wait queues. `mwifiex_dnld_fw()` delegates bus-specific firmware status, winner arbitration, and programming to SDIO/PCIe/USB operations.

## Risks and Edge Cases
Initialization has many partially allocated states; missing cleanup on an intermediate failure can leak command buffers or sleep-confirm skbs. `mwifiex_invalidate_lists()` uses `list_del()` during free, so it assumes list heads were initialized and not already invalidated. Wakeup timeout forces hardware reset if firmware does not respond. Firmware download winner arbitration can skip programming on non-winning functions and must still poll long enough for firmware readiness. Shutdown drains RX by indexing `adapter->priv[rx_info->bss_num]`, so corrupted RX metadata would be risky.

## Test Signals
Validate cold probe, firmware-already-running probe, multi-function winner/non-winner firmware download, manufacturing mode, reset/reinit cycles, wakeup timer card reset, clean module removal with zero pending RX/TX/CMD counters, sleep-confirm command contents, and netdev queue stop/wake behavior under TX timeout and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ioctl.h

## Purpose
`ioctl.h` defines user/configuration-facing mwifiex data structures used by command preparation, cfg80211 glue, debug reporting, power management, AP configuration, register/memory access, custom IE handling, coalescing, MEF, and TDLS operations. Despite the name, these structures are shared internal request/result contracts rather than a standalone ioctl implementation.

## Important APIs, Types, and Functions
The header defines scan types and `struct mwifiex_user_scan`, multicast modes and `struct mwifiex_multicast_list`, band constants, WPA/WEP/AP configuration types (`struct mwifiex_uap_bss_param`, `struct wpa_param`, `struct wep_key`), debug output (`struct mwifiex_debug_info`), reorder/BA table snapshots, encryption keys (`struct mwifiex_ds_encrypt_key`), power and host-sleep config (`struct mwifiex_ds_pm_cfg`, `mwifiex_ds_hs_cfg`, `mwifiex_ds_auto_ds`), 11n/11ac/antenna config, register/eeprom/memory access, generic IE buffers, RSSI subscription, MEF and packet coalescing rules, and TDLS operation parameters.

## Control Flow
Other mwifiex modules populate these structures from cfg80211/netdev/debugfs requests and pass them into `mwifiex_send_cmd()` or status functions. For example multicast updates in `main.c` fill `mwifiex_multicast_list`; AP start code fills `mwifiex_uap_bss_param`; debugfs gathers `mwifiex_debug_info`; key paths consume `mwifiex_ds_encrypt_key`; power paths use `mwifiex_ds_pm_cfg`; custom IE code respects `IEEE_MAX_IE_SIZE` and `MWIFIEX_IE_HDR_SIZE`.

## State and Persistence
The header itself stores no state. Its structs mirror transient request payloads or cached runtime fields inside `mwifiex_private` and `mwifiex_adapter`. Some values, such as WEP keys, WPA passphrases, MEF entries, GTK replay counters, and host-sleep conditions, may be sent to firmware and persist there until reconfigured or firmware resets.

## Dependencies and Integration Points
`ioctl.h` depends on cfg80211 types, Linux WLAN key size constants, mwifiex firmware structures, and `MAX_NUM_TID`/BA constants shared with `main.h`. It is included before or alongside `fw.h`/`main.h` in command, cfg80211, debugfs, power, AP, TDLS, and scan code.

## Risks and Edge Cases
Many structures contain fixed maximum arrays: multicast list 32 addresses, generic IE 256 bytes, EEPROM 256 bytes, MEF 10 filters, coalesce 8 rules, and reorder windows 64 slots. Callers must validate counts before copying. Several fields carry sensitive material, so dumps and error paths should avoid exposing keys/passphrases. Pointer members such as MEF entries and TDLS extension/rate/capability buffers require lifetime discipline by callers.

## Test Signals
Exercise multicast modes, AP security combinations, scan config boundaries, debug info generation, power/host-sleep toggles, memory/register/eeprom access bounds, custom IE size limits, MEF/coalesce rule maxima, TDLS parameter construction, and key installation/removal including WAPI/IGTK/current WEP flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/join.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/join.c

## Purpose
`join.c` builds and handles firmware commands for infrastructure association, ad-hoc start/join, and deauthentication. It translates cfg80211 scan/BSS/security state into mwifiex firmware command layouts and updates driver connection state after firmware responses.

## Important APIs, Types, and Functions
Public functions include `mwifiex_cmd_802_11_associate()`, `mwifiex_ret_802_11_associate()`, `mwifiex_cmd_802_11_ad_hoc_start()`, `mwifiex_cmd_802_11_ad_hoc_join()`, `mwifiex_ret_802_11_ad_hoc()`, `mwifiex_associate()`, `mwifiex_adhoc_start()`, `mwifiex_adhoc_join()`, `mwifiex_deauthenticate()`, `mwifiex_deauthenticate_all()`, and `mwifiex_band_to_radio_type()`. Important helpers append TLVs: generic IE, WPS, WAPI, WPA/WPA2 RSN IE, TSF timestamps, WMM, vendor-specific IE, 11n, 11ac, 11h, channel list, host MLME, and SAE PWE mode.

## Control Flow
Association command preparation stores `priv->attempted_bss_desc`, writes peer address/listen/beacon fields, appends SSID/PHY/SS/rates/auth/channel TLVs, conditionally adds host MLME and SAE H2E data, appends security and capability TLVs, adds WMM/generic/TSF/11h data, computes command size, and writes a masked capability bitmap. The response handler validates the attempted BSS, supports host-MLME wrapped responses, stores association response bytes, maps failures to status codes, and on success updates `media_connected`, current BSS descriptor, WMM state, RSSI/noise history, beacon cache, RA list, carrier, queues, and port gating for WPA/WPA2. Ad-hoc start/join build firmware IBSS descriptors and channel/security/HT/vendor TLVs, while the shared response handler sets `ADHOC_STARTED` or `ADHOC_JOINED` and brings carrier up.

## State and Persistence
Persistent runtime state is in `mwifiex_private`: attempted/current BSS descriptors, current rates, security flags, WMM enablement, RSSI/noise averages, association response cache, ad-hoc state/channel, port-open/scan-block, and beacon cache. Firmware stores the actual association/IBSS/deauth state. Generic and WPS IE buffers are consumed and cleared after use.

## Dependencies and Integration Points
The file depends on command layouts from `fw.h`, state from `main.h`, security constants from cfg80211/802.11 headers, WMM and BA setup, 11n/11ac/11h helpers, scan-derived `mwifiex_bssdescriptor`, netdev carrier/queue APIs, cfg80211 disconnect callbacks, and host MLME management-frame registration.

## Risks and Edge Cases
Buffer pointer arithmetic must match command buffer capacity and TLV sizes. `strlen(out_rates)` is used on rate arrays that rely on zero termination. Fixed data-rate validation can fail association if the AP lacks the selected rate. Association response size subtracts `S_DS_GEN` and must not underflow on malformed firmware responses. Host-MLME response parsing depends on BSSID matching. Ad-hoc start mutates too-long requested SSID length in place. Deauth in host-MLME mode first unregisters management frames; failure there aborts disconnect.

## Test Signals
Validate WPA/WPA2/WAPI/WPS/SAE association, SAE H2E RSNX PWE TLV, 11n/11ac feature gating, WMM and non-WMM association, fixed-rate incompatibility, host-MLME association responses, association timeout/error mapping, ad-hoc start/join/coalescing, deauth for station/ad-hoc/AP modes, and carrier/queue transitions after success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.c

## Purpose
`main.c` is the common mwifiex driver core. It registers adapters, drives firmware request/download completion, owns the main/RX/host-MLME workqueues, coordinates command/event/RX/TX processing, implements netdev operations, handles software shutdown/reinit/removal, sets up wake IRQs, and exposes module parameters/debug helpers.

## Important APIs, Types, and Functions
Exported/common functions include `mwifiex_queue_main_work()`, `mwifiex_main_process()`, `mwifiex_queue_tx_pkt()`, `mwifiex_clone_skb_for_tx_status()`, `mwifiex_set_mac_address()`, `mwifiex_multi_chan_resync()`, `mwifiex_upload_device_dump()`, `mwifiex_drv_info_dump()`, `mwifiex_prepare_fw_dump_info()`, `mwifiex_init_priv_params()`, `is_command_pending()`, `mwifiex_shutdown_sw()`, `mwifiex_reinit_sw()`, `mwifiex_add_card()`, `mwifiex_remove_card()`, and `_mwifiex_dbg()`. Important static paths are `mwifiex_register()`, `mwifiex_unregister()`, `mwifiex_process_rx()`, `_mwifiex_fw_dpc()`, `mwifiex_init_hw_fw()`, netdev callbacks, workqueue callbacks, `mwifiex_uninit_sw()`, and OF wake IRQ handling.

## Control Flow
`mwifiex_add_card()` allocates/registers adapter software, probes wake IRQ from device tree, creates workqueues, calls bus `register_dev()`, then requests firmware asynchronously. `_mwifiex_fw_dpc()` downloads firmware, optionally loads calibration data, enables interrupts, initializes firmware state, registers cfg80211, creates default STA and optional AP/P2P interfaces, and marks the adapter up. The main work function calls `mwifiex_main_process()`, which serializes with `main_proc_lock`, throttles RX backlog, handles interrupts, wakes sleeping firmware when commands/TX are pending, processes events and command responses, confirms sleep, executes pending commands, and drains normal, bypass, and WMM TX queues. RX work drains `rx_data_q` and deaggregates or dispatches packets. Netdev TX validates skb length/headroom, fills mwifiex TX control block, optionally clones for TX status, timestamps, checks TDLS, and queues into bypass or WMM paths.

## State and Persistence
Module parameters include `debug_mask`, `cal_data_cfg`, `driver_mode`, `mfg_mode`, and `aggr_ctrl`. Runtime state is in `mwifiex_adapter`: work flags, workqueues, firmware pointers, command/event/RX/TX flags, power-save state, wake IRQ, coredump buffers, cfg80211/wiphy, and bus ops. Per-interface state is in `mwifiex_private`: netdev, MAC, WMM pending counts, custom IE indexes, scan flags, ACK-status IDR, histogram, and connection fields. Firmware/calibration blobs are released after use; coredumps are handed to `dev_coredumpv()`.

## Dependencies and Integration Points
`main.c` integrates Linux module parameters, firmware loader, cfg80211/wiphy, rtnetlink and netdev ops, skbuff queues, workqueues, timers, device tree IRQ parsing, PM wakeup APIs, devcoredump, USB/SDIO/PCIe bus `if_ops`, WMM/11n/TDLS helpers, and debugfs init/cleanup.

## Risks and Edge Cases
The central risk is asynchronous lifecycle ordering: firmware callbacks, removal, suspend, reset, workqueues, and interrupts share adapter state. `fw_done` completion gates shutdown/reinit but callers must avoid suspend races. `mwifiex_main_process()` has many break/continue paths around sleep, command, scan, and TX locks; regressions can stall commands or data. TX status cloning uses a small IDR range and must preserve skb ownership on allocation failure. Device dump building uses sprintf into dump buffers and reallocates only for firmware sections. Teardown must disable interrupts before destroying workqueues and netdevs.

## Test Signals
Validate add/remove while firmware request is pending, firmware download failure cleanup, reset via `mwifiex_reinit_sw()`, suspend wake IRQ behavior, RX backlog throttling, command/event ordering, PS wakeup timer, netdev open/close/scan abort, TX queue backpressure and timeout reset, MAC address changes, multicast mode changes, device coredump generation, and debug mask logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.h

## Purpose
`main.h` is the central mwifiex common header. It includes Linux and bus headers, declares global module state, defines core constants/macros, debug levels, hardware/power/interface enums, connection/security/rate/WMM/BA/reorder/station/TDLS data structures, bus operation callbacks, the main `mwifiex_private` and `mwifiex_adapter` state containers, and cross-file function prototypes.

## Important APIs, Types, and Functions
Core state types are `struct mwifiex_private`, `struct mwifiex_adapter`, `struct mwifiex_if_ops`, `struct mwifiex_bssdescriptor`, `struct mwifiex_current_bss_params`, `struct mwifiex_wmm_desc`, `struct mwifiex_ra_list_tbl`, `struct mwifiex_rx_reorder_tbl`, `struct mwifiex_sta_node`, `struct cmd_ctrl_node`, and `struct mwifiex_dbg`. Key enums/macros cover driver mode, interface type, hardware status, power-save state, debug masks, packet types, queue thresholds, scan timing, firmware dump sizes, and work flags. The prototype block exports nearly every cross-module driver operation for commands, scans, association, UAP, WMM, 11n/11ac, power, events, RX/TX, debug, TDLS, WoWLAN, DFS/CAC, and adapter lifecycle.

## Control Flow
This header establishes how modules call each other. Bus-specific drivers provide `mwifiex_if_ops`; `main.c` stores those callbacks in `mwifiex_adapter` and orchestrates lifecycle. Command code consumes `cmd_ctrl_node` queues and `mwifiex_send_cmd()` prototypes. Join, scan, UAP, WMM, 11n/11ac, power, and event handlers mutate fields in `mwifiex_private` and `mwifiex_adapter`. Inline helpers choose private contexts by BSS id/role, copy rate arrays, and decide whether queuing should be receiver-address based.

## State and Persistence
`mwifiex_adapter` is the device-wide volatile state: firmware name/blob, bus card pointer, interface ops, workqueues, command queues, interrupt/event flags, TX/RX queues and counters, scan/region settings, firmware capabilities, power-save and host-sleep state, cfg80211 wiphy, wake IRQ, coredump buffers, channel stats, bus aggregation, and coex/TDLS flags. `mwifiex_private` is per virtual interface: BSS identity, netdev/wdev, MAC, connection/security/rate state, WMM queues, station lists, BA/reorder tables, scan state, custom IE cache, AP settings, TDLS, DFS, memory access, bypass queue, and association response cache. No filesystem persistence exists.

## Dependencies and Integration Points
`main.h` ties together Linux netdev/cfg80211/skbuff/workqueue/timer/firmware/devcoredump APIs and mwifiex local headers `decl.h`, `ioctl.h`, `util.h`, `fw.h`, `pcie.h`, `usb.h`, and `sdio.h`. It is included by most mwifiex `.c` files, so changes here have driver-wide build and ABI effects.

## Risks and Edge Cases
Because this header defines shared state, field changes can silently break lock ordering, ownership, or bus implementations. Many fields are protected by specific spinlocks but the protection is documented only by comments and usage. `mwifiex_private` and `mwifiex_adapter` are large mutable structures used from workqueues, IRQ context, netdev callbacks, cfg80211 callbacks, and reset paths. Constants such as queue thresholds, buffer sizes, and IE limits must match firmware and caller assumptions.

## Test Signals
Build all mwifiex bus variants after header changes. Runtime signals include clean STA/AP/P2P virtual interface creation, command queue progress, RX/TX queue accounting, WMM/BA/reorder behavior, TDLS peer tracking, host sleep and wake, DFS/CAC work, firmware dump paths, debugfs/debug-info output, and lockdep/KASAN coverage during add/remove/reset/suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.h -->
