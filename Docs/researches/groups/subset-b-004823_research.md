# Research: subset-b-004823

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/rx.h

## Purpose
Defines Intel iwlwifi firmware receive-side ABI structures and bit fields. It covers legacy pre-9000 RX PHY notifications, 9000+ MPDU descriptors, checksum/security status, reorder metadata, no-data RX reports, RSS/RFH queue configuration, station power-save and BA-window notifications, beacon-filter notifications, and air-sniffer PHY vector reports through HE, EHT, and UHR formats.

## Important APIs, Types, And Functions
Key ABI records include `iwl_rx_phy_info`, `iwl_rx_mpdu_res_start`, `iwl_rx_mpdu_desc`, `iwl_rx_no_data`, `iwl_rx_no_data_ver_3`, `iwl_rss_config_cmd`, `iwl_rxq_sync_cmd`, `iwl_rfh_queue_config`, `iwl_ba_window_status_notif`, and `iwl_rx_phy_air_sniffer_ntfy`. Important enums define RX PHY flags, checksum assist, MPDU status/security bits, reorder fields, HE/EHT/UHR PHY metadata masks, no-data error types, RSS hash functions, PM events, and sniffer status/flags.

## Control Flow
This header has no executable flow; it defines packets exchanged in firmware notifications and host commands. Runtime RX handling first interprets PHY/no-data/sniffer notifications, then parses MPDU descriptor fields for length, MAC header flags, checksum offload, decryption status, station ID, reorder BAID/SN/NSSN, rate, channel, RSSI, GP2, TSF, and optional PHY metadata. Setup flows use RFH and RSS commands before RX queues are active, and multi-queue sync commands can inject notifications into selected RX queues.

## State And Persistence
The file stores no driver state, but its packed little-endian records describe persistent firmware-visible state snapshots: RX queue DMA addresses, RSS key and indirection table, BA-window bitmaps, beacon-filter average energy, and per-frame descriptor metadata. Flexible-array payloads in RXQ sync commands and variable descriptor versions require command-size discipline at call sites.

## Dependencies And Integration Points
Depends on Linux integer/endian annotations, bit helpers, and iwlwifi shared rate/MAC constants from surrounding headers. It integrates with the MVM RX path, reorder buffer management, checksum offload, mac80211 RX status construction, monitor/sniffer paths, queue allocation, beacon filtering, and power-save station handling.

## Risks
This is a binary firmware contract: packed layout, endian conversion, descriptor version selection, and union interpretation must match the loaded firmware. Several fields are overloaded depending on API version, RPA enablement, TSF-overload flags, and PHY info type. Incorrect length or status parsing can corrupt skb boundaries, misreport crypto/checksum validity, break BA reordering, or expose invalid PHY metadata to mac80211.

## Test Signals
Useful signals include successful association traffic across legacy/HT/VHT/HE/EHT rates, checksum-offload correctness, encrypted RX with replay/MIC/ICV failures, A-MPDU reordering and BAR release behavior, RSS multi-queue distribution, monitor-mode PHY reporting, no-data notifications on malformed frames, and beacon-filter notifications during powersave. KASAN, sparse endian checks, and firmware API-version matrix boot tests are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/scan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/scan.h

## Purpose
Defines Intel iwlwifi firmware scan command, response, and notification ABI. It covers directed SSID scans, LMAC and UMAC scan requests, scheduled/offloaded scan profiles, channel optimization, probe request segmentation, 6 GHz/UHB discovery flags, adaptive dwell controls, scan abort/start/complete notifications, match reporting, and channel survey statistics.

## Important APIs, Types, And Functions
Important structures include `iwl_ssid_ie`, `iwl_scan_offload_profile`, `iwl_scan_offload_profile_cfg`, `iwl_scan_req_lmac`, `iwl_lmac_scan_complete_notif`, `iwl_scan_config_v1/v2`, `iwl_scan_config`, `iwl_scan_channel_cfg_umac`, `iwl_scan_req_umac`, `iwl_scan_req_umac_v12/v17/v18`, `iwl_umac_scan_abort`, `iwl_umac_scan_complete`, `iwl_scan_offload_match_info`, `iwl_umac_scan_iter_complete_notif`, and `iwl_umac_scan_channel_survey_notif`. Enums define scan clients, auth algorithms, profile network/band matching, priority, channel flags, UMAC general flags, abort status, and EBS status.

