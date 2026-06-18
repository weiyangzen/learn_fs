# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.c lines 37905-45612

## Scope

This chunk covers the tail portion of `rtw89_8852a_phy_radiob_regs`, the full
`rtw89_8852a_phy_nctl_regs` table, the complete
`rtw89_8852a_txpwr_byrate` table, all 8852A thermal delta swing index arrays,
the complete `rtw89_8852a_txpwr_lmt_2g` table, and the opening entries of
`rtw89_8852a_txpwr_lmt_5g`. It is data-heavy chip-parameter code rather than
procedural C, but these constants directly drive RF/BB register programming and
transmit-power policy for RTL8852A.

## Purpose

The data in this range supplies RTL8852A-specific PHY/RF initialization and
power-control parameters to the generic rtw89 AX PHY code:

- The Radio-B register records finish configuring RF path B. The entries are
  `struct rtw89_reg2_def` address/data pairs consumed through
  `rtw89_8852a_phy_radiob_table`.
- The NCTL register table initializes the RF calibration control block after
  the generic AX NCTL preinit sequence has enabled IQK/DPK clocks, path resets,
  and the NCTL state machine.
- The by-rate table seeds `rtwdev->byr` with per-band, per-NSS, per-rate-section
  power values used when programming `R_AX_PWR_BY_RATE` and rate-offset control.
- The delta swing index arrays provide temperature compensation curves for 2 GHz
  and 5 GHz, path A and path B, positive and negative thermal deltas.
- The 2 GHz and beginning 5 GHz power-limit arrays encode regulatory and
  operating-mode limits indexed by bandwidth, transmit-chain count, rate
  section, beamforming state, regulatory domain, and channel index.

## Important APIs, Types, And Symbols

- `struct rtw89_reg2_def`: register initializer pair `{ addr, data }`. In this
  chunk it represents Radio-B RF writes and NCTL/baseband writes.
- `rtw89_8852a_phy_nctl_regs`: static NCTL table beginning at line 42246. It is
  later exported through `rtw89_8852a_phy_nctl_table`.
- `struct rtw89_txpwr_byrate_cfg`: compact by-rate power record with fields
  `band`, `nss`, `rs`, `shf`, `len`, and packed byte `data`.
- `rtw89_8852a_txpwr_byrate`: 24 compact entries that initialize CCK, OFDM, MCS,
  HEDCM, and offset sections for 2 GHz and 5 GHz.
- `struct rtw89_txpwr_track_cfg`: points to the thermal swing arrays defined in
  this chunk. The file later exposes them through `rtw89_8852a_trk_cfg`.
- `rtw89_8852a_txpwr_lmt_2g`: complete 2 GHz limit tensor:
  `[RTW89_2G_BW_NUM][RTW89_NTX_NUM][RTW89_RS_LMT_NUM][RTW89_BF_NUM][RTW89_REGD_NUM][RTW89_2G_CH_NUM]`.
- `rtw89_8852a_txpwr_lmt_5g`: 5 GHz limit tensor starts in this chunk and
  continues beyond the assigned line range.
- `RTW89_WW`, `RTW89_FCC`, `RTW89_ETSI`, `RTW89_MKK`, `RTW89_IC`, `RTW89_KCC`,
  `RTW89_ACMA`, `RTW89_CHILE`, `RTW89_UKRAINE`, `RTW89_MEXICO`, `RTW89_CN`,
  `RTW89_QATAR`, and `RTW89_UK`: regulatory-domain indexes used by the limit
  arrays.

## Control Flow And Data Flow

There are no functions defined in this chunk. Runtime control flow enters these
tables through chip descriptors and generic PHY helpers:

1. `rtw8852a_chip_info` points `.rf_table[RF_PATH_B]` to
   `rtw89_8852a_phy_radiob_table` and `.nctl_table` to
   `rtw89_8852a_phy_nctl_table`.
2. RF initialization calls `rtw89_phy_init_rf_reg()`, which selects each RF path
   table from firmware elements if present, otherwise from `chip->rf_table[]`.
   It passes each `struct rtw89_reg2_def` to `rtw89_phy_config_rf_reg()` or the
   table-specified config hook.
3. NCTL initialization calls `rtw89_phy_init_rf_nctl()`. For AX chips this first
   calls `rtw89_phy_preinit_rf_nctl_ax()`, which enables IQK/DPK related clocks,
   resets path state, writes `R_NCTL_CFG`, and polls NCTL register `0x8080` for
   readiness. It then loads `chip->nctl_table` with `rtw89_phy_config_bb_reg()`.
4. `rtw89_8852a_dflt_parms` later points `.byr_tbl` at the local by-rate table
   and `.rule_2ghz.lmt` / `.rule_5ghz.lmt` at the power-limit tensors.
5. The by-rate table is loaded by `rtw89_phy_load_txpwr_byrate()`, which expands
   packed bytes into `rtwdev->byr[band][bw]` slots using
   `rtw89_phy_raw_byr_seek()`.
