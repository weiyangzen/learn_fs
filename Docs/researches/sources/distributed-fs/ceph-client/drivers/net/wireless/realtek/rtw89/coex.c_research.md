# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004919`: lines 1-8848, `Docs/researches/chunks/subset-b-004919_research.md`
- `subset-b-004920`: lines 8849-11906, `Docs/researches/chunks/subset-b-004920_research.md`

## Chunk Research

### subset-b-004919: lines 1-8848

# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.c lines 1-8848

## Scope

This chunk covers the first 8,848 lines of `coex.c`, the Realtek rtw89 Bluetooth/Wi-Fi coexistence control engine. It includes the coexistence version table, firmware report parsing, H2C/C2H command handling, policy construction, antenna/grant/RF parameter programming, WLAN role aggregation, Bluetooth info parsing, public notification entry points, delayed-work handlers, and the start of the debug display code. The file continues after this chunk with the detailed debug-info renderers and version-recognition helpers, so this report focuses on runtime control and event handling rather than the final formatted diagnostics.

## Purpose

The code in this chunk keeps Wi-Fi and Bluetooth usable on Realtek combo chips that share RF resources, antenna paths, PTA grants, or adjacent 2.4 GHz spectrum. It observes Wi-Fi state from mac80211/rtw89, Bluetooth state from firmware C2H reports and scoreboard bits, then selects coexistence actions. Those actions program firmware TDMA policies, slot tables, grant signals, scoreboard flags, packet traffic limits, BT AFH channel hints, and RF TX/RX gain constraints.

The core job is to translate dynamic state into one of many coexistence modes:

- Wi-Fi-only, BT-off, BT-idle, WHQL test, freerun, WL RFK, scan/linking, no-link, 5 GHz, 2.4 GHz STA/AP/GO/GC/NAN, 2.4 GHz SCC/MCC, 2.4+5 GHz MCC, and profile-specific BT cases such as HFP, HID, A2DP, A2DP sink, PAN, and profile combinations.
- Shared-antenna versus dedicated-antenna policy choices.
- Older firmware ABI variants and newer v7/v8/MLO/RTL8922A coexistence ABI variants.

## Important APIs, Types, And Constants

The initial static data defines the policy vocabulary:

- `RTW89_COEX_VERSION` identifies the driver-side coexistence logic version.
- `t_def[]` holds default TDMA templates indexed by `enum btc_fbtc_tdma_template`, including off, fixed, auto, packet-save TDMA, and extended-control variants.
- `s_def[]` holds default slot definitions for WLAN, BT, extended 2G/5G/BT slots, leak slots, RFK slots, and FDD slots. Slots carry duration, coexistence table, and slot type.
- `cxtbl[]` maps numeric policy table IDs to 32-bit priority patterns used by slot programming.
- `rtw89_btc_ver_defs[]` maps chip ID and firmware version to firmware report/control ABI versions, buffer length, role-info format, C2H function map, OSI support, MLO support, and desired BT coex version.

Important local enums include:

- `enum btc_b2w_scoreboard` and `enum btc_w2b_scoreboard`, the BT-to-WL and WL-to-BT mailbox/scoreboard bit contracts.
- `enum btc_cx_poicy_type`, the complete policy type space. The high byte selects policy family such as TDMA off, fixed TDMA, auto TDMA, extended control, or user-defined; the low byte selects concrete slot ratios and priority tables.
- `enum btc_wl_link_mode`, the aggregated Wi-Fi mode model used by `_run_coex()`.
- `enum btc_reason_and_action`, which shares one enum for run reasons and selected actions. The decision manager records both in a ring buffer via `_update_dm_step()`.
- `enum btc_ant_phase`, grant/path phases such as `BTC_ANT_WINIT`, `BTC_ANT_W2G`, `BTC_ANT_W5G`, `BTC_ANT_FREERUN`, and RFK protection phases.

Important exported or externally used functions in this chunk are:

- `rtw89_btc_set_policy()` and `rtw89_btc_set_policy_v1()`, chip-ops policy builders called from `chip->ops->btc_set_policy()`.
- `rtw89_btc_ntfy_poweron()`, `rtw89_btc_ntfy_poweroff()`, `rtw89_btc_ntfy_init()`, `rtw89_btc_ntfy_scan_start()`, `rtw89_btc_ntfy_scan_finish()`, `rtw89_btc_ntfy_switch_band()`, `rtw89_btc_ntfy_specific_packet()`, `rtw89_btc_ntfy_role_info()`, `rtw89_btc_ntfy_radio_state()`, `rtw89_btc_ntfy_wl_rfk()`, and `rtw89_btc_ntfy_wl_sta()`.
- Delayed work callbacks `rtw89_coex_act1_work()`, `rtw89_coex_bt_devinfo_work()`, `rtw89_coex_rfk_chk_work()`, and packet notification work handlers for EAPOL, ARP, DHCP, and ICMP.
- `rtw89_btc_c2h_handle()`, the firmware-to-driver event dispatcher for coexistence events.

## Firmware ABI And Report Handling

`_send_fw_cmd()` is the common H2C send wrapper. It rejects zero or oversized payloads, rejects commands before coexistence init, and avoids H2C I/O when Wi-Fi is already in RF-off/LPS RF-off states. Successful sends increment `fwinfo.cnt_h2c`; failures increment `cnt_h2c_fail` and sometimes set `dm->error.map.h2c_buffer_over`.

Firmware report parsing is split across `btc_fw_event()`, `_parse_btc_report()`, and `_chk_btc_report()`. C2H event `BTF_EVNT_RPT` carries a sequence of small records with a 1-byte type and 2-byte length. `_parse_btc_report()` bounds each record against `buf_len` and `ver->info_buf`, then `_chk_btc_report()`:

- Remaps report type indexes for older firmware through `rtw89_btc_fw_rpt_evnt_ver()`.
- Selects the expected target union member and expected length according to ABI fields such as `fcxbtcrpt`, `fcxtdma`, `fcxslots`, `fcxcysta`, `fcxstep`, `fcxmreg`, `fcxbtver`, `fcxbtscan`, and `fcxbtafh`.
- Rejects undefined versions and length mismatches, setting `len_mismch` and per-report validity state.
- Copies valid payloads into `btc->fwinfo` and updates driver state derived from them.

Control reports update firmware report enable maps, WL firmware coex version, WL firmware version, grant state snapshots, BT priority counters, polluted counters, RFK timeout state, buffer mismatch errors, and hang detectors. TDMA and slot reports are compared against `dm->tdma_now` and `dm->slot_now` to detect driver/firmware non-sync. Cycle-stat reports detect leak AP conditions, TDMA cycle hangs, W1/B1/E2G hangs, WL/BT slot drift, and BT slot flood conditions. MREG reports feed monitored BB register readback into `dm->wl_btg_rx_rb` and `dm->wl_pre_agc_rb`. BT version, scan, AFH, and device reports are normalized into `bt->ver_info`, `bt->scan_info_*`, AFH maps, and A2DP device metadata by `_update_bt_report()`.

`rtw89_btc_fw_en_rpt()` maps logical report enable requests to firmware-version-specific bit positions with `rtw89_btc_fw_rpt_ver()`. It emits either the old v1 enable structure or the newer v8 TLV-like structure and only updates `fwinfo->rpt_en_map` after successful H2C.

## Policy Construction And Firmware Programming

`_fw_set_policy()` is the common policy commit path:

1. Records the selected action and policy in the DM step ring.
2. Clears `btc->policy_len` and stores `btc->policy_type`.
3. Calls `_append_tdma()` and `_append_slot()` to append only changed TLVs unless `update_policy_force` is set.
4. Enables coex LPS control before sending if TDMA RX flow control uses null/QoS-null packets.
5. Sends `BTFC_SET/SET_CX_POLICY` to firmware.
6. Copies the committed TDMA and slot state into `dm->tdma_now` and `dm->slot_now` on success.
7. Clears force-update state and releases coex LPS when no longer required.