## Control Flow
The driver first configures scan defaults such as chains, dwell times, MAC address, rates, and supported channels. A scan request then combines general parameters, channel lists, periodic schedules, and probe parameters. Firmware performs channel iteration, may send start and per-iteration/per-channel notifications, emits matched-profile notifications for scheduled scans, and finishes with complete/abort status. UMAC APIs evolved from a flexible-tail command to versioned aggregate parameter structures in v12+.

## State And Persistence
No C state is stored here, but command payloads persist firmware scan state: active clients, blocklists, profiles, schedules, probe frame buffers, short SSIDs, BSSID filters, channel lists, adaptive dwell overrides, and UIDs that identify scans across abort/start/complete notifications. Flexible arrays and fixed maximum channel/profile counts determine command allocation sizes in callers.

## Dependencies And Integration Points
Integrates with mac80211 scan and scheduled-scan APIs, iwlwifi MVM scan builders, firmware command groups, regulatory channel lists, 6 GHz colocated AP discovery, station/probe TX setup, and survey reporting. It relies on Ethernet/SSID constants, bit macros, and TX/rate definitions from neighboring API headers.

## Risks
Versioned structures have subtly different sizes, field ordering, channel limits, and flag meanings. Mixing general flag version 1 and version 2 can change passive scan, preemptive, adaptive dwell, OCE, or 6 GHz behavior. Probe request segment offsets and flexible data tails must match constructed buffers. Bad channel counts or adaptive-dwell bitmaps can overrun firmware expectations or skip regulatory-required passive behavior.

## Test Signals
Validate active/passive scans on 2.4, 5, and 6 GHz; scheduled scan profile matching; abort races; scan preemption; adaptive dwell; fragmented scan; per-channel survey notifications; short-SSID/BSSID filters; and UHB/PSC discovery behavior. Firmware logs, cfg80211 scan completion, and mac80211 survey data are the primary runtime indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/scan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sf.h

## Purpose
Defines the Smart FIFO firmware configuration ABI. Smart FIFO tunes RX FIFO watermarks and aging/idle timers for power/performance behavior across traffic scenarios.

## Important APIs, Types, And Functions
`enum iwl_sf_state` describes Smart FIFO operating states such as full-on, uninitialized, and init-off. `enum iwl_sf_scenario` covers unicast, aggregation, multicast, BA response, and TX response scenarios. Constants define default and BSS-specific watermarks/timers. `struct iwl_sf_cfg_cmd` is the packed command sent to firmware with state, watermarks, and timeout matrices.

## Control Flow
There is no local execution. Callers choose a Smart FIFO state and timer profile based on interface mode and activity, then send `iwl_sf_cfg_cmd` to firmware. Firmware applies the selected transient-state watermarks and per-scenario timeout values to RX FIFO handling.

## State And Persistence
The header stores no state. Firmware persists the configured Smart FIFO state until reconfigured, reset, or device restart. The command embeds two transient watermarks and two timer values for each scenario, so partial initialization bugs can affect multiple traffic classes.

## Dependencies And Integration Points
Uses bit macros and little-endian types from the kernel environment. It integrates with iwlwifi power management and RX buffering decisions, especially BSS configuration and scan/powersave transitions.

## Risks
Timer comments mix microsecond and millisecond wording, so callers should treat constants as firmware-defined units aligned to 32 usec rather than infer from comments. Incorrect watermarks can starve RX buffering or waste power. `SF_LONG_DELAY_ON` is documented as not driver-called, so selecting it directly would violate the intended state machine.

## Test Signals
Exercise association, multicast traffic, aggregation-heavy traffic, scan, and powersave transitions while watching RX drops, latency, and power behavior. Firmware command tracing should confirm expected `iwl_sf_cfg_cmd` values for BSS and default profiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sta.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sta.h

## Purpose
Defines station-table and station-key firmware command ABI for iwlwifi MVM. It describes station flags, add/modify/remove station commands, aggregation setup, U-APSD and power-save state, key programming, management multicast keys, WEP keys, and EOSP notifications.

