# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.c lines 8988-14916

## Scope

This chunk is the tail of the RTW89 8851B static table file. It begins in the final entries of the default 5 GHz RU transmit-power limit table, then defines the type-2 RFE transmit-power limit tables, the exported PHY table descriptors, the by-rate power table bundles, the thermal tracking table bundle, and the RFE parameter selection table used by the 8851B chip definition.

## Purpose

The code is almost entirely immutable calibration and regulatory data. It supplies compiled-in fallback data for Realtek RTL8851B hardware when firmware-provided RFE data is absent or incomplete. The tables encode:

- Regulatory transmit-power caps by band, bandwidth, transmit chain count, rate section, beamforming mode, regulatory domain, and channel index.
- HE/OFDMA RU-specific transmit-power caps for 2.4 GHz and 5 GHz.
- Register-table descriptors for BB, BB gain, RF path A, and NCTL initialization.
- By-rate power table descriptors for default and RFE type 2 variants.
- Thermal tracking delta-swing tables for path A.
- RFE parameter structures that connect all of the above into the core `rtw89_rfe_parms` contract.

## Important APIs, Types, and Symbols

- `rtw89_8851b_txpwr_lmt_2g_type2`: static 2.4 GHz type-2 limit table with dimensions `RTW89_2G_BW_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_REGD_NUM`, and `RTW89_2G_CH_NUM`.
- `rtw89_8851b_txpwr_lmt_5g_type2`: static 5 GHz type-2 limit table with analogous dimensions using `RTW89_5G_BW_NUM` and `RTW89_5G_CH_NUM`.
- `rtw89_8851b_txpwr_lmt_ru_2g_type2`: static type-2 2.4 GHz RU power table indexed by `RTW89_RU_NUM`, `RTW89_NTX_NUM`, regulatory domain, and 2 GHz channel index.
- `rtw89_8851b_txpwr_lmt_ru_5g_type2`: static type-2 5 GHz RU power table indexed by RU, transmit-chain count, regulatory domain, and 5 GHz channel index.
- `rtw89_8851b_phy_bb_table`, `rtw89_8851b_phy_bb_gain_table`, `rtw89_8851b_phy_radioa_table`, `rtw89_8851b_phy_nctl_table`: exported `struct rtw89_phy_table` descriptors. Each points to an earlier register array, its `ARRAY_SIZE()`, and the loader callback (`rtw89_phy_config_bb_reg`, `rtw89_phy_config_bb_gain_reg`, `rtw89_phy_config_rf_reg`, or `rtw89_phy_config_nctl_reg`).
- `rtw89_8851b_byr_table`: static `struct rtw89_txpwr_table` over `_txpwr_byrate` with `rtw89_phy_load_txpwr_byrate`.
- `rtw89_8851b_byr_table_type2`: static `struct rtw89_txpwr_table` over `_txpwr_byrate_type2`.
- `rtw89_8851b_trk_cfg`: exported `struct rtw89_txpwr_track_cfg` linking 5 GHz and 2.4 GHz path-A delta-swing tables, including CCK-specific 2.4 GHz entries.
- `rtw89_8851b_dflt_parms`: exported default `struct rtw89_rfe_parms` using the default by-rate table and default 2 GHz/5 GHz limit/RU tables.
- `rtw89_8851b_rfe_parms_type2`: static RFE type-2 `struct rtw89_rfe_parms` using the type-2 by-rate, 2 GHz, 5 GHz, and RU limit tables from this chunk.
- `rtw89_8851b_rfe_parms_conf`: exported sentinel-terminated `struct rtw89_rfe_parms_conf[]` mapping efuse `rfe_type == 2` to `rtw89_8851b_rfe_parms_type2`.

