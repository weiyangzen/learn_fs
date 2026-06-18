# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.c lines 8849-11906

## Scope

This chunk is the end of the Realtek `rtw89` Bluetooth coexistence implementation. It starts at the tail of `_show_cx_info()`, then covers the full diagnostic dump stack used by `rtw89_btc_dump_info()`, the version-selection helper `rtw89_coex_recognize_ver()`, and two exported notification helpers.

The code in this range is mostly read/format/report logic, but several functions have side effects while rendering diagnostics: they enable or disable firmware reports, refresh PTA grant ownership, copy RFK timeout state into coexistence error bits, and increment dump counters. The final merged file report should connect this chunk to earlier command, notification, C2H parser, policy, and watchdog code that populates the state printed here.

## Purpose

The main runtime purpose is to turn `rtwdev->btc` state into the coex debug output exposed through `rtw89_btc_dump_info()`. The dump is organized into feature-version, coexistence, WLAN, Bluetooth, mechanism, firmware-report, hardware-register, GPIO-debug, and summary sections. It lets driver developers compare driver-selected BTC feature versions against firmware-reported subversions, inspect current WLAN/BT role state, check TDMA/slot policy, read firmware cycle statistics, and diagnose mailbox/report/scoreboard failures.

The secondary purpose is version binding. `rtw89_coex_recognize_ver()` chooses a row from `rtw89_btc_ver_defs[]` based on chip ID and loaded normal firmware version. The selected `struct rtw89_btc_ver` controls all versioned parsing and rendering in this chunk: role-info layout, TDMA layout, slot layout, cycle-statistics layout, step-report layout, monitor-register layout, GPIO-debug layout, report-control layout, and initialization/module-info layout.

The last two exported helpers provide small integration hooks for other driver subsystems: one preserves Bluetooth A2DP airtime by sleeping for a requested interval when appropriate, and one records whether a connection-triggered WLAN RF calibration is active.

## Important APIs, Types, and Data

The public symbols in this chunk are:

- `ssize_t rtw89_btc_dump_info(struct rtw89_dev *rtwdev, char *buf, size_t bufsz)`: appends a complete BTC diagnostic report into the caller-provided buffer and returns bytes written.
- `void rtw89_coex_recognize_ver(struct rtw89_dev *rtwdev)`: sets `rtwdev->btc.ver` by matching chip ID and firmware version against `rtw89_btc_ver_defs[]`.
- `void rtw89_btc_ntfy_preserve_bt_time(struct rtw89_dev *rtwdev, u32 ms)`: sleeps for `ms` milliseconds only when not in SER handling and an A2DP profile exists.
- `void rtw89_btc_ntfy_conn_rfk(struct rtw89_dev *rtwdev, bool state)`: updates `rtwdev->btc.cx.wl.rfk_info.con_rfk`.

Core state comes from `struct rtw89_btc` in `core.h`. The dump reads:

- `btc->ver`, the selected `struct rtw89_btc_ver` feature matrix.
- `btc->cx`, including `struct rtw89_btc_wl_info`, `struct rtw89_btc_bt_info`, third coexistence device info, and WLAN/BT counters.
- `btc->dm`, including mechanism flags, selected TDMA/slot policy, RF/TRX limits, diagnostic step ring, report-selection bitmap, error map, notify counters, and grant state.
- `btc->fwinfo`, including C2H/H2C counters, report enable map, firmware BTC feature subversions, report common validity metadata, and versioned report payload unions.
- `btc->mdinfo`, the module/RFE/antenna description used by both the coexistence info and BT status sections.

The dump is heavily gated by `btc->dm.coex_info_map`, whose bits include `BTC_COEX_INFO_CX`, `BTC_COEX_INFO_WL`, `BTC_COEX_INFO_BT`, `BTC_COEX_INFO_DM`, `BTC_COEX_INFO_MREG`, and `BTC_COEX_INFO_SUMMARY`. If a bit is clear, the corresponding `_show_*()` function returns no output.