## Important APIs, Types, And Functions
Key enums include `iwl_sta_flags`, `iwl_sta_key_flag`, `iwl_sta_modify_flag`, `iwl_sta_mode`, `iwl_sta_sleep_flag`, `iwl_sta_type`, and `iwl_mvm_add_sta_rsp_status`. Main structures are `iwl_mvm_add_sta_cmd_v7`, `iwl_mvm_add_sta_cmd`, `iwl_mvm_add_sta_key_common`, `iwl_mvm_add_sta_key_cmd_v1`, `iwl_mvm_add_sta_key_cmd`, `iwl_mvm_rm_sta_cmd`, `iwl_mvm_mgmt_mcast_key_cmd`, `iwl_mvm_wep_key_cmd`, and `iwl_mvm_eosp_notification`.

## Control Flow
Driver station lifecycle maps to firmware table operations: add a station with MAC/context/type/capability flags, modify selected fields through `modify_mask`, configure BA sessions and queue ownership, install keys, and remove the station on teardown. Power-save changes use sleep flags, U-APSD ACs, and sleep TX counts. Security commands program per-station, multicast management, and WEP keys, then TX/RX paths rely on key offsets and flags.

## State And Persistence
The actual persistent state lives in firmware station/key tables. This header defines the packed records that mutate that state: station ID, MAC context, association/auth flags, channel width/MIMO capabilities, aggregation parameters, queue masks, RX BA window, key material, PN/RSC counters, and management key IDs. Firmware may update some capability flags after action frames.

## Dependencies And Integration Points
Integrates with mac80211 station/key callbacks, iwlwifi MVM station tracking, TX queue setup, RX reorder setup, security offload, TDLS station types, multicast/AP beacon behavior, and U-APSD service period handling. It uses shared context IDs, station counts, endian annotations, and crypto constants.

## Risks
The station table is central to TX, RX, security, and aggregation, so ID/color mismatches or stale station IDs can misdirect traffic. `modify_mask` must match changed fields or firmware may ignore updates. Key flag aliases share bits for WEP/non-WEP meanings, and version differences in TKIP/RSC layout can break replay protection. Queue masks are obsolete for newer TX APIs but still present in older command versions.

## Test Signals
Test add/modify/remove for AP, client, multicast, TDLS, and auxiliary stations; key install/remove for WEP, CCMP, GCMP, TKIP, CMAC/GMAC; RX BA setup/removal; U-APSD/EOSP; powersave transitions; and station-table exhaustion. Firmware responses should surface overload, BA failure, or modify-nonexistent errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/sta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/stats.h

## Purpose
Defines firmware statistics command and notification ABI. It includes older monolithic statistics notifications and newer typed system-statistics notifications for operational, PHY, MAC, RX, TX, duration, and HE counters.

## Important APIs, Types, And Functions
Core legacy structures include `iwl_notif_statistics_v10`, `iwl_notif_statistics_v11`, `iwl_notif_statistics`, `iwl_statistics_cmd`, and their nested RX/TX/general/load structs. Newer system-statistics APIs include `iwl_system_statistics_cmd`, `iwl_statistics_ntfy_hdr`, `iwl_system_statistics_notif_oper`, `iwl_system_statistics_part1_notif_oper`, `iwl_statistics_operational_ntfy`, `iwl_statistics_phy_ntfy`, `iwl_statistics_mac_ntfy`, `iwl_statistics_rx_ntfy`, `iwl_statistics_tx_ntfy`, `iwl_statistics_duration_ntfy`, and `iwl_statistics_he_ntfy`.

## Control Flow
The driver can request statistics, clear counters, disable unsolicited notifications, or configure system-statistics notification cadence and type masks. Firmware emits either legacy aggregate notifications or typed notifications with a common header identifying type, version, and size. Consumers parse nested per-MAC, per-link, per-PHY, and per-station arrays to update debugfs, survey, telemetry, and rate/control diagnostics.

## State And Persistence
No state is stored in this header, but firmware counters persist between reports until reset/clear semantics request clearing. Fields track beacon counts, missed beacons, channel load, RX/TX time, BT coexistence deferrals, aggregation outcomes, PHY errors, CCA, power/temperature, HE trigger/MU activity, and station energy. Some structures differ by MAC/link capacity constants.

