# Research: subset-b-004834

Grouped source research for Intel iwlwifi MVM core/support files. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h

## Purpose
Central private header for the Intel iwlwifi MVM op-mode. It defines the main driver state objects, per-vif/per-link state, feature probes, command helper prototypes, mac80211 callbacks, firmware notification entry points, and cross-file contracts used by the rest of `drivers/net/wireless/intel/iwlwifi/mvm`.

## Important APIs, Types, And Functions
Core types are `struct iwl_mvm`, `struct iwl_mvm_vif`, `struct iwl_mvm_vif_link_info`, `struct iwl_mvm_phy_ctxt`, `struct iwl_mvm_time_event_data`, `struct iwl_mvm_tcm`, `struct iwl_mvm_baid_data`, `struct iwl_mvm_txq`, `struct iwl_mvm_dqa_txq_info`, `struct iwl_mvm_tvqm_txq_info`, `struct ptp_data`, and `struct iwl_mei_scan_filter`. Important enums cover power schemes, scan status/type, SMPS request sources, low-latency causes, thermal/TDLS state, queue status, and MVM status bits.

The header exports prototypes for lifecycle (`iwl_mvm_up`, `iwl_mvm_stop_device`, `iwl_run_init_mvm_ucode`, D3 load/resume), host commands (`iwl_mvm_send_cmd*`), NVM/regulatory (`iwl_nvm_init`, `iwl_mvm_update_mcc`, `iwl_mvm_init_mcc`), PHY contexts, MAC contexts, links, bindings, scanning, rate scaling, power, WoWLAN, BT coexistence, beacon filtering, SMPS, low latency, thermal, FTM, TDLS, PTP, SAR/PPAG/BIOS tables, RFI, channel switching, and mac80211 callbacks. Inline helpers gate firmware features and API variants such as MLD, new RX/TX station APIs, CDB, LAR, RLC offload, scan capabilities, quota format, ultra-high-band channel info, and MEI integration.

## Control Flow
This header does not implement a single runtime flow; it wires together flows implemented in sibling files. `ops.c` allocates `struct iwl_mvm`, initializes locks/work, sets transport callbacks, and dispatches firmware RX notifications to handlers declared here. mac80211 callbacks declared at the end of the file enter interface, station, scan, channel context, TX, key, FTM, and power flows. Firmware command builders in other files use the inline capability helpers to select command versions and data layout.

## State And Persistence
`struct iwl_mvm` is the top-level runtime state for the op-mode and stores transport/firmware/mac80211 handles, locks, notification wait state, NVM data and sections, firmware runtime, station/vif mappings, scan state, debugfs blobs, PHY contexts, time events, firmware key tables, WoWLAN/net-detect state, thermal/BT/TCM state, quota history, queue identifiers, power flags, regulatory state, TDLS/FTM/PTP/time-sync/ACS survey state, and restart/error buffers. `struct iwl_mvm_vif` and `struct iwl_mvm_vif_link_info` persist per-interface and per-link firmware IDs, AP station IDs, BSSID, queues, beacon/probe-response data, power/beacon-filter flags, CSA/ROC/session protection fields, IPv6 offload addresses, keys, and debugfs overrides. Most persistence is in kernel memory; NVM sections, regulatory results, firmware key tables, and MEI CSME ownership data mirror hardware/firmware state and must be rebuilt across restart.

## Dependencies And Integration Points
Depends heavily on mac80211/cfg80211, the iwlwifi transport layer, firmware runtime/debug APIs, firmware command definitions, NVM parsing, ACPI/UEFI, MEI coexistence, thermal, PTP, and Linux networking structures. It is the integration point between MVM implementation files and external callback tables: `iwl_mvm_hw_ops`, `iwl_mvm_mld_hw_ops`, and op-mode callbacks in `ops.c`.

