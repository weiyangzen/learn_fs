# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 43412-46105

## Scope

This chunk is the final portion of `rtw8822c_table.c`. It finishes the `rtw8822c_txpwr_lmt_type5` table and then declares the 8822C DPK/DPD calibration register tables:

- `rtw8822c_txpwr_lmt_type5[]`, completed in this chunk and exported as `rtw8822c_txpwr_lmt_type5_tbl`.
- `rtw8822c_dpk_afe_no_dpk[]`, exported as `rtw8822c_dpk_afe_no_dpk_tbl`.
- `rtw8822c_dpk_afe_is_dpk[]`, exported as `rtw8822c_dpk_afe_is_dpk_tbl`.
- `rtw8822c_dpk_mac_bb[]`, exported as `rtw8822c_dpk_mac_bb_tbl`.
- `rtw8822c_array_mp_cal_init[]`, exported as `rtw8822c_array_mp_cal_init_tbl`.

The file ends at line 46105 after `RTW_DECL_TABLE_PHY_COND(rtw8822c_array_mp_cal_init, rtw_phy_cfg_bb)`.

## Purpose

The visible TX power-limit rows provide board/RFE-specific regulatory cap data for RTL8822C RFE option 5. Each row is a `struct rtw_txpwr_lmt_cfg_pair` tuple of regulatory domain, band, bandwidth, rate section, channel or channel group, and maximum power index. The values include ordinary caps and sentinel-looking `127` entries that preserve the driver's maximum power-index ceiling and effectively indicate unconstrained or placeholder limits for specific combinations.

The DPK tables are hardware register scripts for digital pre-distortion calibration. They configure AFE state before and after DPK, pause or isolate MAC/BB transmit state, program DPD/DPK SRAM windows, and seed the RFK initialization table used during PHY setup. The chunk is table-only code; runtime behavior comes from the generic rtw88 table loaders and from the 8822C calibration functions in `rtw8822c.c`.

## Important APIs, Types, And Macros

`struct rtw_table` is the runtime descriptor that wraps each static array with `.data`, `.size`, `.parse`, optional `.do_cfg`, and `.rf_path`. `rtw_load_table()` calls the descriptor's parser.

`RTW_DECL_TABLE_TXPWR_LMT(rtw8822c_txpwr_lmt_type5)` creates `rtw8822c_txpwr_lmt_type5_tbl` with parser `rtw_parse_tbl_txpwr_lmt`.

`RTW_DECL_TABLE_DPK(...)` is the 8822C-local DPK wrapper. Its parser is `rtw8822c_parse_tbl_dpk()`, which treats the `u32` arrays as repeated triples:

```c
struct dpk_cfg_pair {
	u32 addr;
	u32 bitmask;
	u32 data;
};
```

Each triple becomes `rtw_write32_mask(rtwdev, addr, bitmask, data)`.

`RTW_DECL_TABLE_PHY_COND(rtw8822c_array_mp_cal_init, rtw_phy_cfg_bb)` exports the MP calibration initialization array as a conditional PHY table. Because the data is plain address/data pairs here, `rtw_parse_tbl_phy_cond()` walks it as BB config pairs and calls `rtw_phy_cfg_bb()`. That helper performs delays for pseudo-addresses such as `0xfe` through `0xfa`; otherwise it writes masked/full BB register values through the normal register path.

`rtw8822c_table.h` exposes all exported table descriptors, including the four DPK-related descriptors and the MP calibration-init descriptor in this chunk.

## Control Flow And Integration

For TX power limits, `rtw8822c_rfe_defs` in `rtw8822c.c` selects `RTW_DEF_RFE(8822c, 0, 5, 0)` only for RFE option 5. That macro points `txpwr_lmt_tbl` at `rtw8822c_txpwr_lmt_type5_tbl`. PHY/RFE initialization later loads that table through `rtw_parse_tbl_txpwr_lmt()`, which calls `rtw_phy_set_tx_power_limit()` for every tuple, fills missing regulatory domains from alternatives or world-wide defaults, and then cross-references the limit table with `rtw_xref_txpwr_lmt()`.

For RFK startup, `struct rtw_chip_info rtw8822c_hw_spec` assigns `.rfk_init_tbl = &rtw8822c_array_mp_cal_init_tbl`. Generic PHY table loading invokes `rtw_load_rfk_table()` from `rtw_phy_load_tables()` after AGC/BB/RFE setup and before per-path RF radio tables. The table itself is a long scripted sequence around 0x1b00/0x1b80/0x1b4c/0x1b50/0x1b58/0x1b5c/0x1bd* registers, which appear to select DPD/MP calibration subpages, load LUT entries, and initialize DPD SRAM contents.

For runtime DPK, `rtw8822c_phy_calibration()` calls `rtw8822c_do_dpk()` after GAPK and IQK. The DPK flow:

1. Skips if DPD power is disabled or reloads stored DPK data when the channel matches.
2. Backs up BB and RF registers, including registers modified by the DPK tables.
3. Calls `rtw8822c_dpk_mac_bb_setting()`, which first pauses TX and then loads `rtw8822c_dpk_mac_bb_tbl`.
4. Calls `rtw8822c_dpk_afe_setting(..., true)`, loading `rtw8822c_dpk_afe_is_dpk_tbl`.
5. Runs per-path DPK gain/loss search, one-shot DPK commands, coefficient read/write, and DPK-on sequences.
6. Calls `rtw8822c_dpk_afe_setting(..., false)`, loading `rtw8822c_dpk_afe_no_dpk_tbl`.
7. Restores RF/BB registers and performs RXBB DC calibration.

The DPK tables therefore form only part of a larger stateful calibration transaction; they are bracketed by explicit register backup/restore and by per-path RF writes in `rtw8822c.c`.

## State And Persistence Behavior

The static arrays are immutable compiled-in hardware data. They do not persist state by themselves.

TX power-limit parsing writes into `rtwdev->hal` power-limit structures through `rtw_phy_set_tx_power_limit()` and fallback/cross-reference helpers. That state persists for the driver instance and is used later by transmit power calculations.

DPK runtime state is stored in `rtwdev->dm_info.dpk_info`, including current DPK band/channel/bandwidth, per-path pass bits, DPK TX AGC, coefficients, gain-scaling values, thermal values, and reload flags. The tables in this chunk mutate hardware registers during the calibration window; the DPK code backs up selected BB/RF registers before applying them and restores those registers at the end. Calibration coefficients and per-path result flags persist in driver memory so `rtw8822c_dpk_reload()` can reapply them on the same channel without a full recalibration.

The MP calibration-init table is loaded at PHY initialization as register writes. Its effects persist in hardware registers and DPD/DPK internal memory until reset, reinitialization, or later calibration writes replace them.

## Dependencies

This chunk depends on core rtw88 table infrastructure from `main.h` and `phy.h`, including `struct rtw_table`, `rtw_load_table()`, `RTW_DECL_TABLE_*` macros, `rtw_parse_tbl_phy_cond()`, `rtw_parse_tbl_txpwr_lmt()`, and `rtw_phy_cfg_bb()`.

It depends on 8822C-specific DPK parser support in `rtw8822c.c`: `RTW_DECL_TABLE_DPK` and `rtw8822c_parse_tbl_dpk()`.

It depends on register/mask macros such as `BIT()`, `GENMASK()`, `MASKDWORD`, `MASKBYTE*`, and on register helpers `rtw_write32_mask()`, `rtw_write32()`, `rtw_write8()`, `rtw_read32_mask()`, `rtw_read_rf()`, and `rtw_write_rf()`.

The TX power rows depend on enum value contracts for regulatory domains, bands, bandwidths, rate sections, and channels. There are no named constants in the table body, so tuple field order and enum numbering must remain stable.

## Risks And Edge Cases

The main correctness risk is silent data drift. Most entries are raw register values or numeric tuple fields with no inline semantic names; a one-column shift in `rtw_txpwr_lmt_cfg_pair` rows or a missing `u32` in a DPK triple would still compile but could write wrong limits or wrong hardware registers.

`rtw8822c_array_mp_cal_init[]` is parsed as pairs, while DPK tables are parsed as triples. Accidentally declaring one with the wrong `RTW_DECL_TABLE_*` macro changes how the same raw array is walked and can cause register/value misalignment.

The DPK parser uses `tbl->size / 3`, so a DPK array whose element count is not divisible by three would silently ignore trailing words. The current arrays are intended to be exact triples.

The type5 TX power table is selected only for RFE option 5. If efuse RFE mapping changes or a board is misidentified, this chunk can materially affect regulatory transmit caps. The `127` cap values need to match the driver's `max_power_index` expectations; if that ceiling changes, these rows may need review.

DPK register scripts touch coexistence-sensitive and RF/BB state indirectly through the larger DPK flow. Failures show up as calibration timeout, failed DPK coefficients, reduced transmit quality, or coexistence problems rather than simple compile-time errors.

## Test Signals

Build-level signals:

- The file compiles and `rtw8822c_table.h` extern declarations resolve for `rtw8822c_txpwr_lmt_type5_tbl`, `rtw8822c_dpk_afe_no_dpk_tbl`, `rtw8822c_dpk_afe_is_dpk_tbl`, `rtw8822c_dpk_mac_bb_tbl`, and `rtw8822c_array_mp_cal_init_tbl`.
- Array sizes are nonzero and DPK `u32` element counts remain multiples of three.

Runtime signals:

- With an RTL8822C device using RFE option 5, `rtw_parse_tbl_txpwr_lmt()` should not report unexpected missing regulatory-domain configuration beyond the intended fallback paths, and TX power limits should reflect the type5 rows.
- During PHY init, RFK table loading should complete without register-write faults or hardware-ready timeouts.
- During calibration, `RTW_DBG_RFK` logs should show DPK start/finish per path without repeated "failed to do dpk calibration" or "DPK stuck" warnings.
- DPK reload should trigger only when the current channel matches stored `dpk_info->dpk_ch`, and per-path `dpk_path_ok`, `dpk_txagc`, coefficients, and gain-scaling values should remain coherent across reload.
- RF performance tests should cover 2.4 GHz and 5 GHz, multiple bandwidths including 80 MHz, both RF paths, and RFE option 5 boards because this chunk is dominated by board/RFE-specific power limits and calibration programming.
