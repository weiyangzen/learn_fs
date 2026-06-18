# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814a_table.c lines 10250-20492

## Scope

This chunk covers a data-heavy section of the Realtek rtw88 RTL8814A hardware tables. The range starts inside the tail of `rtw8814a_rf_b[]`, completes RF path B registration, contains all of `rtw8814a_rf_c[]`, all of `rtw8814a_rf_d[]`, and then defines the generic and several board/package-specific transmit-power limit tables through the beginning of `rtw8814a_txpwr_lmt_type7[]`.

The exact in-scope declarations are:

- Tail of `rtw8814a_rf_b[]`, ending with `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_b, B)` at line 10548.
- Full `rtw8814a_rf_c[]` plus `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_c, C)`, lines 10550-12551.
- Full `rtw8814a_rf_d[]` plus `RTW_DECL_TABLE_RF_RADIO(rtw8814a_rf_d, D)`, lines 12553-14583.
- Full `rtw8814a_txpwr_lmt[]`, `rtw8814a_txpwr_lmt_type0[]`, `rtw8814a_txpwr_lmt_type1[]`, `rtw8814a_txpwr_lmt_type2[]`, `rtw8814a_txpwr_lmt_type3[]`, and `rtw8814a_txpwr_lmt_type5[]`, each with 972 `struct rtw_txpwr_lmt_cfg_pair` entries and a corresponding `RTW_DECL_TABLE_TXPWR_LMT(...)` wrapper.
- The first 45 entries of `rtw8814a_txpwr_lmt_type7[]`, from line 20447 through the chunk boundary at line 20492. The type7 table is incomplete in this chunk and must be reconciled with the following chunk.

This file is not executable filesystem logic despite the repository path. It is Linux wireless PHY/RF calibration and regulatory data for the RTL8814A 4-stream Wi-Fi chipset.

## Purpose

The RF arrays provide register programming sequences for the RTL8814A radio paths. They are consumed during PHY table loading to bring each active RF path into a calibrated state. Because RTL8814A supports four RF paths, the chip descriptor exposes one table per path: A, B, C, and D. This chunk owns the end of path B and the complete path C/D table bodies.

The transmit-power limit arrays encode regulatory and board-specific caps by regulatory domain, band, channel width, rate section, and channel. These limits are stored into `rtwdev->hal.tx_pwr_limit_2g` and `rtwdev->hal.tx_pwr_limit_5g`; later TX-power calculations use them to clamp per-rate power indices before programming hardware.

The section is therefore critical to:

- RF path C/D bring-up and calibration for 4x4 RTL8814A devices.
- RF path B completion at the beginning of this chunk.
- Per-regulatory-domain TX power caps for RFE/package variants.
- Runtime power-limit fallback and cross-reference behavior in the shared rtw88 PHY layer.

## Important APIs, Types, and Tables

The RF table declarations use plain `static const u32` arrays. The table stream alternates normal address/data pairs with conditional branch markers such as `0x800000..`, `0x900000..`, `0xA0000000`, and `0xB0000000`. These are interpreted by `rtw_parse_tbl_phy_cond()`, which views the data as `union phy_table_tile` entries and applies branch/condition handling before calling the table's `do_cfg` callback.

`RTW_DECL_TABLE_RF_RADIO(name, path)` wraps an RF array into a public `const struct rtw_table name_tbl` with:

- `.parse = rtw_parse_tbl_phy_cond`
- `.do_cfg = rtw_phy_cfg_rf`
- `.rf_path = RF_PATH_A/B/C/D`

`rtw_phy_cfg_rf()` writes each matched RF entry with `rtw_write_rf(rtwdev, tbl->rf_path, addr, RFREG_MASK, data)` and applies a short delay after normal writes. Special pseudo-addresses `0xffe` and `0xfe` are delay tokens rather than RF registers.

The transmit-power limit tables use:

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

`RTW_DECL_TABLE_TXPWR_LMT(name)` wraps each array as a `struct rtw_table` parsed by `rtw_parse_tbl_txpwr_lmt()`. That parser iterates entries, calls `rtw_phy_set_tx_power_limit()`, fills missing regulatory domains from an alternate or worldwide domain, then cross-references HT/VHT 5 GHz limits where one side is absent.

Important in-scope RF tables:

- `rtw8814a_rf_b_tbl`: completed at the start of this range, mapped to RF path B.
- `rtw8814a_rf_c_tbl`: full RF path C sequence, roughly matching path B but with path-specific differences in registers such as `0x03b`, `0x034`, and later gain/power values.
- `rtw8814a_rf_d_tbl`: full RF path D sequence, similar to path C but with path-D-specific values and repeated conditional channel/RFE sections.

Important in-scope TX-power limit tables:

- `rtw8814a_txpwr_lmt_tbl`: generic/default limits.
- `rtw8814a_txpwr_lmt_type0_tbl`
- `rtw8814a_txpwr_lmt_type1_tbl`
- `rtw8814a_txpwr_lmt_type2_tbl`
- `rtw8814a_txpwr_lmt_type3_tbl`
- `rtw8814a_txpwr_lmt_type5_tbl`
- Partial `rtw8814a_txpwr_lmt_type7[]`, not yet declared as a table in this chunk.

`rtw8814a_table.h` exports these table objects so `rtw8814a.c` can reference them through chip and RFE descriptors.

## Control Flow

RF table loading is driven by `rtw_phy_load_tables()`. The function loads MAC, BB, AGC, optional RFE AGC/BTG, optional RFK, and then iterates `rf_path` from zero to `rtwdev->hal.rf_path_num - 1`. For each active path it selects `chip->rf_tbl[rf_path]` and calls `rtw_load_table()`. In `rtw8814a_hw_spec`, `chip->rf_tbl` is `{&rtw8814a_rf_a_tbl, &rtw8814a_rf_b_tbl, &rtw8814a_rf_c_tbl, &rtw8814a_rf_d_tbl}`, so this chunk supplies the complete path C/D stream and the registered path B table object.

During parsing, `rtw_parse_tbl_phy_cond()` walks two `u32` words at a time as either a condition tile or a register/data pair. Positive and negative condition markers update `is_matched` and `is_skipped`, implementing if/elif/else/endif-like selection. Only matched address/data pairs reach `rtw_phy_cfg_rf()`. The RF tables in this range use many conditional blocks around channel/package/RFE selectors; the repeated `0x800000..`, `0x900000..`, `0xA0000000`, and `0xB0000000` markers are part of this mini-language rather than direct hardware writes.

TX-power limit loading is selected through the RFE definition. In the current `rtw8814a_rfe_defs[]`, RFE option 0 uses `rtw8814a_txpwr_lmt_type0_tbl`, and RFE option 1 uses `rtw8814a_txpwr_lmt_type1_tbl`. The other exported tables in this chunk are still ABI-visible through the table header and may be used by future/alternate RFE mappings, downstream changes, or reconciliation with adjacent chunks.

`rtw_parse_tbl_txpwr_lmt()` records which regulatory domains were present, then stores each tuple into the HAL power-limit arrays. For 2 GHz it writes `hal->tx_pwr_limit_2g[regd][bw][rs][channel_index]`; for 5 GHz it writes `hal->tx_pwr_limit_5g[...]`. The worldwide domain is tightened with the minimum of existing worldwide and newly parsed values. Missing domains are copied from configured alternatives when available or from worldwide as a fallback. Finally, HT and VHT 5 GHz rate-section limits are cross-filled where one of a matching HT/VHT pair is still at the max-power sentinel.

## State and Persistence

The RF arrays are `static const` data and do not hold mutable state. Their effects persist in hardware RF registers after table load until a reset, power cycle, RF reconfiguration, calibration, or later table load overwrites them. Because these are path-specific tables, a wrong path binding would persist incorrect radio state on the corresponding RF chain.

The TX-power limit arrays are also immutable. Runtime state is created when `rtw_parse_tbl_txpwr_lmt()` stores their values in `struct rtw_hal`. Those HAL arrays persist for subsequent TX-power calculations and are reused across channel/rate updates. The parser also mutates worldwide and missing-domain entries based on the parsed table content, so the final runtime limits are not simply a direct copy of the array.

The tables interact with persistent device identity and board state:

- `rtwdev->efuse.rfe_option` selects the RFE definition and therefore the power-limit table.
- `rtwdev->hal.rf_path_num` determines whether paths C and D are loaded.
- `rtwdev->chip->max_power_index` clamps parsed power limits. For RTL8814A this is `0x3f`.
- `rtwdev->chip->is_pwr_by_rate_dec = true` affects nearby power-by-rate parsing, but the limit tables in this chunk already store signed integer limits directly.

## Dependencies and Integration Points

