# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 45613-51011

## Scope

This chunk is the final 5,399-line slice of the Realtek rtw89 RTL8852A table file. It begins inside the 5 GHz transmit-power limit initializer and continues through the end of the file. The content is almost entirely immutable calibration/regulatory data plus the exported descriptor objects that make the earlier table arrays visible to the chip, PHY, RF calibration, and transmit-power setup paths.

The chunk covers:

- The tail and majority of `rtw89_8852a_txpwr_lmt_5g`.
- All of `rtw89_8852a_txpwr_lmt_ru_2g`.
- All of `rtw89_8852a_txpwr_lmt_ru_5g`.
- The exported `rtw89_phy_table`, `rtw89_txpwr_table`, `rtw89_txpwr_track_cfg`, and `rtw89_rfe_parms` descriptors for RTL8852A.

## Purpose

The table data supplies hard-coded per-band transmit-power ceilings for RTL8852A. The ordinary 5 GHz limit table constrains non-RU rate-section power by bandwidth, transmit-chain count, rate-section limit class, beamforming state, regulatory domain, and 5 GHz channel index. The RU tables constrain HE/OFDMA resource-unit power by RU size/class, transmit-chain count, regulatory domain, and channel index for 2.4 GHz and 5 GHz.

The exported descriptors at the end of the file bind these raw arrays into the rtw89 driver framework. `rtw89_8852a_dflt_parms` is the primary integration object: it points `rule_2ghz` and `rule_5ghz` at the static non-RU and RU limit tables and points `byr_tbl` at the by-rate table loader descriptor. The RTL8852A chip-info object in `rtw8852a.c` uses this object as `.dflt_parms`.

## Important APIs, Types, And Objects

The static data follows the pointer shapes defined in `core.h`:

- `struct rtw89_txpwr_rule_5ghz` expects `lmt` with dimensions `[RTW89_5G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]` and `lmt_ru` with dimensions `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_5G_CH_NUM]`.
- `struct rtw89_txpwr_rule_2ghz` expects `lmt_ru` with dimensions `[RTW89_RU_NUM][RTW89_NTX_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `struct rtw89_rfe_parms` groups the by-rate table and the 2 GHz, 5 GHz, optional 6 GHz, differential antenna, and TX-shape rules selected for a device.
- `struct rtw89_phy_table` wraps a `struct rtw89_reg2_def` array plus a count and RF path.
- `struct rtw89_txpwr_table` wraps arbitrary table data plus a loader callback.
- `struct rtw89_txpwr_track_cfg` supplies temperature compensation delta-swing arrays to RF calibration code.

Objects visible in this chunk:

- `rtw89_8852a_txpwr_lmt_5g`: 5 GHz non-RU power limits. This chunk includes 2,288 explicit assignments from line 45613 through the closing brace at line 47901.
- `rtw89_8852a_txpwr_lmt_ru_2g`: 2.4 GHz RU power limits. It contains 1,093 explicit assignments between lines 47904 and 48998.
- `rtw89_8852a_txpwr_lmt_ru_5g`: 5 GHz RU power limits. It contains 1,951 explicit assignments between lines 49001 and 50953.
- `rtw89_8852a_phy_bb_table`, `rtw89_8852a_phy_radioa_table`, `rtw89_8852a_phy_radiob_table`, and `rtw89_8852a_phy_nctl_table`: wrappers for baseband, RF path A, RF path B, and NCTL register tables declared earlier in the file.
- `rtw89_8852a_byr_table`: static by-rate table descriptor with `.load = rtw89_phy_load_txpwr_byrate`.
- `rtw89_8852a_trk_cfg`: temperature tracking config that points to the delta-swing arrays declared earlier in this file.
- `rtw89_8852a_dflt_parms`: default RFE parameter bundle for RTL8852A, referencing the by-rate table and 2 GHz/5 GHz power limit arrays.

## Data Shape And Semantics

The limit tables use designated initializers, so unspecified entries default to zero in `.rodata`. In PHY lookup code, a zero regulatory-domain entry has special behavior: for ordinary and RU power limit lookups, the driver falls back to the `RTW89_WW` entry for the same channel index when the selected regulatory-domain value is zero. This makes zero an overloaded value: it can mean either an intentional zero only where lookup code treats zero literally or, in the main regulatory lookup path, "not populated; use worldwide fallback."

The value range visible in this chunk is 0 through 127. The value `127` appears frequently and is used as a permissive/sentinel-like maximum in many regulatory/channel cells, especially where a domain/channel combination should not further constrain power beyond other limits. Ordinary values are signed `s8` table cells in RF-power units later converted through chip-specific factors.

The chunk explicitly covers regulatory domains including `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, and `RTW89_UK`.

