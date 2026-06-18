# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c lines 20493-23930

## Scope

This chunk covers the last 3,438 lines of `rtw8814a_table.c`. The range starts in the middle of the `rtw8814a_txpwr_lmt_type7[]` transmit-power-limit table, continues through the full `rtw8814a_txpwr_lmt_type8[]` table and its `RTW_DECL_TABLE_TXPWR_LMT()` wrapper, then defines RTL8814A thermal power-tracking tables for the default board type and board types 0, 2, 5, 7, and 8. It ends with the RTL8814A card power-on and power-off command sequences exported as `card_enable_flow_8814a[]` and `card_disable_flow_8814a[]`.

Because the range starts inside a data table, earlier chunks are needed for the beginning of `rtw8814a_txpwr_lmt_type7[]` and for the file-level context around MAC, AGC, BB, RF, baseband power-group, and earlier transmit-power-limit tables. This chunk still includes all code-visible declarations from `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` to the end of the file.

## Purpose

This file is a generated-style hardware data source for the Realtek `rtw88` RTL8814A driver. In this chunk, the data has three runtime roles:

- It completes board-specific transmit power limits for the type 7 and type 8 RFE configurations. Each row is a `struct rtw_txpwr_lmt_cfg_pair` describing regulatory domain, band, channel width, rate section, channel, and limit.
- It provides thermal power-tracking swing-index lookup tables. The driver selects these by RFE definition, current band/channel, transmit rate family, RF path A/B/C/D, temperature direction, and thermal delta from efuse calibration.
- It defines card enable and disable power state flows as `struct rtw_pwr_seq_cmd` arrays. The MAC power sequence parser executes these arrays during device bring-up and shutdown.

The chunk is pure data plus macro-generated `struct rtw_table` exports. There are no local functions with branches or loops here; control flow is in consumers such as `rtw_parse_tbl_txpwr_lmt()`, `rtw_phy_config_swing_table()`, and `rtw_pwr_seq_parser()`.

## Important APIs, Types, and Data

Transmit power limit data uses `struct rtw_txpwr_lmt_cfg_pair` from `phy.h`:

- `regd`: regulatory domain index.
- `band`: 2.4 GHz versus 5 GHz table group.
- `bw`: channel-width bucket.
- `rs`: rate-section bucket.
- `ch`: channel number or channel-group key.
- `txpwr_lmt`: signed 8-bit transmit power limit value; in these tables `63` appears as a sentinel/high cap in many unsupported or unconstrained combinations.

`RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` and `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type8)` produce exported `struct rtw_table` objects named `rtw8814a_txpwr_lmt_type7_tbl` and `rtw8814a_txpwr_lmt_type8_tbl`. Those objects set `.data` to the raw array, `.size` to `ARRAY_SIZE()`, and `.parse` to `rtw_parse_tbl_txpwr_lmt`.

Power tracking data is organized around `struct rtw_pwr_track_tbl` from `main.h`. `RTW_PWR_TRK_TBL_SZ` is 30, and each lookup table maps a clamped thermal delta to a positive or negative swing index. For 5 GHz, `RTW_PWR_TRK_5G_NUM` is 3, so each path/direction has three sub-bands selected by the current channel group. For 2.4 GHz, there are separate OFDM and CCK tables per RF path:

- 5 GHz path tables use path suffixes `5ga`, `5gb`, `5gc`, and `5gd` for RF paths A, B, C, and D, with `_n` and `_p` variants for negative and positive temperature compensation.
- 2.4 GHz OFDM tables use `2ga`, `2gb`, `2gc`, and `2gd`, again split into `_n` and `_p`.
- 2.4 GHz CCK tables use `2g_cck_a`, `2g_cck_b`, `2g_cck_c`, and `2g_cck_d`, split into `_n` and `_p`.
- Exported aggregate structs in this chunk are `rtw8814a_rtw_pwrtrk_tbl`, `rtw8814a_rtw_pwrtrk_type0_tbl`, `rtw8814a_rtw_pwrtrk_type2_tbl`, `rtw8814a_rtw_pwrtrk_type5_tbl`, `rtw8814a_rtw_pwrtrk_type7_tbl`, and `rtw8814a_rtw_pwrtrk_type8_tbl`.

