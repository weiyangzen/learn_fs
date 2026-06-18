# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.h

## Purpose

`fw.h` is the firmware protocol contract for `rtw88`. It defines H2C and C2H command IDs, packet sizes, firmware header layouts, firmware feature bits, reserved-page packet types, WoWLAN/NLO/scan data structures, firmware bitfield pack/unpack macros, feature-check helpers, and prototypes for all firmware interaction routines implemented in `fw.c`.

## Important APIs, Types, and Functions

Key C2H protocol types are `enum rtw_c2h_cmd_id`, `enum rtw_c2h_cmd_id_ext`, `struct rtw_c2h_cmd`, `struct rtw_c2h_adaptivity`, and `struct rtw_c2h_ra_rpt`. Key H2C command types include `struct rtw_h2c_register`, `struct rtw_h2c_cmd`, H2C packet subcommand constants, and command ID constants for media status, power mode, RA, RSSI, beacon filtering, scan, adaptivity, coexistence, WoWLAN, AOAC, NLO, and BT recovery.

Firmware image metadata is represented by `struct rtw_fw_hdr` for newer firmware and `struct rtw_fw_hdr_legacy` for legacy 8051 firmware. `enum rtw_fw_feature` and `enum rtw_fw_feature_ext` gate optional firmware behavior such as LPS C2H, low clock, page features, beacon filter, scan notification, adaptivity, scan offload, and old probe-page numbering.

Reserved/offload data structures include `struct rtw_rsvd_page`, `struct rtw_lps_pg_dpk_hdr`, `struct rtw_lps_pg_info_hdr`, `struct rtw_nlo_info_hdr`, `struct rtw_ch_switch_option`, and enums for reserved packet type, keepalive type, scan channel type, scan report code, and scan notify IDs.

## Control Flow

The header itself has no runtime flow, but it shapes all firmware flow. `rtw_h2c_pkt_set_header()` fills the common packet-H2C category, command ID, and subcommand fields. Inline feature checks test bitmasks stored in `struct rtw_fw_state`. `get_c2h_from_skb()` interprets the packet offset stored in `skb->cb`, which is set by the IRQ-safe C2H receive path.

The many `SET_*` macros encode fields into command buffers through `le32p_replace_bits()` or `u8p_replace_bits()`. The `GET_*` macros decode C2H payloads and firmware dump TLVs.

## State and Persistence

The types defined here describe state persisted elsewhere: firmware feature masks in `rtwdev->fw`, reserved page list entries in vifs and device build lists, firmware sequence counters in `rtwdev->h2c`, WoW and PNO settings in `rtwdev->wow`, and scan offload state in `rtwdev->scan_info`. Packed headers are written into firmware-owned memory or parsed from firmware-owned messages.

## Dependencies and Integration Points

`fw.h` is included by MAC setup, debugfs, power-save, WoWLAN, coexistence, scan, TX report, and mac80211 integration code. It depends on Linux endian and bitfield helpers and on driver types declared in `main.h` and related headers. Because the macros operate on raw byte buffers, callers must zero-initialize H2C packets, set total lengths consistently, and hold required locks before sending.

## Risks

The primary risk is ABI drift. A field location mismatch between these macros and firmware will break behavior while still compiling. Several macros cast arbitrary `u8 *` buffers to `__le32 *`, so callers must provide properly sized, suitably aligned buffers and account for little-endian layout. Structure packing must match firmware exactly; removing `__packed` or changing field sizes would corrupt messages. Feature checks must be respected before using optional firmware commands.

## Test Signals

Build tests should catch prototype drift between `fw.h` and `fw.c`. Runtime tests should verify firmware version parsing, feature-bit gating, H2C byte streams for representative commands, C2H payload decoding, reserved-page location reporting, scan offload command layout, and WoW/NLO command layout against known-good firmware traces.
