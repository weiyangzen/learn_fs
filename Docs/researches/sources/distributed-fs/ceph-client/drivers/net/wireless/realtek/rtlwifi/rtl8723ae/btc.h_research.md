# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/btc.h

## Purpose
`btc.h` provides a small RTL8723AE Bluetooth coexistence support definition shared by coexistence implementation files.

## APIs, Types, And Data
It includes rtlwifi base definitions and `hal_bt_coexist.h`, then defines `struct bt_coexist_c2h_info` with `no_parse_c2h` and `has_c2h` flags. These flags describe firmware-to-host coexistence event availability/parsing state.

## Control Flow, State, And Persistence
The header has no executable flow. The struct is transient driver state for C2H event handling; it reflects firmware notifications rather than persistent storage. Hardware/FW state changes are performed by the coexistence implementation through H2C commands and register writes.

## Dependencies And Integration Points
It is included by `hal_btc.h`, tying low-level C2H bookkeeping to the larger BT coexistence state-machine and policy definitions. It depends on rtlwifi/mac80211 type visibility through `../wifi.h`.

## Risks And Test Signals
Risks are minimal but include stale fields if C2H parsing changes, or circular include assumptions. Signals are clean builds, BT info C2H processing, coexistence periodical callbacks, and no lost BT status updates during Wi-Fi/BT activity.