Power sequence data uses `struct rtw_pwr_seq_cmd` from `main.h`:

- `offset`: MAC or bus-local register offset, or delay duration for delay commands.
- `cut_mask`: hardware cut mask; all commands in this chunk use `RTW_PWR_CUT_ALL_MSK`.
- `intf_mask`: interface selector such as `RTW_PWR_INTF_ALL_MSK`, `RTW_PWR_INTF_USB_MSK`, or `RTW_PWR_INTF_PCI_MSK`.
- `base`: register base; this chunk uses `RTW_PWR_ADDR_MAC` for actual writes/polls and `0` on end markers.
- `cmd`: `RTW_PWR_CMD_WRITE`, `RTW_PWR_CMD_POLLING`, `RTW_PWR_CMD_DELAY`, or `RTW_PWR_CMD_END`.
- `mask` and `value`: bit mask and desired value for write/poll commands, or delay unit for delay commands.

The internal sequence arrays are `init_power_on_8814a[]`, `trans_carddis_to_cardemu_8814a[]`, `trans_cardemu_to_act_8814a[]`, `trans_act_to_cardemu_8814a[]`, and `trans_cardemu_to_carddis_8814a[]`. The exported flow arrays are pointer lists terminated by `NULL`.

## Control Flow

Transmit power limit control flow is indirect. `rtw8814a.c` maps each supported RFE option to a `struct rtw_rfe_def` containing a power-limit table pointer. For RTL8814A, RFE option 0 uses `rtw8814a_txpwr_lmt_type0_tbl`, while RFE option 1 uses `rtw8814a_txpwr_lmt_type1_tbl`; the type 7 and type 8 tables in this chunk are exported for board configurations declared in the table header and for possible reuse by downstream or future RFE mappings. When a selected table is loaded, `rtw_parse_tbl_txpwr_lmt()` walks every `rtw_txpwr_lmt_cfg_pair`, calls `rtw_phy_set_tx_power_limit()` with the six row fields, records which regulatory domains were present, and fills missing domains from an alternative domain or worldwide defaults.

Power tracking flow starts from the selected `rtw_rfe_def->pwr_track_tbl`. `rtw_phy_config_swing_table()` inspects `rtwdev->hal.current_channel` and `rtwdev->dm_info.tx_rate`. On 2.4 GHz CCK rates it points each RF path at the CCK tables; on 2.4 GHz non-CCK rates it points at the OFDM tables; on 5 GHz it selects one of the three 5 GHz sub-band table sets. Later, `rtw_phy_pwrtrack_get_delta()` clamps the temperature delta to `RTW_PWR_TRK_TBL_SZ - 1`, and `rtw_phy_pwrtrack_get_pwridx()` indexes the selected positive or negative table for the effective transmit power adjustment.

Power sequence control flow is executed by `rtw_pwr_seq_parser()`. The chip info for RTL8814A assigns `.pwr_on_seq = card_enable_flow_8814a` and `.pwr_off_seq = card_disable_flow_8814a`. The parser determines the active HCI interface mask from PCIE/USB/SDIO, derives a cut mask from the chip cut version, iterates each sub-sequence until a `NULL` pointer, and then iterates commands until `RTW_PWR_CMD_END`. Commands whose interface or cut mask does not match are skipped. Write commands read-modify-write an 8-bit register, polling commands wait until `(reg & mask) == value`, and delay commands call `udelay()` or `mdelay()`.

The enable flow is:

- `init_power_on_8814a[]`: for USB, set BIT(1) at MAC offset `0x10c2`, then end.
- `trans_carddis_to_cardemu_8814a[]`: move card-disable to card-emulation by setting/clearing bits at offsets `0x0012`, `0x0015`, `0x0023`, `0x0046`, `0x0062`, and interface-specific PCI registers including `0x0005`, `0x0301`, and `0x0071`.
- `trans_cardemu_to_act_8814a[]`: clear suspend-related bits, poll offset `0x0006` BIT(1), program `0x00f0`, `0x0081`, set BIT(0) at `0x0005`, then poll BIT(0) clear at `0x0005`.

