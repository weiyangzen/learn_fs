# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8703b_tables.c

## Purpose
This file contains generated/static hardware initialization and power-limit tables for RTL8703B. It packages BB power-by-rate, TX power limit, MAC register, AGC, baseband, and RF path A programming arrays into `struct rtw_table` exports consumed by `rtw8703b_hw_spec` and the generic rtw88 PHY table loader.

## Important APIs, Types, And Functions
The important exported table objects are produced by macros: `rtw8703b_bb_pg_tbl`, `rtw8703b_txpwr_lmt_tbl`, `rtw8703b_mac_tbl`, `rtw8703b_agc_tbl`, `rtw8703b_bb_tbl`, and `rtw8703b_rf_a_tbl`. The backing arrays are `rtw8703b_bb_pg[]`, `rtw8703b_txpwr_lmt[]`, `rtw8703b_mac[]`, `rtw8703b_agc[]`, `rtw8703b_bb[]`, and `rtw8703b_rf_a[]`.

The declaration macros select the table interpretation: `RTW_DECL_TABLE_BB_PG()` for power-by-rate page data, `RTW_DECL_TABLE_TXPWR_LMT()` for regulatory/channel/rate-section power limits, `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_mac/agc/bb)` for conditional register programming, and `RTW_DECL_TABLE_RF_RADIO(..., A)` for RF path A.

## Control Flow
There is no procedural control flow in this file. During `rtw8703b_phy_set_param()`, `rtw_phy_load_tables()` walks the exported table objects from the chip info and applies each register/value pair through the appropriate MAC, AGC, BB, or RF loader. TX power-limit data is consulted later when transmit power is calculated for the active regulatory group, channel, bandwidth, and rate section.

## State And Persistence
The arrays are read-only driver data. Applying them creates persistent hardware state in MAC, AGC, BB, RF, TX-power, and power-by-rate registers until later updates or reset. Regulatory TX power limits are data state used repeatedly by power calculation rather than one-time register state.

## Dependencies And Integration Points
The file depends on `main.h`, `phy.h`, and `rtw8703b_tables.h` for table types and declarations. It integrates directly with `rtw8703b.c` through `rtw8703b_hw_spec.mac_tbl`, `.agc_tbl`, `.bb_tbl`, `.rf_tbl`, RFE definitions, and power-limit references. The values are vendor-derived hardware programming data and must match the silicon and firmware assumptions.

## Risks
The risk profile is data correctness. A single wrong register/value pair can break initialization, calibration, RF sensitivity, output power, coexistence, or regulatory compliance. The TX power-limit table contains permissive sentinel-like `63` values for some channel/rate combinations; consumers must interpret those correctly. Because table loaders hide control flow behind data, failures can be hard to localize without register traces.

## Test Signals
Signals include successful table loading during probe, working association after PHY init, sane RX sensitivity and TX throughput, correct channel 1-14 behavior, regulatory power-limit selection for FCC/ETSI/MKK mappings, RF path A operation, and no unexpected register-loader warnings. Comparing register dumps against known-good vendor-driver initialization is useful for table regressions.
