# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 57137-57159

## Scope And Purpose

This chunk is the final exported data section of the RTL8852C table file. It closes the `RTW89_TSSI_BANDEDGE_HIGH` row of `rtw89_8852c_tssi_dbw_table` and defines `rtw89_8852c_dflt_parms`, the default radio front-end parameter bundle for the 8852C chip.

The code is table-driven rather than procedural. Its purpose is to bind previously declared 8852C transmit-power tables into the common rtw89 core contract: by-rate power loading, per-band regulatory power limits for 2 GHz, 5 GHz, and 6 GHz, RU-specific power limits for OFDMA, and TX-shape limit tables used when programming band-edge/TSSI behavior. These objects are immutable `const` data and are exported through `rtw8852c_table.h` for the 8852C chip descriptor in `rtw8852c.c`.

## Important APIs, Types, And Data

`rtw89_8852c_tssi_dbw_table` is a `struct rtw89_phy_tssi_dbw_table`, whose shape is `u32 data[RTW89_TSSI_CFG_NUM][RTW89_TSSI_SBW_NUM]`. The specific visible lines complete the `RTW89_TSSI_BANDEDGE_HIGH` profile with 15 sub-band width entries. The full table also includes flat, low, and mid band-edge profiles just above this chunk.

`rtw89_8852c_dflt_parms` is a `struct rtw89_rfe_parms`. The fields populated here are:

- `byr_tbl`: points at `rtw89_8852c_byr_table`, a `struct rtw89_txpwr_table` wrapper around the 8852C by-rate power data and the `rtw89_phy_load_txpwr_byrate` loader.
- `rule_2ghz`, `rule_5ghz`, `rule_6ghz`: each binds normal channel-width power-limit tables through `.lmt` and RU/OFDMA power-limit tables through `.lmt_ru`.
- `tx_shape`: binds `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru`.

The `struct rtw89_rfe_parms` definition also supports dedicated-antenna rules and a `has_da` flag, but this default 8852C initializer leaves those zeroed. That matters because common PHY code checks `has_da` before consulting dedicated-antenna power tables.

## Control Flow And Integration

The chunk itself has no branches or calls. Runtime flow enters through the chip descriptor in `rtw8852c.c`, where `.dflt_parms = &rtw89_8852c_dflt_parms` and `.tssi_dbw_table = &rtw89_8852c_tssi_dbw_table`.

During device setup, `rtw89_core_setup_rfe_parms()` selects the RFE parameters. For RTL8852C, `rfe_parms_conf` is `NULL`, so the core selects `chip->dflt_parms`. It then calls `rtw89_load_rfe_data_from_fw(rtwdev, sel)`, allowing firmware-provided RFE data to override parts of this static default, and finally loads the selected by-rate table with `rtw89_load_txpwr_table(rtwdev, rtwdev->rfe_parms->byr_tbl)`.

The TX-shape pointers are consumed by `rtw8852c_set_tx_shape()`. That function reads the regulatory domain with `rtw89_regd_get()`, indexes `rfe_parms->tx_shape.lmt` by band/rate-section/regdomain, and uses the OFDM TX-shape value as a TSSI band-edge configuration. The value is passed to `rtw89_phy_tssi_ctrl_set_bandedge_cfg()`, which indexes `chip->tssi_dbw_table->data[bandedge_cfg]` and writes the corresponding per-subband values into MAC/PHY registers.

Power-limit pointers are consumed by common TX power paths in `phy.c`, including code that assembles per-band power constraints for 2 GHz, 5 GHz, and 6 GHz and RU-specific limits. The table shapes are fixed by `struct rtw89_txpwr_rule_2ghz`, `struct rtw89_txpwr_rule_5ghz`, and `struct rtw89_txpwr_rule_6ghz`, so each pointer in this initializer must match the expected compile-time dimensions.

## State And Persistence Behavior

The objects in this chunk are static kernel image data. They do not mutate and do not persist runtime state by themselves.

At runtime, `rtwdev->rfe_parms` persists a pointer to the selected parameter bundle for the lifetime of the device. If firmware RFE data is available, `rtw89_load_rfe_data_from_fw()` copies the static defaults into `rtwdev->rfe_data->rfe_parms` and replaces only the tables that have valid firmware configuration. In that case, this chunk acts as the fallback baseline for any fields the firmware does not provide.

The TSSI DBW values are not persisted after table selection except as programmed hardware register state. `rtw89_phy_tssi_ctrl_set_bandedge_cfg()` writes the selected row to registers and updates the band-edge configuration index; subsequent channel/band/regdomain changes can reprogram these values.

## Dependencies

This chunk depends on many earlier definitions in the same source file:

- `rtw89_8852c_byr_table`, which wraps `rtw89_8852c_txpwr_byrate`.
- `rtw89_8852c_txpwr_lmt_2g`, `rtw89_8852c_txpwr_lmt_5g`, and `rtw89_8852c_txpwr_lmt_6g`.
- `rtw89_8852c_txpwr_lmt_ru_2g`, `rtw89_8852c_txpwr_lmt_ru_5g`, and `rtw89_8852c_txpwr_lmt_ru_6g`.
- `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru`.

It also depends on shared rtw89 type definitions from `core.h` and `phy.h`, and on enum constants such as `RTW89_TSSI_BANDEDGE_HIGH`, `RTW89_TSSI_CFG_NUM`, `RTW89_TSSI_SBW_NUM`, `RTW89_BAND_NUM`, and regulatory/rate-section dimension constants.

## Risks And Edge Cases

The highest-risk behavior is silent miscalibration from a wrong table pointer or wrong table dimensions. The compiler enforces much of the array shape through the pointer types, but it cannot validate that the numeric contents are correct for RTL8852C hardware, board layout, or regulatory requirements.

The TSSI DBW table is indexed by a TX-shape/band-edge value. If `rtw89_8852c_tx_shape_lmt` contains a value outside `RTW89_TSSI_CFG_NUM`, `rtw89_phy_tssi_ctrl_set_bandedge_cfg()` returns early and skips programming. If the value is in range but semantically wrong, the driver will write a valid-looking but incorrect band-edge profile.

Because 8852C sets `rfe_parms_conf = NULL`, all boards use this default unless firmware RFE data overrides it. Missing or invalid firmware data therefore falls back to these static tables, making this initializer the compatibility baseline for all 8852C devices.

The `has_da` flag remains false by default. If an 8852C variant requires dedicated-antenna power rules but firmware does not provide them, common code will not use the zero-initialized `rule_da_*` fields.

## Test Signals

Useful validation signals include successful rtw89 module build with no pointer-type or missing-symbol errors from `rtw8852c_table.c`, `rtw8852c_table.h`, and `rtw8852c.c`.

Runtime test signals are hardware-oriented:

- Device probe reaches `rtw89_core_setup_rfe_parms()` and loads `rtw89_8852c_byr_table` without null-pointer faults.
- Channel setup on 2 GHz, 5 GHz, and 6 GHz completes while applying TX power limits and TX-shape settings.
- TSSI band-edge programming writes the expected number of subband entries and does not hit the out-of-range early return for normal regulatory/channel combinations.
- RF certification, conducted power, EVM, and spectral-mask tests remain within limits, especially at band edges and RU/OFDMA transmit modes.
- Regression logs show no WARN/OOPS around `rtw89_phy_tssi_ctrl_set_bandedge_cfg()`, `rtw8852c_set_tx_shape()`, or common TX power setup.
