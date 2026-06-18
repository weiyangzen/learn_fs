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
