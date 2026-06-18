# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.c lines 12321-22204

## Scope

This chunk covers the final 9,884 lines of `rtw8822b_table.c`. It begins in the middle of the RTL8822B RF path A table, completes and exports `rtw8822b_rf_a_tbl`, defines and exports the complete RF path B table, and defines all three RTL8822B transmit-power-limit tables:

- tail of `rtw8822b_rf_a[]`, declared as `rtw8822b_rf_a_tbl` with `RTW_DECL_TABLE_RF_RADIO(rtw8822b_rf_a, A)`
- complete `rtw8822b_rf_b[]`, declared as `rtw8822b_rf_b_tbl` with `RTW_DECL_TABLE_RF_RADIO(rtw8822b_rf_b, B)`
- `rtw8822b_txpwr_lmt_type0[]`, `rtw8822b_txpwr_lmt_type2[]`, and `rtw8822b_txpwr_lmt_type5[]`, each declared as an `rtw_table` with `RTW_DECL_TABLE_TXPWR_LMT`

The chunk is data-heavy and contains no ordinary functions. Runtime behavior is supplied by the shared `rtw88` table framework in `main.h`, `phy.h`, and `phy.c`, and by the RTL8822B chip/RFE selection data in `rtw8822b.c`.

## Purpose

The RF arrays are vendor-provided radio-register recipes for RTL8822B bring-up. They program RF path-specific synthesizer, gain, front-end, and calibration-related registers through the generic PHY conditional-table parser. The path A data in this chunk is only the tail of the full table, so whole-path-A meaning must be merged with the previous chunk. The path B data is complete in this range and mirrors the same conditional register-table style for `RF_PATH_B`.

The transmit-power-limit arrays encode regulatory and board/RFE-specific conducted-power ceilings. RTL8822B has RFE definitions for options 2, 3, and 5 in `rtw8822b.c`; those definitions map to the type2, type0, and type5 power-limit tables respectively. The rows constrain power by regulatory domain, band, channel width, rate section, channel key, and signed limit value before later transmit-power configuration derives hardware power indexes.

## Important APIs, Types, and Data

`struct rtw_table` is the common export shape. It stores a raw data pointer, element count, parser callback, optional per-entry callback, and RF path. The relevant declaration macros are:

- `RTW_DECL_TABLE_RF_RADIO(name, path)`, which expands to a table using `rtw_parse_tbl_phy_cond()`, `rtw_phy_cfg_rf()`, and `RF_PATH_A` or `RF_PATH_B`.
- `RTW_DECL_TABLE_TXPWR_LMT(name)`, which expands to a table using `rtw_parse_tbl_txpwr_lmt()`.

The RF data is stored as `static const u32` address/data pairs with embedded conditional markers. In this chunk, the path-A tail contains thousands of entries over RF registers roughly `0x008-0x0fe`; the complete path-B table contains 3,664 counted RF register entries over 34 distinct RF register numbers, plus more than 400 conditional marker words. Conditional marker values such as `0x83000000`, `0x930000xx`, `0xa0000000`, `0xb0000000`, and `0x40000000` are interpreted by `rtw_parse_tbl_phy_cond()` rather than written as RF registers.

The transmit-power-limit data uses `struct rtw_txpwr_lmt_cfg_pair`:

```c
struct rtw_txpwr_lmt_cfg_pair {
	u8 regd;
	u8 band;
	u8 bw;
	u8 rs;
	u8 ch;
	s8 txpwr_lmt;
};
```

Each of the three limit arrays has 585 rows. Across the three tables there are 1,755 rows total, covering regulatory domains `0`, `1`, and `2`, both 2.4 GHz and 5 GHz bands, channel-width indexes `0`, `1`, and `2`, rate-section indexes `0-5`, and 57 channel keys. Encoded limit values range from `14` through the chip maximum `63`; `63` is significant because `rtw8822b_hw_spec.max_power_index` is `0x3f`.

