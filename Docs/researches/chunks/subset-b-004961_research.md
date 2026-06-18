# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 49276-57136

## Scope

This chunk covers the end of the RTL8852C HE/EHT RU transmit-power limit table data. It starts in the final portion of `rtw89_8852c_txpwr_lmt_ru_5g` and then defines nearly all of `rtw89_8852c_txpwr_lmt_ru_6g`, a static `s8` multidimensional regulatory table for 6 GHz RU-specific transmit-power limits.

The range is data-heavy rather than algorithmic. Its behavior comes from designated initializers, array dimensions, default zero-fill semantics, and the PHY lookup code in `phy.c` that consumes these tables. The chunk ends immediately before the exported PHY/RFE table descriptors that register `rtw89_8852c_txpwr_lmt_ru_6g` into `rtw89_8852c_dflt_parms`.

## Purpose

The chunk provides chip-specific regulatory power caps for resource-unit transmissions on RTL8852C:

- The opening lines finish 5 GHz RU limit entries for RU index `2`, NTX indexes `0` and `1`, multiple regulatory domains, and high 5 GHz channel indexes.
- `rtw89_8852c_txpwr_lmt_ru_6g` maps `(RU size, transmit-chain count, regulatory domain, 6 GHz power class, channel index)` to an RF-domain power limit byte.
- The 6 GHz table includes worldwide defaults under `RTW89_WW`, then overrides for domains such as `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_QATAR`, `RTW89_UK`, and `RTW89_THAILAND`.
- Values of `127` are used as sentinel-like "not constrained/not applicable" entries in the same table shape as other rtw89 generated power tables. Nonzero concrete values, including negative values, are actual limit data consumed by the PHY power decision path.

## Important APIs, Types, and Data

- `rtw89_8852c_txpwr_lmt_ru_6g` is declared as:
  `const s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER][RTW89_6G_CH_NUM]`.
- `RTW89_RU_NUM` covers `RTW89_RU26`, `RTW89_RU52`, `RTW89_RU106`, `RTW89_RU52_26`, and `RTW89_RU106_26`; this chunk populates RU indexes `0`, `1`, and `2`.
- `RTW89_NTX_NUM` indexes transmit stream/chain counts. This table populates NTX indexes `0` and `1`.
- `NUM_OF_RTW89_REG_6GHZ_POWER` covers VLP, LPI, and STD. The lookup fallback uses `RTW89_REG_6GHZ_POWER_DFLT`, which aliases VLP.
- `RTW89_6G_CH_NUM` is 120 and indexes the driver's internal ordered 6 GHz channel table rather than raw IEEE channel numbers.
- `struct rtw89_txpwr_rule_6ghz` stores the `lmt_ru` pointer used by runtime PHY code.
- `struct rtw89_txpwr_lmt_ru_6ghz_data` and `struct rtw89_fw_txpwr_lmt_ru_6ghz_entry` mirror this shape for firmware-provided RFE table overlays, including the extra `reg_6ghz_power` dimension.

## Control Flow

This source chunk has no executable branches. Its control flow is compile-time initialization followed by runtime indexing elsewhere:

1. The C compiler zero-fills unspecified cells in the static array.
2. Designated initializers assign selected legal cells with RF power-limit values.
3. The nearby `rtw89_8852c_dflt_parms` descriptor assigns `.rule_6ghz.lmt_ru = &rtw89_8852c_txpwr_lmt_ru_6g`.
4. `rtw89_phy_get_txpwr_limit_ru()` selects the correct band table during transmit-power limit calculation.
5. For 6 GHz, the lookup reads `(*rule_6ghz->lmt_ru)[ru][ntx][regd][reg6][ch_idx]`; if that cell is zero, it falls back to the worldwide default `RTW89_WW` plus `RTW89_REG_6GHZ_POWER_DFLT`.
6. The selected limit is converted from RF to MAC units, then clamped with optional antenna-gain offset handling, SAR, and transmit-power-envelope constraints.

The most important data-flow detail is that `0` is not just a power value in this path. It also triggers fallback to the worldwide default. Entries that need to avoid fallback use nonzero values, including `127` when the generated table wants an unconstrained/not-applicable marker.