`_append_tdma()` handles three ABI shapes: v1 raw `rtw89_btc_fbtc_tdma`, v3 wrapper, and v7 TLV. `_append_slot_v1()` writes one TLV per changed slot, while `_append_slot_v7()` packs multiple changed v7 slots into one TLV with slot IDs. `rtw89_btc_fw_set_slots()` sends the full initial slot table in either the v1 flexible-array structure or the v7 TLV shape.

`rtw89_btc_set_policy()` is the older policy builder. `rtw89_btc_set_policy_v1()` is the newer and richer builder used by newer chip ops. Both convert `BTC_CXP_*` policy IDs into `dm->tdma` and `dm->slot` edits, but v1 adds more profile-sensitive priority tables, little-endian slot helpers, `OFFE` extended-slot cases for SCC/MCC and 4-way protection, leak AP handling, null-role selection for SCC, and instant TDMA execution.

## Main Control Flow

The main decision engine is `_run_coex()`. It requires wiphy locking (`lockdep_assert_wiphy()`), records the run reason, updates the coarse WL/BT state map, derives the current Wi-Fi link mode from the active role-info ABI, and then follows a strict priority order:

1. Return early for manual control.
2. Ignore BT-triggered reruns when the control state says to ignore BT.
3. Return if Wi-Fi coexistence init failed.
4. Avoid repeated work when RF-off/LPS state has not changed or Wi-Fi is fully off.
5. Clear per-run state such as freerun, FDDT training, and BT scan RX low-priority.
6. Compute freerun eligibility with `_check_freerun()`.
7. Handle always-freerun, WL-only, WL-off/LPS/BT-only, init, BT-off, WHQL, WL RFK, and scanning/linking before ordinary link-mode selection.
8. Dispatch by `BTC_WLINK_*` mode to 2G/5G/SCC/MCC/AP/GO/GC/NAN/other action functions.
9. Store whether BT should be ignored for subsequent BT-triggered reruns.
10. Run `_action_common()` for common side effects.

Action functions are small state-to-policy adapters. For example, `_action_bt_a2dp()` uses auto/packet-save TDMA policies with W1/B1 slot durations tuned for A2DP and scan/linking state; `_action_bt_hid()` prefers priority-table modes that preserve HID latency; `_action_wl_25g_mcc()` uses extended slots for mixed 2.4/5 GHz operation; `_action_wl_rfk()` forces antenna/grant states that protect RF calibration.

`_action_common()` applies side effects that should follow almost every action: PTA request MAC selection, BTG RX control, pre-AGC control, WLAN TX-time limiting, BT AFH channel hints, BT high-LNA scoreboard, RF TX/RX parameter changes, BT scan-priority scoreboard, BT firmware-version report toggling, role/report refresh on init/radio events, scoreboard writes, and OSI info updates on chips/firmware that support offloaded source information.

## WLAN Role, MLO, DBCC, And Traffic State

The driver maintains multiple versions of role-info state because firmware ABI evolved:

- `_update_wl_info()`, `_update_wl_info_v1()`, and `_update_wl_info_v2()` aggregate `wl->link_info[]` into role-info structures for older ABIs.
- `_update_wl_info_v7()` adds richer channel definitions, role maps, client counts, BG/HE/high-5G flags, DBCC handling, and multi-role NOA classification.
- `_update_wl_info_v8()` updates one role/link tuple in `role_info_v8.rlink[role_id][rlink_id]`, recomputes role maps and flags, and either asks PHL/MR channel context APIs for MLO mode or computes non-MLO mode locally.

