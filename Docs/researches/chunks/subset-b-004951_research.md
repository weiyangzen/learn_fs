# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c lines 16048-22927

## Scope

This chunk is the final 6,880-line tail of the RTL8852B rtw89 table source. It starts in the middle of `rtw89_8852b_txpwr_lmt_2g[]`, completes that 2.4 GHz regulatory transmit-power limit matrix, then defines the complete 5 GHz non-RU limit matrix, the complete 2.4 GHz and 5 GHz OFDMA RU limit matrices, and the exported descriptor objects that connect all earlier arrays in `rtw8852b_table.c` to the rest of the driver.

The range is almost entirely static `const` data. Its behavior is produced by generic rtw89 PHY, RF, firmware, and transmit-power code that dereferences these tables through `struct rtw89_chip_info` and `struct rtw89_rfe_parms`.

## Purpose

- Finish `rtw89_8852b_txpwr_lmt_2g`, the per-bandwidth/per-chain/per-rate/per-beamforming/per-regulatory-domain/per-channel 2.4 GHz power-limit table begun in the previous chunk.
- Define `rtw89_8852b_txpwr_lmt_5g`, the equivalent 5 GHz limit matrix for 20/40/80/160 MHz channel widths, 1TX/2TX, CCK/OFDM/MCS-style rate-section indexes where applicable, non-BF/BF modes, regulatory domains, and 53 channel indexes.
- Define `rtw89_8852b_txpwr_lmt_ru_2g` and `rtw89_8852b_txpwr_lmt_ru_5g`, the OFDMA resource-unit transmit-power caps used for RU26/RU52/RU106 and wider AX RU sections.
- Export `rtw89_phy_table` wrappers for the baseband, BB gain, RF path A, RF path B, and NCTL register scripts declared earlier in the file.
- Export `rtw89_8852b_trk_cfg`, which binds thermal tracking delta-swing tables declared in the previous chunk to RTL8852B RFK/TSSI code.
- Export `rtw89_8852b_dflt_parms`, the default RTL8852B RFE power-parameter bundle used when no firmware/ACPI RFE override is selected.

## Important APIs, Types, and Data

- `rtw89_8852b_txpwr_lmt_2g` has type `s8 [RTW89_2G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`. This chunk owns the table's tail from `[0][0][2][0][RTW89_QATAR][10]` through the closing brace at line 16926.
- `rtw89_8852b_txpwr_lmt_5g` spans lines 16928-19571 with shape `s8 [RTW89_5G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `rtw89_8852b_txpwr_lmt_ru_2g` spans lines 19573-20668 with shape `s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `rtw89_8852b_txpwr_lmt_ru_5g` spans lines 20670-22857 with shape `s8 [RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `RTW89_2G_BW_NUM` covers 20/40 MHz; `RTW89_5G_BW_NUM` covers 20/40/80/160 MHz; `RTW89_NTX_NUM` is 1TX/2TX; `RTW89_BF_NUM` is non-BF/BF; `RTW89_2G_CH_NUM` is 14 and `RTW89_5G_CH_NUM` is 53.
- Regulatory-domain indexes include `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, and `RTW89_UK`. Zero-initialized cells are meaningful because runtime code falls back from a selected domain to `RTW89_WW` when the selected cell is zero.
- The repeated `127` values are explicit high/sentinel caps used for unsupported or effectively unconstrained combinations. They differ from zero because zero triggers WW fallback in the generic readers.
- `rtw89_8852b_phy_bb_table`, `rtw89_8852b_phy_bb_gain_table`, `rtw89_8852b_phy_radioa_table`, `rtw89_8852b_phy_radiob_table`, and `rtw89_8852b_phy_nctl_table` are `struct rtw89_phy_table` descriptors. They point to register arrays defined earlier, set `n_regs` with `ARRAY_SIZE`, and assign `RF_PATH_A`/`RF_PATH_B` plus `rtw89_phy_config_rf_reg_v1` for RF tables.
- `rtw89_8852b_byr_table` is a file-local `struct rtw89_txpwr_table` wrapper around `rtw89_8852b_txpwr_byrate[]`; its loader is `rtw89_phy_load_txpwr_byrate`.
- `rtw89_8852b_trk_cfg` maps each thermal delta-swing member to the 2.4 GHz/5 GHz, path A/path B, positive/negative, and CCK/OFDM tables declared before this chunk.
- `rtw89_8852b_dflt_parms` is the exported `struct rtw89_rfe_parms` bundle. It points `.byr_tbl` at the by-rate wrapper, `.rule_2ghz`/`.rule_5ghz` at normal and RU limit matrices, and `.tx_shape` at shaping-limit tables from the previous chunk.

