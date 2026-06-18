# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.c lines 26920-35031

## Scope

This chunk covers the tail of `rtw89_8852c_phy_radiob_regs`, all of `rtw89_8852c_phy_nctl_regs`, the complete `rtw89_8852c_txpwr_byrate` table, the RTL8852C transmit-power thermal tracking delta-swing tables, the transmit-shape limit tables, and the beginning of the 2.4 GHz and 5 GHz transmit-power regulatory limit data. The source is table-driven C data for the Realtek RTW89 RTL8852C wireless driver; it contains no local functions, but it defines data consumed by generic PHY, RF, RFK/TSSI, and transmit-power code paths.

## Purpose

The data in this range programs hardware state and policy for RTL8852C:

- The radio-B table tail continues RF path B initialization using `struct rtw89_reg2_def` register/data pairs. It includes many conditional branch markers encoded in the pseudo-address field, selecting values by RFE package and chip cut/version before writing RF register payloads.
- `rtw89_8852c_phy_nctl_regs` initializes the NCTL block used by RF calibration/control logic. It starts with control registers around `0x8000` and then loads a large microcode-like sequence across NCTL memory/register windows, ending by toggling `0x8080`.
- `rtw89_8852c_txpwr_byrate` provides packed per-rate power offsets by band, NSS, rate section, starting index, length, and packed byte data.
- `_txpwr_track_delta_swingidx_*` arrays provide thermal compensation curves for 2 GHz, 5 GHz, and 6 GHz, split by RF path A/B and positive/negative thermal direction.
- `rtw89_8852c_tx_shape_lmt` and `rtw89_8852c_tx_shape_lmt_ru` encode regulatory transmit-shaping limits per band, shaping mode, RU/non-RU mode, and regulatory domain.
- `rtw89_8852c_txpwr_lmt_2g` and the beginning of `rtw89_8852c_txpwr_lmt_5g` encode regulatory power ceilings as `s8` values indexed by bandwidth, number of transmit chains, rate-section limit bucket, beamforming flag, regulatory domain, and channel index.

## Important Types And APIs

- `struct rtw89_reg2_def`: `{ addr, data }` entries used for BB/RF/NCTL table initialization. The generic loader interprets high bits in `addr` as conditional control records and ordinary values as hardware register addresses.
- `struct rtw89_phy_table`: wraps a `rtw89_reg2_def` array with `n_regs`, `rf_path`, and an optional config callback. Later in the same file, `rtw89_8852c_phy_radiob_table` points at `rtw89_8852c_phy_radiob_regs` with `RF_PATH_B` and `rtw89_phy_config_rf_reg_v1`; `rtw89_8852c_phy_nctl_table` points at `rtw89_8852c_phy_nctl_regs`.
- `rtw89_phy_init_reg()` in `phy.c`: common table interpreter. It selects the matching headline for `rtwdev->efuse.rfe_type` and chip cut/version, tracks branch/elif/else/end/check pseudo-records, and calls the supplied config function only for matched data records.
- `rtw89_phy_init_rf_reg()` consumes chip RF tables, including path B, and can either write immediately or build firmware H2C RF config data through `rtw89_phy_config_rf_reg_v1`.
- `rtw89_phy_init_rf_nctl()` preinitializes the NCTL block, chooses either firmware-provided NCTL data or `chip->nctl_table`, then applies `rtw89_8852c_phy_nctl_table` with BB-register writes.
- `struct rtw89_txpwr_byrate_cfg`: `{ band, nss, rs, shf, len, data }`; used by `rtw89_phy_load_txpwr_byrate()` to unpack up to four byte-sized `s8` offsets into `rtwdev->byr[band][0]`.
- `struct rtw89_txpwr_track_cfg`: pointer table wired later as `rtw89_8852c_trk_cfg`; RFK/TSSI code uses these curves when firmware does not provide a dynamic tracking table.
- `struct rtw89_rfe_parms`: later `rtw89_8852c_dflt_parms` references the by-rate table, transmit-power limit arrays, RU limit arrays, and shape limit arrays. `core.c` selects RFE parameters and calls `rtw89_load_txpwr_table(rtwdev, rtwdev->rfe_parms->byr_tbl)`.

## Control Flow And Integration

The RF path B data in this chunk is not executed directly. During RF initialization, `rtw89_phy_init_rf_reg()` iterates RF paths, selects `chip->rf_table[RF_PATH_B]` or firmware override data, and invokes `rtw89_phy_init_reg()`. The branch records embedded in the table decide which RF entries apply to the current RFE/chip version. Matched path-B records are passed to `rtw89_phy_config_rf_reg_v1`, which ignores pseudo or small addresses below `0x100` and stores RF writes for the selected RF path.

NCTL initialization follows a separate PHY flow. `rtw89_phy_init_rf_nctl()` calls `rtw89_phy_preinit_rf_nctl()`, which enables IQK/DPK clock/reset bits, writes `R_NCTL_CFG`, and polls `0x8080` until the NCTL block reports ready. It then applies `rtw89_8852c_phy_nctl_regs` with `rtw89_phy_config_bb_reg`. The final entries in the NCTL array write `0x8080` to `0x4`, then `0x0`, and clear `0x8088`, which looks like an explicit trigger/reset/cleanup sequence after loading the large NCTL instruction/config image.