The exported symbols are declared in `rtw8822b_table.h` as `rtw8822b_rf_a_tbl`, `rtw8822b_rf_b_tbl`, `rtw8822b_txpwr_lmt_type0_tbl`, `rtw8822b_txpwr_lmt_type2_tbl`, and `rtw8822b_txpwr_lmt_type5_tbl`.

## Control Flow

RF table loading is part of PHY parameter setup. `rtw8822b_phy_set_param()` powers on BB/RF domains and calls `rtw_phy_load_tables()`. That loader applies the chip-level MAC, BB, AGC, optional BTG AGC, RFK-init tables, then iterates `rf_path` from zero to `hal.rf_path_num - 1` and loads `chip->rf_tbl[rf_path]`. For RTL8822B, `rtw8822b_hw_spec` assigns `.rf_tbl = { &rtw8822b_rf_a_tbl, &rtw8822b_rf_b_tbl }`.

When an RF table is loaded, `rtw_load_table()` calls `rtw_parse_tbl_phy_cond()`. The parser reads pairs of 32-bit words as `union phy_table_tile` records, evaluates conditional blocks against `hal->phy_cond` and `hal->phy_cond2`, and invokes `rtw_phy_cfg_rf()` only for matched address/data records. `rtw_phy_cfg_rf()` handles RF delay sentinels `0xffe` and `0xfe`; otherwise it writes the value through `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` and waits briefly with `udelay(1)`.

Power-limit loading happens in board information setup, not in the RF bring-up loop. `rtw_chip_board_info_setup()` obtains the selected `struct rtw_rfe_def` with `rtw_get_rfe_def()`, initializes transmit-power storage, loads `rfe_def->phy_pg_tbl`, then loads `rfe_def->txpwr_lmt_tbl`. For RTL8822B, the RFE map is:

- RFE option `2`: `RTW_DEF_RFE(8822b, 2, 2, 0)`, using `rtw8822b_txpwr_lmt_type2_tbl`
- RFE option `3`: `RTW_DEF_RFE(8822b, 3, 0, 0)`, using `rtw8822b_txpwr_lmt_type0_tbl`
- RFE option `5`: `RTW_DEF_RFE(8822b, 5, 5, 0)`, using `rtw8822b_txpwr_lmt_type5_tbl`

`rtw_parse_tbl_txpwr_lmt()` walks every `rtw_txpwr_lmt_cfg_pair`, records which regulatory domains were explicitly configured, and calls `rtw_phy_set_tx_power_limit()`. That helper clamps each limit to `+/-chip->max_power_index`, maps the channel key to an internal channel index, validates regulatory/bandwidth/rate-section indexes, and stores the result in `hal->tx_pwr_limit_2g` or `hal->tx_pwr_limit_5g`. After the table pass, missing regulatory domains inherit an alternative domain if available or world-wide defaults, then `rtw_xref_txpwr_lmt()` cross-fills missing HT/VHT 5 GHz values.

## State and Persistence

The arrays in this chunk are immutable `static const` data. Persistent effects occur only after parser execution:

- RF table entries persist as radio-register state on path A or path B until reset, power transition, RF reinitialization, channel-related radio programming, or calibration code overwrites the same registers.
- Conditional RF entries depend on the current package/cut/interface/RFE condition snapshot prepared by `rtw_phy_setup_phy_cond()`. The same compiled table can therefore program different RF values on different board layouts.
- Power-limit rows persist in software inside `struct rtw_hal`, specifically the 2 GHz and 5 GHz `tx_pwr_limit_*` arrays. Later `rtw_phy_tx_power_limit_config()` and transmit-power calculations consume that state.
- World-wide regulatory entries are tightened while parsing because `rtw_phy_set_tx_power_limit()` keeps the world-wide value as the minimum of explicit limits for that band/width/rate/channel.
- The source chunk ends at the file end, so all declarations started here are complete. Only path A requires previous-chunk context because this chunk starts inside its array.