## Control Flow

There is no executable control flow in this chunk. Runtime paths are table-driven:

1. `rtw8852b.c` installs the exported PHY descriptors into `rtw8852b_chip_info`: `.bb_table`, `.bb_gain_table`, `.rf_table[RF_PATH_A]`, `.rf_table[RF_PATH_B]`, `.nctl_table`, and `.dflt_parms`.
2. Generic PHY initialization calls `rtw89_phy_init_bb_reg()`, `rtw89_phy_init_rf_reg()`, and `rtw89_phy_init_rf_nctl()`. Those functions choose these descriptors from chip info and pass their `regs`, `n_regs`, `rf_path`, and optional `.config` callback into `rtw89_phy_init_reg()`.
3. RF path A and B tables use `rtw89_phy_config_rf_reg_v1`; BB, BB gain, and NCTL use the generic BB register writer path. The register arrays themselves are outside this chunk, but this tail makes them externally visible through `rtw8852b_table.h`.
4. During transmit-power setup, rtw89 selects `rtwdev->rfe_parms` from chip defaults or firmware/ACPI overrides. For RTL8852B default operation, `rtw89_8852b_dflt_parms` supplies the by-rate, normal limit, RU limit, and shaping tables.
5. `rtw89_phy_load_txpwr_byrate()` decodes `rtw89_8852b_byr_table` into `rtwdev->byr`; later MAC/firmware power programming combines by-rate data with regulatory limits.
6. `rtw89_phy_read_txpwr_limit()` indexes the 2.4/5 GHz normal matrices by band, bandwidth, transmit chain count, rate section, beamforming state, regulatory domain, and channel index. If the selected regulatory value is zero, it retries the same tuple with `RTW89_WW`.
7. `rtw89_phy_read_txpwr_limit_ru()` does the same for RU limits, keyed by band, RU type, transmit chain count, regulatory domain, and channel index.
8. The limit readers convert RF-domain values to MAC-domain units with `rtw89_phy_txpwr_rf_to_mac()` and then clamp against SAR, TPE constraint, and optional antenna-gain/DA limits.
9. RTL8852B RFK/TSSI code reads `rtw89_8852b_trk_cfg` directly to select thermal compensation tables based on band, subband, RF path, and temperature direction.

## State and Persistence Behavior

All tables in this chunk are compile-time constants in the driver image. The chunk does not allocate memory, write files, mutate global state, or perform I/O.

State changes happen only in consumers:

- PHY/RF/NCTL descriptors cause hardware register writes when the generic init path consumes their earlier register arrays.
- The by-rate table is decoded into `rtwdev->byr`.
- `rtwdev->rfe_parms` points at `rtw89_8852b_dflt_parms` unless firmware elements or board-specific RFE configuration replace it.
- Normal and RU limit matrices remain read-only and are consulted whenever tx-power H2C payloads or limit structures are filled for the current channel.
- Thermal delta-swing arrays remain read-only; runtime RFK/TSSI code derives compensation offsets from them and sends/uses those derived values elsewhere.

## Dependencies and Integration Points

