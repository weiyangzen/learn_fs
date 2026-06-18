# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822b_table.c lines 1-12320

## Scope

This chunk covers the beginning of the Realtek `rtw88` RTL8822B table source. It includes the file header and includes, the complete MAC initialization table, the complete AGC table, the complete baseband table, all three RTL8822B RFE-specific baseband power-by-rate tables (`type2`, `type3`, and `type5`), and the beginning of RF path A initialization data. The RF path A table starts at line 11799 and continues past this chunk; RF path B and transmit-power-limit tables are outside this range and must be reconciled by later chunk reports.

The code in this range is almost entirely static calibration and register-programming data. Runtime behavior comes from shared `rtw88` table loaders in `main.h`, `phy.h`, and `phy.c`, plus the RTL8822B chip descriptor in `rtw8822b.c`.

## Purpose

The tables provide the hardware bring-up constants for RTL8822B devices:

- `rtw8822b_mac[]` is a compact list of byte-sized MAC register writes used during chip initialization.
- `rtw8822b_agc[]` programs automatic gain control tables and related gain/RSSI behavior through repeated writes, mainly to AGC/BB register windows such as `0x81c`, with many conditional branches for RFE options.
- `rtw8822b_bb[]` programs baseband register defaults, PHY timing, thresholds, digital front-end parameters, and large table-window payloads through addresses such as `0x800` onward and dense repeated writes to `0x1b80`.
- `rtw8822b_bb_pg_type2[]`, `rtw8822b_bb_pg_type3[]`, and `rtw8822b_bb_pg_type5[]` store per-band, per-RF-path, and per-transmit-chain power-by-rate offsets for different board/RFE definitions.
- `rtw8822b_rf_a[]` starts RF path A radio-register initialization, including conditional path- and RFE-dependent values for synthesizer/front-end registers.

These tables separate vendor-provided register recipes from driver control code. The driver can select and parse a table generically while chip-specific constants remain in this generated-style source file.

## Important APIs, Types, and Data

The central exported objects produced by this chunk are `const struct rtw_table` instances created by declaration macros:

- `RTW_DECL_TABLE_PHY_COND(rtw8822b_mac, rtw_phy_cfg_mac)` exports `rtw8822b_mac_tbl`.
- `RTW_DECL_TABLE_PHY_COND(rtw8822b_agc, rtw_phy_cfg_agc)` exports `rtw8822b_agc_tbl`.
- `RTW_DECL_TABLE_PHY_COND(rtw8822b_bb, rtw_phy_cfg_bb)` exports `rtw8822b_bb_tbl`.
- `RTW_DECL_TABLE_BB_PG(rtw8822b_bb_pg_type2)`, `type3`, and `type5` export the RFE-specific power-by-rate tables.

`struct rtw_table` carries the raw data pointer, element count, parser callback, optional per-entry config callback, and RF path. For MAC/AGC/BB/RF tables, `RTW_DECL_TABLE_PHY_COND_CORE` stores the raw `u32` array and uses `rtw_parse_tbl_phy_cond()`. That parser treats the data as `union phy_table_tile` records, where normal address/data records call `tbl->do_cfg()` and high-bit marker records encode IF/ELIF/ELSE/ENDIF-style hardware conditions.

The important parser/config callbacks are:

- `rtw_parse_tbl_phy_cond()` evaluates condition markers against `hal->phy_cond` and `hal->phy_cond2`, then dispatches matching entries.
- `rtw_phy_cfg_mac()` writes MAC entries with `rtw_write8()`.
- `rtw_phy_cfg_agc()` writes AGC entries with `rtw_write32()`.
- `rtw_phy_cfg_bb()` writes BB entries with `rtw_write32()`, but treats sentinel addresses `0xfe`, `0xfd`, `0xfc`, `0xfb`, `0xfa`, and `0xf9` as delays.
- `rtw_phy_cfg_rf()` is used for RF tables such as the partial `rtw8822b_rf_a[]`; it writes `RFREG_MASK` radio values via `rtw_write_rf()` and treats RF sentinel addresses as delays.
- `rtw_parse_tbl_bb_pg()` consumes `struct rtw_phy_pg_cfg_pair` arrays and stores power-by-rate offsets with `rtw_phy_store_tx_power_by_rate()`.

The three power-group arrays use `struct rtw_phy_pg_cfg_pair` fields `{ band, rf_path, tx_num, addr, bitmask, data }`. The rows in this chunk cover both bands (`0` and `1`), both RF paths (`0` and `1`), and one- or two-stream transmit-chain groups (`tx_num` values `0` and `1`) for BB registers around `0x0c20-0x0c4c` and `0x0e20-0x0e4c`.

## Control Flow

The table load path is generic:

1. Device setup calls `rtw_phy_setup_phy_cond()`, which snapshots package, cut, platform, interface type, and efuse/RFE option into `rtwdev->hal`.
2. `rtw_phy_load_tables()` loads the chip-level `mac_tbl`, `bb_tbl`, and `agc_tbl`; then it loads RF tables for each active RF path.
3. Each `rtw_load_table()` calls the table's parser. For the MAC/AGC/BB tables in this chunk, `rtw_parse_tbl_phy_cond()` walks pairs of 32-bit words, evaluates conditional markers, and applies matching address/data records through the table-specific config callback.
4. TX-power setup later obtains the selected `struct rtw_rfe_def` with `rtw_get_rfe_def()` and loads `rfe_def->phy_pg_tbl`; for RTL8822B that points to one of the `rtw8822b_bb_pg_type*` tables declared here.