## Risks And Edge Cases
The header encodes many firmware-version compatibility decisions; incorrect feature gating can select the wrong command size or field layout. State fields have mixed locking requirements: `mvm->mutex`, RCU, spinlocks, wiphy lock, and workqueues all appear in the contracts. Per-link MLO state coexists with legacy `deflink`, so callers must use the correct link path. Queue constants and firmware IDs use sentinel values, and accidental reuse can stall TX or remove the wrong station. Debugfs and compile-time feature guards change struct contents and helper behavior.

## Test Signals
Build with combinations of `CONFIG_IWLWIFI_DEBUGFS`, `CONFIG_PM_SLEEP`, `CONFIG_THERMAL`, `CONFIG_IWLWIFI_KUNIT_TESTS`, `CONFIG_IWLMEI`, and LED support. Exercise firmware capability matrices for old/new RX, old/new TX, MLD/non-MLD, CDB, RLC offload, LAR, quota versions, and ultra-high-band channel info. Runtime signals include successful mac80211 registration, interface add/remove, scan, association, channel switch, power-save update, firmware restart, WoWLAN, PTP registration, and clean teardown without lockdep or RCU warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/mvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c

## Purpose
Loads, writes, parses, and regulatory-updates Intel wireless NVM data for MVM devices. It reads hardware NVM/OTP sections through firmware commands, optionally overlays an external NVM file, parses antenna/MAC/regulatory information, uploads NVM sections back to the NIC, and drives LAR MCC regulatory updates.

## Important APIs, Types, And Functions
Public entry points are `iwl_nvm_init`, `iwl_mvm_load_nvm_to_nic`, `iwl_mvm_update_mcc`, `iwl_mvm_init_mcc`, and `iwl_mvm_rx_chub_update_mcc`. Static helpers include `iwl_nvm_write_chunk`, `iwl_nvm_read_chunk`, `iwl_nvm_write_section`, `iwl_nvm_read_section`, and `iwl_parse_nvm_sections`. It uses `struct iwl_nvm_access_cmd`, `struct iwl_nvm_access_resp`, `struct iwl_nvm_section`, `struct iwl_nvm_data`, multiple MCC response versions, and cfg80211 regdomain objects.

## Control Flow
`iwl_nvm_init` allocates a temporary EEPROM-sized buffer, iterates every possible NVM section, reads each section in 2 KiB chunks via `NVM_ACCESS_CMD`, handles absent sections as nonfatal, duplicates successful section data into `mvm->nvm_sections`, exposes debugfs blobs when enabled, optionally reads an external NVM file, then parses the required sections into `mvm->nvm_data`. `iwl_mvm_load_nvm_to_nic` walks stored sections and writes each nonempty one in chunks. `iwl_mvm_update_mcc` sends `MCC_UPDATE_CMD`, normalizes firmware response versions into v8 layout, validates variable payload lengths, handles world-domain MCC zero as `"00"`, and returns an allocated response. `iwl_mvm_init_mcc` replays saved FW regulatory data or asks cfg80211/BIOS for an initial MCC. `iwl_mvm_rx_chub_update_mcc` handles asynchronous CHUB MCC notifications and installs changed regdomains unless associated and the update came from Wi-Fi.

## State And Persistence
Mutates `mvm->nvm_sections`, `mvm->nvm_data`, debugfs NVM blob wrappers, `mvm->lar_regdom_set` through helpers, and the wiphy regulatory domain. NVM data is persistent hardware/firmware configuration copied into kernel memory; external NVM overrides can replace sections at initialization. MCC updates persist in cfg80211 regulatory state and may be replayed to firmware.

## Dependencies And Integration Points
Depends on firmware command transport through `iwl_mvm_send_cmd`, NVM parser/fixup helpers from `iwl-nvm-utils.h` and `iwl-nvm-parse.h`, cfg80211 regulatory APIs, BIOS MCC/SAR helpers, LAR firmware capabilities, and the INIT firmware path in `ops.c`. `mvm.h` inline helpers consume the parsed antenna and LAR fields.