The `struct rtw89_btc_ver` fields are the central compatibility contract. This chunk branches on `fcxbtcrpt`, `fcxtdma`, `fcxslots`, `fcxcysta`, `fcxstep`, `fcxnullsta`, `fcxmreg`, `fcxgpiodbg`, `fcxbtscan`, `fcxbtafh`, `fwlrole`, `fcxctrl`, and `fcxinit`. The code assumes the selected row matches the firmware reports placed into `btc->fwinfo`; mismatches are surfaced as debug text or by returning no output from an incompatible formatter.

String conversion helpers map enum values to readable names:

- `steps_to_str()` decodes notification reasons, coexistence actions, and policy IDs.
- `id_to_slot()` decodes cycle-slot IDs such as `W1`, `B1`, `B2W`, `E2G`, and `B1FDD`.
- `id_to_evt()` decodes firmware step events such as TDMA entry, slot timers, beacon early, A2DP empty, BT retry/relink, and extended EBT/E2G events.
- `id_to_mode()`, `id_to_ant()`, `id_to_polut()`, `id_to_regtype()`, and `id_to_gdbg()` decode coex mode, antenna path, BT-polluted WLAN TX source, monitored register type, and GPIO debug signal IDs.

## Control Flow

`rtw89_btc_dump_info()` is the top-level renderer. It increments `dm->cnt_notify[BTC_NCNT_SHOW_COEX_INFO]`, prints the page/run counters, prints firmware-versus-driver BTC feature subversions, and then appends sections in a fixed order:

1. `_show_cx_info()` prints overall coexistence/version/module data. The first lines of this chunk complete that function by printing WL/BT firmware versions, module CV/RFE/antenna/isolation values, third coexistence type, DBCC, and TX/RX NSS. If BT is enabled but the BT FW version is still unknown, it enables `RPT_EN_BT_VER_INFO`; otherwise it disables that report.
2. `_show_wl_info()` prints WLAN link mode and status flags, then `_show_wl_role_info()` prints each active port or MLO radio link.
3. `_show_bt_info()` prints BT enable/connect/profile/link/AFH/raw-info/traffic request/scan/Tx power data, and may enable or disable BT scan, Tx power, AFH, LE AFH, and device-info firmware reports.
4. `_show_dm_info()` prints the current coexistence mechanism state, including action, reason, antenna path, init mode, manual/auto state, RF/TRX parameters, WLAN TX limits, and BT request length.
5. `_show_fw_dm_msg()` prints firmware-sourced diagnostics: errors, TDMA policy, slots, cycle statistics, null-data status, and firmware step traces. It chooses the cycle and step formatter from `ver->fcxcysta` and `ver->fcxstep`.
6. `_show_mreg_v1()`, `_show_mreg_v2()`, or `_show_mreg_v7()` prints scoreboard, PTA/grant state, BT-pollution type where supported, and monitor-register values, selected by `ver->fcxmreg`.
7. `_show_gpio_dbg()` prints GPIO-debug enable maps and pin routing if a valid firmware report exists.
8. `_show_summary_v1()`, `_show_summary_v4()`, `_show_summary_v5()`, `_show_summary_v105()`, `_show_summary_v7()`, or `_show_summary_v8()` prints H2C/C2H/report/mailbox/RFK/AOAC/notify counters, selected by `ver->fcxbtcrpt`.

The buffer write pattern is uniform: each helper accepts the current output pointer and remaining length, uses `scnprintf()`, and returns the number of bytes appended. The top-level caller advances `p` and passes `end - p` onward. There is no explicit final truncation flag; standard `scnprintf()` behavior bounds the writes.

WLAN role control flow has one important layout branch. When `ver->fwlrole == 8`, `_show_wl_role_info()` iterates `btc->cx.wl.rlink_info[i][j]` across BTC role index and MAC index. Otherwise it iterates `btc->cx.wl.link_info[i]`, but still loops over both MAC indices. For each active link it prints role, PHY, MLME state, client count, mode, channel, bandwidth, MAC ID, TX timing/retry caps, RSSI, busy flag, traffic direction, TX/RX rates, traffic levels, and RX rate-drop count.

