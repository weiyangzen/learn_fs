# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.c lines 8072-16047

## Scope

This chunk covers a large data-driven section of the RTL8852B rtw89 PHY table source. It starts in the middle of `rtw89_8852b_phy_radiob_regs[]`, includes the end of the RF path-B register script, the full `rtw89_8852b_phy_nctl_regs[]` NCTL script, the by-rate transmit-power table, thermal tracking delta-swing tables, transmit-shape limits, and the beginning of the 2.4 GHz regulatory transmit-power limit matrix.

The range is not standalone C logic. Its behavior comes from how rtw89 generic PHY and tx-power code interprets static arrays of `struct rtw89_reg2_def`, `struct rtw89_txpwr_byrate_cfg`, and multidimensional regulatory limit tables.

## Purpose

The tables in this chunk provide chip-specific calibration and policy constants for RTL8852B:

- RF path B initialization entries program radio registers for the second RF chain, including conditional branches keyed by RFE type and chip cut/version.
- NCTL entries initialize the baseband network-control/calibration engine around addresses `0x8000` through `0x8cb4`, finishing with control writes to `0x8080` and `0x8088`.
- By-rate transmit-power entries define packed per-rate power baselines for 2.4 GHz and 5 GHz across CCK/OFDM/MCS/HE-style rate sections and NSS combinations.
- Delta-swing tables define thermal compensation offsets for TSSI tracking by band, RF path, direction, subband, and CCK/OFDM distinction.
- Transmit-shape limit tables select regulatory shaping modes per band and regulatory domain.
- The 2.4 GHz power-limit matrix gives per-bandwidth, per-transmit-chain, per-rate-section, per-beamforming, per-regulatory-domain, per-channel limits used by runtime power queries.

## Important APIs, Types, and Data

- `struct rtw89_reg2_def` is a simple `{ addr, data }` pair. For normal BB/NCTL writes `addr` is a baseband register address. For RF tables, low register numbers are RF register addresses and high pseudo-addresses encode the rtw89 conditional table language.
- `rtw89_8852b_phy_radiob_regs[]` is declared earlier at line 7136 and ends in this chunk at line 13249. Lines 8072-13249 contribute about 5,177 register-table entries to RF path B.
- `rtw89_8852b_phy_nctl_regs[]` spans lines 13251-14572 and contains about 1,320 BB/NCTL register writes.
- `struct rtw89_txpwr_byrate_cfg` encodes `{ band, nss, rate-section, shift, len, data }`; each byte in `data` becomes one signed/unsigned raw by-rate power entry after `rtw89_phy_load_txpwr_byrate()` unpacks it.
- `rtw89_8852b_txpwr_byrate[]` has 24 entries. It covers band index `0` and `1`, multiple NSS/rate-section combinations, and packed values such as `0x50505050`, `0x484c5050`, `0x44484c50`, and `0x34383c40`.
- `_txpwr_track_delta_swingidx_*` arrays provide `DELTA_SWINGIDX_SIZE` thermal compensation tables. The 5 GHz tables are indexed by subband group and RF path flavor (`5ga`/`5gb`, positive/negative); the 2.4 GHz tables are flat path/rate-family tables for OFDM and CCK.
- `rtw89_8852b_tx_shape_lmt` and `rtw89_8852b_tx_shape_lmt_ru` set regulatory-domain shaping mode IDs. FCC, IC, and Mexico select nonzero shape IDs in several 2.4/5 GHz cases, while ETSI, MKK, KCC, ACMA, CN, Qatar, UK, Ukraine, and Chile are zero in this chunk.
- `rtw89_8852b_txpwr_lmt_2g` begins at line 14739. This chunk includes its worldwide defaults and early domain-specific assignments through `[0][0][2][0][RTW89_CN][10]` at line 16047, not the full array.

## Control Flow

At device initialization, `rtw8852b.c` installs these tables into `struct rtw89_chip_info`: `.rf_table[RF_PATH_B] = &rtw89_8852b_phy_radiob_table`, `.nctl_table = &rtw89_8852b_phy_nctl_table`, `.dflt_parms = &rtw89_8852b_dflt_parms`, and `.bb_table`/`.bb_gain_table` for earlier arrays outside this chunk.

RF initialization calls `rtw89_phy_init_rf_reg()`. It selects the compiled radio-B table unless firmware elements override it, then calls `rtw89_phy_init_reg()`. The generic table interpreter first chooses a headline branch based on RFE type and chip cut using `get_phy_headline()`, `get_phy_target()`, and `get_phy_compare()`. It then walks conditional opcodes in the `addr` high nibble: `0x8`/`0x9` branch-if/elif, `0xa` else, `0xb` end, and `0x4` check. Matched RF path-B entries are applied through `rtw89_phy_config_rf_reg_v1()`, which writes RF registers and stores larger-address entries for firmware H2C replay.

NCTL initialization calls `rtw89_phy_init_rf_nctl()`. Before consuming this table, the driver runs an NCTL preinit path that enables IQK/DPK clocks and polls `R_NCTL_CFG`/`0x8080`. It then applies `rtw89_8852b_phy_nctl_regs[]` through `rtw89_phy_config_bb_reg()`, so delay pseudo-registers and `BYPASS_CR_DATA` are handled generically while normal entries become baseband writes.

Transmit-power setup is indirect. `rtw89_8852b_dflt_parms` points `.byr_tbl` at `rtw89_8852b_byr_table`; that table's `.load` callback is `rtw89_phy_load_txpwr_byrate()`. The loader iterates each packed config, seeks the target by-rate slot via `rtw89_phy_raw_byr_seek()`, and writes one byte per rate index. Power-limit queries later read `rtw89_8852b_txpwr_lmt_2g` through `rtw89_phy_get_txpwr_limit()` and use regulatory fallback: if the selected regulatory domain entry is zero, the driver uses the `RTW89_WW` entry for that channel.