## Dependencies and Integration Points

This source depends on the shared `rtw88` infrastructure:

- `main.h` defines `struct rtw_table`, `struct rtw_rfe_def`, `rtw_load_table()`, RF path constants, chip-info fields, and HAL power-limit storage.
- `phy.h` defines `struct rtw_txpwr_lmt_cfg_pair` and the table declaration macros.
- `phy.c` implements `rtw_parse_tbl_phy_cond()`, `rtw_phy_cfg_rf()`, `rtw_parse_tbl_txpwr_lmt()`, `rtw_phy_set_tx_power_limit()`, and `rtw_phy_load_tables()`.
- `rtw8822b_table.h` exposes the table symbols to the chip implementation.
- `rtw8822b.c` wires these objects into `rtw8822b_hw_spec` and `rtw8822b_rfe_defs`.

The RF tables integrate with hardware through `rtw_write_rf()` and `RFREG_MASK`. The power-limit tables integrate with regulatory-domain handling, efuse RFE option decoding, rate-section indexes, channel-index mapping, and the later transmit-power-by-rate and transmit-power-limit configuration paths.

## Risks

- The RF arrays use an implicit two-word table language. Any missing or extra `u32` can misalign subsequent records and either skip required programming or write wrong RF registers.
- Conditional markers look like ordinary constants. Changing parser semantics or declaring the RF arrays with the wrong macro would turn branch metadata into invalid writes.
- The chunk begins in the middle of `rtw8822b_rf_a[]`; reviewing this chunk alone cannot validate the full path-A conditional structure or entry count.
- RF path correctness is path-sensitive. Accidentally binding the path-B data to `RF_PATH_A`, or vice versa, would program the wrong radio chain.
- Power-limit rows are regulatory-sensitive. Incorrect `regd`, `band`, `bw`, `rs`, `ch`, or `txpwr_lmt` fields can reduce range and throughput or exceed allowed conducted power.
- RFE selection is sparse. RTL8822B defines entries for RFE options 2, 3, and 5; unsupported or misread efuse `rfe_option` values cause `rtw_get_rfe_def()`/board setup failure rather than falling back to an arbitrary table.
- Limit value `63` often means the maximum/default ceiling. Treating it as a special sentinel outside the existing parser would be risky; the current code stores it as a normal clamped maximum and uses separate xref logic for missing HT/VHT values.
- These tables appear generated from vendor data. Semantic review is hard, so safe edits need structural validation and hardware evidence.

## Test and Validation Signals

Useful validation is a mix of build-time symbol checks, structural table checks, and RTL8822B hardware testing:

- Compile coverage should confirm the table exports declared in `rtw8822b_table.h` are defined exactly once and consumed by `rtw8822b.c`.
- Static checks should verify RF `u32` arrays have even element counts and that conditional branch records remain structurally balanced for `rtw_parse_tbl_phy_cond()`.
- RF bring-up logs or register traces should confirm both `rtw8822b_rf_a_tbl` and `rtw8822b_rf_b_tbl` load when `hal.rf_path_num` is two, and that writes target the expected RF path.
- Probe tests should exercise each supported RFE option, especially 2, 3, and 5, and verify that `rtw_chip_board_info_setup()` selects the matching power-group and power-limit tables.
- Transmit-power validation should cover 2.4 GHz and 5 GHz channels, 20/40/80 MHz widths, HT/VHT rate sections, and one-/two-stream modes for every supported RFE table.
- Regulatory debug output from `RTW_DBG_REGD` can reveal missing-domain fallback behavior in `rtw_parse_tbl_txpwr_lmt()`.
- Conducted RF tests should compare measured output power against expected limits, with attention to rows using the maximum value `63` and rows that differ between type0, type2, and type5.
- Regression tests should compare RF register traces before and after any table changes because ordinary unit tests cannot prove these vendor constants are electrically correct.
