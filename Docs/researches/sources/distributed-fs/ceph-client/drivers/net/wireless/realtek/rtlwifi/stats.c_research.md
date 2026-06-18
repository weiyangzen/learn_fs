# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.c

## Purpose
Provides shared rtlwifi receive signal conversion and smoothing. It converts hardware dBm/EVM values to percentages, maps raw signal percentages to UI-oriented strength values, and updates rolling RSSI, PWDB, link-quality, SNR, EVM, CFO, and per-station smoothed power statistics for packets that match the current BSSID.

## Important APIs, Types, And Functions
Exported functions are `rtl_query_rxpwrpercentage`, `rtl_evm_db_to_percentage`, `rtl_signal_scale_mapping`, and `rtl_process_phyinfo`. Internal helpers include `rtl_translate_todbm`, `rtl_process_ui_rssi`, `rtl_update_rxsignalstatistics`, `rtl_process_pwdb`, and `rtl_process_ui_link_quality`. The code operates on `struct rtl_stats`, `struct rtl_priv`, `struct rtl_phy`, `struct rtl_sta_info`, and the rolling-window state under `rtlpriv->stats`.

## Control Flow
Chip-specific RX code fills a `rtl_stats` instance and calls `rtl_process_phyinfo`. Non-BSSID packets are ignored. Matching packets update UI RSSI only for packets to self or beacons, then update smoothed PWDB either per station in AP/adhoc modes or globally in `rtlpriv->dm.undec_sm_pwdb`, and finally update UI link quality if the packet carries nonzero signal quality. RSSI uses a fixed-size sliding window; per-path RSSI, SNR, EVM, and CFO use exponential smoothing with `RX_SMOOTH_FACTOR`. Signal conversion helpers are exported for descriptor parsers.

## State And Persistence
All state is in memory: rolling-window arrays and indexes under `rtlpriv->stats`, smoothed per-station `drv_priv->rssi_stat.undec_sm_pwdb`, global `rtlpriv->dm.undec_sm_pwdb`, and latest receive signal power. No filesystem persistence exists.

## Dependencies And Integration Points
Integrated with every rtlwifi chip-specific RX descriptor parser. It depends on mac80211 station lookup under RCU, `rtl_find_sta`, the shared `rtl_stats` layout in `wifi.h`, and RF path counts from `rtlpriv->phy`. Exported symbols allow chip modules to link against these helpers.

## Risks And Edge Cases
`rtl_process_ui_link_quality` reads `rx_mimo_sig_qual`, while several newer chip paths, including RTL8821AE, fill `rx_mimo_signalquality`; that mismatch can leave per-stream EVM smoothing stale. `rtl_process_ui_rssi` ignores non-self non-beacon packets, so some traffic patterns update PWDB but not UI RSSI. The initial `recv_signal_power == 0` sentinel can be ambiguous if a legitimate computed value is 0 dBm. Per-station smoothing is skipped in station mode because the code only calls `rtl_find_sta` when the opmode is not station.

## Test Signals
RX tests should cover BSSID match/mismatch, to-self data, beacons, AP/adhoc station lookup, CCK versus OFDM/HT/VHT stats, sliding-window wraparound, rising and falling RSSI smoothing, and per-stream EVM updates. Cross-chip tests should verify whether `rx_mimo_sig_qual` or `rx_mimo_signalquality` is populated before link-quality smoothing.
