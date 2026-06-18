# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.c lines 1-8987

## Scope

This chunk covers lines 1-8987 of `rtw8851b_table.c`, the first portion of the Realtek RTW89 RTL8851B static PHY and transmit-power table file. The chunk is data-only C: it has no executable functions, but it defines the bulk of the early register-init and regulatory power-limit arrays consumed later by exported `rtw89_8851b_*` descriptors outside this chunk. The requested range ends inside `rtw89_8851b_txpwr_lmt_ru_5g`, so that table is only partially visible here and must be reconciled with the next chunk before whole-file conclusions are finalized.

## Purpose

The file provides built-in default tables for the RTL8851B Wi-Fi PHY when firmware-provided PHY elements are absent or when chip/RFE selection points at built-in defaults. In this chunk, the tables encode:

- Baseband register programming for RTL8851B PHY bring-up.
- BB gain programming with conditional/headline rows understood by the generic PHY table parser.
- RF path A radio register programming for the single-radio RTL8851B path.
- NCTL microcode/control-block programming used during RF calibration/control initialization.
- Per-rate transmit-power offsets for the default and type2 RFE variants.
- Thermal tracking delta-swing tables for path A, 2 GHz, 5 GHz, and 2G CCK.
- Regulatory transmit-shape and transmit-power limit tables for 2 GHz, 5 GHz, and the start of RU-specific limits.

## Important Data Structures And Symbols

- `rtw89_8851b_phy_bb_regs[]` at line 9 is a `static const struct rtw89_reg2_def` array of `{addr, data}` pairs. It holds the main BB register script, ending at line 987. Rows include normal register writes plus values in the high synthetic address range used by the PHY table parser for condition/headline handling.
- `rtw89_8851b_phy_bb_reg_gain[]` at line 989 is another `rtw89_reg2_def` table, ending at line 1270. It starts with `0xF00...` headline rows and contains repeated gain rows selected by RFE/CV conditions.
- `rtw89_8851b_phy_radioa_regs[]` at line 1272 is the RF path A table, ending at line 2251. RTL8851B exposes one RF path in the chip info, so this is the radio table that backs `chip->rf_table[RF_PATH_A]`.
- `rtw89_8851b_phy_nctl_regs[]` at line 2253 is the NCTL table, ending at line 3245. It programs NCTL registers and embedded command/microcode-like words from the `0x8000` range through calibration/control sequences.
- `rtw89_8851b_txpwr_byrate[]` at line 3247 and `rtw89_8851b_txpwr_byrate_type2[]` at line 3285 are `struct rtw89_txpwr_byrate_cfg` arrays. Each row describes band, NSS, rate section, start index, packed byte count, and packed power data.
- `_txpwr_track_delta_swingidx_*` arrays at lines 3323-3359 are thermal compensation delta tables. The 5 GHz path-A tables are two-dimensional over subband/path slots; the 2 GHz and CCK path-A tables are one-dimensional arrays of `DELTA_SWINGIDX_SIZE` entries.
- `rtw89_8851b_tx_shape_lmt` and `rtw89_8851b_tx_shape_lmt_ru` at lines 3361-3408 map band/regulatory-domain combinations to transmit shaping selections for legacy/OFDM and RU modes.
- `rtw89_8851b_txpwr_lmt_2g` at lines 3410-4926 is a complete 2 GHz power-limit tensor indexed by bandwidth, transmit-chain count, rate-section limit class, beamforming flag, regulatory domain, and 2 GHz channel index.
- `rtw89_8851b_txpwr_lmt_5g` at lines 4928-6840 is a complete 5 GHz power-limit tensor indexed by bandwidth, transmit-chain count, rate-section limit class, beamforming flag, regulatory domain, and 5 GHz channel index.
- `rtw89_8851b_txpwr_lmt_ru_2g` at lines 6842-7601 is a complete RU-specific 2 GHz power-limit tensor indexed by RU size, transmit-chain count, regulatory domain, and 2 GHz channel index.
- `rtw89_8851b_txpwr_lmt_ru_5g` starts at line 7603. This chunk includes entries through line 8987, but the array continues beyond this chunk and is not closed here.

