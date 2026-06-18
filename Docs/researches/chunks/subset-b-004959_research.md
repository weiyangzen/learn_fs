# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 35032-41891

## Purpose

This chunk is static regulatory transmit-power data for the Realtek RTL8852C `rtw89` wireless driver. It covers the tail of `rtw89_8852c_txpwr_lmt_5g` and the opening section of `rtw89_8852c_txpwr_lmt_6g`, not executable logic. The data gives per-channel absolute TX power limits for 5 GHz and 6 GHz operation, keyed by bandwidth, number of TX chains, rate section, beamforming state, regulatory domain, and, for 6 GHz, the 6 GHz power mode.

The 5 GHz table starts at line 33981 as:

```c
const s8 rtw89_8852c_txpwr_lmt_5g[RTW89_5G_BW_NUM][RTW89_NTX_NUM]
                                 [RTW89_RS_LMT_NUM][RTW89_BF_NUM]
                                 [RTW89_REGD_NUM][RTW89_5G_CH_NUM]
```

The 6 GHz table starts at line 36955 as:

```c
const s8 rtw89_8852c_txpwr_lmt_6g[RTW89_6G_BW_NUM][RTW89_NTX_NUM]
                                 [RTW89_RS_LMT_NUM][RTW89_BF_NUM]
                                 [RTW89_REGD_NUM][NUM_OF_RTW89_REG_6GHZ_POWER]
                                 [RTW89_6G_CH_NUM]
```

## Important Data and Types

- `rtw89_8852c_txpwr_lmt_5g`: 5 GHz absolute power-limit table. This chunk begins in the middle of the table at `[0][0][2][0][RTW89_KCC][15]` and continues through the end of the 5 GHz initializer before the 6 GHz declaration.
- `rtw89_8852c_txpwr_lmt_6g`: 6 GHz absolute power-limit table. This chunk begins the table with `RTW89_WW` defaults and then country/domain-specific rows such as `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`, `RTW89_MEXICO`, `RTW89_UKRAINE`, `RTW89_CHILE`, `RTW89_QATAR`, and `RTW89_THAILAND`.
- `struct rtw89_txpwr_rule_5ghz` and `struct rtw89_txpwr_rule_6ghz` in `core.h`: typed pointers that describe the exact dimensions consumed by generic PHY TX power code.
- `struct rtw89_rfe_parms`: binds these generated chip tables into the runtime RFE parameter set. At the end of the file, `rtw89_8852c_dflt_parms.rule_5ghz.lmt` points to `rtw89_8852c_txpwr_lmt_5g`, and `.rule_6ghz.lmt` points to `rtw89_8852c_txpwr_lmt_6g`.

The table values are signed 8-bit power quantities in the driver's RF power representation. Later PHY code converts selected values through `rtw89_phy_txpwr_rf_to_mac()` before writing MAC TX power pages. The value `0` is significant because lookup code treats it as "no explicit value, fall back to `RTW89_WW`." The value `127` is a sentinel-like high limit frequently used for unsupported/prohibited/not-constraining combinations; it is still data and is carried through the same min/fallback logic.

## Control Flow and Integration

There is no local control flow in this range; all behavior comes from consumers:

1. `rtw8852c_chip_info.dflt_parms` points to `rtw89_8852c_dflt_parms`.
2. Channel/power setup in `rtw8852c_set_txpwr()` calls `rtw89_phy_set_txpwr_limit()` after by-rate power, offsets, and TX shape are configured.
3. The AX implementation, `rtw89_phy_set_txpwr_limit_ax()`, builds per-NSS power-limit pages by calling `rtw89_phy_fill_txpwr_limit_ax()`.
4. Fill helpers call `rtw89_phy_read_txpwr_limit()` for each rate/bandwidth/beamforming/channel slot.
5. `rtw89_phy_read_txpwr_limit()` chooses the 5 GHz or 6 GHz rule pointer based on `chan->band_type`, indexes by channel-to-table index, regulatory domain from `rtw89_regd_get()`, and 6 GHz power type from `rtwdev->regulatory.reg_6ghz_power`.
6. If a domain-specific entry is zero, the code falls back to the `RTW89_WW` entry. The selected RF-limit value is combined with optional dynamic antenna-gain offset, SAR, and 6 GHz TPE constraint, then converted and written to MAC registers via `rtw89_mac_txpwr_write32()`.

