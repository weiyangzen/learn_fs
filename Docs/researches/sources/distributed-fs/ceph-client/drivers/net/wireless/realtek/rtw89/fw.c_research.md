# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/fw.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004924`: lines 1-9119, `Docs/researches/chunks/subset-b-004924_research.md`
- `subset-b-004925`: lines 9120-11346, `Docs/researches/chunks/subset-b-004925_research.md`

## Chunk Research

### subset-b-004924: lines 1-9119

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/fw.c lines 1-9119

## Scope and purpose

This chunk covers the first 9119 lines of `fw.c`, the Realtek rtw89 firmware orchestration layer. The code in this range recognizes and validates firmware images, parses multi-firmware and embedded element formats, downloads firmware sections through H2C transport, builds firmware log dictionaries, sends many firmware commands for MAC/PHY/BT coexistence/scan offload state, dispatches C2H firmware events, and prepares hardware scan channel and packet-offload lists.

The file is not a standalone driver entry point. It is a shared service layer used by chip-specific MAC/PHY operations, mac80211 callbacks, WoWLAN code, RF calibration code, and Bluetooth coexistence logic. Most public functions allocate a command skb, fill little-endian command fields via `le32_encode_bits()` or RTW89 `SET_*` macros, attach an H2C header with `rtw89_h2c_pkt_set_hdr()`, and send it through `rtw89_h2c_tx()` or `rtw89_h2c_tx_and_wait()`.

## Firmware image recognition and download

Important APIs and types:

- `rtw89_fw_check_rdy()` polls chip MAC status callbacks until the requested firmware download stage reports ready, maps checksum/security/CV failures to hard errors, and sets `RTW89_FLAG_FW_RDY`.
- `rtw89_fw_hdr_parser_v0()` and `rtw89_fw_hdr_parser_v1()` decode firmware headers into `struct rtw89_fw_bin_info`, including section count, dynamic header length, download address, section lengths, checksum extension, part size, and secure-section metadata.
- `__parse_security_section()`, `__parse_formatted_mssc()`, `__get_mssc_key_idx()`, and `__check_secure_blacklist()` select secure-boot key material from MSS/MSSC trailers and reject blacklisted secure firmware when the chip provides a blacklist.
- `rtw89_mfw_get_hdr_ptr()`, `rtw89_mfw_validate_hdr()`, `rtw89_mfw_recognize()`, and `rtw89_mfw_get_size()` support Realtek MFW containers, selecting normal, CE, WoWLAN, BB MCU, or log-format payloads by type and chip cut version.
- `rtw89_fw_recognize()` chooses the active normal and WoWLAN firmware variants, validates variant minimum version, recognizes optional log-format firmware, enables firmware feature bits, and passes version information to coexistence code.
- `rtw89_fw_recognize_elements()` walks firmware elements after the MFW payload and dispatches each element through `__fw_element_handlers`.
- `rtw89_fw_download()`, `__rtw89_fw_download()`, `rtw89_fw_download_suit()`, `rtw89_fw_download_hdr()`, and `rtw89_fw_download_main()` perform CPU reset/enable, header download, section download, BB MCU download, retry, and final FreeRTOS readiness checks.

Key control flow:

1. Firmware is requested asynchronously by `rtw89_load_firmware_work()` and completion is waited on by `rtw89_wait_firmware_completion()`.
2. `rtw89_fw_recognize()` selects a firmware suit from a legacy raw image or MFW container, updates version fields, records `wiphy->fw_version`, and derives `rtwdev->fw` feature bits from `fw_feat_tbl`.
3. `rtw89_fw_recognize_elements()` starts after the aligned MFW payload size and builds side tables from embedded elements: BB/RF register tables, TX power tables, TX power tracking, RFK log formats, regulatory maps, AFE power sequence, diagnostic MAC, and TX compensation data.
4. Download parses header sections again, tells secure IDMEM-share mode to lower layers, checks H2C firmware-download path readiness, sends a tweaked firmware header, sends each section split by `info->part_size`, optionally overlays selected secure key data, and waits for download/Freertos completion.

State and persistence:

- Firmware payload ownership lives in `rtwdev->fw.req.firmware`; `rtw89_unload_firmware()` cancels the loader, releases the firmware object, frees firmware log formats, and frees element-built PHY tables.
- Version and command metadata are persisted in `struct rtw89_fw_suit` fields and `rtwdev->fw.h2c_seq`, `rec_seq`, `h2c_counter`, and `c2h_counter`.
- Parsed element tables persist under `rtwdev->fw.elm_info`; TX power RFE data persists in `rtwdev->rfe_data`; regulatory data is devm-managed in `elm_info->regd`.
- Secure-boot behavior depends on persistent chip/efuse-like state in `rtwdev->fw.sec`, `rtwdev->hal.cv`, `rtwdev->hal.aid`, and chip `fw_blacklist`.

Risks in this area:

- Header parsers trust many firmware-provided sizes after boundary checks. The final `fw_end == bin` check is important; any future parser path must preserve complete size accounting including checksum and MSSC trailers.
- `rtw89_fw_update_ver_v1()` reads command version from a field macro named `FW_HDR_V1_W3_CMD_VERSERION` while using `hdr->w7`; this may be intentional macro naming, but it is a review point for new header formats.
- Element parsing treats handler return `1` as "ignore" and any other nonzero as failure. New handlers must preserve this convention or the `needed_fw_elms` reconciliation becomes misleading.
- Download retry loops run the full WCPU enable/download path up to five times and dump firmware PC/status on failure; tests should include failure injection for checksum/security/path-ready/readiness errors.