Bluetooth status rendering also performs report-control decisions. If scan info has not been updated, it enables `RPT_EN_BT_SCAN_INFO`; once scan info exists, it disables that report and prints either v1 inquiry/page/LE/init windows or v2 BG/init/LE windows. If WL firmware coex major version is at least 9 and any BT profile exists, it enables `RPT_EN_BT_TX_PWR_LVL`; otherwise it disables that report. AFH reports are enabled only when a BT profile or BLE connection exists. LE AFH is enabled only for `fcxbtafh == 2` and BLE connection. BT device info is requested for incomplete A2DP metadata: missing flush time, missing vendor ID, or latency flag.

Firmware cycle-statistics formatters are version-specific but structurally similar. They validate `pfwinfo->rpt_fbtc_cysta.cinfo.valid`, print cycle/slot/beacon/collision/skip/leak counters, print average and maximum WLAN/BT/leak timing, then reconstruct recent cycle history from ring buffers. Versions 2, 3, 4, and 5 reconstruct a ring of alternating BT/WLAN slot durations. Versions 3 and later also include A2DP TX/RX stats when A2DP exists. Version 7 adds WLAN RX error ratios, A2DP no-empty streak data, BT slot-flood threshold/count, and CRLF-prefixed formatting used by newer reports.

Firmware step rendering has two implementations. `_show_fbtc_step_v2()` handles older reports with `pos_old` and `pos_new`, reconstructing a ring that may wrap and printing raw slot/event numeric IDs plus time deltas. `_show_fbtc_step_v3()` first checks the report enable map for `RPT_EN_FW_STEP_INFO`, validates the common info and firmware version, then prints up to `FCXDEF_STEP` recent entries with decoded slot/event names and deltas.

Monitor-register rendering has three variants. v1 and v2 read current grants from chip registers through `_get_gnt()` and use the firmware monitor-register report for values. v2 also prints `wl->bt_polut_type[wl->pta_req_mac]`. v7 does not read grant registers directly in the formatter; it prints cached `dm->gnt` grant state, uses `chip->para_ver & BTC_FEAT_PTA_ONOFF_CTRL` to label PTA ownership as hardware controlled, and prints register types with symbolic names.

`rtw89_coex_recognize_ver()` uses a simple first-match search. The `rtw89_btc_ver_defs[]` table is documented as descending firmware version per chip; for the current chip, the first entry with `suit_ver_code >= fw_ver_code` is selected. If no row matches, it falls back to `RTW89_DEFAULT_BTC_VER_IDX`. The chosen table index and version code are logged with `rtw89_debug()`.

## State and Persistence

Most functions in this chunk are diagnostic readers, but they are not completely pure.

Persistent or externally visible state changes include:

- `rtw89_btc_dump_info()` increments `BTC_NCNT_SHOW_COEX_INFO` every time a dump is requested.
- `_show_bt_info()` and the tail of `_show_cx_info()` call `rtw89_btc_fw_en_rpt()`, which can send `BTFC_SET/SET_REPORT_EN` H2C commands and update `btc->fwinfo.rpt_en_map` if firmware accepts the command.
- `_show_mreg_v1()` and `_show_mreg_v2()` refresh `btc->dm.pta_owner` from `rtw89_mac_get_ctrl_path()`.
- `_show_summary_v1()` and `_show_summary_v4()` copy BT RFK timeout report state into `bt->rfk_info.map.timeout` and then into `dm->error.map.wl_rfk_timeout`. The field name suggests WLAN RFK timeout, but it is assigned from the BT RFK timeout counter in these legacy report paths.
- `rtw89_coex_recognize_ver()` persists the selected version definition pointer in `btc->ver`; all later coexistence commands, reports, and dumps rely on this selection.
- `rtw89_btc_ntfy_conn_rfk()` persists the connection RFK flag in `btc->cx.wl.rfk_info.con_rfk`.
- `rtw89_btc_ntfy_preserve_bt_time()` does not mutate driver state, but it delays the current caller via `fsleep(ms * 1000)` when an A2DP descriptor exists and SER recovery is not active.

The firmware report payloads printed here are stored in `btc->fwinfo` by earlier C2H handling. Common report metadata (`struct rtw89_btc_rpt_cmn_info`) controls whether each formatter trusts a report. Several functions return no output when `valid` is false, when the requested firmware version does not match the report version, or when the matching report-enable bit is not set.

