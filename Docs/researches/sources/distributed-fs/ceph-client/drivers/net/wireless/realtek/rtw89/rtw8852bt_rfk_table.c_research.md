# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.c

Purpose: Defines RTL8852BT RFK register tables consumed by TSSI setup. The tables program system TSSI registers, per-path/per-band settings, TX power control, HE TB power, TSSI DCK, DAC gain, slope calibration, and alignment defaults.

Important APIs and types: Uses `struct rtw89_reg5_def`, `RTW89_DECL_RFK_WM()`, and `RTW89_DECLARE_RFK_TBL()` to export `struct rtw89_rfk_tbl` symbols such as common system defaults, A/B 2G/5G system tables, init TX power, HE TB, DCK, DAC gain, slope, alignment, and final slope tables.

Control flow: No runtime branch logic in this file. `rtw8852bt_rfk.c` selects tables with `rtw89_rfk_parser()` and `rtw89_rfk_parser_by_cond()` by path, band, and channel range.

State and persistence: Immutable data. Parsed writes persist in TSSI hardware blocks until recalibration, scan/channel update, reset, or another RFK pass.

Dependencies and integration points: Includes `rtw8852bt_rfk_table.h`; tightly coupled to `_tssi_set_sys()`, `_tssi_ini_txpwr_ctrl_bb()`, `_tssi_set_dck()`, `_tssi_set_dac_gain_tbl()`, `_tssi_slope_cal_org()`, `_tssi_alignment_default()`, and `_tssi_set_tssi_slope()`.

Risks: Hardware table values have little compiler validation. Cross-path address mistakes or wrong masks can create asymmetric RF behavior. Subband alignment depends on correct channel classification.

Test signals: TSSI logs, register dumps after TSSI operations, path A/B transmit-power tracking, 2G/5G subband sweeps, HE TB behavior, and comparison with vendor reference tables.