## Risks And Edge Cases
Chunked reads must not overflow configured EEPROM size. `READ_NVM_CHUNK_NOT_VALID_ADDRESS` is nonfatal only after offset zero. Required sections vary by `nvm_type`; missing SW, regulatory, MAC/HW, or PHY_SKU sections cause parse failure. MCC responses are variable-length and version-dependent, so payload length validation is critical. Regulatory updates while associated can disrupt active connections and are intentionally filtered for Wi-Fi-sourced changes.

## Test Signals
Exercise blank OTP, missing optional sections, missing mandatory sections, EEPROM-size overflow guard, external NVM overlay, NVM writeback failures, all MCC response versions, LAR disabled/enabled combinations, BIOS MCC override, CHUB MCC updates while associated and idle, and regdomain allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c

## Purpose
Builds firmware protocol offload commands used for WoWLAN/D3 and related low-power operation, including ARP, IPv6 neighbor solicitation, BTM offload, and QoS sequence handoff.

## Important APIs, Types, And Functions
`iwl_mvm_set_wowlan_qos_seq` copies per-TID QoS sequence numbers from an AP station into a WoWLAN config command with firmware sequence semantics. `iwl_mvm_send_proto_offload` builds and sends `PROT_OFFLOAD_CONFIG_CMD` using one of several command layouts: v1, v2, v3 small, or v4/large. It uses `struct iwl_proto_offload_cmd_common`, `struct iwl_ns_config`, `struct iwl_targ_addr`, IPv6 address arrays stored in `struct iwl_mvm_vif`, and mac80211 vif ARP configuration.

## Control Flow
QoS sequence handoff subtracts `0x10` from each next sequence because firmware increments before use while the host stores the next value after use. Protocol offload command construction first selects IPv6 NS layout from firmware capability flags. For new NS offload layouts it groups target IPv6 addresses by solicited-node multicast address, skips tentative addresses when actual NS offload is enabled, fills target address to NS config mappings, and counts valid addresses. Older layouts copy up to their supported address count and set the NDP MAC. ARP offload is enabled from `vif->cfg.arp_addr_list[0]`; BTM offload is enabled if supported. The selected command size and pointer are adjusted for older large-NS command versions that lack `sta_id`, and the command is sent.

## State And Persistence
Reads `mvmvif->target_ipv6_addrs`, `mvmvif->tentative_addrs`, `vif->cfg.arp_addr_cnt`, `vif->cfg.arp_addr_list`, `vif->addr`, and AP station TID sequence state. It does not retain state itself; it serializes host network addressing and sequence state into firmware-owned low-power offload state.

## Dependencies And Integration Points
Depends on IPv6/addrconf helpers, firmware capability flags, WoWLAN command definitions, mac80211 vif configuration, and `iwl_mvm_send_cmd`. It is called by D3/WoWLAN setup paths declared in `mvm.h`.

## Risks And Edge Cases
Tentative IPv6 addresses must be skipped only when firmware will answer NS, otherwise wake filtering could hide duplicate-address-detection traffic. New NS layouts have independent limits for target addresses and NS config entries, so deduplication and counts must remain consistent. Command version `<4` for large NS offload shifts the command pointer to the common field; wrong sizing would corrupt firmware parsing. Only the first ARP address is offloaded.

## Test Signals
Cover no IPv6, tentative IPv6 with offload enabled/disabled, duplicate solicited-node multicast addresses, address counts above each firmware limit, ARP-only offload, BTM capability on/off, disable-offloading mode, command version `<4` large layout, and QoS sequence wrap/underflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/offloading.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c

## Purpose
Implements the MVM op-mode module registration, device/op-mode startup and teardown, transport callback table, firmware notification dispatch, async notification worker model, debug dump sanitization, MEI/CSME ownership callbacks, queue backpressure handling, RF-kill/CT-kill state handling, and firmware error/restart hooks.

