# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.h

## Purpose

`coex.h` is the public coexistence interface for the Realtek `rtw89` driver. It defines the WLAN/BT coexistence vocabulary shared by the core driver, firmware command path, radio calibration code, packet-notification logic, and debug/reporting paths. The header is intentionally state-heavy: most declarations are enums, register constants, bit masks, work periods, and small inline helpers that let other driver modules encode coexistence state into firmware-facing formats.

The file also declares the notification entry points implemented by the coexistence engine. Those functions let the rest of the driver report power transitions, scan state, band changes, special packets, role changes, radio/LPS state, WLAN RF calibration phases, station traffic state, BT C2H messages, and diagnostic dumps.

## Important APIs, Types, and Constants

The mode and RFK enums define the high-level coexistence state machine:

- `enum btc_mode` distinguishes normal, WLAN-only, BT-only, and WLAN-off operation.
- `enum btc_wl_rfk_type` names WLAN RF calibration operations (`IQK`, `LCK`, `DPK`, `TXGAPK`, `DACK`, `RXDCK`, `TSSI`, `CHLK`).
- `enum btc_wl_rfk_state` marks RFK start/stop and one-shot transitions.
- `BTC_RFK_PATH_MAP`, `BTC_RFK_PHY_MAP`, and `BTC_RFK_BAND_MAP` define the packed PHY/path/band encoding used by `rtw89_btc_phymap()`.

Packet and role notification types connect `core.c` TX/RX and mac80211 lifecycle events to BTC:

- `enum btc_pkt_type` covers DHCP, ARP, EAPOL start/end, ICMP, and sentinel `PACKET_MAX`.
- `enum btc_role_state` reports station/AP role starts, stops, type changes, association phases, and disconnects.
- `enum btc_rfctrl` and `enum btc_lps_state` map driver radio and low-power states to BTC decisions.

Hardware control enums and register constants model coexistence knobs:

- `enum btc_pri`, `enum btc_bt_trs`, `enum btc_bt_btg`, `enum btc_ant`, `enum btc_switch`, `enum btc_ant_div_pos`, and status enums encode antenna, priority, traffic, and BTG/pre-AGC control dimensions.
- `R_BTC_BB_BTG_RX`, `R_BTC_BB_PRE_AGC_S0/S1`, `B_BTC_BB_GNT_MUX`, and `B_BTC_BB_PRE_AGC_*` identify baseband fields used by coexistence status/control code.
- Zigbee/LTE/3CX and workaround feature bits are represented by `enum btc_3cx_type`, `enum btc_wa_type`, and `enum btc_chip_feature`.

The declared public functions are the integration surface:

- Lifecycle: `rtw89_btc_ntfy_poweron()`, `rtw89_btc_ntfy_poweroff()`, `rtw89_btc_ntfy_init()`, `rtw89_coex_power_on()`, `rtw89_coex_recognize_ver()`.
- Scan/channel/role: `rtw89_btc_ntfy_scan_start()`, `rtw89_btc_ntfy_scan_finish()`, `rtw89_btc_ntfy_switch_band()`, `rtw89_btc_ntfy_role_info()`.
- Packet notifications: `rtw89_btc_ntfy_specific_packet()` and the workqueue callbacks for EAPOL, ARP, DHCP, and ICMP.
- RF/LPS/calibration: `rtw89_btc_ntfy_radio_state()`, `rtw89_btc_ntfy_wl_rfk()`, `rtw89_btc_ntfy_conn_rfk()`, `rtw89_btc_ntfy_preserve_bt_time()`.
- Firmware/debug: `rtw89_btc_c2h_handle()`, `rtw89_btc_dump_info()`, `rtw89_btc_set_policy()`, `rtw89_btc_set_policy_v1()`, periodic work callbacks.

Inline helpers:

- `rtw89_btc_phymap()` packs RF path bits, PHY index bits, and current channel band from `rtw89_chan_get()` into the BTC RFK map.
- `rtw89_btc_path_phymap()` is a single-path wrapper.
- `rtw89_coex_query_bt_req_len()` returns `rtwdev->btc.bt_req_len`, currently ignoring `phy_idx`.
- `rtw89_get_antpath_type()` combines a PHY map and antenna-path type into a 16-bit style key.
- `_slot_set_le()`, `_slot_set()`, `_slot_set_dur()`, `_slot_set_type()`, and `_slot_set_tbl()` write firmware coexistence slot tables in little-endian format, selecting either `btc->dm.slot.v1` or `btc->dm.slot.v7` according to `btc->ver->fcxslots`.

## Control Flow

This header itself does not run a full state machine, but it defines the cross-module control flow:

1. Core lifecycle code powers MAC/HCI/PHY and calls BTC power/init/radio notifications.
2. mac80211 scan/channel/association paths report scan starts, scan completion, band switches, and role transitions.
3. TX code recognizes EAPOL, ARP, DHCP, and ICMP packets and queues the corresponding `wiphy_work` callbacks declared here.
4. RF calibration and dynamic-maintenance paths pass packed PHY/path/band maps into BTC notification APIs.
5. Coexistence policy code writes slot tables through the inline setters, which abstract firmware table version differences.

The slot setters are the most direct state mutation in the header. They require a valid `btc->ver` and a supported `fcxslots` value. Unsupported values silently leave the slot unchanged, which makes version recognition a prerequisite for correct policy programming.

## State and Persistence Behavior

There is no external persistence. Runtime state lives in `struct rtw89_dev`, especially `rtwdev->btc`, and in nested coexistence decision-management fields (`btc->dm.slot.*`, `btc->bt_req_len`, version metadata). Slot mutations persist only in driver memory until firmware H2C policy programming consumes them or the device is reinitialized.

RSSI state helpers (`BTC_RSSI_HIGH`, `BTC_RSSI_LOW`, `BTC_RSSI_CHANGE`) encode hysteresis-like state classes. They are pure macros but preserve an important convention: "stay" states count as high/low while only non-stay states count as a change.

## Dependencies and Integration Points

`coex.h` includes `core.h`, so it depends on core driver types such as `struct rtw89_dev`, `struct rtw89_btc`, channel contexts, PHY/path enums, and kernel bitfield helpers. It is consumed by `core.c`, PHY/RFK code, firmware C2H/H2C code, debugfs/reporting paths, and chip-specific coexistence policy implementations.

Major integration points:

- mac80211-facing core lifecycle and TX/RX code in `core.c`.
- Firmware command/event handling through `fw.h`/C2H callbacks.
- Channel context and multi-PHY state through `rtw89_chan_get()` and PHY index/path maps.
- Baseband/MAC register programming through constants defined here and used by coexistence implementation files.

## Risks and Edge Cases

- `rtw89_coex_query_bt_req_len()` ignores `phy_idx`; this is safe only while BT request length is device-global. Multi-PHY/MLO changes could need per-PHY request length.
- Slot setter helpers do not validate `sid` bounds. Callers must ensure the slot id is valid for the selected firmware coexistence slot version.
- Slot setter helpers silently do nothing for unexpected `btc->ver->fcxslots` values. Version-recognition failures can therefore degrade coexistence policy without an immediate local error.
- `rtw89_btc_phymap()` assumes `rtw89_chan_get()` returns a valid channel for the passed channel context and that `phy_idx`, path bits, and band type fit the declared masks.
- Because this header bridges firmware ABI versions (`fcxslots == 1` versus `7`), layout drift in the corresponding `struct rtw89_btc` slot definitions is high risk.

## Test Signals

Useful validation signals include:

- Build coverage for all BTC users after enum/API additions, especially sparse/endian warnings around slot table writes.
- Runtime BTC debug dumps from `rtw89_btc_dump_info()` showing recognized coexistence version and expected slot contents.
- Scan, association, RFK, LPS, and power-cycle tests with Bluetooth active to verify notification ordering.
- Packet-trigger tests for EAPOL/ARP/DHCP/ICMP confirming the work callbacks fire and policy changes are visible in debug logs.
- MLO/DBCC tests that exercise `rtw89_btc_phymap()` across PHY indices and bands.