- `rtw8852b_table.h` declares the exported symbols defined at the end of this chunk.
- `rtw8852b.c` is the chip-info integration point that makes these tables active for RTL8852B devices.
- `core.h` defines `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, `struct rtw89_rfe_parms`, regulatory-domain enums, channel-count constants, bandwidth constants, and matrix shapes.
- `phy.h` and `phy.c` provide `rtw89_phy_config_rf_reg_v1`, `rtw89_phy_load_txpwr_byrate`, PHY register initialization, by-rate loading, normal tx-power limit reading, and RU tx-power limit reading.
- `fw.c` can load firmware-provided transmit-power/RFE data and can clone/override `struct rtw89_rfe_parms`; this matters because `rtw89_8852b_dflt_parms` is a default, not necessarily the only possible runtime source.
- `rtw8852b_rfk.c` consumes `rtw89_8852b_trk_cfg` for chip-specific thermal tracking.
- mac80211/cfg80211 regulatory state feeds `rtw89_regd_get()`, which selects the regulatory-domain dimension used to index these matrices.

## Risks and Edge Cases

- The requested range starts mid-`rtw89_8852b_txpwr_lmt_2g`; conclusions about the full 2.4 GHz matrix must include the previous chunk.
- Regulatory power data is compliance-sensitive. Swapping dimension order, channel indexes, NTX indexes, rate-section indexes, or regulatory-domain enum positions can produce illegal or overly restrictive transmit power.
- Zero and `127` are not interchangeable. Zero means "no explicit value here, fall back to WW"; `127` is an explicit table value and prevents fallback.
- 5 GHz channel indexes are not simple IEEE channel numbers. Runtime conversion uses `rtw89_channel_to_idx()`, so table edits must align with the driver's internal 53-entry channel index scheme.
- Wider bandwidth fill paths read multiple adjacent channel offsets, such as `ch +/- 2`, `+/- 4`, `+/- 6`, `+/- 8`, `+/- 10`, and `+/- 14`. Missing edge entries or incorrect center-channel assumptions can affect 40/80/160 MHz limit generation.
- RU limit tables are separate from normal MCS/OFDM limits. Keeping one updated while leaving the other stale can make OFDMA behavior diverge from non-OFDMA behavior on the same regulatory domain and channel.
- `rtw89_8852b_byr_table` is intentionally `static`; external code accesses it only through `rtw89_8852b_dflt_parms`. Removing or exporting it directly would change the table ownership model.
- The RF table wrappers depend on `.config = rtw89_phy_config_rf_reg_v1` for both radio paths. Accidentally omitting `.config` would route RF table entries through the default init behavior and break RF register programming semantics.
- `rtw89_8852b_dflt_parms` has no 6 GHz rules and no DA-specific rules populated. That is consistent with RTL8852B 2.4/5 GHz support, but consumers must continue to validate band support before indexing.

## Test Signals

- Build coverage for `rtw8852b_table.c` catches type/shape mismatches in the multidimensional initializers and exported descriptors.
- Module load or boot on RTL8852B should show successful BB/RF/NCTL initialization with no invalid PHY package, invalid RF table, or NCTL polling failures.
- Regulatory smoke tests should compare reported/programmed tx-power limits across 2.4 GHz channels 1-14 and representative 5 GHz channels for FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, UK, and WW fallback.
- 20/40/80/160 MHz 5 GHz channel tests should verify the multi-offset fill paths do not read unintended zero fallback or sentinel values.
- OFDMA validation should exercise RU26/RU52/RU106 limit generation in both 2.4 GHz and 5 GHz, especially domains/channels where normal and RU limits intentionally differ.
- Debug output around `RTW89_DBG_TXPWR` and tx-power H2C payloads can confirm that `rtw89_phy_read_txpwr_limit()` and `rtw89_phy_read_txpwr_limit_ru()` select expected domain values and fall back to `RTW89_WW` only when the selected cell is zero.
- Thermal or simulated-temperature tests should verify `rtw89_8852b_trk_cfg` still selects the expected positive/negative delta-swing table for path A/path B and 2.4/5 GHz operation.

## Cross-Chunk Notes

The previous chunk contains the by-rate table, thermal delta-swing arrays, transmit-shape tables, and the beginning of `rtw89_8852b_txpwr_lmt_2g`. This chunk finishes the power-limit data and publishes the descriptor objects that make the entire file usable by the RTL8852B driver. The later merge/reconciliation report should describe `rtw8852b_table.c` as one cohesive data provider rather than treating this tail's exported wrappers separately from the earlier static arrays they reference.
