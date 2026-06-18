# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/mac.c

## Purpose

`mac.c` programs the AR9170 MAC block. It applies timing, rate, QoS, operating mode, multicast, virtual MAC, beacon timer, key cache, retry, and transmit-power-control settings derived from mac80211 state, EEPROM calibration, firmware capabilities, and driver policy.

## Important APIs, Types, and Functions

Exported functions include `carl9170_set_dyn_sifs_ack()`, `carl9170_set_rts_cts_rate()`, `carl9170_set_slot_time()`, `carl9170_set_mac_rates()`, `carl9170_set_qos()`, `carl9170_init_mac()`, `carl9170_mod_virtual_mac()`, `carl9170_update_multicast()`, `carl9170_set_operating_mode()`, `carl9170_set_hwretry_limit()`, `carl9170_set_beacon_timers()`, `carl9170_upload_key()`, `carl9170_disable_key()`, and `carl9170_set_mac_tpc()`. The local helper `carl9170_set_mac_reg()` writes six-byte MAC/BSSID-style registers.

## Control Flow

`carl9170_init_mac()` writes a baseline MAC register program: OTUS interface selection, retry/filter defaults, RX control, timing, AMPDU defaults, FCS behavior, multicast hash, and beacon interrupt disable. Runtime config callbacks in `main.c` then call targeted setters. Operating-mode setup reads the main VIF under RCU, selects STA/AP/IBSS/mesh/monitor-compatible CAM and RX control modes, writes MAC address and BSSID, and updates sniffer/encryption/RX control registers. Beacon timers compute global beacon interval and PRETBTT from the main VIF and number of beaconing interfaces.

## State and Persistence Behavior

The file persists hardware register state and updates driver mirrors including `ar->cur_mc_hash`, `ar->global_beacon_int`, `ar->global_pretbtt`, and encryption mode consequences from `ar->rx_software_decryption` and `ar->sniffer_enabled`. Key commands mutate firmware CAM state. `carl9170_set_mac_tpc()` uses EEPROM-derived power arrays and current mac80211 power level to set ACK/RTS/CTS/QoS-null power and chain masks.

## Dependencies and Integration Points

It depends on mac80211 VIF/BSS config, ath common MAC/BSSID fields, EEPROM masks and power tables, firmware command ABI, register batch helpers, PHY channel state, and constants from `hw.h`/`wlan.h`. It is called from start/config/filter/BSS/key/interface/channel code in `main.c` and `phy.c`.

## Risks and Edge Cases

`carl9170_mod_virtual_mac()` computes `(id - 1) * 8`; callers must avoid using ID 0 as a slave ACK-table entry. Monitor behavior deliberately avoids promiscuous sniffer ACK generation and instead uses station mode plus relaxed filters. Beacon intervals below 15 TU return `-ERANGE`; multi-VIF beacon interval sharing depends on the main VIF. Hardware crypto offload must stay synchronized with the policies in `main.c`.

## Test Signals

Exercise STA, AP, mesh, IBSS, monitor/filter transitions, BSSID changes, basic-rate changes, slot time changes, multicast hash updates, beacon enable/disable, and key set/delete for WEP/TKIP/CCMP. Register traces should verify expected writes to CAM, RX control, encryption, beacon, QoS, and TPC registers.