## Important APIs, Types, And Functions
Module entry points are `iwl_mvm_init` and `iwl_mvm_exit`. The op-mode callbacks are `iwl_op_mode_mvm_start`, `iwl_op_mode_mvm_stop`, `iwl_mvm_rx`, `iwl_mvm_rx_mq`, `iwl_mvm_rx_mq_rss`, `iwl_mvm_stop_device`, `iwl_mvm_set_hw_ctkill_state`, and helpers in `IWL_MVM_COMMON_OPS`. Important private structures include `struct iwl_rx_handlers`, `enum iwl_rx_handler_context`, `struct iwl_async_handler_entry`, `struct iwl_mvm_frob_txf_data`, and `mei_ops`. It exports command-name arrays `iwl_mvm_groups` for debug/KUnit command decoding.

## Control Flow
Module initialization registers rate control and the `"iwlmvm"` op-mode. `iwl_op_mode_mvm_start` allocates mac80211 HW with MLD or legacy ops, initializes `struct iwl_mvm`, firmware runtime, BIOS/UEFI tables, rate API version checks, RX/TX API selection, queue IDs, locks, lists, work items, notification waits, transport configuration, PHY DB, scan command buffer, thermal/TCM/time-sync state, MEI registration, NVM acquisition, and finally mac80211/debugfs registration. NVM acquisition uses CSME data when available, otherwise starts hardware, runs INIT firmware, initializes MCC/regulatory data, and stops the device.

Firmware RX dispatch first handles fast-path MPDU/PHY/data-path notifications, otherwise `iwl_mvm_rx_common` logs time points, checks debug triggers, wakes notification waiters, validates notification size, and either calls sync handlers directly or steals the RX page into an async handler list. Async work drains matching contexts with or without `mvm->mutex`, or through wiphy work when both wiphy and MVM locking are required. Queue state callbacks map hardware queues back to station/TID TXQs and stop/wake mac80211 queues or run pending TXQ transmission.

Stop and error paths unregister MEI/mac80211, cancel workers, exit LEDs/thermal/PTP, free scan/mcast/error/NVM/PHY DB/runtime allocations, leave the transport op-mode, and free HW. Firmware errors abort waits, delete debug timers, dump logs unless suppressed, set restart-request status, collect dumps with mutex protection, and request mac80211 restart only for supported regular-fw cases.

## State And Persistence
Creates and owns the lifetime of `struct iwl_mvm` and most fields declared in `mvm.h`: locks, workqueues, status bits, notification wait data, queue maps, scan buffers, PHY DB, firmware runtime, NVM data, MEI state, thermal/TCM/PTP state, debugfs state, and error recovery buffers. Hardware/firmware state is started and stopped through the transport. Debug dump sanitizers overwrite key material in captured TX FIFOs, host commands, and firmware memory dumps before persistence in debug dumps.

## Dependencies And Integration Points
Depends on Linux module/mac80211/cfg80211, iwlwifi op-mode registration, transport configuration, firmware runtime/debug APIs, PHY DB, NVM/regulatory helpers, rate control, scan/time-event/FTM/thermal/BT/MEI/time-sync subsystems, and all firmware notification handlers registered in `iwl_mvm_rx_handlers`. It is the main integration point between transport callbacks and MVM subsystems.

## Risks And Edge Cases
Startup has many partially initialized unwind paths; missing a cleanup leaks runtime, PHY DB, scan buffers, or MEI registration. Rate API consistency checks must match firmware command/notification versions. Async RX handlers steal RX pages and rely on context-specific locking; wrong context can deadlock or race. RF-kill during INIT must abort notification waits without double-stopping unified firmware. Queue mapping differs between old DQA and new TVQM APIs. Dump sanitization must avoid leaking encryption keys while not corrupting unrelated debug data. CSME-owned devices can defer mac80211 registration until SAP connection work completes.

## Test Signals
Exercise module load/unload, start failure at each allocation/init phase, CSME-owned startup with deferred SAP work, NVM from firmware and MEI, old/new RX APIs, old/new TX queue APIs, MLD and non-MLD registration, async notification contexts, unknown/short notifications, queue full/not-full callbacks, RF-kill and CT-kill changes, firmware crash/restart, debug dump collection/sanitization, and clean op-mode stop with no pending work or lockdep reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c

