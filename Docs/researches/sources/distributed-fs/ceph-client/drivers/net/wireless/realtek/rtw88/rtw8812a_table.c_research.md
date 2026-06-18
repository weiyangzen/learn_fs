# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812a_table.c

## Purpose
`rtw8812a_table.c` contains static hardware programming data for RTL8812A. It exports typed rtw88 tables for MAC, AGC, BB, PHY power-gain, RF path A/B, TX power limits, power transition sequences, and thermal power tracking. The file is almost entirely declarative data consumed by `rtw8812a.c` through `rtw_chip_info` and by generic rtw88 table loaders.

## Important APIs, tables, and macros
- `rtw8812a_mac_tbl`: generated from `rtw8812a_mac[]` with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_mac)` for MAC register initialization.
- `rtw8812a_agc_tbl`, `rtw8812a_agc_diff_lb_tbl`, `rtw8812a_agc_diff_hb_tbl`: AGC table programming and 5 GHz low/high-band differential updates loaded during calibration.
- `rtw8812a_bb_tbl`: BB register initialization table.
- `rtw8812a_bb_pg_tbl` and `rtw8812a_bb_pg_rfe3_tbl`: PHY power-gain tables declared with `RTW_DECL_TABLE_BB_PG`, with a separate table for RFE type 3.
- `rtw8812a_rf_a_tbl` and `rtw8812a_rf_b_tbl`: RF radio path tables declared with `RTW_DECL_TABLE_RF_RADIO`.
- `rtw8812a_txpwr_lmt_tbl`: regulatory/channel/rate TX power limits declared with `RTW_DECL_TABLE_TXPWR_LMT`.
- `card_enable_flow_8812a`, `enter_lps_flow_8812a`, and `card_disable_flow_8812a`: exported arrays of `struct rtw_pwr_seq_cmd` sequence pointers.
- `rtw8812a_rtw_pwr_track_tbl` and `rtw8812a_rtw_pwr_track_rfe3_tbl`: exported thermal tracking lookup tables for default and RFE3 boards.

## Control flow and state behavior
The data tables are loaded by external control flow. MAC/AGC/BB/RF arrays use rtw88 table encodings that include raw address/value pairs and conditional selector words, allowing the generic table loader to apply entries only for matching conditions. Power sequence arrays are interpreted by the rtw88 power-sequence engine: card-disabled to card-emulation, card-emulation to active, active to low-power state, active to card-emulation, and card-emulation to card-disabled. Commands include register writes, polling, and delays with interface masks for PCI and USB-specific steps.

Power tracking tables map thermal deltas to swing/power adjustments for 2.4 GHz, 5 GHz path A/B, positive/negative temperature direction, CCK/OFDM, and RFE3-specific behavior. These tables are immutable and referenced through `struct rtw_pwr_track_tbl`; runtime state lives in `rtwdev->dm_info` and PHY code, not in this file.

## Dependencies and integration points
The file includes `main.h`, `phy.h`, and `rtw8812a_table.h`. It depends on table declaration macros from rtw88 PHY code and power-sequence definitions from core rtw88 headers. `rtw8812a.c` points `rtw_chip_info` fields to the exported tables: `mac_tbl`, `agc_tbl`, `bb_tbl`, `rf_tbl`, RFE definitions' `phy_pg_tbl`/`txpwr_lmt_tbl`/`pwr_track_tbl`, and power on/off sequences. `rtw8812a_phy_calibration()` directly loads `rtw8812a_agc_diff_lb_tbl` or `rtw8812a_agc_diff_hb_tbl` based on channel.

## Risks and edge cases
- Tables encode vendor hardware knowledge as constants. Errors typically appear as failed bring-up, low sensitivity, poor TX power, or regulatory violations rather than compile failures.
- Conditional table markers are opaque; malformed condition ordering can skip or over-apply register writes.
- Power sequence commands are interface-mask-sensitive. A USB/PCI mask mistake can break suspend/resume or power-on sequencing.
- RFE3 has distinct BB power-gain and power-track tables; incorrect `rfe_option` parsing in EFUSE sends hardware through the wrong table set.
- TX power limit tables must stay aligned with regulatory code expectations and channel/rate indexes.

## Test signals
Test signals include successful `rtw_load_table()` calls during power-on/PHY init, reliable card enable/disable and LPS entry/exit on both USB and PCI masks where applicable, expected AGC diff table load by channel, correct RFE3 power-gain selection, no table parser warnings, stable thermal power tracking across positive and negative temperature deltas, and regulatory TX power values matching the `rtw8812a_txpwr_lmt_tbl` limits.