The 5 GHz non-RU table indexes include bandwidth, transmit-chain count, rate-section limit class, beamforming flag, regulatory domain, and a compact Realtek channel index. The chunk shows dense worldwide default entries first, followed by region-specific overrides. The 2 GHz RU table indexes 14 channel slots and includes dense worldwide defaults followed by regional overrides; channel index 13 commonly uses `127` for region-specific rows. The 5 GHz RU table mirrors the 5 GHz regulatory/channel override style using the smaller RU index shape.

## Control Flow And Integration

There is no executable control flow in this chunk beyond C initializers, but the runtime path is direct:

1. `rtw8852a.c` stores `&rtw89_8852a_dflt_parms` in the RTL8852A chip-info `.dflt_parms` field and uses the PHY table descriptors for BB, RF path A, RF path B, and NCTL setup.
2. `rtw89_core_setup_rfe_parms()` chooses an RFE parameter set from chip defaults or an RFE-specific config. For RTL8852A, `rfe_parms_conf` is `NULL`, so the default parameter object is selected unless firmware RFE data overrides it.
3. `rtw89_load_rfe_data_from_fw()` may replace pieces of the static `rtw89_rfe_parms` with firmware-provided by-rate or limit data when valid firmware tables exist. Otherwise these static tables remain authoritative.
4. `rtw89_load_txpwr_table()` calls the table's load callback. For `rtw89_8852a_byr_table`, `rtw89_phy_load_txpwr_byrate()` expands compact by-rate entries into `rtwdev->byr`.
5. Transmit-power limit readers in `phy.c` consult `rtwdev->rfe_parms`. For RU limits, `rtw89_phy_read_txpwr_limit_ru()` indexes `rule_2ghz.lmt_ru`, `rule_5ghz.lmt_ru`, or `rule_6ghz.lmt_ru`, applies regulatory fallback to `RTW89_WW`, applies optional antenna-gain differential limits, converts RF units to MAC units, then clamps against SAR and TPE constraints.
6. Fill helpers such as `rtw89_phy_fill_txpwr_limit_ru_*_ax()` repeatedly call the reader to populate hardware command structures for each bandwidth/RU arrangement.

The temperature tracking descriptor integrates separately with `rtw8852a_rfk.c`, where thermal tracking logic selects arrays from `rtw89_8852a_trk_cfg` by band, RF path, and subband.

## State And Persistence Behavior

The tables in this chunk are compile-time constants stored in the kernel image. They do not mutate at runtime, allocate memory, or persist state externally. Runtime state is created by consumers:

- `rtwdev->rfe_parms` stores the selected static or firmware-augmented parameter bundle.
- `rtwdev->byr` stores expanded by-rate offsets loaded from `rtw89_8852a_byr_table`.
- Regulatory state, SAR state, TPE constraints, current channel, and firmware feature flags are held elsewhere and determine how these constants are interpreted.

Because the data is static, any update requires rebuilding the driver. Firmware RFE data can override supported pieces at runtime, but the static tables remain fallback/default behavior.

## Dependencies

