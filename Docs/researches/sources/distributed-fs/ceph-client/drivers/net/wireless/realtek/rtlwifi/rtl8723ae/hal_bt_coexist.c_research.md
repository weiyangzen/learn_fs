# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.c

## Purpose
`hal_bt_coexist.c` provides shared RTL8723AE Wi-Fi/Bluetooth coexistence helpers: Wi-Fi state classification, RSSI hysteresis, AGC/backoff controls, FW balance commands, all-off wrappers, and state-change checks.

## APIs, Types, And Functions
Public functions include `_rtl8723_dm_bt_check_wifi_state`, RSSI state helpers, `rtl8723e_dm_bt_get_rx_ss`, `rtl8723e_dm_bt_balance`, AGC table and BB backoff controls, all-off wrappers, AP aggregation rejection stub, coexistence state-change check, and Wi-Fi uplink detection.

## Control Flow, State, And Persistence
Wi-Fi state updates set bits in `rtlpriv->btcoexist.cstate` for idle/uplink/downlink, legacy/HT20/HT40, RSSI level, and BT3.0 operation. RSSI helpers use hysteresis against prior BT RSSI states. Mechanism functions write AGC table/RF registers, BB backoff registers, and H2C command `0xc` for time balance. All-off wrappers avoid duplicate work using `fw/sw/hw_coexist_all_off` flags. State persists in `rtlpriv->btcoexist`, baseband/RF registers, and firmware coexistence settings.

## Dependencies And Integration Points
It depends on `dm.h`, `fw.h`, `phy.h`, `reg.h`, `hal_btc.h`, rtlwifi PCI/core state, RSSI metrics, and H2C command submission. `hal_btc.c` calls these helpers to apply profile policies.

## Risks And Test Signals
Risks include stale state bits, hysteresis bugs, duplicate or missing all-off transitions, register value regressions, and an empty aggregation-rejection stub. Signals are BT coexistence debug state transitions, stable Wi-Fi RSSI/throughput with BT traffic, and correct all-off behavior before low power.