The disable flow is:

- `trans_act_to_cardemu_8814a[]`: write several active-state MAC registers (`0x0c00`, `0x0e00`, `0x1002`, `0x001f`, `0x0007`, `0x0005`) with a one-microsecond delay and additional USB-specific low-power bits at `0x0008`, `0x0066`, `0x0041`, `0x0042`, and `0x004e`, then poll BIT(1) clear at `0x0005`.
- `trans_cardemu_to_carddis_8814a[]`: transition from card-emulation to card-disable by programming offsets `0x0003`, `0x0080`, `0x0081`, `0x0045`, `0x0046`, `0x0047`, `0x0015`, `0x0012`, `0x0023`, `0x0008`, `0x0007`, `0x001f`, `0x0020`, `0x0021`, `0x0076`, `0x0091`, `0x0070`, and `0x0005`.

## State and Persistence

All transmit power limit tables are compile-time `static const` data, except for the macro-emitted `const struct rtw_table` wrappers. Once parsed, their values populate mutable arrays in `struct rtw_hal`, including 2.4 GHz and 5 GHz per-regulatory-domain/channel-width/rate-section/channel power limits. Those cached limits persist in the driver until reinitialized by chip bring-up or another table load.

All power tracking leaf arrays are `static const u8` data. The exported `struct rtw_pwr_track_tbl` objects hold pointers into those arrays and have no mutable local state. Runtime state lives in `rtwdev`: efuse thermal calibration values, EWMA thermal averages, current channel, current TX rate, selected RFE definition, and the `struct rtw_swing_table` pointers configured from these constants. The lookup tables are therefore persistent calibration policy, while actual thermal tracking state changes dynamically with temperature sampling.

The power sequence arrays are immutable command scripts. Their effects persist in hardware registers and device power state, not in this file. The parser skips commands by interface mask, so a PCIe device and a USB device execute different subsets of the same sequences. Polling commands can block bring-up/shutdown until hardware reaches the expected state or the parser returns `-EBUSY`.

## Dependencies and Integration Points

This chunk depends on declarations from `main.h`, `phy.h`, and `rtw8814a_table.h`. `BIT()`, `ARRAY_SIZE()`, `RTW_PWR_*` masks, `RTW_PWR_TRK_*` constants, `struct rtw_table`, `struct rtw_pwr_track_tbl`, `struct rtw_pwr_seq_cmd`, and `struct rtw_txpwr_lmt_cfg_pair` are all defined outside this file.

The table header exports the type 7 and type 8 transmit-power-limit table wrappers, all six power-tracking aggregate tables, and the card enable/disable flow arrays. `rtw8814a.c` integrates the exported enable/disable flows into `rtw8814a_hw_spec` and maps RFE definitions to selected baseband power-group, transmit-power-limit, and power-tracking tables. In the visible consumer code, only RFE options 0 and 1 are wired for RTL8814A, but this table file exports a wider set of board-type data.

`phy.c` consumes the transmit-power-limit wrappers through `rtw_load_table()` and `rtw_parse_tbl_txpwr_lmt()`. It consumes power-tracking tables through `rtw_phy_config_swing_table()` and `rtw_phy_pwrtrack_get_pwridx()`.

`mac.c` consumes power sequence arrays through `rtw_pwr_seq_parser()`, which is called from MAC power-on/power-off paths using `chip->pwr_on_seq` and `chip->pwr_off_seq`. That parser performs hardware register writes and polling through the rtw88 register accessors.

Hardware integration is direct and sensitive: the power sequences touch RTL8814A MAC power-control registers, USB-specific power bits, and PCIe-specific registers. The power-limit and power-tracking tables control RF transmit power behavior across regulatory domains, channel groups, bandwidths, rate sections, RF paths, and board layouts.

## Risks