## State and Persistence Behavior

The table is immutable static driver data. It is compiled into the module image and persists for the life of the loaded driver. Runtime state is not stored in this chunk.

The table affects persistent in-memory PHY behavior through `rtw89_8852c_dflt_parms`: once the chip's RFE parameters point to this static table, every RU transmit-power limit query can use it. Firmware RFE loading can instead populate `rtwdev->rfe_data.lmt_ru_6ghz` and update the active parameter pointers; that overlay uses the same dimensions and lookup semantics but is filled dynamically from firmware records.

## Dependencies and Integration Points

- The file includes `phy.h`, `reg.h`, and `rtw8852c_table.h`, which provide table types, chip declarations, register helpers, and PHY integration declarations.
- Regulatory domain selection comes from `rtw89_regd_get()` and the country/regulatory mapping in `regd.c`.
- The 6 GHz power-class dimension comes from `rtwdev->regulatory.reg_6ghz_power`.
- Channel indexes come from `rtw89_channel_to_idx()`, so table coordinates must match the driver's internal 6 GHz channel ordering.
- Runtime clamping integrates with `rtw89_phy_ant_gain_offset()`, `rtw89_phy_txpwr_rf_to_mac()`, `rtw89_query_sar()`, and `rtw89_phy_get_tpe_constraint()`.
- Firmware override support in `fw.c` validates `rtw89_fw_txpwr_lmt_ru_6ghz_entry` bounds before writing `data->v[ru][nt][regd][reg_6ghz_power][ch_idx]`.

## Risks and Edge Cases

- Table values are regulatory-critical. A wrong index, copied value, or domain assignment can either over-limit transmit power or unnecessarily reduce throughput.
- The table relies on generated designated initializers. Missing entries are zero, and zero means "try worldwide default" in the lookup path, so accidental omission can silently alter behavior instead of producing a compile error.
- `127` is a meaningful sentinel-like value in the power table ecosystem. Replacing it with `0` changes behavior because zero falls back, while `127` is consumed as a nonzero table result.
- The 6 GHz table has five dimensions. Any mismatch between `RTW89_6G_CH_NUM`, regulatory enum ordering, power-class enum ordering, or RU enum ordering would compile but select the wrong regulatory value at runtime.
- The chunk starts inside the 5 GHz table, so merge-level documentation should connect this report with the preceding chunk to describe the full `rtw89_8852c_txpwr_lmt_ru_5g` declaration and earlier entries.
- Per-regulatory overrides are sparse. Domains without explicit entries inherit through zero fallback, but only after the lookup tests the exact selected domain/power-class cell.

## Test Signals

Useful validation signals include:

- Build coverage for `rtw8852c_table.c` to catch initializer bounds and declaration-shape mismatches.
- Static checks comparing the declared dimensions against `struct rtw89_txpwr_rule_6ghz`, `struct rtw89_txpwr_lmt_ru_6ghz_data`, and `struct rtw89_fw_txpwr_lmt_ru_6ghz_entry`.
- Runtime debug or trace checks around `rtw89_phy_get_txpwr_limit_ru()` for 6 GHz channels, confirming selected `(ru, ntx, regd, reg6, ch_idx)` cells and worldwide fallback behavior.
- Regulatory smoke tests across US/FCC, EU/ETSI, Japan/MKK, Canada/IC, Korea/KCC, Australia/ACMA, UK, Qatar, Thailand, and Chile mappings.
- 6 GHz VLP/LPI/STD power-class tests, especially channel indexes where the table switches from concrete limits to `127`.
- Throughput and RF conformance tests using HE/EHT RU transmissions on 6 GHz to confirm the final MAC-programmed limit is the minimum of RU table, SAR, antenna-gain adjusted dual-antenna limit when present, and TPE constraint.

## Cross-Chunk Notes

The final per-file report should merge this with adjacent chunks that define the full non-RU 6 GHz table, the 2 GHz and 5 GHz RU tables, and the `rtw89_8852c_dflt_parms` registration immediately after this range. The key connection is that this chunk supplies static RTL8852C 6 GHz RU regulatory data, while `phy.c` supplies the lookup semantics and `fw.c` supplies optional firmware override loading for the same table shape.
