# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/fw.h

## Purpose

`fw.h` is the Realtek rtw89 driver's firmware ABI header. It defines the host-to-controller (H2C) commands, controller-to-host (C2H) reports, firmware image metadata, RF calibration/offload payloads, scan/offload formats, WoWLAN formats, coexistence messages, MCC/MRC scheduling commands, and chip-operation wrappers used by the rest of the rtw89 driver.

The file is not a standalone implementation unit. Its primary job is to freeze byte layouts and bit positions shared with firmware, then expose helper setters and function prototypes implemented mostly in `fw.c`. Because these structures are transmitted to device firmware or parsed from firmware buffers, `__packed`, little-endian fields, `GENMASK()` masks, and fixed enum values are part of the external contract.

## Important APIs, Types, and Constants

Firmware loading and image parsing:
- `enum rtw89_fw_dl_status` defines firmware download status values polled by `rtw89_fw_check_rdy()`, including checksum, security, CV mismatch, download-ready, and init-ready states.
- `struct rtw89_fw_hdr`, `struct rtw89_fw_hdr_v1`, `struct rtw89_fw_hdr_section`, `struct rtw89_fw_hdr_section_v1`, `struct rtw89_fw_bin_info`, and `struct rtw89_fw_hdr_section_info` describe firmware binary headers, section counts, dynamic headers, download addresses, checksum/security flags, and per-section payload locations.
- `struct rtw89_mfw_hdr` and `struct rtw89_mfw_info` model multi-firmware containers selected by chip variant, customer version, firmware type, and MP flag.
- `struct rtw89_fw_element_hdr` describes separately packaged firmware elements such as BB/RF register tables, tx-power tables, RFK log formats, regulatory data, AFE power sequences, diagnostic MAC rules, and TX compensation.
- `rtw89_compat_fw_hdr_ver_code()` and `rtw89_fw_get_filename()` are inline helpers for selecting normal vs multi-firmware header versioning and building firmware filenames.

H2C/C2H command transport:
- `H2C_HEADER_LEN`, `struct fwcmd_hdr`, and masks `H2C_HDR_CAT`, `H2C_HDR_CLASS`, `H2C_HDR_FUNC`, `H2C_HDR_H2C_SEQ`, `H2C_HDR_TOTAL_LEN`, `H2C_HDR_REC_ACK`, and `H2C_HDR_DONE_ACK` define the common firmware command header stamped by `rtw89_h2c_pkt_set_hdr()`.
- `struct rtw89_c2h_hdr` and `struct rtw89_fw_c2h_attr` describe the common C2H skb header and per-packet callback metadata stored through `RTW89_SKB_C2H_CB()`.
- `enum rtw89_fw_c2h_category`, `H2C_CAT_MAC`, `H2C_CAT_OUTSRC`, and H2C class/function constants partition commands into firmware info, WoW, PS, FW download, frame exchange, address/security/BA CAM, FW offload, MCC, MLO, MRC, AP, RA, DM, RF notify, and RFK domains.
- Wait-condition macros such as `RTW89_FW_OFLD_WAIT_COND()`, `RTW89_MCC_WAIT_COND()`, `RTW89_MRC_WAIT_COND()`, `RTW89_MLO_WAIT_COND()`, `RTW89_PS_WAIT_COND()`, and `RTW89_WOW_WAIT_COND()` turn firmware tag/function IDs into keys used by `rtw89_h2c_tx_and_wait()`.

Register-message path:
- `struct rtw89_mac_h2c_info`, `struct rtw89_mac_c2h_info`, `struct rtw89_h2creg_hdr`, `struct rtw89_c2hreg_hdr`, and `struct rtw89_c2hreg_phycap` define a small register-backed firmware messaging path with fixed four-word payloads.
- `enum rtw89_mac_h2c_type` and `enum rtw89_mac_c2h_type` enumerate register message functions such as scheduler TX enable, feature query, PHY capability, WoW CPU I/O RX ack, AOAC report requests, and PS leave ack.

