# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8723b1ant.h

## Purpose
Defines the RTL8723B one-antenna Bluetooth coexistence data model and external callback interface. It documents the BT-info bit layout, report sources, normalized BT and Wi-Fi status states, coexistence algorithm IDs, dynamic/station state structures, thresholds, and chip-specific notification functions used by the rtlwifi coexistence dispatcher.

## Important APIs, Types, And Functions
BT-info bit macros identify FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection bits. `BT_INFO_8723B_1ANT_A2DP_BASIC_RATE()` extracts the A2DP basic-rate flag from BT-info extension byte 4. `BTC_RSSI_COEX_THRESH_TOL_8723B_1ANT` defines RSSI hysteresis tolerance, and `BT_8723B_1ANT_WIFI_NOISY_THRESH` is the scan/AP-count threshold used as a noisy-environment signal.

`enum _BT_INFO_SRC_8723B_1ANT` names Wi-Fi firmware, BT response, and BT active/auto report sources. `enum _BT_8723B_1ANT_BT_STATUS` normalizes parsed BT status. `enum _BT_8723B_1ANT_WIFI_STATUS` describes Wi-Fi contexts used by TDMA adjustment and action selection: disconnected idle, disconnected association/auth/scan, connected scan, connected special packet, connected idle, and connected busy. `enum _BT_8723B_1ANT_COEX_ALGO` lists profile-combination algorithms, although the C implementation primarily uses status/action helpers rather than a single exported algorithm dispatch table.

`struct coex_dm_8723b_1ant` stores mechanism state: antenna position, ignore-WLAN-active, PS-TDMA, auto-report, LPS/RPWM, low-penalty RA, coexistence table values, backup rate/retry/AMPDU registers, algorithm/status, Wi-Fi channel info, rate mask, ARP count, and error condition. `struct coex_sta_8723b_1ant` stores observed station/environment inputs including BT disabled/profile flags, profile counts, abnormal/WHCK/inquiry/remote-name/high-priority flags, IPS/LPS, counters, RSSI, C2H history, scan AP count, CCK lock/noise data, CRC counters, A2DP bitpool, and chip cut version.

The external callback prototypes cover power-on setup, hardware init, coex-DM init, IPS/LPS, scan/connect/media/special packet, BT-info, RF status, halt, PnP, periodic maintenance, and seq-file display. The header declares `ex_btc8723b1ant_pnp_notify()` twice with different parameter spelling but identical type.

## Control Flow
The header has no executable control flow. It describes a callback-driven module: the common coexistence layer initializes the chip, sends event notifications, supplies BT-info C2H buffers, and requests periodic maintenance/debug output. The implementation stores observations in `coex_sta_8723b_1ant`, records applied decisions in `coex_dm_8723b_1ant`, and uses the declared enums/macros to select one-antenna coexistence behavior.

## State And Persistence
Both state structs are designed for long-lived coexistence state across periodic ticks and event callbacks. Previous/current fields in `coex_dm_8723b_1ant` are persistence hooks for avoiding duplicate hardware writes, while backup fields preserve Wi-Fi rate/retry/AMPDU settings. `coex_sta_8723b_1ant` accumulates counters and history that influence later decisions, including CCK lock, pop events, wrong-profile inference, scan AP count, and forced LPS state.

## Dependencies And Integration Points
The header requires kernel integer/bool types, `BIT`/`BITn` macros, `struct btc_coexist`, and `struct seq_file` from the surrounding rtlwifi include stack. It is paired with `halbtc8723b1ant.c` and the common Realtek BT coexistence dispatcher, which selects these callbacks for RTL8723B one-antenna hardware.

## Risks
The header exposes large mutable structs with no locking, lifetime, or per-device ownership model, mirroring the implementation's static-singleton approach. Fixed 10-byte BT-info history arrays require strict length discipline from C2H callers. The duplicated PnP prototype is harmless to C but signals maintenance drift. Several enum values and fields are implementation-specific magic numbers, so external code should not infer generic semantics without checking the companion implementation.

## Test Signals
Build tests should ensure all prototypes resolve and duplicate declarations remain type-identical. Runtime tests should confirm state fields shown by `ex_btc8723b1ant_display_coex_info()` match BT-info reports, Wi-Fi events, antenna path decisions, LPS/RPWM state, coex table type, CCK lock, and scan AP count. Fuzz or boundary testing of BT-info lengths is useful because the state structure only reserves 10 bytes per report source.