This chunk depends on `main.h`, `phy.h`, and `rtw8814a_table.h`. The key shared declarations are `struct rtw_table`, `struct rtw_txpwr_lmt_cfg_pair`, `RTW_DECL_TABLE_RF_RADIO`, and `RTW_DECL_TABLE_TXPWR_LMT`.

Integration points include:

- `rtw8814a_hw_spec` in `rtw8814a.c`, which installs the RF table pointers and RFE definitions into the chip descriptor.
- `rtw_phy_load_tables()` in `phy.c`, which loads RF tables for active paths.
- `rtw_phy_cfg_rf()` in `phy.c`, which turns RF table entries into `rtw_write_rf()` operations using the table's path.
- `rtw_parse_tbl_txpwr_lmt()` in `phy.c`, which turns power-limit tuples into HAL arrays and performs regulatory-domain fallback.
- `rtw_phy_get_tx_power_index()` and related TX-power paths later in `phy.c`, which consume the parsed limit arrays when deriving final transmit power.
- Regulatory domain helpers such as `rtw_regd_has_alt()`, because missing domains in these tables can be copied from alternate domains.

The RF register writes ultimately depend on lower rtw88 register access, RF path base addresses in `rtw8814a_hw_spec`, and the device's hardware/firmware state at PHY bring-up time.

## Risks

The RF arrays are fragile calibration data. Small changes to an address/data pair, conditional marker, or ordering can alter synthesizer, gain, tracking, path enable, or channel-specific calibration behavior. The path C and D arrays are similar but not identical; blindly copying values between them risks breaking one RF chain while leaving the others apparently functional.

The chunk boundary is a risk. The source range starts inside `rtw8814a_rf_b[]` and ends inside `rtw8814a_txpwr_lmt_type7[]`. A final file-level report must merge adjacent chunks before drawing conclusions about complete path B contents or type7 power-limit behavior.

The conditional table encoding is not self-validating. `rtw_parse_tbl_phy_cond()` depends on paired words and specific bitfield encodings in `union phy_table_tile`. If a data pair accidentally matches a condition pattern, or if a condition marker is malformed, the parser can skip or apply a large block unexpectedly.

The TX-power limit data is regulatory-sensitive. Incorrect values can underpower the device, reduce throughput, or exceed regional conducted-power limits. The values are clamped to `max_power_index`, but that only bounds magnitude; it does not prove the regulatory mapping is correct.

The current RFE map references only type0 and type1 for RTL8814A, but this file exports more type-specific tables. Unused-looking tables should not be removed without checking vendor variants and downstream RFE mappings.

Power-limit fallback can hide missing table coverage. If a regulatory domain is absent, the parser copies an alternate or worldwide table. That keeps runtime arrays populated but can make domain-specific omissions less obvious unless debug logs are reviewed.

## Test and Validation Signals

Useful validation for this chunk is mostly hardware- and integration-based:

- Probe an RTL8814A device with four RF paths and confirm `rtw_phy_load_tables()` loads RF paths A-D without RF write failures.
- Use debug logging around table loading to confirm path C uses `rtw8814a_rf_c_tbl` and path D uses `rtw8814a_rf_d_tbl`, with the expected `.rf_path` values.
- Exercise both supported `efuse.rfe_option` values in `rtw8814a_rfe_defs[]` and confirm RFE 0 selects `rtw8814a_txpwr_lmt_type0_tbl` while RFE 1 selects `rtw8814a_txpwr_lmt_type1_tbl`.
- Watch for `wrong txpwr_lmt` warnings from `rtw_phy_set_tx_power_limit()`. Such warnings would indicate invalid `regd`, `band`, `bw`, `rs`, or channel values in one of these arrays.
- Check `RTW_DBG_REGD` output for regulatory domains filled from alternatives or worldwide; unexpected fallback may indicate missing table coverage.
- Validate conducted TX power on 2.4 GHz channels 1-14 and 5 GHz channels 36-165 across CCK, OFDM, HT, and VHT sections, with both 20 MHz and 40 MHz widths covered by these tables.
- Run throughput/RSSI checks with 1x1 through 4x4 path configurations to catch RF path C/D calibration mistakes that would not appear on lower-chain devices.
- Build-test the file to verify all table wrappers declared in this chunk match the extern declarations in `rtw8814a_table.h`.
- During merge/reconciliation, verify the next chunk completes `rtw8814a_txpwr_lmt_type7[]` and supplies its `RTW_DECL_TABLE_TXPWR_LMT(rtw8814a_txpwr_lmt_type7)` wrapper.