The dump output reflects volatile runtime state: link roles, traffic statistics, BT profile descriptors, AFH maps, scoreboard values, mailbox counters, TDMA slots, firmware cycle stats, and notify counters can change between calls. The version definitions and string maps are compile-time constants.

## Dependencies and Integration Points

This chunk depends on core `rtw89` device state and Linux kernel helpers:

- `struct rtw89_dev`, `struct rtw89_btc`, `struct rtw89_btc_cx`, `struct rtw89_btc_dm`, report unions, counters, profile descriptors, role structs, and version structs from `core.h`.
- H2C class/function constants, coexistence H2C layout decisions, and BTC driver-info/report semantics from `fw.h`.
- Public coexistence prototypes, BTC modes, packet/RFK/radio enums, report periods, antenna/path helpers, slot setters, and `BTC_COEX_INFO_*` semantics from `coex.h` and earlier `coex.c`.
- Register constants and accessors such as `rtw89_read32()`, `rtw89_mac_read_lte()`, `rtw89_mac_get_ctrl_path()`, `R_AX_LTE_SW_CFG_1`, `R_AX_GNT_VAL`, `R_AX_GNT_SW_CTRL`, and `R_AX_GNT_VAL_V1`.
- Endian helpers such as `le16_to_cpu()`, `le32_to_cpu()`, and `cpu_to_le32()` because firmware report payloads are little-endian on the host.
- Kernel formatting, bit, and delay helpers including `scnprintf()`, `FIELD_GET()`, `GENMASK()`, `BIT()`, `test_bit()`, and `fsleep()`.

The primary external consumer is the driver debug path that calls `rtw89_btc_dump_info()`, likely through debugfs or driver diagnostic plumbing. The output is intended for humans and support tooling rather than for stable machine parsing; labels and ordering are useful but not an ABI.

The report-control side effects integrate directly with firmware. `rtw89_btc_fw_en_rpt()` sends H2C commands through `_send_fw_cmd()` and suppresses report enabling when WLAN is RF-off or in low power state. That means diagnostic reads can request more firmware telemetry, but the request can be skipped or fail depending on power state and firmware command handling.

The version recognizer integrates with firmware loading. It calls `rtw89_fw_suit_get(rtwdev, RTW89_FW_NORMAL)` and `RTW89_FW_SUIT_VER_CODE()` after the normal firmware suit is known. The selected `btc->ver` must be available before commands or report parsers choose struct layouts.

The exported `rtw89_btc_ntfy_preserve_bt_time()` and `rtw89_btc_ntfy_conn_rfk()` are declared in `coex.h` for use outside this compilation unit. They are small but can affect timing and RFK coexistence decisions in connection or calibration paths.

## Risks

- The chunk is dominated by versioned wire-format interpretation. If `rtw89_btc_ver_defs[]` selects the wrong row for a firmware image, the dump can read the wrong union member, silently omit data, or report misleading counters.
- Adding a new firmware report format requires updates in multiple places: the version-definition table, the corresponding `_show_*()` dispatcher in `rtw89_btc_dump_info()` or `_show_fw_dm_msg()`, the string maps, and the report parser that fills `btc->fwinfo`.
- Diagnostic reads are side-effecting. Calling `rtw89_btc_dump_info()` can change report enable state, send H2C commands, increment counters, and update RFK timeout/error state. Tests and support scripts should not treat it as a purely passive snapshot.
- The buffer accounting relies on repeated `scnprintf(p, end - p, ...)`. If `p` ever advances past `end`, `end - p` underflows as `size_t`. In normal kernel `scnprintf()` use this is mitigated by bounded writes and expected buffer sizing, but unusually small buffers would make truncation hard to detect because no explicit truncation marker is returned.
- `_show_wl_role_info()` loops over `RTW89_MAC_NUM` even when `fwlrole != 8` and indexes the same `link_info[i]` for every MAC index. That can duplicate non-v8 role lines if `RTW89_MAC_NUM` is greater than 1. This may be intentional for shared loop shape, but it is a maintainability trap.
- `_show_wl_role_info()` prints `plink->client_cnt - 1` as an unsigned value. If `client_cnt` is zero on an active link, the displayed client count underflows.
- `_show_bt_info()` prints only `afh[0]` through `afh[9]` even though `BTC_BT_AFH_GROUP` is 12 in `core.h`. That may be a deliberate compact display, but it omits two bytes of BR/EDR AFH state.
- `_show_summary_v1()` and `_show_summary_v4()` assign `dm->error.map.wl_rfk_timeout` from BT RFK timeout state. The resulting error bit name can mislead diagnostics unless earlier code relies on this legacy behavior.
- Some version-specific functions return no output on invalid reports without printing why. For example `_show_fbtc_step_v3()` returns immediately if the report-enable bit is not present. That makes absence of output ambiguous between disabled report, invalid report, incompatible version, and no events.
- `_show_mreg_v1()` and `_show_mreg_v2()` iterate `pmreg->reg_num` and use `chip->mon_reg[i]`. Correctness depends on firmware report validation and monitor-register table sizing done earlier; this formatter does not independently clamp `reg_num` against the chip table length.
- `_get_gnt()` supports only a subset of chip IDs directly. v1/v2 monitor-register output on unsupported future chips would leave grant fields zeroed while still printing them unless the version selection avoids those paths.
- `rtw89_btc_ntfy_preserve_bt_time()` multiplies `ms * 1000` in `u32` arithmetic before passing it to `fsleep()`. Very large `ms` values would overflow the microsecond conversion; callers are expected to pass bounded coexistence delays.

