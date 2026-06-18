# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.c lines 33743-43411

## Scope

This chunk covers a large static-data region in the Realtek `rtw88` RTL8822C table file. It begins in the late portion of the `rtw8822c_rf_b[]` radio-path-B programming script, includes the end of that array and its `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)` wrapper, then contains the complete `rtw8822c_txpwr_lmt_type0[]` table and the first large portion of `rtw8822c_txpwr_lmt_type5[]`.

The range is not algorithmic C code. It is vendor-derived PHY/RF configuration data consumed by generic `rtw88` table parsers. The beginning is mid-array and the ending is mid-array, so the complete RF-B script and complete type-5 power-limit table require adjacent chunks during merge.

## Purpose

The RF-B portion supplies conditional RF register writes for RTL8822C radio path B. The values are interpreted as address/data pairs plus condition opcodes by `rtw_parse_tbl_phy_cond()`, then applied through `rtw_phy_cfg_rf()`. In this chunk the RF script repeatedly programs RF registers such as `0x033`, `0x03f`, `0x051`, `0x052`, `0x092`, `0x08f`, `0x088`, `0x019`, and `0x0ef`, with conditional branch markers such as `0x8f000000`, `0x9f000001`, `0x91...`, `0x92...`, `0x93...`, `0x94...`, `0x95...`, `0xa0000000`, and `0xb0000000`. These encode hardware-package, interface, board, and RFE-dependent RF initialization branches.

The power-limit portions provide regulatory and board-variant transmit-power ceilings. Each `struct rtw_txpwr_lmt_cfg_pair` row is `{ regd, band, bw, rs, ch, txpwr_lmt }`, where `regd` indexes `RTW_REGD_*`, `band` selects 2.4 GHz or 5 GHz PHY band, `bw` uses `RTW_CHANNEL_WIDTH_*`, `rs` uses rate sections such as CCK, OFDM, HT, and VHT, `ch` is the channel or 5 GHz center-channel bucket, and `txpwr_lmt` is a signed power-index limit. Many rows use `127`, which matches the initialized maximum-power sentinel and effectively means no table-specific tightening after clamping.

`rtw8822c_txpwr_lmt_type0[]` is the default RTL8822C RFE power-limit profile used by RFE definitions 0, 1, 2, 3, 4, and 6. `rtw8822c_txpwr_lmt_type5[]` is the alternate profile used by RFE definition 5; this chunk covers its 2.4 GHz and early 5 GHz entries but stops before the array is complete.

## Important APIs, Types, and Data

Important data and wrappers in this range:

- `rtw8822c_rf_b[]`: `u32` conditional PHY/RF table for radio path B. This chunk contains the latter part of the array and its closing declaration.
- `RTW_DECL_TABLE_RF_RADIO(rtw8822c_rf_b, B)`: creates `rtw8822c_rf_b_tbl` with `.parse = rtw_parse_tbl_phy_cond`, `.do_cfg = rtw_phy_cfg_rf`, and `.rf_path = RF_PATH_B`.
- `rtw8822c_txpwr_lmt_type0[]`: complete `struct rtw_txpwr_lmt_cfg_pair` table covering multiple regulatory domains, both bands, 20/40/80 MHz-style width indices, CCK/OFDM/HT/VHT sections, and 2.4/5 GHz channels.
- `RTW_DECL_TABLE_TXPWR_LMT(rtw8822c_txpwr_lmt_type0)`: creates `rtw8822c_txpwr_lmt_type0_tbl` with `.parse = rtw_parse_tbl_txpwr_lmt`.
- `rtw8822c_txpwr_lmt_type5[]`: alternate RFE-5 power-limit table. The chunk starts the array but does not include its wrapper or final entries.

The key shared types are `struct rtw_table`, `struct rtw_txpwr_lmt_cfg_pair`, and the PHY table pair/condition union used by `rtw_parse_tbl_phy_cond()`. The table declarations are exposed through `rtw8822c_table.h` and selected by `rtw8822c.c`.

## Control Flow

RF table load flow:

1. RTL8822C chip setup stores RF table pointers in `rtw8822c_hw_spec.rf_tbl`.
2. Generic PHY bring-up calls `rtw_load_table(rtwdev, tbl)`.
3. `rtw_parse_tbl_phy_cond()` walks the `u32` RF table as condition/config tiles, evaluates positive and negative condition markers, and calls the table's `do_cfg` only for matched branches.
4. For `rtw8822c_rf_b_tbl`, `rtw_phy_cfg_rf()` writes matched address/data pairs to RF path B with `rtw_write_rf()`. It treats `0xffe` and `0xfe` as delay pseudo-registers.

Power-limit table load flow:

1. `rtw8822c_rfe_defs[]` chooses an RFE definition from efuse/RFE state. Entries 0, 1, 2, 3, 4, and 6 use type 0; entry 5 uses type 5.
2. Main initialization loads the selected `rfe_def->txpwr_lmt_tbl`.
3. `rtw_parse_tbl_txpwr_lmt()` iterates every tuple, records which regulatory domains were configured, and calls `rtw_phy_set_tx_power_limit()`.
4. `rtw_phy_set_tx_power_limit()` clamps the signed limit to the chip maximum, maps the channel to a 2G/5G channel index, stores it in `hal->tx_pwr_limit_2g` or `hal->tx_pwr_limit_5g`, and keeps the world-wide domain as the minimum of configured limits.
5. After parsing, missing regulatory domains are filled from an alternative domain or from `RTW_REGD_WW`; 5 GHz HT/VHT gaps are cross-referenced.
6. Later transmit-power index calculation calls `rtw_phy_get_tx_power_limit()` and combines the chosen limit with efuse base power, per-rate offset, remnant tracking, and SAR before writing TXAGC.

## State and Persistence

The arrays in this chunk are `static const`; they do not mutate at runtime. Their effects persist in two places:

- RF-B register writes persist in hardware until another RF table load, channel switch, calibration routine, power transition, or reset rewrites those RF registers.
- Parsed power limits persist in `struct rtw_hal` arrays `tx_pwr_limit_2g` and `tx_pwr_limit_5g`. These arrays are initialized to the chip maximum, then tightened by loaded table rows and used for later per-rate/per-channel transmit-power decisions.

The selected power-limit profile is board/RFE state dependent. RFE option 5 gets a different type-5 regulatory matrix than the default type-0 matrix, so efuse parsing and RFE definition selection are part of the persistent behavior even though this file only contains constants.

## Dependencies and Integration Points

This chunk depends on the `rtw88` PHY table framework in `phy.h`, `main.h`, and `phy.c`:

- `RTW_DECL_TABLE_RF_RADIO` and `RTW_DECL_TABLE_TXPWR_LMT` wrap raw arrays as `struct rtw_table` descriptors.
- `rtw_load_table()` dispatches through the descriptor parser.
- `rtw_parse_tbl_phy_cond()` interprets condition markers embedded in RF scripts.
- `rtw_phy_cfg_rf()` writes RF registers for the configured path.
- `rtw_parse_tbl_txpwr_lmt()` and `rtw_phy_set_tx_power_limit()` translate table tuples into the HAL transmit-power-limit matrices.

The chunk integrates with RTL8822C chip setup in `rtw8822c.c`: `rtw8822c_hw_spec.rf_tbl` references `rtw8822c_rf_b_tbl`, and `rtw8822c_rfe_defs[]` chooses `rtw8822c_txpwr_lmt_type0_tbl` or `rtw8822c_txpwr_lmt_type5_tbl`. It also integrates with regulatory-domain handling, efuse/RFE option discovery, channel/bandwidth selection, rate-section mapping, SAR handling, and TX power programming.

## Risks

- The RF script is opaque and sequencing-sensitive. The conditional markers, delays, and register writes must remain paired exactly as generated; deleting or moving one value can desynchronize the parser and write incorrect RF registers.
- The chunk begins in the middle of `rtw8822c_rf_b[]`, so any local-only review can miss the condition state that led into line 33743. Merge-stage research should describe the full RF-B script using adjacent chunks.
- Power-limit tuple field order is positional. Swapping `band`, `bw`, `rs`, `ch`, or `txpwr_lmt` compiles cleanly but silently corrupts regulatory behavior.
- Regulatory risk is high. These limits feed final TX power decisions; incorrect values can underpower links, violate regional limits, or interact badly with SAR reductions and efuse power offsets.
- `127` entries depend on chip maximum clamping and initialization semantics. Treating them as literal restrictive limits or changing `max_power_index` behavior would alter many rows at once.
- Type 5 is incomplete in this chunk. Final conclusions about RFE-5 limits must include lines after 43411 through the table wrapper.
- There are no semantic checks that every meaningful combination is present. The parser only warns on invalid indexes, then fills missing regulatory domains from alternatives or `WW`; missing rows can therefore become broad fallback behavior.

## Test and Validation Signals

Useful validation is mostly hardware and driver-integration oriented:

- Build tests should catch table syntax, missing wrappers, or broken extern declarations in `rtw8822c_table.h`.
- Probe/init logs on RTL8822C hardware should show successful RF table loading with no PHY/RF table parser warnings or RF access failures.
- RFE-option coverage should test default RFE options and RFE option 5 to confirm the selected `txpwr_lmt_type0` or `txpwr_lmt_type5` table is loaded.
- Regulatory-domain tests should exercise FCC, MKK, ETSI, IC, KCC, ACMA, Chile, Mexico, CN, Qatar, UK, and WW fallback paths, watching for `"wrong txpwr_lmt"` and `"txpwr regd ... does not be configured"` debug messages.
- Channel/rate tests should verify 2.4 GHz channels 1-14 and 5 GHz channel groups across 20/40/80 MHz operation, CCK/OFDM/HT/VHT sections, and both RF paths where applicable.
- Conducted-power or calibrated radiated-power measurements should compare final TXAGC-derived output against expected regulatory caps for type 0 and type 5 boards.
- Regression tests should include channel changes and suspend/resume because RF register state from the RF-B script and parsed HAL power matrices must survive normal initialization flows and be refreshed after reset-like transitions.
