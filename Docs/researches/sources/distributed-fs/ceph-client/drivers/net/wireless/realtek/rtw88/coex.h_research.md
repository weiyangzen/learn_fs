# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.h

## Purpose
`coex.h` defines the public constants, enums, parameter structs, chip-operation wrappers, exported functions, and small state predicates for the `rtw88` coexistence engine in `coex.c`.

## Important definitions and APIs
The header defines timing constants (`COEX_REQUEST_TIMEOUT`, `COEX_MIN_DELAY`, `COEX_RFK_TIMEOUT`), firmware H2C 0x69 opcodes, TDMA timer types, RSSI state predicates, and response payload extractors. Enums describe BT MP info operations, antenna phases, coexistence run reasons, LTE table types, GNT setup states, external antenna positions/control sources, coexistence algorithms, BT profile bitmaps, Wi-Fi link modes, scoreboard bits, power-save types, RSSI hysteresis states, notifier event types, BT status values, throughput direction, Wi-Fi priority masks, common chip setup commands, indirect register types, PSTDMA type, and BT RSSI encoding type.

Small parameter structs include `coex_table_para` for BT/WL PTA table values, `coex_tdma_para` for five-byte TDMA firmware parameters, `coex_5g_afh_map` for Wi-Fi-to-BT AFH channel mapping, and `coex_rf_para` for Wi-Fi/BT TX power and RX gain decisions.

The inline wrappers dispatch to chip operations: `rtw_coex_set_init()`, `rtw_coex_set_ant_switch()`, `rtw_coex_set_gnt_fix()`, `rtw_coex_set_gnt_debug()`, `rtw_coex_set_rfe_type()`, `rtw_coex_set_wl_tx_power()`, and `rtw_coex_set_wl_rx_gain()`. Function prototypes expose C2H response handling, indirect register access, scoreboard writes, lifecycle notifiers, BT/HID/FW debug notifications, delayed-work handlers, periodic status checks, HID list query, and debugfs display.

## Control flow and integration
This header is included by core, firmware, debug, mac80211, and chip-specific files. It creates a two-layer integration model: generic coexistence policy in `coex.c` calls wrappers, and chip files provide the hardware-specific details through `struct rtw_chip_ops`. External driver code calls the notifiers when mac80211 or firmware state changes; `coex.c` converts those events into table/TDMA/antenna decisions.

## State and persistence behavior
The header itself is stateless, but its enums are persisted in runtime fields inside `struct rtw_coex_stat` and `struct rtw_coex_dm` defined in `main.h`. Scoreboard bit definitions are shared with firmware/BT and persist in `REG_WIFI_BT_INFO`. TDMA, table, antenna, GNT, and RF settings persist in device registers or firmware state until overwritten.

## Dependencies and risks
Dependencies include Linux bit operations, endian helpers, mac80211 types, SKB/workqueue/seq_file declarations through included driver headers, and chip ops. The highest risk is semantic drift between enum values and firmware/chip table expectations. Some inline wrappers assume the corresponding chip op exists, while `rtw_coex_set_ant_switch()` explicitly allows NULL; chip operation tables must be complete for chips that enable BT coexistence.

## Test signals
Compile coverage should include debugfs enabled and disabled, coexistence-capable and Wi-Fi-only chips, and all transport types. Runtime signals include correct calls from scan/connect/media/LPS/IPS paths, valid BT info decoding, debugfs `coex_info` output, no NULL callback crashes, and stable behavior when `rtw_coex_disabled()` or `rtw_coex_active_query_bt_info()` is exercised on chips such as RTL8821A.