## Purpose
Manages firmware PHY context commands for channel definitions, channel width/control-position encoding, RX/TX chain selection, RLC configuration, PHY context add/modify/remove, reference counts, and active PHY context counting.

## Important APIs, Types, And Functions
Public functions are `iwl_mvm_get_channel_width`, `iwl_mvm_get_ctrl_pos`, `iwl_mvm_phy_send_rlc`, `iwl_mvm_phy_ctxt_add`, `iwl_mvm_phy_ctxt_ref`, `iwl_mvm_phy_ctxt_changed`, `iwl_mvm_phy_ctxt_unref`, and `iwl_mvm_phy_ctx_count`. Static helpers build firmware command headers/data and RX chain fields: `iwl_mvm_phy_ctxt_cmd_hdr`, `iwl_mvm_phy_ctxt_set_rxchain`, `iwl_mvm_phy_ctxt_cmd_data_v1`, `iwl_mvm_phy_ctxt_cmd_data`, and `iwl_mvm_phy_ctxt_apply`.

## Control Flow
Channel width and control position translate cfg80211 channel definitions into firmware constants. PHY context add records channel/width/center frequency, sends `PHY_CONTEXT_CMD` with ADD, then increments refcount. Change validates an existing ref, sends only RLC if the channel definition did not change and RLC version supports that split, otherwise removes/adds when CDB binding changes bands, or sends MODIFY. Unref decrements and sends REMOVE when the last reference drops. RLC send is skipped when firmware offloads RLC or the context disables it; otherwise it sends `RLC_CONFIG_CMD` v2 with RX chain info.

## State And Persistence
Mutates `struct iwl_mvm_phy_ctxt` fields: `channel`, `width`, `center_freq1`, `ref`, and uses `rlc_disabled`. Firmware state persists until remove or reset. RX chain selection depends on valid antenna masks from NVM/firmware/debugfs and may promote one active chain to two for diversity when allowed.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 channel definitions, firmware command versions, `iwl_mvm_set_chan_info_chandef` and channel info helpers from `mvm.h`, antenna helpers, RLC offload feature gating, and `iwl_mvm_send_cmd_pdu`. Channel context and binding code call these APIs under `mvm->mutex`.

## Risks And Edge Cases
Invalid channel widths warn and fall back to 20 MHz. Control-position encoding is bit-sensitive for wide channels. Command version handling changes struct size and padding; ultra-high-band channel info changes tail placement. Refcount misuse can remove an active PHY context or modify a non-added one. Band changes with CDB binding support require remove/add rather than modify. RLC offload version boundaries must be correct.

## Test Signals
Cover 20/40/80/160/320 MHz widths, all primary-channel offsets, add/change/unref lifecycles, refcount warnings, same-channel RLC-only update, band-switch remove/add path, RLC offload skip, debugfs RX chain override, static/dynamic chain diversity behavior, and active context count across STA/AP interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/phy-ctxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c

## Purpose
Builds and sends device and per-MAC power management commands, decides when power save and U-APSD are allowed, manages beacon filtering/beacon abort settings, responds to firmware U-APSD misbehaving AP notifications, and exposes debugfs-readable/overrideable power parameters.

## Important APIs, Types, And Functions
Public entry points are `iwl_mvm_power_update_device`, `iwl_mvm_power_update_mac`, `iwl_mvm_power_update_ps`, `iwl_mvm_power_vif_assoc`, `iwl_mvm_power_uapsd_misbehaving_ap_notif`, `iwl_mvm_power_mac_dbgfs_read`, `iwl_mvm_beacon_filter_debugfs_parameters`, `iwl_mvm_enable_beacon_filter`, and `iwl_mvm_disable_beacon_filter`. Key static helpers include `iwl_mvm_power_build_cmd`, `iwl_mvm_power_send_cmd`, `iwl_mvm_power_set_pm`, `iwl_mvm_power_set_ps`, `iwl_mvm_power_set_ba`, `iwl_mvm_power_configure_uapsd`, `iwl_mvm_power_allow_uapsd`, `iwl_mvm_power_config_skip_dtim`, and beacon-filter command helpers.

