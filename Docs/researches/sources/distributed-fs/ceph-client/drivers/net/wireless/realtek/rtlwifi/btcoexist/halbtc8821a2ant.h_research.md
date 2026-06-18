# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8821a2ant.h

## Purpose
Defines the RTL8821A two-antenna coexistence contract: BT status bit masks, RSSI thresholds, BT-info sources, coexistence algorithms, dynamic-management state, station/runtime state, and exported notification APIs used by the generic coexistence dispatcher.

## Important APIs, Types, and Functions
Important constants include `BT_INFO_8821A_2ANT_B_*` bit definitions for C2H BT status byte interpretation, `BTC_RSSI_COEX_THRESH_TOL_8821A_2ANT`, and Wi-Fi/BT RSSI thresholds used to shift between two-antenna TDMA and one-antenna-like PS-TDMA behavior. `enum _BT_INFO_SRC_8821A_2ANT` identifies Wi-Fi firmware, BT response, and BT active auto-report sources. `enum _BT_8821A_2ANT_BT_STATUS` normalizes BT idle, connected idle, ACL busy, SCO busy, and mixed states. `enum _BT_8821A_2ANT_COEX_ALGO` enumerates SCO, HID, A2DP, PAN HS/EDR, and profile-mix algorithms.

`struct coex_dm_8821a_2ant` caches the current and previous coexistence decisions: firmware mechanisms, PS-TDMA bytes and adjustment state, BT auto-report state, low-penalty retry, DAC swing, table register values, limited DIG, algorithm, BT status, Wi-Fi channel H2C bytes, and LPS/RPWM values. `struct coex_sta_8821a_2ant` stores observed state: profile booleans, IPS/LPS state, priority counters, BT RSSI, C2H buffers/counters, retry count, BT extension info, Wi-Fi CRC counters, selected coexistence table type, forced LPS flag, and version-display counter. The public declarations are the `ex_btc8821a2ant_*` callbacks consumed by `halbtcoutsrc.c`.

## Control Flow
This header has no runtime flow, but it shapes the flow in `halbtc8821a2ant.c`: BT C2H bits update `coex_sta`, `coex_sta` plus RSSI thresholds choose an algorithm, and `coex_dm` records the programmed mechanism to avoid redundant writes. External notifications all enter through declared `ex_btc8821a2ant_*` functions.

## State and Persistence Behavior
The structures are intended as long-lived driver-private state, but the implementation instantiates them as static globals in the C file. Previous/current pairs in `coex_dm_8821a_2ant` act as a write-coalescing cache. C2H arrays preserve recent BT info per source for diagnostics.

## Dependencies and Integration Points
Depends on `struct btc_coexist`, `struct seq_file`, `u8/u32/bool`, and bit macros supplied by the surrounding Realtek/kernel headers. It is included through the BT coexistence precompiled include path and is tightly coupled to the generic enums in `halbtcoutsrc.h`.

## Risks and Test Signals
The header exposes many numeric algorithm and bit encodings without type-safe wrappers, so C2H parsing or table dispatch can silently drift if firmware encodings change. The fixed 10-byte C2H buffers require callers to bound lengths. Tests should validate bit-to-profile decoding, RSSI threshold hysteresis, each algorithm enum path, and diagnostic output for every stored field.