The link-mode classifiers preserve an order that matters: no-link, 5G-only, NAN, too many roles, DBCC, 2G+5G MCC, 2G SCC/MCC, then single-role 2G. `_chk_dbcc()` identifies which PHY carries 2.4 GHz, chooses the PTA request band, and distinguishes single 2G role, 2G SCC/MCC, and 2G+5G MCC inside DBCC/MLO combinations. `_update_wl_mlo_info()` queries `rtw89_query_mr_chanctx_info()` for both hardware bands, derives MLO RF combination, path RF bands, MLO enable/adie flags, DBCC-like PTA ownership, and the effective coexistence link mode.

`rtw89_btc_ntfy_role_info()` is the public role update entry point. It reads vif/link/STA state under RCU, fills `struct rtw89_btc_wl_link_info`, copies beacon/DTIM/channel/bandwidth/channel definition/MAC ID/capability mode fields, updates the correct role-info ABI, clears leak and 4-way/connecting state when appropriate, then reruns coexistence.

`rtw89_btc_ntfy_wl_sta()` walks stations atomically. The iterator updates per-link RSSI hysteresis, busy state, UL/DL direction, rate/drop counters, traffic levels, and `dm->trx_info`. It triggers `_run_coex()` when RSSI, busy, direction, or monitored BB readback state changes, and sends role driver info when traffic rates/levels change.

## Bluetooth State Handling

BT state enters through scoreboard reads and BT-info C2H events. `_update_bt_scbd()` reads the shared scoreboard, updates BT enable, mailbox availability, WHQL test, BTG type, A2DP activity, LNA constraint, RFK run/request, high-LNA state, BT connect state, and patch-code state. It resets BT info on re-enable and reruns coexistence on material changes unless the caller requested update-only mode.

`_update_bt_info()` parses the six-byte BT info payload into profile and activity descriptors:

- Low byte 2: connect, SCO busy, inquiry/page, ACL busy, HFP/HID/A2DP/PAN existence.
- Low byte 3: retry, CQDDR, inquiry, mesh busy, page.
- High byte 0: BT RSSI converted through chip ops and hysteresis.
- High byte 1: BLE connect, reinit, relink, ignore-WL, voice, BLE scan, role switch, multi-link.
- High byte 2: PAN active, AFH update, A2DP active, slave role, HID slot and pair count.
- High byte 3: A2DP bitpool, 3M rate, A2DP sink.

Profile existence builds `b->profile_cnt.now` and drives `_action_by_bt()`. A new A2DP existence queues delayed device-info work so the driver can later clear play-latency state after firmware reports device details.

`_update_bt_txpwr_info()` stores BT TX power descriptor data from newer BT query-TX-power C2H events.

## Antenna, Grants, Scoreboard, And RF Controls

The grant/antenna path separates old and new chips:

- `_set_gnt()` updates `dm->gnt.band[]` and immediately calls `rtw89_chip_mac_cfg_gnt()`.
- `_set_gnt_v1()` also tracks WLAN_ACT mux state, supports BT index selection, and writes desired grant/WLAN_ACT state into `dm->ost_info` for OSI-capable firmware instead of always applying locally.
- `_set_ant_v0()` handles legacy chips with explicit control-path owner changes and PLT programming.
- `_set_ant_v1()` handles RTL8922A-style grant and WLAN_ACT programming, with special force cases for DBCC changes and BTG RX source changes.

Scoreboard helpers `_read_scbd()` and `_write_scbd()` wrap `rtw89_mac_get_sb()` and deferred `rtw89_mac_cfg_sb()` writes. `_write_scbd()` only marks `wl->scbd_change`, and `_action_common()` performs the actual MAC scoreboard write, which batches scoreboard changes with policy side effects.

RF and baseband controls include:

- `_set_wl_tx_power()`, `_set_wl_rx_gain()`, `_set_bt_tx_power()`, and `_set_bt_rx_gain()` for coexistence-specific TX/RX gain adjustment.
- `_set_rf_trx_para()`, which selects RF parameter presets from chip tables based on antenna type, profile count, link mode, traffic direction, RSSI levels, BT RSSI, FDDT state, and DBCC placement.
- `_set_btg_ctrl()` to tell BB/HAL whether BTG RX should ignore or honor GNT_BT.
- `_set_wl_preagc_ctrl()` to control pre-AGC/no-BTG behavior for dedicated antenna cases and specific link modes.
- `_set_wl_tx_limit()` to constrain per-station TX time and retry limit when latency-sensitive BT profiles are active.
- `_set_bt_afh_info_v0()` and `_set_bt_afh_info_v1()` to tell BT firmware which 2.4 GHz Wi-Fi channel span should be avoided or considered in AFH decisions.