The matching declarations for the exported symbols live in `rtw8851b_table.h`. `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, `struct rtw89_rfe_parms`, and `struct rtw89_rfe_parms_conf` are defined in `core.h`; `struct rtw89_txpwr_track_cfg` is defined in `phy.h`.

## Control Flow and Runtime Integration

There is no executable control flow inside this chunk beyond static initializers. Runtime flow enters through consumers:

- `rtw8851b.c` wires the exported PHY table descriptors and RFE parameter tables into the 8851B `rtw89_chip_info` instance. The chip info fields `.bb_table`, `.bb_gain_table`, `.rf_table`, `.nctl_table`, `.dflt_parms`, and `.rfe_parms_conf` point at symbols defined here.
- During device setup, `rtw89_core_setup_rfe_parms()` reads the efuse RFE type. If the type matches an entry in `rtw89_8851b_rfe_parms_conf`, type-2 parameters are selected; otherwise the default parameters are used.
- `rtw89_core_setup_rfe_parms()` then calls `rtw89_load_rfe_data_from_fw()`, allowing firmware RFE tables to override by-rate, limit, RU, and TX-shape pointers. After selection/override, `rtw89_load_txpwr_table()` loads the chosen by-rate table into `rtwdev->byr`.
- `rtw89_phy_read_txpwr_limit()` indexes the selected `rtwdev->rfe_parms` 2 GHz or 5 GHz limit table by bandwidth, NTX, rate section, BF mode, regulatory domain, and channel index. If the specific regulatory-domain entry is zero, it falls back to `RTW89_WW`.
- `rtw89_phy_read_txpwr_limit_ru()` does the same for RU tables. Both power-limit paths clamp table results with SAR and TPE constraints and apply antenna-gain handling when dynamic antenna tables are present.
- The PHY table descriptors are consumed by generic PHY initialization helpers in `phy.c`, which iterate register arrays and call the descriptor-specific config callback.
- `rtw89_8851b_rfk.c` uses `rtw89_8851b_trk_cfg` to select positive/negative thermal swing deltas for 2.4 GHz and 5 GHz path-A tracking.

## State and Persistence Behavior

The tables are `const` or `static const` storage and persist for the lifetime of the loaded driver/module. They are not mutated directly. Runtime state is derived from them:

- By-rate values are copied into `rtwdev->byr` by the selected table loader.
- The selected RFE parameter pointer is stored in `rtwdev->rfe_parms`.
- Firmware-loaded RFE data can replace selected pointers with mutable data in `rtwdev->rfe_data`, but the compiled tables remain the fallback.
- Regulatory domain, channel, SAR, TPE, and antenna-gain state determine which entries are read and how results are clamped at runtime.

Sparse zero-initialized entries are meaningful: `rtw89_phy_read_txpwr_limit()` treats zero as missing for the primary regulatory domain lookup and falls back to the worldwide table. Value `127` appears throughout the data as a permissive/no-effective-limit sentinel in this driver family, so consumers must preserve signed 8-bit semantics and not treat every nonzero value as a literal small dBm cap without conversion.

## Dependencies

This chunk depends on earlier arrays in the same file:

- Register arrays such as `_bb_table`, `_bb_gain_table`, `_radioa_table`, and `_nctl_table`.
- By-rate arrays `_txpwr_byrate` and `_txpwr_byrate_type2`.
- TX-shape tables `rtw89_8851b_tx_shape_lmt` and `rtw89_8851b_tx_shape_lmt_ru`.
- Default power-limit/RU tables defined before this chunk.
- Thermal delta arrays such as `_txpwr_track_delta_swingidx_5ga_*`, `_txpwr_track_delta_swingidx_2ga_*`, and `_txpwr_track_delta_swingidx_2g_cck_a_*`.

It also depends on shared RTW89 constants and enums from `core.h`, including rate sections (`RTW89_RS_CCK`, `RTW89_RS_OFDM`, `RTW89_RS_MCS`), regulatory domains (`RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`), bandwidth counts, channel counts, RU counts, and BF/NTX dimensions.

## Risks and Maintenance Notes

- Table dimension drift is the main correctness risk. If `RTW89_*_NUM` constants change, every initializer index must remain within bounds and the semantic channel mapping in `rtw89_channel_to_idx()` must still match the table layout.
- Regulatory errors are high impact. A wrong value can under-limit performance or over-limit transmission beyond domain constraints. The type-2 tables should be reviewed against vendor/regulatory source data, especially values for `RTW89_FCC`, `RTW89_ETSI`, `RTW89_CN`, and DFS/UNII channel groups.
- Sparse initializer semantics are subtle. Zero means missing/fallback in non-RU limit reads, while `127` commonly means effectively unrestricted. Mechanical rewrites must preserve zeros and sentinels exactly.
- RFE selection depends on efuse `rfe_type`. If a board variant uses type 2 but efuse data is wrong or missing, the driver falls back to `rtw89_8851b_dflt_parms`, changing by-rate and power-limit behavior.
- Firmware RFE loading can override these compiled tables. Debugging field behavior must account for `rtwdev->rfe_data` and not assume the static arrays are always active.
- The chunk ends the file and exports externally visible symbols. Linkage mistakes, missing declarations, or accidental `static` changes on exported objects would break the 8851B chip-info wiring.

## Test Signals

- Build the RTW89 driver with warnings enabled; compiler array-bound checks and type mismatches are the first signal for dimension or linkage errors in these large designated initializers.
- Exercise RTL8851B probe/init and verify BB, BB gain, RF path A, and NCTL table loading reaches the expected `rtw89_phy_config_*` callbacks.
- Test boards with default and RFE type-2 efuse configurations; confirm `rtw89_core_setup_rfe_parms()` selects the expected `rtw89_rfe_parms` and that firmware RFE override paths still work when RFE blobs are present.
- Validate transmit power on representative 2.4 GHz channels 1, 6, 11, 13/14 and 5 GHz UNII/DFS groups under multiple regulatory domains.
- Exercise HE/OFDMA RU transmit paths to cover `rtw89_phy_read_txpwr_limit_ru()` and the RU tables, not only legacy/HT/VHT/HE-MCS non-RU paths.
- Run thermal tracking/RFK scenarios on 2.4 GHz CCK and 5 GHz channels to confirm `rtw89_8851b_trk_cfg` points to path-A delta tables with plausible up/down swing behavior.