The conditional table language is important for this file. Markers such as `0x80000000`, `0x900000xx`, `0xa0000000`, and `0xb0000000` are not register writes. They form condition blocks whose positive/negative records are compared with the current cut/package/interface/RFE state. Only matched records are written. This is why the AGC and RF data contain many repeated address writes for different RFE options.

Within this chunk, data flow transitions are:

- Lines 9-137: MAC register/value pairs and export of `rtw8822b_mac_tbl`.
- Lines 139-10147: AGC conditional PHY table and export of `rtw8822b_agc_tbl`.
- Lines 10149-11644: BB conditional PHY table and export of `rtw8822b_bb_tbl`.
- Lines 11646-11797: three BB power-by-rate tables and their `struct rtw_table` exports.
- Lines 11799-12320: beginning of the conditional RF path A table; the table is incomplete at the chunk boundary.

## State and Persistence

The arrays themselves are `static const` and have no mutable state. Persistence occurs when shared parsers apply them:

- MAC, AGC, BB, and RF entries persist as hardware register state until reset, power transition, channel/radio reconfiguration, another table load, or later calibration code overwrites those registers.
- Conditional parsing depends on current `hal->phy_cond` and efuse-derived `rfe_option`; the same static table can therefore produce different hardware state on different board layouts or interfaces.
- BB power-group rows do not immediately write hardware registers. They populate software power-by-rate storage in `struct rtw_hal` through `rtw_phy_store_tx_power_by_rate()`. Later `rtw_phy_tx_power_by_rate_config()` and transmit-power index calculations use that persisted software state when configuring actual transmit power.
- The RF path A data starts in this chunk but is not a complete persistence unit here. A loader would only see the full `rtw8822b_rf_a[]` at compile time; research for this chunk should avoid treating lines 11799-12320 as the whole RF path A recipe.

## Dependencies and Integration Points

This source depends on `main.h`, `phy.h`, and `rtw8822b_table.h`. The header declares all exported RTL8822B table objects consumed by the chip descriptor.

The main integration point is `rtw8822b.c`, where the RTL8822B `struct rtw_chip_info` assigns:

- `.mac_tbl = &rtw8822b_mac_tbl`
- `.agc_tbl = &rtw8822b_agc_tbl`
- `.bb_tbl = &rtw8822b_bb_tbl`
- `.rf_tbl = { &rtw8822b_rf_a_tbl, &rtw8822b_rf_b_tbl }`
- `.rfe_defs = rtw8822b_rfe_defs`

The RFE definitions connect board variants to the `bb_pg_type2`, `bb_pg_type3`, and `bb_pg_type5` tables in this file, along with transmit-power-limit and power-tracking tables defined elsewhere in the same source file or companion chip code.

The lower-level hardware dependencies are `rtw_write8()`, `rtw_write32()`, `rtw_write_rf()`, RF path numbering, register masks, efuse parsing, HCI type detection, and the `rtw88` transmit-power model. Invalid table contents can affect MAC bring-up, AGC behavior, baseband receive/transmit quality, RF path state, and regulatory transmit-power behavior.

## Risks

- The table format is implicit and fragile. A single inserted or removed 32-bit word can desynchronize address/data pairing or condition records for thousands of following entries.
- Conditional markers resemble data values. Treating high-bit marker records as register writes, or changing parser semantics, would program nonsensical addresses and break hardware initialization.
- RFE selection is safety-critical. If efuse `rfe_option`, package, cut, or interface conditions are wrong, the parser may apply gain, RF, or power-by-rate constants intended for a different board front end.
- The MAC table uses byte writes while AGC/BB use 32-bit writes and RF uses radio-register writes. Moving an array to the wrong declaration macro would change access width and target bus.
- BB delay sentinels are meaningful only through `rtw_phy_cfg_bb()`. Converting them to raw writes or dropping delays can violate PHY sequencing requirements.
- Power-by-rate data affects conducted output power. Bad `band`, `rf_path`, `tx_num`, address, mask, or packed offset values can cause poor throughput, unstable rate control, or regulatory power-limit violations.
- The chunk boundary occurs inside `rtw8822b_rf_a[]`; any final report must merge with later chunks before making complete statements about RF path A initialization.
- The source appears generated from vendor tables. Manual edits are hard to review by semantic inspection, so regressions may only be visible on hardware or through table-shape validation.

## Test and Validation Signals

Useful validation for this chunk is mostly structural plus hardware bring-up:

- Build coverage should ensure all exported table symbols from this chunk match `rtw8822b_table.h` and the `rtw8822b.c` chip descriptor.
- Static table checks should verify that MAC/AGC/BB/RF conditional arrays have even `u32` element counts and that branch marker pairs remain balanced enough for `rtw_parse_tbl_phy_cond()`.
- Parser instrumentation or debug logs around `rtw_phy_setup_phy_cond()` and `rtw_parse_tbl_phy_cond()` can confirm the expected RFE/cut/interface branches are selected for representative PCIe, USB, and SDIO devices.
- Probe/init tests on RTL8822B hardware should confirm `rtw_phy_load_tables()` completes without unsupported RF-path errors, failed RF writes, or early device bring-up failures.
- RF tests should verify both paths are initialized when `hal.rf_path_num` is 2; this chunk only starts RF path A, so path-level validation must include later chunks.
- Receive sensitivity and RSSI tests across 2.4 GHz and 5 GHz channels are good signals for AGC and BB table correctness.
- Conducted transmit-power tests across bands, RF paths, and one-/two-stream rates should validate the `bb_pg_type2`, `type3`, and `type5` power-by-rate tables selected by each RFE definition.
- Regression tests should compare register traces before and after table changes, with special attention to conditional branches and delay sentinels.