## Notification Entry Points

Initialization and power notifications:

- `rtw89_btc_ntfy_poweron()` increments notification counters.
- `rtw89_btc_ntfy_poweroff()` marks WL RF off, clears busy/LPS, clears all WL scoreboard bits, reruns coex, disables all firmware reports, and snapshots RF-off state.
- `rtw89_btc_ntfy_init()` resets all coexistence state, stores mode (`BTC_MODE_WL`, `BTC_MODE_BT`, `BTC_MODE_WLOFF`, or normal), invokes chip RFE/init configuration, sets WL scoreboard active/on/BTLOG, reads BT scoreboard, checks PTA ownership, sends init/control driver info, programs monitor registers and full slot table, then runs initial coex.

Scan, band, packet, and radio notifications:

- `rtw89_btc_ntfy_scan_start()` and `rtw89_btc_ntfy_scan_finish()` toggle scan state, scan band/phy map, DBCC scan band, scan driver info, and force an instant TDMA execution on scan finish.
- `rtw89_btc_ntfy_switch_band()` updates DBCC scan band and reruns coex.
- `rtw89_btc_ntfy_specific_packet()` treats DHCP as connecting and EAPOL as 4-way handshake, schedules `coex_act1_work` to clear temporary states, and gives shorter EAPOL protection when HFP/HID exists. ARP and ICMP only count/log and return.
- Packet work handlers leave PS mode for EAPOL, DHCP, and ICMP before notifying.
- `rtw89_btc_ntfy_radio_state()` maps RF control state into RF-off/LPS/busy bits, toggles reports and scoreboard, reinitializes chip coexistence config on RF-on, resets BT-count hang state, forces instant TDMA, reruns coex, and snapshots RF/LPS state.

RF calibration notification:

- `rtw89_btc_ntfy_wl_rfk()` wraps `_ntfy_wl_rfk()`. On RFK start it polls for allowance up to 100 ms unless BT IQK timeout has already been latched. `_ntfy_wl_rfk()` rejects WL RFK while BT RFK is running/requested and not timed out, sets/clears `BTC_WSCB_WLRFK`, queues RFK timeout work for accepted starts, and reruns coex for start/stop transitions.

Firmware C2H:

- `rtw89_btc_c2h_handle()` verifies class `BTFC_FW_EVENT`, remaps function IDs with `rtw89_btc_c2h_get_index_by_ver()`, increments C2H counters, and dispatches report parsing, BT-info parsing, scoreboard updates, BT register/loopback debug values, CX runinfo counts, and BT TX-power descriptor updates.

## State And Persistence Behavior

The primary persistent state lives under `rtwdev->btc`:

- `btc->ver` points to the chosen firmware ABI descriptor from `rtw89_btc_ver_defs[]`.
- `btc->cx` stores current WL state, BT state, counters, DBCC/role/link information, and other coexistence source state.
- `btc->dm` stores the active decision state: current and committed TDMA/slot tables, selected policy/action, error map, DM counters, grant state, RF TRX parameters, OSI info, WL TX limits, leak/freerun/FDDT flags, E2G slot limits, and DM step ring.
- `btc->fwinfo` stores firmware report contents, C2H/H2C counters, enabled report map, report validity, length mismatch bitmaps, firmware subversions, and event counters.
- `btc->ctrl` stores manual/ignore/freerun control knobs whose layout depends on `fcxctrl`.
- `btc->mdinfo` stores module/RFE/antenna/switch metadata used at init and in freerun decisions.