## Firmware features and logs

`fw_feat_tbl` maps chip IDs and firmware version thresholds to `RTW89_FW_FEATURE_*` bits, including scan offload, beacon filtering/tracking, LPS behavior, crash-trigger formats, RFK notification formats, BE address-CAM compatibility, and MLO/MLSR-related capabilities. `rtw89_early_fw_feature_recognize()` can request firmware before full device initialization, inspect a compatible version code, and seed early feature bits.

Firmware logs are handled by:

- `rtw89_fw_log_prepare()` and `rtw89_fw_log_create_fmts_dict()`, which parse a log-format firmware suit into ID and format-string arrays.
- `rtw89_fw_log_dump()`, which distinguishes plain C2H strings from formatted log records with `RTW89_C2H_FW_LOG_SIGNATURE`.
- `rtw89_fw_h2c_fw_log()`, which enables selected firmware log components such as init, task, power-save, error, MLO, and scan through H2C.

Test signals include visible `rtw89_info()` firmware version lines, `C2H log:` output, feature-dependent behavior changes, and warning/error logs for malformed log payloads or missing log-format firmware.

## H2C command construction pattern

Common helpers:

- `rtw89_fw_h2c_alloc_skb_with_hdr()` and `rtw89_fw_h2c_alloc_skb_no_hdr()` reserve chip H2C descriptor space and, when needed, H2C header room.
- `rtw89_h2c_pkt_set_hdr()` pushes an 8-byte firmware command header, sets type/category/class/function/sequence/length, optionally requests receive and done acknowledgements, and forces a receive acknowledgement every fourth AX command.
- `rtw89_h2c_pkt_set_hdr_fwdl()` is a firmware-download-specific header helper that does not advance `h2c_seq`.
- `rtw89_fw_h2c_raw_with_hdr()` and `rtw89_fw_h2c_raw()` send caller-provided command bytes.
- `rtw89_fw_send_all_early_h2c()` replays saved early commands from `rtwdev->early_h2c_list`; `rtw89_fw_free_all_early_h2c()` frees that list under wiphy lock expectations.

Most functions follow the same error-handling contract: allocate skb, fill fixed-length payload, set H2C header, send, free skb on send failure, and return the transport status. Commands that need firmware completion use `rtw89_h2c_tx_and_wait()` with `rtwdev->mac.fw_ofld_wait` and a condition token.

## MAC CAM, BA, CCTL, beacon, join, and role commands

This chunk implements many MAC-facing H2Cs:

- Address/BSSID/security CAM updates: `rtw89_fw_h2c_cam()` selects legacy or newer address-CAM format based on chip generation and `ADDR_CAM_V0`; `rtw89_fw_h2c_dctl_sec_cam_v1/v2/v3()` and default DMAC table variants fill security/control table formats via CAM helpers.
- BA CAM: `rtw89_fw_h2c_ba_cam()`, `rtw89_fw_h2c_ba_cam_v1()`, `rtw89_fw_h2c_init_dynamic_ba_cam_v0_ext()`, and `rtw89_fw_h2c_init_ba_cam_users()` allocate/release static BA entries, configure bitmap size from AMPDU buffer size, and initialize dynamic BA users.
- CMAC/CCTL defaults and association updates: `rtw89_fw_h2c_default_cmac_tbl*()`, `rtw89_fw_h2c_assoc_cmac_tbl*()`, `rtw89_fw_h2c_ampdu_cmac_tbl*()`, `rtw89_fw_h2c_txtime_cmac_tbl*()`, `rtw89_fw_h2c_punctured_cmac_tbl*()`, and `rtw89_fw_h2c_txpath_cmac_tbl()` program per-MACID transmission policy, rates, padding, puncturing, retry/time limits, AMPDU BA bitmap, and TX path.
- Beacon and P2P: `rtw89_fw_h2c_update_beacon()` and `_be()` fetch a TIM beacon from mac80211, append P2P NoA data when present, compute TIM offset relative to the 802.11 header, and send the full beacon payload to firmware. `rtw89_fw_h2c_p2p_act()` sends NoA action parameters.
- Timing/power/media: `rtw89_fw_h2c_tbtt_tuning()`, `rtw89_fw_h2c_pwr_lvl()`, `rtw89_fw_h2c_role_maintain()`, `rtw89_fw_h2c_join_info()`, `rtw89_fw_h2c_notify_dbcc()`, `rtw89_fw_h2c_macid_pause()`, `rtw89_fw_h2c_set_edca()`, `rtw89_fw_h2c_tsf32_toggle()`, and `rtw89_fw_h2c_set_ofld_cfg()` push state about TBTT shifts, beacon timeout thresholds, firmware role, MLO main MACID, DBCC, MACID pause/sleep, EDCA, TSF32 reporting, and offload configuration.

The association table functions rely on RCU-protected mac80211 state (`ieee80211_bss_conf`, `ieee80211_link_sta`) and derive HE/EHT nominal packet padding with `__get_sta_he_pkt_padding()` and `__get_sta_eht_pkt_padding()`. This is a high-risk area for null pointer regressions: callers must provide valid link state and hold correct mac80211/wiphy synchronization so the RCU dereferences with `true` requirements are valid.