## Control Flow
Device power update sets global power-save flags from module power scheme, per-interface `ps_disabled`, debugfs overrides, external 32 kHz clock validity, and D3 no-sleep requirements. MAC power update gathers uploaded active vifs by role, disables PM on all, then selectively enables PM for standalone BSS/P2P, multi-channel client cases, or same-channel BSS+P2P without AP conflicts. It sends per-MAC power commands for BSS/P2P vifs, then updates beacon abort for BSS. Power command building always sets a keep-alive period at least 3 DTIMs and at least 25 seconds, then enables PS/PM only when global, mac80211, and MVM policy allow it. It selects default, short low-latency, or WoWLAN timeouts, optional low-power RX, DTIM skipping, U-APSD, snooze, and debugfs overrides.

Beacon filtering can only be enabled for the allowed non-P2P station vif with a DTIM period. CQM RSSI and debugfs parameters adjust the filter command. Misbehaving AP notifications find the vif whose link AP station ID matches firmware, store the AP address, and suppress U-APSD on reconnection.

## State And Persistence
Mutates `mvm->ps_disabled`, `mvmvif->pm_enabled`, `mvmvif->bf_enabled`, `mvmvif->ba_enabled`, `mvmvif->uapsd_misbehaving_ap_addr`, and debugfs `mac_pwr_cmd` snapshots. Firmware receives `POWER_TABLE_CMD`, `MAC_PM_POWER_TABLE`, and `REPLY_BEACON_FILTERING_CMD`; these settings persist in firmware until changed or reset. D3 status changes timeout/DTIM behavior for WoWLAN.

## Dependencies And Integration Points
Depends on mac80211 vif/link state, module parameter `iwlmvm_mod_params.power_scheme`, firmware power command definitions, beacon filter API versions, cfg80211 channel/radar flags, TDLS station counting, low-latency helpers, P2P NoA attributes, debugfs structures from `mvm.h`, and `iwl_mvm_send_cmd_pdu`. Called by association, interface state, WoWLAN, and low-latency/power recalculation paths.

## Risks And Edge Cases
Power policy is role-sensitive: enabling PM with AP/GO, TDLS, same-channel combinations, P2P opportunistic PS, or low latency can break traffic. DTIM skipping is disabled for long DTIM periods or radar channels. U-APSD must avoid APs firmware flagged as misbehaving and P2P cases firmware cannot support. Debugfs overrides can force unusual command combinations. Beacon filter enable silently no-ops unless the vif is eligible and allowed.

## Test Signals
Cover CAM/BPS/LP module schemes, `ps_disabled` vifs, BSS-only, P2P-only, BSS+P2P same and different channel, BSS+AP, TDLS present, D3/WoWLAN timeouts, radar channel DTIM skip suppression, low-latency P2P, U-APSD all ACs/snooze and partial ACs, misbehaving AP notification/reassociation, beacon filter enable/disable/CQM parameters, debugfs overrides, and firmware command failure rollback of `mvm->ps_disabled`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c

## Purpose
Registers an iwlwifi PTP hardware clock (PHC) backed by the device GP2 timer, translates/wraps/scales GP2 timestamps into adjusted nanoseconds, supports frequency/time adjustment, and provides system-device cross timestamps either through firmware synced-time command or host loop sampling.