H2C payload families:
- Security and CAM helpers include `RTW89_SET_FWCMD_SEC_*`, `struct rtw89_h2c_ba_cam`, `struct rtw89_h2c_ba_cam_v1`, `struct rtw89_h2c_ba_cam_init`, and DCTL/CMAC table setters.
- Rate adaptation uses `struct rtw89_h2c_ra`, `struct rtw89_h2c_ra_v1`, and masks for RA mode, bandwidth, MAC ID, RA mask, CSI, EHT mode, and partial-BW ER.
- Control table updates use many `SET_CMC_TBL_*` helpers plus `struct rtw89_h2c_cctlinfo_ud_g7` and `struct rtw89_h2c_cctlinfo_ud_be`; the second half of these structs stores masks, so fields can be updated selectively.
- Beacon, join, role, power-save, packet drop, EDCA, general packet, and tx-duty commands are modeled by small packed structs and bitfield setters such as `struct rtw89_h2c_bcn_upd`, `struct rtw89_h2c_bcn_upd_be`, `struct rtw89_h2c_join_v1`, `struct rtw89_h2c_role_maintain`, `struct rtw89_h2c_pwr_lvl`, `struct rtw89_h2c_lps_ch_info`, `struct rtw89_h2c_fwips`, and `struct rtw89_h2c_tx_duty`.
- Scan offload uses `struct rtw89_mac_chinfo_ax`, `struct rtw89_mac_chinfo_be`, `struct rtw89_h2c_chinfo`, `struct rtw89_h2c_chinfo_be`, `struct rtw89_h2c_scanofld`, `struct rtw89_h2c_scanofld_be`, `struct rtw89_h2c_scanofld_be_macc_role`, and `struct rtw89_h2c_scanofld_be_opch`. AX and BE chips use different element widths and different handling of period/duration fields.
- WoWLAN uses `struct rtw89_h2c_wow_global`, `struct rtw89_h2c_cfg_nlo`, `struct rtw89_h2c_wow_wakeup_ctrl`, `struct rtw89_h2c_wow_cam_update`, `struct rtw89_h2c_wow_payload_cam_update`, `struct rtw89_h2c_wow_gtk_ofld`, and `struct rtw89_h2c_arp_offload`.
- Bluetooth coexistence uses `struct rtw89_h2c_cxhdr`, `struct rtw89_h2c_cxhdr_v7`, `struct rtw89_h2c_cxinit`, versioned role structs (`rtw89_h2c_cxrole_v7`, `rtw89_h2c_cxrole_v8`), control and OSI structs, and many `RTW89_SET_FWCMD_CX*` setters.
- MCC and MRC use argument structs (`rtw89_fw_mcc_add_req`, `rtw89_fw_mcc_start_req`, `rtw89_fw_mrc_add_arg`, `rtw89_fw_mrc_start_arg`, etc.) plus packed H2C structs. MRC has nested flexible payloads for schedules, slots, and per-slot roles.
- RF/RFK offload uses `rtw89_fw_h2c_rf_reg_info`, RF notify structs, RFK pre-notify versions, TSSI/IQK/DPK/TXGAPK/DACK/RXDCK/TAS/TXIQK/CIM3K H2C structs, and matching RF log/report C2H structs.

C2H report families:
- Generic ack and formatted logs are represented by `struct rtw89_c2h_done_ack` and `struct rtw89_fw_c2h_log_fmt`.
- Runtime reports include beacon update done, beacon filter report, RA report, LPS report, FW scan report, scan offload report, TX reports, MCC/MRC TSF and status reports, MLO link configuration report, packet offload response, tx-duty report, WoW AOAC report, power interrupt notify, RFK state reports, RF run logs, and RF calibration report logs.
- Static assertions ensure report buffers such as `rtw89_mac_mcc_tsf_rpt` and `rtw89_mac_mrc_tsf_rpt` fit the common completion buffer.

Public function prototypes:
- Firmware lifecycle: `rtw89_fw_recognize()`, `rtw89_fw_recognize_elements()`, `rtw89_early_fw_feature_recognize()`, `rtw89_fw_download()`, `rtw89_load_firmware_work()`, `rtw89_unload_firmware()`, `rtw89_wait_firmware_completion()`.
- Command allocation and sending: `rtw89_fw_h2c_alloc_skb_with_hdr()`, `rtw89_fw_h2c_alloc_skb_no_hdr()`, `rtw89_fw_h2c_raw_with_hdr()`, `rtw89_fw_h2c_raw()`, `rtw89_h2c_pkt_set_hdr()`.
- Feature commands: CMAC/DMAC/BA CAM, beacon update, role/join, scan offload, RA, coexistence, RF/RFK, PS/LPS/IPS, WoW, MCC/MRC, AP info, MLO link cfg, and firmware logging/debugging.
- Chip-dispatch inlines (`rtw89_chip_h2c_default_cmac_tbl()`, `rtw89_chip_h2c_ba_cam()`, etc.) route common callers through `rtwdev->chip->ops`, allowing AX/G7/BE payload variants to be selected by chip definition.