## Dependencies And Integration Points
Includes `mac.h` and `mac-cfg.h` for MAC/link/station limits. Integrates with iwlwifi debugfs statistics, mac80211 survey/station reporting, firmware health monitoring, beacon filtering, BT coexistence diagnostics, MLO/link accounting, and channel-load based policy decisions.

## Risks
Versioned structures differ in array dimensions and field availability; parsing by the wrong notification version can shift every following counter. Many counters are firmware-defined diagnostic values with sparse comments, so higher-level policy must avoid overinterpreting them. Reset/disable flags can unintentionally suppress periodic diagnostics or clear evidence needed for debugging.

## Test Signals
Issue on-demand and periodic stats commands, verify notification type/version/size handling, compare legacy and typed reports on supported firmware, validate channel load and beacon counters during association, force missed beacons and TX failures, and inspect HE counters during HE trigger/MU traffic. Sparse endian checks help catch missing `le32_to_cpu()` conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/system.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/system.h

## Purpose
Defines small system-level firmware configuration commands for SOC latency/stabilization and feature disablement.

## Important APIs, Types, And Functions
Constants define SOC configuration flags for discrete device mode and low latency, plus LTR apply-delay masks/values. `struct iwl_soc_configuration_cmd` carries SOC flags and stabilization latency. `struct iwl_system_features_control_cmd` carries a four-dword bitmap of features to disable.

## Control Flow
There is no local execution. During device initialization or feature negotiation, the driver sends SOC configuration to communicate platform latency and power-stability constraints, and may send system feature control to disable firmware features by bitmap.

## State And Persistence
Firmware persists the applied SOC and feature settings until reset or reconfiguration. The header itself is stateless. Version 1 of SOC configuration treats `flags` as a whole integer with only the discrete flag available, while version 2 permits independent bits.

## Dependencies And Integration Points
Uses kernel bit and little-endian types. It integrates with iwlwifi transport/device initialization, platform power management, latency tolerance reporting, and firmware capability gating.

## Risks
The version-specific interpretation of `flags` is easy to misuse: setting newer independent bits against a version-1 command can change the integer value in a way firmware does not expect. Incorrect latency values or LTR delay selection can affect power sequencing, wake latency, or XTAL stability.

## Test Signals
Boot devices across integrated and discrete platforms, verify firmware accepts SOC configuration, check low-latency mode behavior, and confirm disabled feature bitmaps produce expected capability changes without firmware asserts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tdls.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tdls.h

## Purpose
Defines firmware ABI for Tunneled Direct Link Setup (TDLS) support, especially TDLS channel switching, PTI templates, peer station bookkeeping, and sequence-number handoff for firmware-generated TDLS traffic.

## Important APIs, Types, And Functions
Key definitions include `IWL_TDLS_STA_COUNT`, `enum iwl_tdls_channel_switch_type`, `iwl_tdls_channel_switch_timing`, `iwl_tdls_channel_switch_frame`, `iwl_tdls_channel_switch_cmd`, `iwl_tdls_channel_switch_notif`, `iwl_tdls_sta_info`, `iwl_tdls_config_cmd`, `iwl_tdls_config_sta_info_res`, and `iwl_tdls_config_res`.

## Control Flow
The driver configures TDLS peer state with station IDs, reserved TIDs, initial SSNs, initiator flags, and PTI request template data. For channel switch, it sends a command describing whether to request, respond and move, or just move channel; the command includes peer timing from received frames, target channel info, TX parameters, and a frame template. Firmware reports channel-switch start status and returns last sequence numbers in config responses.

## State And Persistence
Firmware persists TDLS peer configuration for up to four peers, including per-peer station IDs, reserved TX TIDs, SSN counters, initiator state, and AP-facing TX sequence state. Channel-switch command data is transient, but firmware-generated PTI and channel-switch frames depend on stored templates and offsets.

## Dependencies And Integration Points
Includes `fw/api/tx.h` for TX command parameters and `fw/api/phy-ctxt.h` for channel information. Integrates with mac80211 TDLS operations, iwlwifi station table management, off-channel scheduling, template TX, and sequence-number synchronization with host state.

