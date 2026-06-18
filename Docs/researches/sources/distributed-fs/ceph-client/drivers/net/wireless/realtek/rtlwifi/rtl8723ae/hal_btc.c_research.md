# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.c

## Purpose
`hal_btc.c` is the RTL8723AE Bluetooth coexistence policy engine. It queries firmware BT info, monitors BT hardware counters, classifies BT profiles, builds `btdm_8723` coexistence policies, and applies them through firmware commands, PTA tables, BB/RF settings, and software rate/AGC tweaks.

## APIs, Types, And Functions
Public functions include `rtl8723e_dm_bt_turn_off_bt_coexist_before_enter_lps`, media-status notification, all-off implementations, `rtl8723e_dm_bt_set_bt_dm`, `rtl8723e_dm_bt_coexist_8723`, and `rtl_8723e_c2h_command_handle`. Internal helpers set H2C commands (`0x11`, `0x14`, `0x15`, `0x21`-`0x26`, `0x29`, `0x33`, `0x38`, `0x3a`), PTA table registers, RF LPF, DAC swing, retry index, WLAN_ACT timing, and profile-specific PS-TDMA bytes.

## Control Flow, State, And Persistence
The watchdog path queries BT information, reads high/low priority counters, detects BT enable/disable, chooses 2-antenna logic, handles inquiry/page windows, then selects common, HID/SCO/eSCO, or FTP/A2DP policy. `rtl8723e_dm_bt_set_bt_dm` skips unchanged policies, handles hold-for-BT-operation, applies all-off or ordered mechanism changes, delays for DAC swing, and updates BT power. State lives in static `hal_coex_8723` plus `rtlpriv->btcoexist`; writes persist in firmware and hardware.

## Dependencies And Integration Points
It depends on `hal_btc.h`, `hal_bt_coexist.h`, `fw.h`, `phy.h`, `reg.h`, rtlwifi/mac80211 state, common PHY helpers, C2H registers, and optional `btc_ops->btc_periodical`.

## Risks And Test Signals
Risks include static global multi-device leakage, C2H length/ownership errors, policy oscillation, ordering bugs between TDMA/HID/PS-TDMA, unimplemented 1-antenna path, and poor BT/Wi-Fi fairness. Signals are BT info C2H parsing, counter changes, profile-specific debug actions, LPS all-off, and throughput/latency under A2DP, HID, SCO, PAN/FTP, inquiry, and idle scenarios.