## Control Flow

The main firmware-command flow is consistent across command families:

1. A caller in core, MAC, PHY, PS, scan, WoW, MCC/MRC, or coexistence code prepares driver state such as MAC ID, link, channel, role, wake pattern, RA mask, or calibration parameters.
2. The implementation in `fw.c` allocates an skb through `rtw89_fw_h2c_alloc_skb_with_hdr()` or `rtw89_fw_h2c_alloc_skb_no_hdr()`. With a header, space is reserved for both the firmware H2C header and the chip-specific H2C descriptor.
3. The command body is filled using packed structs and `le32_encode_bits()` or the inline `RTW89_SET_*` helpers from this header. For selective table updates, both value words and mask words are filled.
4. `rtw89_h2c_pkt_set_hdr()` stamps the common H2C header with type, category, class, function, ack requirements, and payload length.
5. Most commands call `rtw89_h2c_tx()`. Commands that need firmware confirmation call the wait wrapper with a condition key derived from the class/function, group, schedule index, packet ID, or MAC ID.
6. Firmware reports arrive as C2H skbs. The C2H parser decodes `struct rtw89_c2h_hdr`, attaches `rtw89_fw_c2h_attr` to `skb->cb`, and dispatches to handlers that parse typed C2H structs from this header. Some reports complete pending wait conditions or copy TSF/report data into wait buffers.

Firmware recognition has a separate flow:

1. Loader code obtains a firmware blob selected by basename and format.
2. Normal or multi-firmware headers are distinguished by `RTW89_MFW_SIG` via `rtw89_compat_fw_hdr_ver_code()`.
3. Header parsers use `FW_HDR*` and `FWSECTION_HDR*` masks to compute base/dynamic header length, section count, part size, checksum/security flags, section type, memory download address, and secure-section metadata.
4. Recognized element headers populate `rtwdev->fw.elm_info` and related chip/RFE data. Later PHY, RF, tx-power, regulatory, and diagnostic paths consume those element pointers.
5. `rtw89_fw_download()` sends sections to hardware and `rtw89_fw_check_rdy()` polls chip-specific status until `RTW89_FWDL_WCPU_FW_INIT_RDY` or an error status is observed.

Chip-version control flow is explicit. AX and BE payload formats coexist throughout the header. Examples include scan offload AX vs BE, BA CAM v0/v1, CMAC table G7/BE formats, RFK pre-notify versions, WoW CAM update v0/v1, and firmware feature checks such as `SCAN_OFFLOAD_BE_V0`, `CH_INFO_BE_V0`, or RFK command version bits. Chip ops in chip files bind the right function variants for each chip.

## State and Persistence Behavior

This header defines interfaces that update device firmware state rather than local persistent files. Important state effects include:

- Firmware readiness is represented in `rtwdev->flags` through `RTW89_FLAG_FW_RDY` after `rtw89_fw_check_rdy()` succeeds.
- Firmware binary recognition stores version, section, security, and element metadata in `rtwdev->fw`, including `rtwdev->fw.sec`, `rtwdev->fw.elm_info`, feature bits, and loaded firmware object references.
- Packet offload state persists in driver bitmaps and firmware slots. `rtw89_fw_h2c_add_pkt_offload()` acquires an ID from `rtwdev->pkt_offload`, sends the packet template to firmware, and releases the ID on failed confirmation or deletion.
- Scan offload state is maintained in `rtwdev->scan_info`, including prepared channel lists, packet template lists, operation channel data, and extra operation-channel state; firmware receives channel-list and scan-start/stop commands.
- Power-save and WoWLAN commands persist suspend-time behavior in firmware: keep-alive packet IDs, disconnect detection, ARP response, GTK/PTK/IGTK material, wakeup filters, pattern CAM entries, NLO SSID lists, and AOAC report retrieval.
- MCC/MRC and MLO commands create firmware-side schedules, TSF synchronization, MACID bitmaps, duration changes, link configuration, and status/TSF wait results.
- AP info uses a driver-side `refcount_ap_info` around firmware power-interrupt enablement, avoiding duplicate enable/disable H2Cs.
- RFK/RF offload state is coupled to `rtwdev->rfk_mcc`, `rtwdev->mlo_dbcc_mode`, channel state, efuse/RFE data, and firmware elements. Reports are returned through C2H log/report structures.