## Power-save, WoWLAN, and packet offload

The chunk creates firmware-owned packet templates:

- `rtw89_eapol_get()`, `rtw89_sa_query_get()`, and `rtw89_arp_response_get()` synthesize protected EAPOL, SA Query, and ARP response frames using current vif/link addresses and WoWLAN security parameters.
- `rtw89_fw_h2c_add_general_pkt()` builds PS-Poll, probe response, null, QoS null, EAPOL, SA Query, or ARP packet templates and registers them with firmware packet offload.
- `rtw89_fw_h2c_general_pkt()` installs common PS/offload packet IDs for a MACID.
- `rtw89_fw_release_general_pkt_list_vif()` and `rtw89_fw_release_general_pkt_list()` either notify firmware to delete packet IDs or only release the local bitmap when firmware is not available.
- `rtw89_fw_h2c_add_pkt_offload()` and `rtw89_fw_h2c_del_pkt_offload()` allocate IDs from `rtwdev->pkt_offload`, send add/delete commands with wait conditions, and maintain bitmap consistency.

LPS/low-power helpers include `rtw89_fw_h2c_lps_parm()`, `rtw89_fw_h2c_lps_ch_info()`, `rtw89_fw_h2c_lps_ml_cmn_info()`, `rtw89_fw_h2c_lps_ml_cmn_info_v1()`, and `rtw89_bb_lps_cmn_info_rx_gain_fill()`. These BE-only multi-link commands send MLO/DBCC mode, per-link channels, beacon rates, RSSI minima, duplicated beacon offsets, and RX-gain calibration tables; completion is polled through PHY registers such as `R_CHK_LPS_STAT` or `R_CHK_LPS_STAT_BE4`.

State and risks:

- Packet IDs persist in per-link `general_pkt_list`, scan `pkt_list[]`, WoWLAN PNO lists, and the global `pkt_offload` bitmap. Any error path that forgets to release an acquired bitmap bit will exhaust `RTW89_MAX_PKT_OFLD_NUM`.
- Template generation mixes RCU-protected BSS data and stored link fields. Address and security changes around suspend/resume or MLO link changes need targeted tests.
- LPS ML commands copy large gain tables indexed by band, bandwidth, path, and PHY. Invalid channel context or path selection can lead to wrong firmware calibration data even when the H2C succeeds.

## Beacon filter, throughput, rate adaptation, and thermal/offload H2Cs

Additional firmware offload commands include:

- `rtw89_fw_h2c_tx_duty()` computes active/pause duty cycle for thermal protection, with a static assertion that configured levels stay under 100 percent.
- `rtw89_fw_h2c_set_bcn_fltr_cfg()` enables/disables RSSI and beacon monitoring when firmware supports `BEACON_FILTER`, using mac80211 CQM threshold/hysteresis and feature-dependent beacon loss count width.
- `rtw89_fw_h2c_rssi_offload()` reports RSSI observations to firmware for beacon filtering.
- `rtw89_fw_h2c_tp_offload()` sends per-vif TX/RX throughput values.
- `rtw89_fw_h2c_ra()` sends rate-adaptation state, including AX and BE/EHT formats, rate masks, bandwidth/NSS/LDPC/STBC/SGI/GI-LTF fields, CSI feedback rate control for AX, and extra BE fields in v1.

These flows depend on `rtw89_ra_info`, `rtw89_traffic_stats`, `rtw89_rx_phy_ppdu`, and firmware feature bits. Test signals include successful H2C transport, firmware done acknowledgements where requested, RA debug logs, and observable rate-control/beacon-filter behavior under association and roaming tests.

## Bluetooth coexistence integration

The `cxdrv` H2Cs serialize driver-side Wi-Fi state to firmware/BT coexistence logic:

- `rtw89_fw_h2c_cxdrv_init()` and `_v7()` send module/antenna/initial coexistence topology.
- `rtw89_fw_h2c_cxdrv_role()`, `_v1()`, `_v2()`, `_v7()`, and `_v8()` send role maps, active port roles, DBCC/link-mode details, and versioned compact structures.
- `rtw89_fw_h2c_cxdrv_osi_info()` sends out-source set info.
- `rtw89_fw_h2c_cxdrv_ctrl()` and `_v7()` send manual/free-run/ignore-BT controls.
- `rtw89_fw_h2c_cxdrv_trx()` sends WLAN/BT RSSI, TX/RX levels, power/gain, rates, throughput, and error ratio.
- `rtw89_fw_h2c_cxdrv_rfk()` sends RFK state, path map, PHY map, band, and type.

These functions depend on `rtwdev->btc`, `btc->ver`, `btc->cx.wl`, and `btc->dm` structures populated by coexistence code. Version fields (`fcxinit`, `fwlrole`, `fcxctrl`, `fcxosi`) must match the firmware's expected layout; the many near-duplicate role formats are a regression risk when adding chip generations.

## RF, RFK, and PHY offload commands

RF-related H2Cs in this chunk include:

- `rtw89_fw_h2c_rf_reg()` sends RF register programming pages to RF path-specific H2C classes.
- `rtw89_fw_h2c_rf_ntfy_mcc()`, `rtw89_fw_h2c_mcc_dig()`, `rtw89_fw_h2c_rf_ps_info()`, `rtw89_fw_h2c_rf_pre_ntfy()`, and `rtw89_fw_h2c_rf_pre_ntfy_mcc()` notify firmware about MCC channels, DIG PD thresholds, BE RF power-save RF18 values, MLO/DBCC mode, RFK channel tables, RF mode registers, RFE type, AID, and ACV.
- Calibration offloads `rtw89_fw_h2c_rf_tssi()`, `rtw89_fw_h2c_rf_iqk()`, `rtw89_fw_h2c_rf_dpk()`, `rtw89_fw_h2c_rf_txgapk()`, `rtw89_fw_h2c_rf_dack()`, `rtw89_fw_h2c_rf_rxdck()`, `rtw89_fw_h2c_rf_tas_trigger()`, `rtw89_fw_h2c_rf_txiqk()`, and `rtw89_fw_h2c_rf_cim3k()` package current channel/bandwidth/band/PHY/path/CV/debug fields for firmware calibration jobs.

The main cross-chunk dependency is that later C2H RFK handlers must interpret completion/status for these offloads. This chunk only sends commands and logs send failures. The format chosen for several commands is gated by `RTW89_FW_FEATURE_RFK_*` bits, so firmware-version tests are important.

## C2H event handling and register mailbox

C2H logic in this range:

- `rtw89_fw_c2h_parse_attr()` extracts category, class, function, and length into skb control block `RTW89_SKB_C2H_CB`.
- `rtw89_fw_c2h_irqsafe()` handles atomic-safe C2H events immediately when `rtw89_mac_c2h_chk_atomic()` or `rtw89_phy_c2h_chk_atomic()` permits it; otherwise it queues the skb on `rtwdev->c2h_queue` and schedules `rtwdev->c2h_work`.
- `rtw89_fw_c2h_cmd_handle()` dispatches MAC events to `rtw89_mac_c2h_handle()`, BTC PHY-class events to `rtw89_btc_c2h_handle()`, and other out-source events to `rtw89_phy_c2h_handle()`, skipping hex dumps for firmware log C2Hs.
- `rtw89_fw_c2h_work()` drains queued C2Hs under wiphy lock.
- `rtw89_fw_c2h_purge_obsoleted_scan_events()` removes queued scan events whose stored sequence no longer matches `scan_info->seq`.
- `rtw89_fw_msg_reg()`, `rtw89_fw_write_h2c_reg()`, and `rtw89_fw_read_c2h_reg()` implement a register mailbox path with control-register polling, H2C/C2H counters, USB-specific C2H timeout, and optional read-only C2H receive.
- `rtw89_fw_st_dbg_dump()` reads firmware status/debug registers and dumps program counters when powered on.

Synchronization requirements are explicit: most non-GET_FEATURE register H2Cs assert wiphy lock; queue movement uses `spin_lock_irqsave`; C2H command handling returns early unless `RTW89_FLAG_RUNNING` is set.

## Hardware scan and PNO scan preparation

This chunk contains the beginning and core of hardware scan offload support for AX and BE:

- Packet template preparation: `rtw89_hw_scan_update_probe_req()` creates per-SSID probe requests; `rtw89_append_probe_req_ie()` duplicates them per supported band, appends band/common IEs, marks 6 GHz wildcard templates, and registers each template with packet offload.
- 6 GHz RNR support: `rtw89_update_6ghz_rnr_chan_ax()` adds directed 6 GHz probe templates for RNR-discovered BSSIDs and extends scan dwell/period as needed.
- AX channel list building: `rtw89_pno_scan_add_chan_ax()`, `rtw89_hw_scan_add_chan_ax()`, `rtw89_pno_scan_add_chan_list_ax()`, `rtw89_hw_scan_prep_chan_list_ax()`, `rtw89_hw_scan_add_chan_list_ax()`, and `rtw89_hw_scan_free_chan_list_ax()` build and upload `struct rtw89_mac_chinfo_ax` entries in batches capped by `RTW89_SCAN_LIST_LIMIT_AX`.
- BE channel list building: `rtw89_pno_scan_add_chan_be()`, `rtw89_hw_scan_add_chan_be()`, `rtw89_pno_scan_add_chan_list_be()`, `rtw89_hw_scan_prep_chan_list_be()`, `rtw89_hw_scan_add_chan_list_be()`, and `rtw89_hw_scan_free_chan_list_be()` do the same for `struct rtw89_mac_chinfo_be`, including RNR-assisted skipping of non-PSC 6 GHz channels.
- Scan H2Cs: `rtw89_fw_h2c_scan_list_offload_ax()` and `_be()` upload channel info arrays; `rtw89_fw_h2c_scan_offload_ax()` and `_be()` start/stop scan offload, handle delayed start, operation-channel info, BE MLO/operation-channel flex sections, prohibited 6 GHz channels, no-CCK probe rates, and firmware wait conditions.
- Cleanup and AP/P2P NoA interaction: `rtw89_hw_scan_release_pkt_list()` deletes scan packet-offload templates; `rtw89_hw_scan_cleanup()` resets scan request/IE/scanning state; `rtw89_hw_scan_update_link_beacon_noa()` and the visible part of `rtw89_hw_scan_update_beacon_noa()` estimate scan TU from the channel list and update P2P GO beacons with NoA descriptors while scan runs.

Important scan state:

- `rtwdev->scan_info` owns `pkt_list[]`, `chan_list`, `op_chan`, `extra_op`, `scanning_vif`, `seq`, `abort`, `connected`, and `delay`.
- Each `rtw89_pktofld_info` stores firmware packet ID plus 6 GHz metadata such as wildcard flag, SSID, BSSID, and channel.
- Normal scan uses `rtwvif->scan_req` and `rtwvif->scan_ies`; PNO scan uses `rtwdev->wow.nd_config` and `rtwdev->wow.pno_pkt_list`.

Risks and edge cases:

- Hardware scan path has many ownership transfers between temporary lists and `scan_info->chan_list`; failure paths must free entries exactly once.
- AX upload avoids putting an operating-channel `tx_null` entry last in a full batch due to known USB chip behavior. This invariant should be preserved if scan batching changes.
- 6 GHz wildcard and RNR probe handling affects whether firmware transmits probes and how long it dwells. Regressions may appear only with hidden SSIDs, PSC/non-PSC channels, colocated 6 GHz scan flags, or `duration_mandatory`.
- BE scan flex-section sizes depend on firmware feature bits `SCAN_OFFLOAD_BE_V0` and `CH_INFO_BE_V0`; tests should cover both old and new firmware layouts.
- Scan event purging relies on C2H attr fields `is_scan_event` and `scan_seq` being set by lower-level handlers or RX parsing outside this chunk.

## Dependencies and integration points

Internal headers and subsystems used by this chunk:

- `cam.h`: address/BSSID/DCTL/security CAM fill helpers and CAM structure formats.
- `chan.h`: channel context access and channel conversion helpers.
- `coex.h`: Bluetooth coexistence version recognition and C2H/H2C data structures.
- `debug.h`: logging, hex dumps, debug-category checks.
- `fw.h`: firmware headers, command structures, feature bits, H2C/C2H macros, wait condition macros.
- `mac.h`: chip generation callbacks, H2C transport, C2H MAC handlers, TSF access, scan hooks.
- `phy.h`: PHY/RF command handlers, gain tables, RFK helpers, RF register access.
- `ps.h`, `wow.h`: low-power/WoWLAN security and PNO state.
- Linux/mac80211 APIs: firmware loader, skb allocation, RCU-protected vif/link/sta state, generated PS-Poll/null/probe/beacon frames, cfg80211 scan requests, supported bands/channels.

The main exported symbols in this chunk are H2C helpers used by chip ops and other rtw89 modules, including DCTL/DMAC/CCTL variants, BA CAM variants, beacon updates, RF notifications, and firmware blacklist defaults.

## Test and validation signals

Useful validation coverage for this chunk:

- Firmware request/recognition with legacy and MFW images, optional CE/WoWLAN/logfmt suits, secure and non-secure images, blacklisted images, and missing required elements.
- Firmware download failure injection for path-ready timeout, header parse error, section send failure, secure key selection failure, checksum/security status failure, and FreeRTOS readiness timeout.
- H2C unit or trace tests that confirm command category/class/function/length, ack bits, and sequence behavior for representative AX and BE commands.
- Association tests across non-HE, HE, and EHT peers to verify CMAC padding, puncturing, rate, and join-info formats.
- Packet offload tests that exhaust, add, delete, and cleanup packet IDs through normal disconnect, scan abort, suspend/resume, and firmware-not-ready paths.
- Hardware scan tests over active, DFS, P2P, connected, 6 GHz PSC/non-PSC, RNR-colocated, random sequence, no-CCK, delayed, and BE MLO scenarios.
- C2H tests that confirm atomic dispatch, deferred queue drain, scan event purge by sequence, firmware log formatting, and register mailbox timeout/counter behavior.
- RFK/coexistence tests on old/new firmware feature layouts to confirm command size and fields match selected version gates.

## Cross-chunk references

The assigned range stops inside `rtw89_hw_scan_update_beacon_noa()`. Later chunks are expected to cover the remainder of hardware scan start/abort/completion callbacks, WoWLAN/MCC commands, AP-info refcounting, TX power table loading, and RFE parameter lookup. This chunk establishes the firmware image, H2C/C2H, packet-offload, and scan-list infrastructure that those later functions rely on.

### subset-b-004925: lines 9120-11346

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/fw.c lines 9120-11346

## Scope

This chunk covers the tail of the Realtek rtw89 firmware-interface source file. It starts inside the hardware scan implementation and continues through firmware H2C command builders for scan, crash triggering, packet drop, WoWLAN, firmware IPS, MCC/MRC/MLO scheduling, AP power-interrupt state, and firmware-loaded transmit-power/RFE tables.

The range is not a standalone compilation unit. It depends heavily on earlier helper definitions in `fw.c`, firmware command layout macros, and rtw89 core/mac/phy/channel-context APIs. The functions here are nevertheless substantive entry points used by the rest of the driver to program firmware behavior and to translate firmware-provided regulatory/RFE data into in-memory PHY tables.

## Purpose

The code in this chunk is an adapter between high-level rtw89 driver state and firmware command/data contracts:

- Hardware scan routines preserve the current operating channel, pause channel contexts, alter RX filtering, coordinate beacon/NoA behavior for MCC, and restore mac80211 state when scan completes or aborts.
- H2C builders allocate firmware command skbs, fill little-endian bitfields, attach firmware command headers, send commands, and sometimes wait for matching C2H completion conditions.
- WoWLAN helpers configure keep-alive, ARP response, disconnect detection, PNO/NLO, wakeup sources, CAM pattern entries, GTK rekey offload, AOAC reporting, and global WoW security parameters.
- MCC and MRC helpers program multi-channel/multi-role schedules and request TSF synchronization data from firmware.
- MLO and AP helpers configure firmware-visible link/AP state with explicit wait or refcount semantics.
- RFE/tx-power loaders validate firmware table entries and install by-rate, limit, RU-limit, and transmit-shape data into `rtwdev->rfe_data` and derived `rtw89_rfe_parms`.