## Risks
Frame template offsets must point to valid timing/PTI data inside variable payloads. Sequence-number handoff between firmware-generated frames and host queues can duplicate or skip sequence numbers if responses are ignored. TDLS channel timing is in microseconds and tied to peer-provided IEs, so unit mistakes can break off-channel rendezvous. The fixed peer count limits concurrent TDLS links.

## Test Signals
Exercise TDLS peer add/remove, PTI request generation, channel-switch request/response/move flows, off-channel duration handling, and teardown while switching. Validate sequence numbers after firmware-based TX and confirm firmware notifications match mac80211 TDLS state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tdls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/time-event.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/time-event.h

## Purpose
Defines firmware scheduling ABI for time events, remain-on-channel operations, Hotspot/AUX ROC, P2P activities, and session protection. These commands reserve channel/time windows needed for association, P2P discovery/negotiation, quiet periods, channel switch, and other MAC activities.

## Important APIs, Types, And Functions
Key enums include `iwl_time_event_type`, v1/v2 fragmentation and repetition constants, `iwl_time_event_policy`, `iwl_mvm_hot_spot`, `iwl_roc_activity`, and `iwl_session_prot_conf_id`. Main structures are `iwl_time_event_cmd`, `iwl_time_event_resp`, `iwl_time_event_notif`, `iwl_hs20_roc_req`, `iwl_hs20_roc_res`, `iwl_roc_req_v5`, `iwl_roc_req`, `iwl_roc_notif`, `iwl_session_prot_cmd`, and `iwl_session_prot_notif`.

## Control Flow
The driver adds/removes time events by MAC/link ID and action. Firmware assigns unique IDs, schedules events according to apply time, max delay, dependencies, duration, repetition, fragmentation, and policy bits, then sends start/end notifications. ROC commands request a channel and duration for P2P/Hotspot activities. Session protection requests reserve association or P2P windows and always produce start/end notifications, even on scheduling failure.

## State And Persistence
Scheduled events persist in firmware until they expire, repeat-endlessly, are removed, or are superseded by session protection rules. Persistent identifiers include MAC/link IDs, unique event IDs, session IDs, activity IDs, and configuration IDs. The header itself stores no state but defines the fields used by driver-side tracking.

## Dependencies And Integration Points
Includes PHY channel context definitions and depends on common MAC context action/id concepts. Integrates with association protection, P2P listen/action scans, remain-on-channel mac80211 operations, CSA/NoA behavior, firmware scheduler arbitration, and MLO link-specific protection in newer notification versions.

## Risks
Time units mix GP2 timestamps, microseconds, and TUs across structures. Misinterpreting policy bits can create absent/present windows at the wrong time or suppress critical notifications. Unique IDs from responses must be retained for removal and matched against notifications. Only one concurrent session protection per vif is supported, so adding a new one replaces the old one.

## Test Signals
Validate association under scan/P2P load, ROC start/end notifications, ROC cancellation, P2P discovery and negotiation, session protection replacement, endless/repeated events, TSF/dependency scheduling, and firmware failure notifications. Race tests around remove vs. start/end notification are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/time-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tx.h

## Purpose
Defines firmware TX command, TX response, block-ack notification, beacon template, TX flush, and scheduler queue configuration ABI for iwlwifi. It spans older v6 TX commands, newer v9/v10+ TX command formats, status decoding, aggregation feedback, compressed BA notifications, beacon offload, and queue flushing.

## Important APIs, Types, And Functions
Key enums include `iwl_tx_flags`, `iwl_tx_cmd_flags`, `iwl_tx_pm_timeouts`, `iwl_tx_cmd_sec_ctrl`, `iwl_tx_offload_assist_flags_pos`, `iwl_tx_status`, `iwl_tx_agg_status`, `iwl_mvm_ba_resp_flags`, `iwl_dump_control`, and `iwl_scd_cfg_actions`. Core structures include `iwl_tx_cmd_v6_params`, `iwl_tx_cmd_v6`, `iwl_dram_sec_info`, `iwl_tx_cmd_v9`, `iwl_tx_cmd`, `iwl_tx_resp_v3`, `iwl_tx_resp`, `iwl_mvm_ba_notif`, `iwl_compressed_ba_notif`, `iwl_mac_beacon_cmd_v6/v7`, `iwl_mac_beacon_cmd`, `iwl_extended_beacon_notif`, `iwl_tx_path_flush_cmd`, and `iwl_scd_txq_cfg_cmd`.

