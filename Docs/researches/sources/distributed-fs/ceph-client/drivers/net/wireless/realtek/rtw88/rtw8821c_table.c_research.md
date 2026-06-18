<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c

## Purpose

This file is the generated/static PHY table payload for the Realtek RTW8821C chip in the `rtw88` wireless driver. It contains no executable control-flow functions of its own beyond table declaration macros; its job is to package MAC, AGC, BB, RF, per-rate power-group, and transmit-power-limit register data as `struct rtw_table` objects consumed by the common PHY loader.

The tables are used by `rtw8821c.c` through `rtw8821c_hw_spec`, where `.mac_tbl`, `.agc_tbl`, `.bb_tbl`, and `.rf_tbl` point at the exported table objects declared here. During `rtw8821c_phy_set_param()`, the chip powers up BB/RF domains, clears `REG_RXPSEL` reset state, calls `rtw_phy_load_tables(rtwdev)`, restores RX path selection, then continues with crystal-cap programming, `rtw_phy_init()`, power tracking, and beamforming setup. This makes the register payload here part of device bring-up rather than runtime policy.

## Important APIs, Types, and Data

- `rtw8821c_mac[]`: address/value MAC initialization pairs. The payload starts with low MAC/system registers such as `0x010`, `0x025`, queue and timing ranges around `0x420`-`0x70b`, and is declared with `RTW_DECL_TABLE_PHY_COND(rtw8821c_mac, rtw_phy_cfg_mac)`.
- `rtw8821c_agc[]`: AGC programming stream declared with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_agc)`. It contains conditional markers such as `0x80001004`, `0x90001005`, and many writes to `0x81c`, which is the AGC table load register pattern used by the Realtek table interpreter.
- `rtw8821c_agc_btg_type2[]`: alternate AGC payload for BTG/RFE type 2 layouts, also wired to `rtw_phy_cfg_agc`. Its presence matches `rtw8821c` efuse/RFE handling where BTG-capable RFE options need different gain behavior.
- `rtw8821c_bb[]`: baseband initialization stream declared with `RTW_DECL_TABLE_PHY_COND(..., rtw_phy_cfg_bb)`, including BB register writes and conditional table blocks.
- `rtw8821c_bb_pg_type0[]`: `struct rtw_phy_pg_cfg_pair` array for path/rate-group power-index programming. It is declared through `RTW_DECL_TABLE_BB_PG`.
- `rtw8821c_rf_a[]`: RF radio table for path A only, declared through `RTW_DECL_TABLE_RF_RADIO(rtw8821c_rf_a, A)`. This reflects 8821C being a single-stream chip in the associated `rtw8821c_hw_spec` (`.rf_tbl = {&rtw8821c_rf_a_tbl}`).
- `rtw8821c_txpwr_lmt_type0[]`: `struct rtw_txpwr_lmt_cfg_pair` rows declared through `RTW_DECL_TABLE_TXPWR_LMT`. Rows encode regulatory domain/rate/bandwidth/channel-group/path constraints and cap values, with `63` appearing as the common sentinel-like maximum/disabled cap value used by the table format.

The file depends on `main.h` for common driver types, `phy.h` for table macros and parser functions, and `rtw8821c_table.h` for the extern declarations that expose the generated `struct rtw_table` objects.

## Control Flow and Integration

There is no direct function call flow inside this file. The table declaration macros create named table descriptors that the driver core invokes indirectly:

1. Bus-specific modules (`rtw8821ce.c`, `rtw8821cs.c`, `rtw8821cu.c`) match a PCI/SDIO/USB device and pass `&rtw8821c_hw_spec` as driver data.
2. The common bus probe builds an `rtw_dev` whose `chip` field points to `rtw8821c_hw_spec`.
3. The common power-on sequence eventually calls `rtw8821c_ops.phy_set_param`.
4. `rtw8821c_phy_set_param()` enables BB/RF domains and calls `rtw_phy_load_tables(rtwdev)`.
5. `rtw_phy_load_tables()` follows the chip info table pointers and applies these payloads via parser callbacks such as `rtw_phy_cfg_mac`, `rtw_phy_cfg_agc`, `rtw_phy_cfg_bb`, RF radio loaders, BB power-group loaders, and transmit-power-limit loaders.

The conditional numeric records embedded in the `u32` arrays are interpreted by the PHY table engine. They are not ordinary register/value pairs exclusively; values such as `0x80001005`, `0x90000400`, `0xA0000000`, and `0xB0000000` are condition/control tokens that select chip cut, package, platform, interface, or RFE variants before applying subsequent writes.

## State and Persistence Behavior

The arrays are `static const` and persist only as read-only kernel module data. They do not hold mutable runtime state and do not allocate memory. Runtime state is created by side effects when the PHY loader writes hardware registers and RF registers. Those side effects last until hardware reset, suspend/power-off, or a later channel/RF reconfiguration rewrites overlapping registers.

Because this file is data-only, persistence risks are primarily around stale or incorrect hardware payload values. A wrong AGC/BB/RF row can survive across the active power session and manifest as poor sensitivity, broken RF path selection, bad TX power, regulatory noncompliance, or BT coexistence issues.

## Dependencies and Integration Points

- `rtw8821c.c`: consumes the generated table symbols through `rtw8821c_hw_spec`.
- `phy.h` and PHY loader code: define the table declaration macros, conditional parser format, register write helpers, and BB/RF/TX power table application routines.
- `rtw8821c_table.h`: public header for these table symbols.
- Bus glue (`rtw8821ce.c`, `rtw8821cs.c`, `rtw8821cu.c`): indirectly consumes this file by passing `rtw8821c_hw_spec` to common probe paths.
- Firmware and calibration flows: run after table load and assume these base hardware defaults are valid.

## Risks

- The file is large, generated-looking, and numeric. Review cannot infer semantic correctness from C type checking; hardware validation is required.
- Conditional table tokens must match the parser contract. A malformed token can skip rows, write rows to the wrong variant, or leave hardware partially initialized.
- `rtw8821c_agc_btg_type2_tbl` is declared but not directly referenced in the inspected `rtw8821c_hw_spec` fields. It may be selected indirectly by RFE definitions or table-loader logic; if that linkage is absent or broken, BTG type 2 devices could use the wrong gain table.
- TX power limit rows are regulatory-sensitive. Errors can cause underpowered links or illegal transmit power for a region/bandwidth/rate combination.
- RF table only covers path A. That is expected for 8821C, but any future attempt to use the file for a dual-path variant would be structurally wrong.
- Since register writes happen during bring-up before normal traffic, failures can appear as probe timeouts, silent association failures, or low throughput rather than obvious kernel errors.

## Test Signals

- Build coverage should ensure all macro-generated symbols match the externs in `rtw8821c_table.h` and the chip spec references in `rtw8821c.c`.
- Probe tests for PCI, SDIO, and USB 8821C devices should confirm `rtw_phy_load_tables()` succeeds and the firmware reaches normal operation.
- RF smoke tests should cover 2.4 GHz, 5 GHz, channel 14 if supported by regulatory configuration, and HT/VHT rates.
- RFE/BT coexistence testing should include devices whose efuse selects BTG-related RFE options to verify the alternate AGC payload is selected correctly.
- Regulatory and power tests should compare per-rate/channel TX power against expected efuse and regulatory caps.
- Suspend/resume and power-cycle tests should confirm the static tables are reapplied cleanly and no register programming order dependency is exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821c_table.c -->