## Important APIs, Types, and Functions

### Hardware Scan

- `rtw89_hw_scan_set_extra_op_info()` inspects `rtwdev->hal.entity_mgnt.active_list` for an active vif other than the scanning vif. When firmware advertises `SCAN_OFFLOAD_EXTRA_OP`, it records one extra operating channel in `rtwdev->scan_info.extra_op` with MAC ID, port, channel, and link pointer.
- `rtw89_hw_scan_start()` initializes `rtwdev->scan_info`, selects the scan MAC address, runs scan prehandling, stops mac80211 queues, disables port RX sync, calls `rtw89_core_scan_start()`, relaxes RX filters, pauses channel contexts, suspends DIG, and updates MCC beacon/NoA when applicable.
- `rtw89_hw_scan_complete_cb()` restores the hardware RX filter, completes scan state, reports `ieee80211_scan_completed()`, wakes queues, reenables RX sync and AP beacons, resumes DIG, cleans scan state, and clears MCC beacon/NoA updates.
- `rtw89_hw_scan_complete()` wraps completion in `rtw89_chanctx_proceed()` so channel-context sequencing happens in the required order for coexistence and MCC state transitions.
- `rtw89_hw_scan_abort()` marks `scan_info.abort`, sends a stop scan-offload command, and always completes the scan as aborted after the firmware-side stop path has synchronized.
- `rtw89_is_any_vif_connected_or_connecting()` treats any nonzero link BSSID as connected or connecting, feeding scan target-channel mode decisions.
- `rtw89_hw_scan_offload()` builds `struct rtw89_scan_option`, optionally asks the chip MAC generation ops to add the channel list, and calls `rtw89_mac_scan_offload()`. On BE chips it additionally fills operation, scan mode, band, MLO mode, and operating-channel counts, including the extra-op entry above.

### Generic and WoW H2C Commands

- `rtw89_fw_h2c_trigger_cpu_exception()` selects a firmware crash trigger encoding based on `CRASH_TRIGGER_TYPE_1` or `CRASH_TRIGGER_TYPE_0` feature bits and sends a test H2C command.
- `rtw89_fw_h2c_pkt_drop()` sends a packet-drop command using `struct rtw89_pkt_drop_params`; unsupported selector values are only debug logged.
- `rtw89_fw_h2c_keep_alive()` optionally creates a null-data offload packet and configures firmware keep-alive for the link MAC ID.
- `rtw89_fw_h2c_arp_offload()` optionally creates an ARP response offload packet and sends the ARP offload command.
- `rtw89_fw_h2c_disconnect_detect()` programs firmware disconnect detection only when `RTW89_WOW_FLAG_EN_DISCONNECT` is set, with fixed check period and retry count values.
- `rtw89_fw_h2c_cfg_pno()` transfers sched-scan match-set SSIDs from `rtwdev->wow.nd_config` into the NLO command when enabled.
- `rtw89_fw_h2c_wow_global()` sends global WoW enable state, MAC ID, pairwise/group security algorithms, and key metadata.
- `rtw89_fw_h2c_wow_wakeup_ctrl()` enables wake sources according to pattern count and WoW flags, including MLD magic-packet enable when the vif is MLD.
- `rtw89_fw_h2c_wow_cam_update()` and `rtw89_fw_h2c_wow_cam_update_v1()` program two firmware generations of WoW pattern CAM format. Both are exported symbols for chip-specific modules.
- `rtw89_fw_h2c_wow_gtk_ofld()` configures GTK rekey offload when a group cipher algorithm exists, allocating EAPOL and optional SA Query packet templates before populating GTK/PMF fields.
- `rtw89_fw_h2c_fwips()` sends firmware idle power-save configuration and waits on `rtwdev->mac.ps_wait`.
- `rtw89_fw_h2c_wow_request_aoac()` requests an AOAC report C2H and waits on `rtwdev->wow.wait`.
- `rtw89_h2c_tx_and_wait()` is the shared send-and-wait helper. It prepares a wait condition, transmits the skb, maps send failure to `-EBUSY`, treats SER handling as an unreachable-but-known positive result, and delegates final status to `rtw89_wait_for_cond_eval()`.

### MCC and MRC Scheduling