## Control Flow
TX callers build command parameters, append the 802.11 header and payload, select rate/security/offload/lifetime/retry behavior, and submit through transport queues. Firmware returns per-frame or aggregated TX responses, later BA or compressed BA notifications advance aggregation queues. AP/IBSS paths install beacon templates and receive beacon TX notifications. Flush commands remove queued frames by queue bitmap or station/TID, and SCD config commands enable, disable, or retarget scheduler queues.

## State And Persistence
Persistent firmware-visible state includes TX queue configuration, station/TID ownership, beacon templates, security DRAM info, sequence control behavior, and aggregation progress. Per-command state includes lifetime, retry limits, offload flags, key selection, rate, and header/payload bytes. Flexible arrays in TX commands, responses, compressed BA notifications, and beacon templates require exact command sizing.

## Dependencies And Integration Points
Includes Linux 802.11 header definitions and integrates with mac80211 TX, iwlwifi transport/TFD queues, rate control/TLC, security offload, BT coexistence, AP beaconing, aggregation state machines, station table configuration, and TXQ scheduling.

## Risks
TX ABI version changes alter command layout and flag semantics. Incorrect length accounting around MAC header padding, IV/MIC/ICV/FCS exclusions, or A-MSDU offload can corrupt transmitted frames. Aggregation status is not equivalent to BA success; callers must combine TX responses with BA notifications. Queue flush and SCD retargeting can race with station teardown if IDs or colors are stale.

## Test Signals
Exercise unicast, multicast, management, EAPOL/high-priority, encrypted, A-MSDU, and aggregated TX across firmware API versions. Verify BA/compressed BA accounting, retry/failure statuses, beacon template updates with CSA/ECSA/BTWT, queue flush responses, and scheduler queue enable/disable flows. Air captures and mac80211 TX status propagation are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/txq.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/txq.h

## Purpose
Defines TX queue numbering, FIFO selection, queue sizing, and TXQ hardware scheduler configuration ABI for iwlwifi DQA and newer queue APIs.

## Important APIs, Types, And Functions
`enum iwl_mvm_dqa_txq` reserves queue IDs for command, auxiliary, P2P device/monitor injection, groupcast, BSS client, management, AP probe response, and data queues. `enum iwl_mvm_tx_fifo`, `enum iwl_gen2_tx_fifo`, and `enum iwl_bz_tx_fifo` define firmware FIFO mappings. `enum iwl_tx_queue_cfg_actions` controls queue enablement and short TFD format. `iwl_tx_queue_cfg_cmd` and `iwl_tx_queue_cfg_rsp` are the packed command/response structures.

## Control Flow
During queue setup, the driver chooses a station/TID, flags, cyclic buffer size, byte-count table DMA address, and TFD queue DMA address, then sends `iwl_tx_queue_cfg_cmd`. Firmware returns the assigned queue number, failure flags, and initial write pointer. Higher-level TX code then maps station/TID traffic or reserved management/control traffic onto these queues.

## State And Persistence
Queue configuration persists in firmware scheduler state and host DMA rings until disabled or device reset. The header defines persistent queue IDs, FIFO mappings, default queue sizes for EHT/HE/legacy, and management/command queue capacities. DMA addresses in the command tie firmware queue state to host-allocated memory.

## Dependencies And Integration Points
Integrates with iwlwifi transport queue allocation, TX command submission, station/TID mapping, aggregation setup, management queue pools, monitor injection, P2P device operation, and generation-specific FIFO selection. It is closely related to scheduler commands in `tx.h`.

## Risks
Queue ID reservations are policy contracts; reusing reserved queues incorrectly can starve command, aux, BSS client, or management traffic. `cb_size` is encoded as an exponent-derived value with documented limits, so wrong encoding can mismatch host ring allocation. DMA addresses must remain valid and aligned for firmware ownership.

## Test Signals
Validate queue allocation on legacy, HE, EHT, Gen2, and BZ FIFO mappings; station/TID queue setup; management queue exhaustion fallback; monitor injection vs. P2P device mutual exclusion; aggregation queue creation; and firmware response failure flags. TX stalls and queue write-pointer mismatches are primary regression indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/txq.h -->