## Test and Validation Signals

Static validation signals:

- Build with `W=1` or equivalent and ensure every `rtw89_btc_ver_defs[]` format value has a matching formatter or parser path. New values for `fcxbtcrpt`, `fcxcysta`, `fcxstep`, `fcxmreg`, `fcxgpiodbg`, `fwlrole`, `fcxbtscan`, or `fcxbtafh` should not silently fall through.
- Check that `rtw89_btc_dump_info()` remains declared in `coex.h` and that the two exported helpers have matching `EXPORT_SYMBOL()` entries.
- Check monitor-register report parsers clamp firmware `reg_num` to the chip monitor-register array before `_show_mreg_*()` reads it.
- Check every `CASE_BTC_*` string map contains entries for newly added reason/action/policy/slot/event/GPIO/register enums.
- Verify format specifiers match field widths and signedness, especially little-endian counters, signed dBm values, and unsigned client/profile counts.

Runtime validation signals:

- Exercise the debug dump with all `coex_info_map` bits enabled and verify the output includes feature subversion, CX, WL, BT, mechanism, firmware, hardware, GPIO, and summary sections for supported chips.
- Run the dump while WLAN is active, RF-off, and in LPS. Report-control H2C requests should be suppressed in RF-off/LPS states and summary paths should print invalid-report fallback text rather than stale firmware counters.
- Use firmware versions that select legacy (`fcxbtcrpt` 1/4/5/105) and newer (`fcxbtcrpt` 7/8) rows and verify the corresponding summary formatter is used.
- Test chips with `fcxcysta` 2, 3, 4, 5, and 7 to ensure cycle statistics decode without malformed slot history or endian mistakes.
- Test both non-MLO role reports (`fwlrole` 0/1/2/7) and MLO radio-link reports (`fwlrole` 8) to validate active role iteration and link-mode display.
- Establish BT HFP, HID, A2DP source/sink, PAN, BLE, and multi-link scenarios and verify `_show_bt_profile_info()` and `_show_bt_info()` reflect profile descriptors, AFH maps, scan windows, Tx power report state, and A2DP device-info requests.
- Trigger A2DP with missing device metadata and verify a dump enables `RPT_EN_BT_DEVICE_INFO`, then verify the report is disabled once flush time, vendor ID, and latency state are populated.
- Trigger BT/WLAN RFK paths and verify RFK request/go/reject/timeout counters and `rtw89_btc_ntfy_conn_rfk()` state are reflected consistently.
- On RTL8852A/B/BT, RTL8851B, RTL8852C, and RTL8922A hardware, compare grant/scoreboard output with known register states and PTA ownership.
- Confirm repeated dump calls increment only `BTC_NCNT_SHOW_COEX_INFO` and do not unexpectedly change coexistence policy, TDMA slots, or link state outside intentional report-enabling side effects.