The relevant type definitions live outside this file: `struct rtw89_reg2_def` and `struct rtw89_phy_table` in `core.h`, `struct rtw89_txpwr_byrate_cfg` and `struct rtw89_txpwr_track_cfg` in `phy.h`, and `struct rtw89_rfe_parms` in `core.h`. The corresponding public table declarations are in `rtw8851b_table.h`, while the concrete descriptor initializers that bind these static arrays into exported `rtw89_8851b_*` objects are after this chunk.

## Control Flow And Consumers

There is no local control flow in this chunk. Runtime control is driven by generic RTW89 consumers:

- `rtw89_phy_init_bb_reg()` chooses `chip->bb_table` and `chip->bb_gain_table` unless firmware elements override them. Those descriptors later point at `rtw89_8851b_phy_bb_regs` and `rtw89_8851b_phy_bb_reg_gain`. The common `rtw89_phy_init_reg()` parser interprets headline and branch/check markers, selects rows by RFE type and chip version, and calls the table-specific config callback for each active row.
- `rtw89_phy_init_rf_reg()` iterates the chip RF paths and loads the RF table for each path. For RTL8851B the chip info references only path A, so the `rtw89_8851b_phy_radioa_regs` data is the RF programming source.
- `rtw89_phy_init_rf_nctl()` preinitializes NCTL state and then feeds `chip->nctl_table` into the same generic register-table parser, using BB-register writes for NCTL register programming.
- `rtw89_core_setup_rfe_parms()` selects an RFE parameter set from `chip->rfe_parms_conf`, optionally overlays firmware RFE data, then calls `rtw89_load_txpwr_table()` on the selected by-rate table. The built-in by-rate arrays in this chunk therefore seed `rtwdev->byr` when selected.
- `rtw89_phy_load_txpwr_byrate()` consumes each `rtw89_txpwr_byrate_cfg` row by unpacking `data` byte by byte into rate descriptors.
- `rtw89_phy_read_txpwr_limit()` and `rtw89_phy_read_txpwr_limit_ru()` index the selected `rtw89_rfe_parms` power-limit tensors by band, bandwidth or RU size, NSS, rate section, beamforming, regulatory domain, and channel index. The 2 GHz, 5 GHz, and RU arrays in this chunk feed those lookups once the later RFE descriptors point at them.
- Thermal tracking consumers in PHY/RFK code use the `rtw89_txpwr_track_cfg` pointers, which later reference these `_txpwr_track_delta_swingidx_*` arrays. The tables are expanded into firmware thermal offset tables using `DELTA_SWINGIDX_SIZE`.

## State And Persistence

All data in this chunk is `static const`; it is compiled into the driver image and never mutated in place. Runtime state is created in other modules by reading these tables into device structures or writing their values to hardware/firmware:

- Register tables persist as compiled defaults and are applied to device registers during initialization or reinitialization.
- By-rate power data is copied/unpacked into `rtwdev->byr`.
- RFE parameter selection stores a chosen `const struct rtw89_rfe_parms *` in `rtwdev->rfe_parms`; built-in tables remain immutable unless firmware RFE data causes a dynamically allocated replacement/overlay.
- Transmit-power limit arrays are not copied wholesale during normal lookup; they remain pointer-backed lookup tables from the selected RFE parameter set.
- The large number of `127` entries in power-limit tables appears to be a sentinel/max value used to represent unlimited, unavailable, or effectively disabled combinations, depending on the consumer's min/constraint logic.

## Dependencies And Integration Points