- MCC commands are fixed-length H2Cs with wait conditions keyed by group and function: `rtw89_fw_h2c_add_mcc()`, `rtw89_fw_h2c_start_mcc()`, `rtw89_fw_h2c_stop_mcc()`, `rtw89_fw_h2c_del_mcc_group()`, `rtw89_fw_h2c_reset_mcc_group()`, `rtw89_fw_h2c_mcc_req_tsf()`, `rtw89_fw_h2c_mcc_macid_bitmap()`, `rtw89_fw_h2c_mcc_sync()`, and `rtw89_fw_h2c_mcc_set_duration()`.
- `rtw89_fw_h2c_mcc_req_tsf()` copies a firmware C2H TSF report from `wait->data.buf` to the caller's `struct rtw89_mac_mcc_tsf_rpt`.
- `rtw89_fw_h2c_mcc_macid_bitmap()` asserts byte-aligned `RTW89_MAX_MAC_ID_NUM`, calculates the dynamic bitmap payload length, and embeds the bitmap after a descriptor prefix.
- `rtw89_fw_h2c_mrc_add_slot()` is a size-calculation and optional-fill helper for variable-length MRC slot records. It encodes slot duration, courtesy parameters, role metadata, channel fields, and MACID bitmaps.
- `rtw89_fw_h2c_mrc_add()` builds a variable-length MRC schedule command from a header followed by encoded slots.
- `rtw89_fw_h2c_mrc_start()`, `rtw89_fw_h2c_mrc_del()`, and `rtw89_fw_h2c_mrc_req_tsf()` use `rtwdev->mcc.wait` and MRC wait conditions for firmware acknowledgements or TSF reports.
- `rtw89_fw_h2c_mrc_upd_bitmap()`, `rtw89_fw_h2c_mrc_sync()`, and `rtw89_fw_h2c_mrc_upd_duration()` send asynchronous updates for MRC MACID membership, TSF sync offset, and slot duration.

### AP, MLO, and TX Power/RFE

- `rtw89_fw_h2c_ap_info()` sends a low-level AP power-interrupt enable command.
- `rtw89_fw_h2c_ap_info_refcount()` wraps AP info enable/disable in `rtwdev->refcount_ap_info`. Enable only sends the command on a zero-to-one transition; disable only sends on the final decrement. During SER failures it warns and returns success to avoid refcount underflow on later disable.
- `rtw89_fw_h2c_mlo_link_cfg()` enables/disables firmware MLO link configuration for a link MAC ID and waits on `rtwdev->mlo.wait`.
- `__fw_txpwr_entry_zero_ext()` and `__fw_txpwr_entry_acceptable()` allow firmware tx-power entry records to be shorter than the configured entry size only if the unseen extension bytes are zero. This preserves forward/backward table compatibility while rejecting nonzero unknown extensions.
- `fw_txpwr_*_entry_valid()` validators reject table records outside array bounds for by-rate, 2/5/6 GHz power limit, RU limit, and transmit-shape tables.
- `rtw89_fw_load_txpwr_byrate()` decodes packed per-rate power bytes and writes them through `rtw89_phy_raw_byr_seek()` into `rtwdev->byr[band][bw]`.
- `rtw89_fw_load_txpwr_lmt_*()`, `rtw89_fw_load_txpwr_lmt_ru_*()`, `rtw89_fw_load_tx_shape_lmt()`, and `rtw89_fw_load_tx_shape_lmt_ru()` populate multidimensional RFE data arrays after validation.
- `rtw89_fw_has_da_txpwr_table()` checks whether dual-antenna limit and RU-limit tables exist for every band supported by the chip.
- `rtw89_load_rfe_data_from_fw()` overlays firmware-provided RFE data on top of optional initial RFE parameters, installs table loaders/pointers for valid sections, calculates `parms->has_da`, and returns the selected parameter block.

## Control Flow

Hardware scan start follows a strict setup sequence: clone the current operating channel, discover extra operating-channel metadata, update scan ownership and address state, run firmware/mac prehandling, stop queues, disable RX sync, notify core scan start, relax RX filtering, pause channel contexts, suspend DIG, and then adjust MCC beacon/NoA state. Completion reverses those effects through a channel-context callback so the channel/coexistence ordering is preserved before MCC entity progression.

Most H2C command functions follow the same pattern: allocate an skb with H2C header space, reserve the payload with `skb_put()`, encode fields using `RTW89_SET_FWCMD_*` macros or `le32_encode_bits()`, set the firmware command header with category/class/function identifiers, send via `rtw89_h2c_tx()`, and free the skb on send failure. Commands that must synchronize with firmware use `rtw89_h2c_tx_and_wait()`, whose condition is selected by subsystem-specific wait macros such as `RTW89_MCC_WAIT_COND()`, `RTW89_MRC_WAIT_COND()`, and `RTW89_MLO_WAIT_COND()`.

The RFE loading flow is data driven. `rtw89_load_rfe_data_from_fw()` checks each `rtw89_txpwr_conf` with `rtw89_txpwr_conf_valid()`. Valid by-rate data is attached as a lazy table loader; valid limit/shape sections are immediately expanded into typed arrays and pointer fields in `struct rtw89_rfe_parms`. Invalid entries inside a valid table are skipped per-entry rather than failing the entire load.

## State and Persistence Behavior

The persistent runtime state in this chunk lives in driver memory and firmware state, not on disk:

- `rtwdev->scan_info` stores the cloned operating channel, extra-op channel metadata, connected/connecting flag, scanning link, abort flag, delay, and related scan request pointers.
- `rtwvif->scan_ies` and `rtwvif->scan_req` are set at scan start and are expected to be cleaned by earlier/later scan cleanup helpers outside this chunk.
- RX filter state is temporarily derived from `rtwdev->hal.rx_fltr` and restored from that canonical value at scan completion.
- WoW commands consume `rtwdev->wow`, including flags, packet templates, pattern count, GTK/security algorithms, NLO configuration, and wait state.
- MCC/MRC/MLO commands use wait objects in `rtwdev->mcc.wait`, `rtwdev->mlo.wait`, `rtwdev->wow.wait`, and `rtwdev->mac.ps_wait`; some report payloads are read back from `wait->data.buf`.
- `rtwdev->refcount_ap_info` persists AP info enable state across nested users.
- Firmware tx-power data is persisted into `rtwdev->rfe_data` and returned as `struct rtw89_rfe_parms` pointers used by PHY/regulatory code after firmware parsing.