Thermal tracking uses `rtw89_8852b_trk_cfg`, which is declared later in the file and points at the delta-swing arrays in this chunk. Runtime TSSI code chooses the appropriate table by band/subband/path and expands the 30-entry delta-swing data into a 128-entry firmware compensation table around the programmed package thermal value.

## State and Persistence Behavior

All data here is compiled into the driver image as static `const` tables. The chunk does not allocate memory, mutate state, or persist anything to disk.

Runtime state changes happen only when other code consumes the tables:

- RF and NCTL table application writes hardware registers and may also stage RF entries into `struct rtw89_fw_h2c_rf_reg_info` so firmware can mirror RF settings.
- By-rate loading writes decoded values into `rtwdev->byr`.
- Regulatory limit tables remain read-only and are referenced through `struct rtw89_rfe_parms` in `rtw89_8852b_dflt_parms`.
- Thermal tracking tables remain read-only and are referenced through `rtw89_8852b_trk_cfg`; generated compensation data is placed into firmware H2C payloads at runtime.

## Dependencies and Integration Points

This chunk depends on:

- `phy.h` for conditional table macros, `struct rtw89_txpwr_byrate_cfg`, and `struct rtw89_txpwr_track_cfg`.
- `core.h` for `struct rtw89_reg2_def`, `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, `struct rtw89_rfe_parms`, and regulatory/power-limit array shapes.
- `phy.c` for `rtw89_phy_init_reg()`, `rtw89_phy_config_rf_reg_v1()`, `rtw89_phy_config_bb_reg()`, `rtw89_phy_load_txpwr_byrate()`, TSSI thermal-table expansion, and tx-power-limit query logic.
- `rtw8852b.c` for chip-info wiring that makes these tables active on RTL8852B.
- rtw89 regulatory code for mapping country/domain state to `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`, `RTW89_QATAR`, `RTW89_UK`, and fallback `RTW89_WW`.

## Risks and Edge Cases

- The requested range starts inside `rtw89_8852b_phy_radiob_regs[]`, so any isolated review must remember that headline entries and earlier path-B setup are outside this chunk. Misreading the range as a complete table would miss branch-selection context.
- RF pseudo-addresses and real RF register addresses share the same `{ addr, data }` structure. A wrong conditional opcode, missing branch end, or malformed headline can make `rtw89_phy_init_reg()` skip or wrongly apply large sections of path-B initialization.
- `rtw89_phy_config_rf_reg_v1()` treats RF addresses below `0x100` differently from larger entries when staging firmware replay data. Changing table address conventions can affect both direct RF writes and firmware-side RF state.
- NCTL writes are order-sensitive. The tail writes to `0x8080`/`0x8088` are control-state transitions, not arbitrary constants; reordering them around the preinit poll or calibration data block can break RFK/NCTL readiness.
- By-rate entries pack four byte-sized values into one `u32`. Endianness of the unpacking is logical little-endian via shifting, so editing a hex literal changes rate indexes from low byte upward.
- Power-limit table values use zero as "no explicit domain limit, fall back to WW" in query code, while nonzero values are real quarter-dB-style RF-domain limits later converted to MAC units. The sentinel value `127` appears as an effectively disabled/not-applicable cap in parts of these regulatory matrices.
- This chunk ends mid-`rtw89_8852b_txpwr_lmt_2g`; later assignments may override or complete additional indices. Merge-level research should reconcile the full array before drawing complete regulatory conclusions.
- Regulatory data is compliance-sensitive. Off-by-one channel indexes, wrong regulatory-domain constants, or swapped NTX/rate-section dimensions can produce incorrect EIRP limits.

## Test Signals

Useful validation signals for this chunk include:

- Boot or module-load logs on RTL8852B with `RTW89_DBG_PHY_TRACK`, `RTW89_DBG_TXPWR`, and `RTW89_DBG_TSSI` enabled; look for invalid PHY package, NCTL poll failure, RF H2C config failure, unknown by-rate section, or unexpected tx-power warnings.
- RF bring-up checks that both RF paths initialize, especially path B, and that scan/association work on both antennas after `rtw89_phy_init_rf_reg()`.
- Calibration smoke tests covering IQK/DPK/TSSI after NCTL initialization; failures around `0x8080` readiness or RFK sequencing point back to the NCTL script.
- Tx-power unit tests or debugfs inspection comparing decoded by-rate values in `rtwdev->byr` against the packed `rtw89_8852b_txpwr_byrate[]` byte order.
- Regulatory tx-power tests on 2.4 GHz channels 1-14 across FCC, ETSI, MKK, IC, KCC, ACMA, Chile, Ukraine, Mexico, CN, Qatar, UK, and WW fallback domains.
- Thermal chamber or simulated-thermal tests that verify positive/negative delta-swing index selection for 2.4 GHz CCK/OFDM and 5 GHz path A/path B subbands.

## Cross-Chunk Notes

Earlier chunks for this file contain the start of `rtw89_8852b_phy_radiob_regs[]`, the full BB and radio-A tables, and BB gain data. Later chunks contain the rest of `rtw89_8852b_txpwr_lmt_2g`, the 5 GHz limit matrices, RU-limit matrices, final `struct rtw89_phy_table` wrappers, `rtw89_8852b_trk_cfg`, and `rtw89_8852b_dflt_parms`. The final reconciled report should connect this chunk's data with those wrappers rather than treating the static arrays as independent exported APIs.