This chunk depends on dimension and enum constants from the rtw89 core/PHY headers, including `RTW89_5G_BW_NUM`, `RTW89_2G_CH_NUM`, `RTW89_5G_CH_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_RU_NUM`, and `RTW89_REGD_NUM`, plus regulatory enum values such as `RTW89_WW`, `RTW89_FCC`, and `RTW89_ETSI`.

It also depends on arrays declared earlier in the same file:

- `rtw89_8852a_phy_bb_regs`
- `rtw89_8852a_phy_radioa_regs`
- `rtw89_8852a_phy_radiob_regs`
- `rtw89_8852a_phy_nctl_regs`
- `rtw89_8852a_txpwr_byrate`
- `_txpwr_track_delta_swingidx_*`
- `rtw89_8852a_txpwr_lmt_2g`, which is referenced in `rtw89_8852a_dflt_parms` but is declared before this chunk

The exported declarations are in `rtw8852a_table.h`, and the chip-info consumer is in `rtw8852a.c`.

## Risks And Edge Cases

- Dimension/order mismatches are high risk. The arrays are positional and deeply nested; swapping bandwidth, NTX, rate-section, BF, regulatory, or channel dimensions can compile while producing wrong power limits at runtime.
- Zero values are semantically sensitive because PHY code treats zero regulatory entries as missing and falls back to `RTW89_WW`. An intended low limit encoded as zero may not behave as a strict zero limit in the main lookup path.
- `127` values likely represent a maximum/unlimited policy cell. Misplacing them can silently remove a regulatory cap for a domain/channel/RU combination.
- The chunk starts after the declaration of `rtw89_8852a_txpwr_lmt_5g`, so reviewers of this chunk alone must remember that the initializer shape is inherited from line 45571.
- RTL8852A advertises 2.4 GHz and 5 GHz support only in `rtw8852a.c`; 6 GHz rule fields in `rtw89_rfe_parms` remain unused/default for this chip. Accidentally wiring 6 GHz consumers to these defaults would be invalid.
- `support_ant_gain` is false for RTL8852A in the observed chip info, so differential antenna-gain rules are not populated here. If that feature were enabled later, default `rule_da_*` pointers would need valid data before `rtw89_can_apply_ant_gain()` could safely allow DA limit use.
- The final descriptors are external ABI-like symbols inside the driver. Renaming or making them static without updating `rtw8852a_table.h` and `rtw8852a.c` breaks chip registration or module linkage.

## Test And Validation Signals

Useful validation signals for this chunk are mostly build-time and hardware/regulatory behavior oriented:

- Compile with the rtw89 RTL8852A objects enabled to catch descriptor type mismatches, missing externs, and array-shape errors.
- Confirm `ARRAY_SIZE()` values in the final `rtw89_phy_table`/`rtw89_txpwr_table` descriptors match the intended source arrays.
- Exercise RTL8852A bring-up paths that load BB, RF A, RF B, NCTL, by-rate, and default RFE parameters.
- On hardware, test 2.4 GHz and 5 GHz association across representative channels and bandwidths, especially DFS/high-5 GHz channel indexes where the tables contain many region-specific overrides.
- Use rtw89 debugfs transmit-power views, where available, to inspect selected normal and RU power limits for multiple regulatory domains and verify fallback from domain-specific zero cells to `RTW89_WW`.
- Regulatory regression tests should compare effective limits for FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, and UK against vendor/regulatory reference data.
- RF thermal tracking tests should verify that `rtw89_8852a_trk_cfg` still maps path A/path B and 2 GHz/5 GHz arrays expected by `rtw8852a_rfk.c`.

## Cross-Chunk Notes

This chunk cannot fully describe the source file alone because many referenced arrays are declared earlier. The final merge lane should combine this report with earlier chunks covering the BB/RF/NCTL register arrays, by-rate table, delta-swing arrays, and the beginning of the 2 GHz and 5 GHz transmit-power limit tables.