Because many payloads include key material, wake filters, regulatory/tx-power data, or calibration data, correctness depends on preserving exact layouts and endian conversions. There is no on-disk persistence here except loaded firmware blobs supplied by the kernel firmware subsystem.

## Dependencies

Direct header dependency:
- `core.h` supplies core rtw89 types such as `rtw89_dev`, chip info, vif/sta link types, scan option types, wait buffers, firmware info, channel/band enums, RF paths, constants such as `RTW89_PHY_NUM`, and Linux/mac80211 types exposed through core includes.

Kernel/framework dependencies used by declarations and inline helpers:
- Linux bitfield helpers: `BIT()`, `GENMASK()`, `FIELD_GET()`, `FIELD_PREP()`, `le32p_replace_bits()`, `le16p_replace_bits()`, `u8p_replace_bits()`, `le32_get_bits()`, `le32_encode_bits()`, `u8_encode_bits()`.
- Linux endian types: `__le16`, `__le32`, `__le64`, `cpu_to_le32()`.
- skb and wireless types: `struct sk_buff`, `struct wiphy`, `struct wiphy_work`, `struct work_struct`, `struct firmware`, `struct ieee80211_scan_request`, `struct ieee80211_ampdu_params`, `struct ieee80211_p2p_noa_desc`, `IEEE80211_MAX_SSID_LEN`, `ETH_ALEN`.
- List/flexible-array machinery: `struct list_head`, `__counted_by`, `DECLARE_FLEX_ARRAY`, `struct_size()`, `offsetofend()`, and `static_assert()`.

Implementation dependencies:
- `fw.c` includes `cam.h`, `chan.h`, `coex.h`, `debug.h`, `mac.h`, `phy.h`, `ps.h`, `reg.h`, `util.h`, and `wow.h`; the prototypes in this header are implemented against those modules.
- PHY code consumes RFK/TSSI/IQK/RF log structures and sends RF offload H2Cs during calibration.
- PS code calls LPS, RF PS info, LPS channel/common info, TSF toggle, P2P action, beacon filter, and TRX protect helpers.
- Chip files assign function pointers to the variant-specific wrappers declared here.

## Integration Points

`fw.c` is the main implementation of this ABI. It uses these structs and masks to construct commands for firmware download, command transport, C2H dispatch, scan offload, packet offload, WoW, coexistence, RFK, MCC/MRC, MLO, AP info, and tx-power/regulatory element loading.

Chip definitions integrate through `struct rtw89_chip_ops`. AX chips such as RTL8852C bind older payloads (`rtw89_fw_h2c_default_cmac_tbl`, `rtw89_fw_h2c_ba_cam`, `rtw89_fw_h2c_wow_cam_update`), while BE chips such as RTL8922D bind BE/v1/v3 variants (`rtw89_fw_h2c_default_cmac_tbl_be`, `rtw89_fw_h2c_ba_cam_v1`, `rtw89_fw_h2c_wow_cam_update_v1`, `rtw89_fw_h2c_default_dmac_tbl_v3`).

mac80211/cfg80211 integration happens through scan, association, BA session, beacon, WoWLAN, P2P NoA, scheduled scan/PNO, AMPDU, and channel contexts. Driver state is converted into firmware MAC IDs, ports, bands, BSS config fields, and packet templates.

The power-save path in `ps.c` calls firmware LPS, RF PS, LPS channel/common info, and TRX protect helpers when entering or leaving low power. WoW paths combine `wow.h` key/pattern data with the H2C formats defined here.

The PHY/RF path calls RA and RFK/RF offload helpers. RF reports and formatted RF logs are parsed from C2H payloads whose layouts are declared here, and firmware elements supply BB/RF/tx-power/regulatory tables consumed by PHY setup.

Coexistence code uses the CX H2C definitions to send WLAN role, traffic, RFK, control, init, and OSI state to firmware/Bluetooth coexistence logic.