By-rate transmit power initialization is driven from device bring-up in `core.c`: after the driver selects default or firmware-supplied RFE parameters, it loads `rfe_parms->byr_tbl`. For the static RTL8852C defaults, `rtw89_8852c_byr_table` points at the `rtw89_8852c_txpwr_byrate` entries in this chunk. `rtw89_phy_load_txpwr_byrate()` unpacks each byte of `data` into the rate-section storage selected by `band`, `nss`, and `rs`.

Thermal tracking integration is in `rtw8852c_rfk.c`. The TSSI tracking path first checks for firmware-provided `rtwdev->fw.elm_info.txpwr_trk`; if absent, it selects the static arrays from `rtw89_8852c_trk_cfg` based on channel subband and RF path. For 6 GHz it maps channel band indexes in pairs to rows 0-3 of the 6 GHz A/B positive/negative arrays.

The transmit-shape and transmit-power limit arrays are consumed indirectly through `rtw89_8852c_dflt_parms`. Generic PHY transmit-power filling code indexes these arrays by band, channel, regulatory domain, bandwidth, beamforming, RU mode, and NSS, then combines them with offsets and dynamic limits before programming hardware.

## State And Persistence Behavior

All definitions in this chunk are static or const compile-time data. They are immutable after module load and do not persist runtime state themselves. Runtime state is produced when generic loader code copies or applies these values:

- RF and NCTL arrays persist as hardware register/NCTL RAM state until reset, power cycle, reinitialization, firmware override, or channel/RFK reconfiguration changes them.
- By-rate values are unpacked into `rtwdev->byr`, becoming per-device RAM state used for later transmit-power programming.
- Thermal tracking arrays remain read-only lookup tables. Runtime thermal offsets are computed into temporary/local state and TSSI structures in RFK/TSSI code.
- Regulatory limit arrays stay const; the selected limits are read repeatedly during channel or regulatory changes and converted into hardware/MAC transmit-power commands.

Because firmware elements can override several table sources (`elm_info->rf_radio`, `elm_info->rf_nctl`, `fw.elm_info.txpwr_trk`, firmware RFE data), this chunk is the built-in fallback/default dataset rather than the only possible runtime source.

## Dependencies

This chunk depends on RTW89 core definitions and constants from nearby driver headers:

- `core.h` for `struct rtw89_phy_table`, `struct rtw89_txpwr_table`, RFE parameter structures, RF path enums, regulatory-domain counts, and transmit-power limit dimensions.
- `phy.h` for `struct rtw89_txpwr_byrate_cfg`, `struct rtw89_txpwr_track_cfg`, `DELTA_SWINGIDX_SIZE`, rate-section constants, and PHY loader prototypes.
- `rtw8852c_table.h` for external declarations consumed by `rtw8852c.c` and `rtw8852c_rfk.c`.
- `phy.c`, `core.c`, and `rtw8852c_rfk.c` for the consumers that interpret, copy, or apply the tables.
- Hardware/firmware contracts for RTL8852C register encodings. The many numeric values are not self-describing and must match Realtek hardware specifications and calibration expectations.

## Risks And Edge Cases

- Table corruption is high impact. A single wrong NCTL or RF value can break RF bring-up, calibration, sensitivity, transmit quality, or regulatory behavior without producing compile errors.
- Conditional branch pseudo-addresses in the RF table are fragile. Incorrect RFE/CV targets can silently select the wrong path for specific board packages or chip cuts.
- `rtw89_phy_load_txpwr_byrate()` trusts `rs`, `nss`, `shf`, and `len` to fit the destination rate arrays. Bad table dimensions would write the wrong per-rate slot or potentially overrun if constants and table entries diverge.
- Values of `127` in transmit-power limit tables appear to mean an invalid/unlimited/disabled sentinel in this driver family. Misinterpreting them as a normal high dBm value would be dangerous; consumers must preserve the existing sentinel semantics.
- Regulatory-domain tables are sparse designated initializers. Unspecified entries default to zero, so missing rows may unintentionally clamp power to zero unless zero is expected for that dimension.
- Thermal tracking rows must stay aligned with subband selection logic in `rtw8852c_rfk.c`. Adding 6 GHz subband indexes or changing subband enums without updating these arrays would choose the wrong compensation curve.
- Firmware override behavior means tests using only firmware-supplied tables may not exercise these static fallback arrays.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build with `W=1` or equivalent kernel warnings to catch malformed initializers and dimension mismatches in the large multi-dimensional arrays.
- Confirm probe/init logs do not report `invalid PHY package`, `failed to load CR`, RF H2C config failures, or `failed to poll nctl block`.
- Exercise boards with multiple `efuse.rfe_type` and chip cut/version combinations so the RF path B conditional table headlines and branches are actually selected.
- Verify RF/NCTL initialization by checking successful IQK/DPK/TSSI calibration, stable association, channel switching, scan, and throughput on both RF paths.
- Validate transmit power by reading programmed by-rate offsets and regulatory limit outputs for 2.4 GHz and 5 GHz channels, especially channels with sentinel `127`, domain-specific exceptions, and edge channels.
- Run thermal/TSSI tracking across temperature deltas and confirm path A/B swing index offsets follow the expected positive and negative curves for 2 GHz, 5 GHz subbands, and 6 GHz subbands.