- The transmit power limit rows are dense numeric data with no per-row names. A swapped field, missing row, or incorrect sentinel value can silently produce wrong regulatory limits or fallback behavior.
- `63` appears frequently as a cap/sentinel-like value in the power-limit tables. Consumers treat it as a normal `s8` table value, so interpretation relies on surrounding rtw88 power-limit logic and chip maximum power index.
- This chunk starts inside `rtw8814a_txpwr_lmt_type7[]`. File-level review must merge with the previous chunk to validate that type 7 has a complete initializer and consistent row coverage.
- Type 7 and type 8 board tables differ materially. Accidentally mapping an RFE option to the wrong table would alter both regulatory power limits and thermal compensation behavior for a board variant.
- Power tracking arrays must have exactly `RTW_PWR_TRK_TBL_SZ` entries and 5 GHz arrays must have exactly `RTW_PWR_TRK_5G_NUM` rows. The compiler catches many size mismatches because dimensions are explicit, but semantically wrong values or path ordering errors still compile.
- The path naming is reversed relative to common A-to-D listing in some places: aggregate struct fields map RF path A to `5ga`/`2ga`, B to `5gb`/`2gb`, C to `5gc`/`2gc`, and D to `5gd`/`2gd`. A generator or manual edit that changes suffixes can miscalibrate one or more chains.
- Power sequence register ordering is hardware-critical. Reordering writes, changing delays, or changing poll masks can leave the device stuck in card-emulation, fail bring-up, or fail low-power shutdown.
- Interface masks must remain precise. USB-only commands in `init_power_on_8814a[]` and `trans_act_to_cardemu_8814a[]`, and PCI-only commands in `trans_carddis_to_cardemu_8814a[]`, should not be broadened without hardware evidence.
- Poll failures in `rtw_pwr_seq_parser()` surface as `-EBUSY`; repeated failures would likely appear as probe, resume, or shutdown failures rather than compile-time errors.
- There are no comments in the table data explaining source provenance, units, or board-type differences. Regression review requires comparing against vendor tables, measured RF behavior, or known-good upstream data.

## Test and Validation Signals

Useful static validation:

- Build the driver with this table file enabled and treat missing symbols or initializer-size warnings as hard failures.
- Confirm `rtw8814a_table.h` declarations match exported symbols: `rtw8814a_txpwr_lmt_type7_tbl`, `rtw8814a_txpwr_lmt_type8_tbl`, the six `rtw8814a_rtw_pwrtrk*` aggregate tables, and both card flow arrays.
- Check that every `struct rtw_pwr_track_tbl` field required by `rtw_phy_config_swing_table()` is non-NULL for all exported board types.
- Check each `RTW_PWR_TRK_TBL_SZ` table has 30 values and each 5 GHz table has three rows.
- Compare type 7 and type 8 transmit-power-limit row counts and row coverage against the generated manifest or vendor source.

Useful runtime and hardware validation:

- Probe RTL8814A over supported PCIe and USB paths and verify `card_enable_flow_8814a[]` completes without power-polling errors.
- Exercise suspend/resume, module unload/reload, and device removal to verify `card_disable_flow_8814a[]` reaches card-disable state and does not leave the device wedged for the next probe.
- Enable rtw88 regulatory/debug logging and verify `rtw_parse_tbl_txpwr_lmt()` does not report unexpected missing regulatory domains for a selected RFE table.
- Test 2.4 GHz CCK, 2.4 GHz OFDM, and 5 GHz low/mid/high channel groups so `rtw_phy_config_swing_table()` selects every major table family.
- Heat/cool the device or emulate thermal deltas where possible and verify `rtw_phy_pwrtrack_get_delta()` and `rtw_phy_pwrtrack_get_pwridx()` stay within bounds and do not log "power track table overflow", "swing table not configured", or "invalid swing table index".
- Measure conducted or radiated transmit power across board/RFE variants, RF paths A-D, bandwidths, rates, and representative channels to catch wrong path mapping or incorrect board-type table selection.
- Validate regulatory behavior for channels where the tables use high-cap values, especially 5 GHz channel groups around 149, 153, 157, 161, and 165 where many rows in this chunk differ from lower-band rows.