## Important APIs, Types, And Functions
Public APIs are `iwl_mvm_ptp_init`, `iwl_mvm_ptp_remove`, and `iwl_mvm_ptp_get_adj_time`. PTP callbacks are `iwl_mvm_phc_get_crosstimestamp`, `iwl_mvm_ptp_gettime`, `iwl_mvm_ptp_settime`, `iwl_mvm_ptp_adjtime`, and `iwl_mvm_ptp_adjfine`. Static helpers include `iwl_mvm_ptp_update_new_read`, `iwl_mvm_get_crosstimestamp_fw`, `iwl_mvm_phc_get_crosstimestamp_loop`, and delayed `iwl_mvm_ptp_work`.

## Control Flow
Initialization fills `ptp_clock_info`, sets callback pointers, initializes scaled frequency to `SCALE_FACTOR`, names the clock, initializes delayed wrap-tracking work, and registers the PHC. Reads take `mvm->mutex`, read GP2 from firmware/hardware, call `iwl_mvm_ptp_get_adj_time`, and return nanoseconds as a timespec or cross timestamp. Cross timestamping uses firmware `WNM_PLATFORM_PTM_REQUEST_CMD` when synced-time capability exists; otherwise it samples host sync time five times and chooses the smallest system-vs-GP2 delta. `adjtime` accumulates delta. `adjfine` snapshots current adjusted time before changing scale, resets wrap/delta origin, and applies the scaled ppm offset. Periodic delayed work reads GP2 before expected wrap to keep wrap tracking current.

## State And Persistence
Uses `mvm->ptp_data`: registered clock pointer, clock info, delayed work, `last_gp2`, `wrap_counter`, scale update GP2/time, `scaled_freq`, and `delta`. State is runtime-only and reset on remove. Firmware GP2 is a 32-bit microsecond counter, so wrap accounting is essential for continuity.

## Dependencies And Integration Points
Depends on Linux PTP clock framework, timekeeping, math64 helpers, `iwl_mvm_get_systime`, `iwl_mvm_get_sync_time`, firmware synced-time capability, `iwl_mvm_send_cmd`, and lifecycle hooks from `ops.c` (`iwl_mvm_ptp_remove` during stop). Consumers may request RX timestamps in PTP clock time through `mvm->rx_ts_ptp`.

## Risks And Edge Cases
Old GP2 reads can look like wraparound; the 5 ms threshold filters small backwards reads. Missing periodic work around the one-hour wrap can break monotonic conversion. `iwl_mvm_get_crosstimestamp_fw` does not free the response on the success path in the code as read, which is a leak risk unless ownership is handled elsewhere. `settime` is unsupported. Frequency adjustment resets delta and wrap origin, so callers expecting independent phase/frequency control need coverage.

## Test Signals
Verify PHC registration/unregistration, unavailable PTP module behavior, gettime monotonicity across GP2 wrap, old-read filtering, adjtime delta accumulation, adjfine scaling before and after reads, firmware synced-time and fallback loop cross timestamps, invalid firmware response length, delayed work cancellation on remove, and repeated init/remove without stale clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c

## Purpose
Computes and uploads firmware time-quota allocation across active PHY bindings/MACs, with special handling for low-latency bindings and debugfs minimum quota overrides.

## Important APIs, Types, And Functions
The public function is `iwl_mvm_update_quotas`. Private state collection uses `struct iwl_mvm_quota_iterator_data` and `iwl_mvm_quota_iterator`. Command layout helpers are in `mvm.h`: `iwl_mvm_quota_cmd_size` and `iwl_mvm_quota_cmd_get_quota`.

## Control Flow
`iwl_mvm_update_quotas` requires `mvm->mutex`, exits early when firmware supports dynamic quota or when hardware restart is in progress, then iterates active interfaces. The iterator skips a caller-specified disabled vif, ignores inactive/unassociated roles, maps each vif to its PHY context ID as binding ID, validates color consistency, counts active interfaces per binding, records debugfs minimums, and marks low-latency bindings. The updater initializes all quota entries invalid, computes equal quota across active MACs or reserves `QUOTA_LOWLAT_MIN` when exactly one low-latency binding coexists with non-low-latency traffic, fills valid `id_and_color` entries, gives remainder to the first nonzero binding, suppresses practically unchanged commands unless forced, sends `TIME_QUOTA_CMD`, and caches the successful command in `mvm->last_quota_cmd`.