## Dependencies and Integration Points

This chunk integrates with:

- Linux mac80211/cfg80211 scan APIs: `struct ieee80211_scan_request`, `struct cfg80211_scan_request`, `ieee80211_stop_queues()`, `ieee80211_wake_queues()`, and `ieee80211_scan_completed()`.
- rtw89 channel-context management: `rtw89_chanctx_pause()`, `rtw89_chanctx_proceed()`, `rtw89_chan_get()`, entity modes, and MCC/MRC scheduling state.
- rtw89 core/mac/phy helpers: scan core notifications, RX filter programming, port RX sync, AP beacon enable, DIG suspend/resume, and raw by-rate table access.
- Firmware feature negotiation through `RTW89_CHK_FW_FEATURE()` and chip-generation checks such as `RTW89_CHIP_BE`.
- H2C transport and firmware command ABI: `rtw89_fw_h2c_alloc_skb_with_hdr()`, `rtw89_h2c_pkt_set_hdr()`, `rtw89_h2c_tx()`, and a large set of command-specific field macros and packed structs.
- Wait/C2H infrastructure: `rtw89_wait_for_cond_prep()`, `rtw89_wait_for_cond_eval()`, subsystem wait structures, and SER flags.
- WoWLAN packet-template helpers such as `rtw89_fw_h2c_add_general_pkt()`.
- RFE/PHY regulatory types and constants for bands, bandwidths, rate sections, RU indexes, NSS/NTX counts, regulatory domains, 6 GHz power modes, and channel-index dimensions.

## Risks and Edge Cases

- Scan cleanup correctness depends on every early-return path restoring state. `rtw89_hw_scan_start()` cleans up if prehandling fails, but failures after queue stop/RX sync changes would need matching unwind if new error paths are added.
- `rtw89_hw_scan_set_extra_op_info()` records only the first other active vif/link. In multi-link or multiple concurrent roles, firmware behavior depends on that single extra-op representation being sufficient.
- BE scan offload fills `num_opch` based on `connected` and `extra_op.set`; incorrect connected-state detection from nonzero BSSID could alter target-channel mode.
- H2C functions assume caller-provided pointers, lengths, and counts are already bounded by higher layers. Examples include PNO match-set count, MRC slot/role counts, MCC bitmap pointer, and firmware table dimensions.
- Several send failures are normalized to `-EBUSY`, while allocation failures return `-ENOMEM` and feature absence may return `-EOPNOTSUPP`; callers need to handle these distinctions.
- `rtw89_h2c_tx_and_wait()` returns a positive value when waiting is considered unreachable during SER, so callers that only check `< 0` versus `!= 0` may behave differently. Most local callers treat any nonzero as failure when they need the report payload.
- WoW offload setup can allocate packet templates before the final H2C send. Failure handling frees the command skb but packet-template lifecycle is controlled elsewhere, so repeated enable failures could be sensitive to the surrounding offload manager.
- `rtw89_fw_h2c_ap_info_refcount()` intentionally returns success during SER even if the firmware command failed. That avoids refcount corruption but means firmware and driver AP info state can temporarily diverge until recovery.
- RFE table validators silently skip invalid entries rather than failing the whole firmware RFE load. This makes the driver robust to bad records but can hide partial regulatory/power table loss unless debug instrumentation checks the resulting tables.
- The tx-power compatibility check only accepts nonzero extension bytes as invalid. If a future firmware format changes semantics without nonzero extension markers, older drivers may still accept records incorrectly.

## Test Signals

Useful validation signals for this chunk include:

- Hardware scan smoke tests with disconnected, connected, MCC, MLO, random-MAC, and abort flows; confirm queues wake, RX filters restore, DIG resumes, and `ieee80211_scan_completed()` is emitted exactly once.
- Firmware trace/debug logs for `RTW89_DBG_HW_SCAN` and `RTW89_DBG_FW`, including extra operating channel selection, packet-drop selector warnings, and H2C send failures.
- WoWLAN suspend/resume tests covering magic packet, pattern match, disconnect wake, ARP/keep-alive, GTK rekey, PNO/NLO, AOAC report wait, and MLD magic wake enable.
- MCC/MRC integration tests that add/start/stop/delete schedules, request TSF reports, update bitmaps/durations, and verify C2H wait conditions and report payload copying.
- SER/recovery tests while H2C wait commands are in flight, especially AP info refcount behavior and positive return handling from `rtw89_h2c_tx_and_wait()`.
- Firmware RFE fixture tests with valid and intentionally out-of-range tx-power records, shortened records with zero extension bytes, shortened records with nonzero extension bytes, and band combinations that should or should not set `has_da`.
- Static analysis for unchecked dynamic counts in variable-length H2Cs and for consistency between H2C payload sizes and firmware struct definitions.

## Cross-Chunk Notes

Earlier chunks define helpers used here, including scan prehandle/cleanup, scan channel-list construction, H2C allocation/header helpers, wait infrastructure, firmware feature tables, command field macros, and tx-power configuration iteration macros. Later merge work should connect this chunk with the earlier firmware download/parsing code to describe how `rtwdev->rfe_data` is allocated/populated before `rtw89_load_rfe_data_from_fw()` consumes it.