MCC/MRC and MLO managers use schedule/link arguments from this header and wait for matching C2H status/TSF/link reports. The wait-condition macros are the handshake contract between senders and C2H completion handlers.

## Risks and Edge Cases

ABI drift is the highest risk. Many structs are wire formats with comments warning not to insert fields in the middle. Adding fields, changing enum values, or changing masks can break firmware compatibility even if the C code still builds.

Endian and alignment mistakes are severe. Payloads are little-endian and packed. Direct assignment of host-endian values into `__le32` fields, missing `cpu_to_le32()`, or using the wrong mask can silently send malformed commands.

Flexible array and variable-length payloads need exact sizing. Scan lists, MRC schedules, firmware elements, C2H logs, and dynamic firmware headers depend on `struct_size()`, `elem_size`, and version-specific lengths. Incorrect lengths can truncate H2Cs, overrun skbs, or desynchronize firmware parsing.

Version gating is fragile. The header supports multiple generations and firmware feature versions. If a command uses a BE field against an older firmware feature set, or an AX path against a BE chip, firmware may reject the command or perform the wrong action.

Wait conditions must match C2H completions. The macros derive conditions from packet IDs, operation IDs, groups, schedule indexes, or MAC IDs. A mismatch causes hangs/timeouts in `rtw89_h2c_tx_and_wait()` even if firmware completed the command.

Security-sensitive data is present in firmware payloads and C2H reports: GTK/PTK/IGTK material, replay counters, wake pattern CAM, secure firmware sections, and MSS key selection. Debug dumps and logs must avoid leaking secrets.

Scan and WoW offload depend on firmware-side resources. Packet offload IDs, scan channel limits, NLO SSID count, pattern count, and channel-list limits can fail with `-ENOSPC`, `-ENOMEM`, or firmware ack failures. Cleanup paths must release bitmaps and packet templates on failure.

C2H parsing must validate lengths. Several report structs have flexible data or versioned field placement. Handlers should check `len` before casting to larger formats to avoid reading beyond skb data.

Refcount and recovery handling can mask errors. AP info deliberately returns success during SER after warning. Callers should account for recovery mode and not treat every zero return as firmware state certainty.

## Test Signals

Build-level signals:
- Compile the rtw89 driver with sparse/endian checking to catch incorrect assignments to `__le32` fields and pointer casts in inline setters.
- Enable warnings around packed structs, flexible arrays, `struct_size()`, and `static_assert()` failures; these are early indicators of ABI layout regression.

Firmware-load signals:
- Boot/probe logs should show successful firmware recognition, firmware element recognition, download completion, and transition to `RTW89_FWDL_WCPU_FW_INIT_RDY`.
- Negative firmware tests should surface the specific status strings for checksum failure, security failure, CV mismatch, or unexpected status.

Runtime H2C/C2H signals:
- `RTW89_DBG_FW`, `RTW89_DBG_RA`, `RTW89_DBG_TXRX`, scan, RFK, and WoW debug categories should show command allocation/send success and matching C2H completions.
- Commands using `rtw89_h2c_tx_and_wait()` should complete without timeout for packet offload add/delete, scan start/stop, IPS, WoW AOAC request, MCC/MRC start/stop/TSF, MLO link cfg, and TRX protect.

Feature tests:
- Association should update CMAC/DMAC/join/role/RA/BA CAM paths for both legacy and MLO links.
- Hardware scan and PNO should exercise AX and BE scan channel-list payloads, start/stop C2Hs, and scan completion paths.
- Suspend/resume WoWLAN should test magic packet, disconnect, pattern match, NLO, GTK offload, ARP offload, keep-alive, AOAC report parsing, and packet template cleanup.
- RFK tests should exercise TSSI, IQK, DPK, TXGAPK, DACK, RXDCK, TAS, TXIQK, CIM3K, and verify expected C2H RF logs/reports without length errors.
- MCC/MRC tests should verify schedule add/start/delete, TSF report copying, duration updates, bitmap updates, and status reports under multi-channel operation.

Regression indicators:
- Firmware H2C timeout messages, "failed to send h2c", malformed firmware log output, scan abort hangs, packet offload ID leaks, unexpected firmware status, wrong RA rate reports, or WoW wake reason/key replay mismatches point back to layouts and masks defined in this header.