The RU-limit path is adjacent in the same driver architecture but not in this line range: `rtw89_8852c_txpwr_lmt_ru_*` begins later in this file. This chunk feeds absolute power limits, not RU-specific OFDMA limits.

## State and Persistence

The tables are compile-time `static const` data in the kernel image. They are not mutated after load. Runtime state affected by this data is indirect:

- Current country/regulatory mapping in `rtwdev->regulatory` chooses the regulatory-domain index.
- Current channel context chooses band, bandwidth, primary channel, and 6 GHz power mode.
- SAR, antenna-gain, and TPE state can further reduce the selected table value.
- The resolved values are written into hardware/MAC power-limit pages during channel or TX-power reconfiguration.

Firmware RFE element handling can replace RFE parameter pointers when valid firmware-provided TX-power data exists, but the default RTL8852C path wires these arrays through `rtw89_8852c_dflt_parms`.

## Dependencies

- Dimension constants and enums from `core.h`: `RTW89_5G_BW_NUM`, `RTW89_6G_BW_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_REGD_NUM`, `RTW89_5G_CH_NUM`, `RTW89_6G_CH_NUM`, and `NUM_OF_RTW89_REG_6GHZ_POWER`.
- Regulatory-domain definitions such as `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`, `RTW89_MEXICO`, `RTW89_UKRAINE`, `RTW89_CHILE`, `RTW89_QATAR`, and `RTW89_THAILAND`.
- Generic PHY power-limit helpers in `phy.c`, especially `rtw89_phy_read_txpwr_limit()`, `rtw89_phy_fill_txpwr_limit_ax()`, and `rtw89_phy_set_txpwr_limit_ax()`.
- RTL8852C chip glue in `rtw8852c.c`, especially `rtw8852c_set_txpwr()` and the `.dflt_parms` chip-info assignment.

## Risks and Edge Cases

- The multidimensional initializer is easy to corrupt manually. A wrong index order changes regulatory behavior without compiler errors because the type still matches.
- Zero has fallback semantics, so accidentally changing a legitimate low limit to zero can silently select the `RTW89_WW` limit.
- `127` entries are intentionally common; treating them as ordinary dBm values in documentation or generated tooling would be misleading. They are table sentinels/high non-limiting values in the driver's power-limit space.
- 6 GHz rows include an extra power-mode axis. Mixing `[regd][reg6][ch_idx]` order with 5 GHz's `[regd][ch_idx]` order would cause severe regulatory misapplication.
- This is compliance-sensitive data. Regressions can cause underpowered links, certification failure, or over-limit transmission in specific countries/channels.

## Test Signals

- Build coverage: compile the `rtw89` driver with `rtw8852c_table.c`; type/dimension mismatches in these arrays or `rtw89_rfe_parms` pointers should fail at compile time.
- Runtime debug: enable `RTW89_DBG_TXPWR` and verify channel changes log `set txpwr limit with ch=... bw=...`, then inspect resulting TX power pages through existing debugfs/register tooling.
- Regulatory matrix checks: exercise 5 GHz and 6 GHz channels across domains such as FCC, ETSI, MKK, KCC, ACMA, CN, UK, and WW fallback, confirming zeros fall back and `127` entries do not become unintended caps.
- Channel-width checks: verify 20/40/80/160 MHz 5 GHz paths and 6 GHz power-mode selections, because both axes are present in this chunk.
- SAR/TPE interaction checks: confirm final MAC limits are the minimum of the table-derived value, SAR, and 6 GHz TPE constraint where applicable.