Hardware-visible persistence includes MAC scoreboard bits, grant configuration, PTA request source, PLT tables, BB BTG/pre-AGC registers, TX power controls, RX gain controls, station TX time/retry limits, and firmware-side TDMA/slot/report/driver-info state. Most of these persist until the next coexistence action, radio transition, firmware reset, or device reset.

The code intentionally avoids redundant hardware/firmware writes by comparing new state to `*_now` or cached values. Force paths exist for init, power/radio transitions, command control, DBCC changes, policy force, and instant TDMA execution.

## Dependencies And Integration Points

This chunk depends on rtw89 core structures and helpers declared in `chan.h`, `coex.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `ps.h`, and `reg.h`.

Major integration points include:

- Firmware H2C helpers: `rtw89_fw_h2c_raw_with_hdr()`, `rtw89_fw_h2c_cxdrv_init*()`, `rtw89_fw_h2c_cxdrv_role*()`, `rtw89_fw_h2c_cxdrv_ctrl*()`, `rtw89_fw_h2c_cxdrv_trx()`, `rtw89_fw_h2c_cxdrv_rfk()`, and `rtw89_fw_h2c_cxdrv_osi_info()`.
- MAC/BB/RF helpers: grant config, PLT config, scoreboard get/set, TX time/retry get/set, BT/WL control path, PTA source register writes, BB register reads, and chip ops for BTG/pre-AGC/TX power/RX gain.
- mac80211/wiphy APIs: wiphy delayed work, RCU link dereference, station iteration, and power-save exit before selected packet notifications.
- Chip-specific operations through `rtwdev->chip->ops`: RFE setup, initial coexistence config, policy builder selection, BT RSSI conversion, WL S1 standby, WL TX power control, WL RX gain control, BTG and no-BTG BB control.
- PHL/MR/MLO channel context APIs through `rtw89_query_mr_chanctx_info()` and `rtwdev->mlo_dbcc_mode`.

## Risks And Edge Cases

The largest correctness risk is ABI drift. The same firmware event type has many version-specific structures, lengths, and bit positions. If `rtw89_btc_ver_defs[]` selects the wrong ABI for a chip/firmware version, valid C2H reports can be rejected as length mismatches, copied into the wrong union shape, or interpreted with wrong counters and flags.

The policy tables are dense numeric encodings. Priority-table choices such as `cxtbl[8]`, `cxtbl[17]`, or `cxtbl[25]` are meaningful but opaque; changing one index can compile cleanly while altering latency/fairness behavior for BT HID, A2DP, 4-way handshake, scan, RFK, or MCC cases.

Several paths rely on strict ordering. `_run_coex()` comments that sequence matters, and moving RF-off, init, RFK, scan, or BT-off checks can produce wrong grant ownership or firmware policy. `_chk_btc_report()` also requires BT slot flood checking before cycle hang for v7 CYSTA reports.

Buffer safety is mostly explicit but still delicate. Policy TLV builders check v7 slot overflow, but other appended policy shapes rely on `RTW89_BTC_POLICY_MAXLEN` and expected enum/table sizes. Report parsing protects against overrun by checking `buf_len`, but it stops silently on malformed records.

There are visible suspicious lines worth targeted validation when this code is modified:

- `_set_bt_afh_info_v1()` computes `en`, `ch`, and `bw`, but assigns `wl_afh->en/ch/bw` from zero-initialized `buf[]` instead of those computed values, and increments the channel-update counter only when `_send_fw_cmd()` returns nonzero. That differs from v0 behavior and may be intentional only if later code fills `buf`, which is not visible in this chunk.
- `_set_wl_preagc_ctrl()` uses `rinfo_v7->dbcc_2g_phy` in the `role_ver == 8` branch. If not intentional, v8 DBCC pre-AGC decisions can use stale v7 state.
- `__rtw89_btc_ntfy_wl_sta_iter()` initially selects `wl->rlink_info[port][mac_idx]` for fwlrole v8, but later resets `link_info = &wl->link_info[port]` before updating busy/dir fields. This may leave v8 per-link traffic state partly split between old and new storage.

Power-state races are another risk. `_send_fw_cmd()` rejects H2C while WL is off/LPS RF-off, but several notification paths intentionally toggle reports and scoreboard around RF transitions. Tests need to cover rapid scan, LPS, radio state, and poweroff/poweron sequences.

Manual-control and ignore-BT modes suppress parts of the state machine. Debug or command interfaces that set those bits can make BT-info or scoreboard updates appear ignored until control is cleared.

RFK arbitration depends on timely scoreboard updates and delayed timeout work. If BT RFK request/run bits stick, WL RFK can be rejected repeatedly; if timeout handling is too aggressive, coexistence may permit overlapping calibrations.

## Test Signals

Build and static signals:

- `coex.c` compiles for chips spanning old and new ABI entries: RTL8852A/B/C/BT, RTL8851B, and RTL8922A.
- `rtw89_btc_set_policy` and `rtw89_btc_set_policy_v1` remain exported and referenced by chip ops.
- Flexible-array allocations in slot and monitor-register setup use the intended counts and do not trigger compiler fortify/count warnings.

Firmware/report signals:

- After init, H2C counters increase without repeated `cnt_h2c_fail`, and report enable maps match requested monitor/all/BT-version transitions.
- C2H report parsing marks expected reports valid with no unexpected `len_mismch` bits for every supported firmware version in `rtw89_btc_ver_defs[]`.
- TDMA and slot reports match `dm->tdma_now` and `dm->slot_now`; `tdma_no_sync` and `slot_no_sync` should not persist under normal operation.
- CYSTA counters should move over time without repeated cycle, W1/B1/E2G, or slot-drift hang flags.

Runtime coexistence signals:

- Wi-Fi scan, association, EAPOL/4-way, DHCP, station traffic changes, RF-on/off/LPS, and WL RFK each produce expected `_run_coex()` reasons and actions in BTC debug logs.
- BT profile transitions from no profile to HFP/HID/A2DP/PAN and combinations produce policy changes appropriate to profile latency and Wi-Fi link mode.
- Shared-antenna and dedicated-antenna devices choose different grant/policy behavior, especially for HID/A2DP, freerun, 5 GHz, and 2.4 GHz SCC/MCC.
- DBCC and MLO cases update PTA request band, DBCC 2G PHY, role link mode, and OSI info consistently when links move between MAC0/MAC1.
- Station TX-time limits are enabled for HFP/HID-sensitive cases, preserve original TX time/retry values, and restore them when BT profiles stop or link mode moves to 5 GHz/no-link.

Hardware/interop signals:

- Scoreboard bits `ACTIVE`, `ON`, `TDMA`, `WLRFK`, `WLBUSY`, `RXGAIN`, `RXSCAN_PRI`, `BT_HILNA`, and `BTLOG` toggle as expected through init, poweroff, scan, RFK, and BT RX-gain changes.
- AFH channel info sent to BT reflects the active 2.4 GHz channel and bandwidth, especially on RTL8922A/v8 paths.
- RFK start should either be allowed quickly or reject with BT RFK request/run evidence; repeated `RFK notify timeout` indicates scoreboard or arbitration failure.
- Throughput and latency tests should include 2.4 GHz STA with BT HID, A2DP, HFP, PAN, combined profiles, scan while streaming, 4-way handshake under BT traffic, 2G SCC/MCC, 2.4+5 MCC, DBCC, MLO, LPS transitions, and high/low RSSI boundaries.

## Cross-Chunk Notes

The chunk ends inside `_show_cx_info()`. Later lines in the same source file render debugfs/debug string summaries for CX/WL/BT/DM/MREG/CYSTA/slot/summary state and include `rtw89_coex_recognize_ver()` plus small preserve-time/RFK notification helpers. Merge reconciliation should combine this runtime-control report with the later debug-output chunk to describe the whole file.

### subset-b-004920: lines 8849-11906

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