6. Channel changes eventually use `rtw89_phy_set_txpwr_byrate_ax()` and
   `rtw89_phy_set_txpwr_limit_ax()` to read the expanded by-rate and limit data,
   pack four signed bytes into 32-bit MAC power registers, and write
   `R_AX_PWR_BY_RATE` / `R_AX_PWR_LMT` pages.

The RF table entries include many high-bit encoded addresses such as
`0x80010000`, `0x90010001` through `0x90360002`, `0xA0000000`, and
`0xB0000000`, interleaved with low RF addresses such as `0x03f`, `0x033`,
`0x0de`, `0x087`, and `0x06f`. These are not ordinary MMIO offsets. They are
condition or branch marker encodings interpreted by the PHY table loader through
`get_phy_cond()`, `get_phy_target()`, and related helpers before actual writes
are issued.

## State And Persistence Behavior

All data in this range is static `const` data compiled into the driver module.
It is not persisted to disk and is not mutated in place. Runtime state changes
occur when generic PHY code copies or applies these constants:

- RF and NCTL register entries are applied to hardware registers during device
  initialization and calibration setup.
- By-rate entries are expanded into the in-memory `rtwdev->byr` cache.
- Power-limit entries remain read-only tables and are queried dynamically when
  building MAC power-limit pages for a band, bandwidth, channel, NSS/NTX count,
  rate section, and regulatory domain.
- Thermal swing arrays remain read-only and are referenced through
  `rtw89_8852a_trk_cfg` by RF calibration or tracking code outside this chunk.

Firmware element support can override some built-in tables. `rtw89_phy_init_reg`
chooses firmware-supplied RF/NCTL tables when `rtwdev->fw.elm_info` has them,
otherwise falls back to the compiled chip tables researched here.

## Dependencies And Integration Points

- Depends on `rtw8852a_table.h` for exported table declarations and on `core.h`
  / `phy.h` for `struct rtw89_phy_table`, `struct rtw89_reg2_def`,
  `struct rtw89_txpwr_byrate_cfg`, `struct rtw89_txpwr_track_cfg`, and
  regulatory/array dimension constants.
- Integrated into `rtw8852a_chip_info` in `rtw8852a.c`, which binds these tables
  to RTL8852A chip operations.
- Integrated into the generic AX PHY implementation through `rtw89_phy_gen_ax`,
  especially `preinit_rf_nctl`, `set_txpwr_byrate`, and `set_txpwr_limit`.
- Power-limit reads combine this table data with regulatory state, SAR,
  optional antenna-gain offsets, and TPE constraints before values are written
  to hardware.
- The 2 GHz table uses both world defaults and explicit regional overrides.
  If a regional entry is zero, `rtw89_phy_read_txpwr_limit()` falls back to the
  `RTW89_WW` entry for the same index. Some values are `127`, which functions
  as an effectively open or sentinel-like high limit in this table family.

## Risks And Maintenance Notes

- The chunk begins mid-table. Lines 37905-42244 are only the tail of
  `rtw89_8852a_phy_radiob_regs`, so whole-file research must combine this with
  earlier chunks to understand the full Radio-B sequence and initial branch
  headline records.
- The chunk ends at the start of `rtw89_8852a_txpwr_lmt_5g`; the 5 GHz limit
  table is incomplete here and must be reconciled with following chunks.
- Register tables are opaque hardware recipes. Small transcription errors in
  address/data pairs can silently break RF path B, calibration, channel
  switching, or transmit power.
- The high-bit table markers must remain intact. Treating encoded control
  records as normal RF writes, or reordering them, would break conditional table
  selection by RFE type and chip cut version.
- The power-limit tensors rely on exact enum ordering and array dimensions.
  Changes to `RTW89_*_NUM`, regulatory-domain enum values, or rate-section
  indexes require coordinated table regeneration.
- Signed `s8` power values are later packed into 8-bit register fields. Values
  above normal power ranges, especially `127`, should be understood as table
  sentinel/high-limit behavior before changing them.
- By-rate `data` is little-endian byte-packed by repeated `data >>= 8` in
  `rtw89_phy_load_txpwr_byrate()`. Changing `shf`, `len`, or byte order changes
  the expanded rate map.

## Test Signals

Useful validation signals after edits to this chunk include:

- Driver load and probe for RTL8852A without `invalid PHY package` or
  `failed to load CR` warnings from `rtw89_phy_init_reg()`.
- No `failed to poll nctl block` error during NCTL preinit.
- Successful RF initialization for both paths, with no RF H2C config warnings
  from `rtw89_phy_init_rf_reg()`.
- Channel switching across 2 GHz and 5 GHz with `RTW89_DBG_TXPWR` traces showing
  by-rate and limit programming for expected channel and bandwidth values.
- Regulatory-domain checks that confirm explicit regional entries override
  `RTW89_WW` and zero entries fall back as expected.
- RF calibration and thermal tracking behavior across temperature changes,
  especially path A/B delta swing application for 2 GHz CCK/non-CCK and 5 GHz.
- Over-the-air sanity tests for TX power, throughput, association stability, and
  coexistence behavior after suspend/resume and channel changes.
