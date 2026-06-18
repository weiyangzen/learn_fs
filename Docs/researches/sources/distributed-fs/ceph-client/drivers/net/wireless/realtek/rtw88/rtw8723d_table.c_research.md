# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723d_table.c

## Purpose
This file contains static/generated hardware tables for RTL8723D. It packages MAC, AGC, BB, power-by-rate, RF path A, and TX power-limit data into rtw88 table objects consumed by `rtw8723d_hw_spec` and generic table loaders.

## Important APIs, Types, And Functions
The exported tables are declared through macros as `rtw8723d_mac_tbl`, `rtw8723d_agc_tbl`, `rtw8723d_bb_tbl`, `rtw8723d_bb_pg_tbl`, `rtw8723d_rf_a_tbl`, and `rtw8723d_txpwr_lmt_tbl`. Backing arrays include `rtw8723d_mac[]`, `rtw8723d_agc[]`, `rtw8723d_bb[]`, `rtw8723d_bb_pg[]`, `rtw8723d_rf_a[]`, and `rtw8723d_txpwr_lmt[]`.

The table macros indicate interpretation: conditional MAC/AGC/BB register loading with `rtw_phy_cfg_mac`, `rtw_phy_cfg_agc`, and `rtw_phy_cfg_bb`; RF radio programming for path A; BB power-group programming; and regulatory TX power-limit lookup.

## Control Flow
This file is data-only. During PHY setup, `rtw_phy_load_tables()` applies MAC/AGC/BB/RF tables referenced from `rtw8723d_hw_spec`. TX power-limit entries are consulted later by power calculation code using regulatory group, 2.4 GHz band, bandwidth, rate section, and channel.

## State And Persistence
The arrays are read-only kernel data. Loading the tables produces persistent hardware register state until reset/reprogramming. The TX power-limit table is persistent policy data used across channel and regulatory changes.

## Dependencies And Integration Points
The file depends on `main.h`, `phy.h`, and `rtw8723d_table.h`. It integrates with `rtw8723d.c` through the chip descriptor and RFE definitions. It also depends on the generic rtw88 table declaration macros and loader functions interpreting the pair arrays correctly.

## Risks
Incorrect table data can cause probe failures, broken RX/TX sensitivity, calibration failures, invalid output power, or regulatory violations. The RF table is path-A only, so assumptions about path mapping must match `rtw8723d.c`. The TX power-limit table is dense and hard to audit manually; off-by-one channel, bandwidth, or rate-section entries are plausible regression points.

## Test Signals
Test signals include clean table load, stable association and throughput, expected RSSI/false-alarm behavior, successful IQK and power tracking after table load, correct TX power across FCC/ETSI/MKK-style regulatory groups, and register dumps matching known-good initialization data.