## State And Persistence
Reads active vif state (`assoc`, `ap_ibss_active`, `monitor_active`, `phy_ctxt`, low-latency flags), debugfs minimum quota, and `mvm->status`. Mutates only firmware scheduling state and `mvm->last_quota_cmd`; no durable host persistence exists.

## Dependencies And Integration Points
Depends on mac80211 active interface iteration, MVM vif/PHY context state, low-latency helper `iwl_mvm_vif_low_latency`, firmware dynamic-quota capability, command format version gating from `mvm.h`, and `iwl_mvm_send_cmd_pdu`. Called when interface/channel/low-latency state changes.

## Risks And Edge Cases
The code assumes `NUM_PHY_CTX <= MAX_BINDINGS` and currently `MAX_BINDINGS == 4`. PHY context ID is treated as binding ID. Equal split is by active interface count, not just binding count, so multi-interface bindings receive proportionally more quota. Low-latency reservation only applies when exactly one low-latency binding coexists with other bindings. Suppression threshold can skip small but real changes unless `force_update` is true. Zero quota for valid bindings warns.

## Test Signals
Cover no active interfaces, one STA, AP/IBSS active and inactive, monitor active, disabled vif exclusion, multiple vifs on one binding, multiple bindings, one low-latency binding with and without other traffic, multiple low-latency bindings, debugfs minimum override, unchanged-command suppression, forced upload, dynamic quota capability skip, hardware restart skip, and firmware send failure preserving `last_quota_cmd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c

## Purpose
Contains Radio Frequency Interference Mitigation (RFIm/RFI) command support and the default DDR-frequency-to-Wi-Fi-channel lookup table. In the code as read, runtime support is intentionally disabled pending platform support detection.

## Important APIs, Types, And Functions
Public APIs are `iwl_rfi_supported`, `iwl_rfi_send_config_cmd`, `iwl_rfi_get_freq_table`, and `iwl_rfi_deactivate_notif_handler`. The default `iwl_rfi_table` is an array of `struct iwl_rfi_lut_entry` with DDR frequency units of 16.666 MHz and affected 5 GHz/6 GHz channel lists.

## Control Flow
`iwl_rfi_supported` currently always returns false. Therefore `iwl_rfi_send_config_cmd` and `iwl_rfi_get_freq_table` return `-EOPNOTSUPP` before sending firmware commands. If enabled in the future, config command construction would require `mvm->mutex`, copy either the default table or an OEM-provided table, set `cmd.oem` for custom tables, and send `SYSTEM_GROUP/RFI_CONFIG_CMD`. Frequency-table query would send `SYSTEM_GROUP/RFI_GET_FREQ_TABLE_CMD` with `CMD_WANT_SKB`, validate response payload size, duplicate the response, and free the firmware response. Deactivate notifications log the firmware-provided reason.

## State And Persistence
No mutable host state is kept in the current disabled path. If enabled, firmware would persist the RFI table and expose a frequency table response until reset or reconfiguration. The handler only reads notification payload.

## Dependencies And Integration Points
Depends on firmware RFI command definitions, system command group IDs, PHY band constants, `iwl_mvm_send_cmd`, and the notification dispatch table in `ops.c` for `RFI_DEACTIVATE_NOTIF`. Public prototypes are declared in `mvm.h`.

## Risks And Edge Cases
The feature is hard-disabled even if firmware has RFI capability, so callers must handle `-EOPNOTSUPP`. Default table correctness is hardware/platform-sensitive. If support is enabled later, response-size validation, mutex coverage, OEM table sizing, and platform capability detection become critical.

## Test Signals
Current tests should assert unsupported returns for config and get-table calls, no firmware command emission when unsupported, and notification logging behavior. Future enabled tests should cover default vs OEM tables, firmware send errors, malformed response size, allocation failure, and deactivate reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c -->