This chunk depends on `phy.h`, `reg.h`, and `rtw8851b_table.h`. Through those headers it depends on RTW89 core enums and dimensions such as `RTW89_BAND_NUM`, `RTW89_RS_TX_SHAPE_NUM`, `RTW89_REGD_NUM`, `RTW89_2G_BW_NUM`, `RTW89_5G_BW_NUM`, `RTW89_NTX_NUM`, `RTW89_RS_LMT_NUM`, `RTW89_BF_NUM`, `RTW89_2G_CH_NUM`, `RTW89_5G_CH_NUM`, `RTW89_RU_NUM`, and `DELTA_SWINGIDX_SIZE`.

Primary integration happens in `rtw8851b.c`, where the RTL8851B chip-info structure references the exported descriptors from this table file as `.bb_table`, `.bb_gain_table`, `.rf_table`, `.nctl_table`, `.dflt_parms`, and `.rfe_parms_conf`. The exported descriptor definitions are not in this chunk, but the arrays here are their backing storage. Regulatory integration also depends on `regd.c`/regulatory state because the power-limit lookup path maps the current regulatory domain to indices such as `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`, `RTW89_ACMA`, `RTW89_CN`, `RTW89_UK`, and `RTW89_WW`.

## Risks And Fragile Areas

- Array dimensionality is contract-critical. Any enum count or channel-index mapping change in `core.h` or PHY code can silently reinterpret designated initializers or leave unintended zero defaults.
- The power values are regulatory-sensitive. Incorrect values can reduce range, violate allowed limits, or disable channels/RU combinations. The dense use of `127` sentinels requires the downstream min/constraint logic to treat them consistently.
- The register tables include parser control rows encoded as synthetic addresses. Mechanical sorting, deduplication, or formatting that changes order would alter initialization behavior.
- The chunk boundary splits `rtw89_8851b_txpwr_lmt_ru_5g`; any research or validation that treats this chunk as a complete source file would miss the rest of the RU 5 GHz limits and all final descriptor wiring.
- Because this is compiled static data, many mistakes are compile-clean but behaviorally visible only on RTL8851B hardware, with symptoms such as failed NCTL polling, RF calibration failures, poor sensitivity, invalid EIRP, or channel-specific throughput drops.
- The type2 by-rate and later type2 limit tables support alternate RFE configurations. Only the by-rate type2 array appears in this chunk; the rest of the type2 power-limit/RFE descriptors are later in the file.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build with `W=1`/sparse-style checks to catch malformed initializers, enum-dimension drift, missing braces, or signedness issues in `s8` tables.
- Boot/probe RTL8851B hardware and confirm BB/RF/NCTL init completes without `invalid PHY package`, `failed to load CR`, RF H2C config warnings, or NCTL poll errors.
- Confirm `rtw89_core_setup_rfe_parms()` selects the expected default or type2 RFE parameters for observed efuse `rfe_type`, and that `rtw89_phy_load_txpwr_byrate()` populates sane per-rate entries.
- Exercise 2.4 GHz and 5 GHz association, scan, transmit, and RU/OFDMA paths across channels and regulatory domains to catch bad channel-index or regulatory-domain rows.
- Compare conducted power/EIRP and thermal tracking behavior against vendor calibration data, especially at boundaries where entries switch from concrete limits to `127`.
- For chunk reconciliation, verify the next chunk closes `rtw89_8851b_txpwr_lmt_ru_5g` and later descriptors point to all arrays declared here.

## Unresolved Cross-Chunk References

- `rtw89_8851b_txpwr_lmt_ru_5g` continues past line 8987 and must be completed by the following chunk before its regulatory coverage can be judged.
- The type2 limit arrays, descriptor initializers (`rtw89_8851b_phy_bb_table`, `rtw89_8851b_dflt_parms`, `rtw89_8851b_rfe_parms_conf`, etc.), and exact pointer wiring are after this chunk.
- Whole-file research should reconcile whether the default and type2 RFE parameter blocks point at the expected combinations of by-rate, limit, RU limit, and transmit-shape tables.
