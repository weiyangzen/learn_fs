# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c lines 4812-13824

## Scope

This chunk covers the N-PHY static calibration-data region in `drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c`, from the tail of a radio/channel table through line 13824. The range contains no executable functions; its runtime behavior comes from later functions in the same file that select these tables by PHY revision, radio revision, channel, band, and internal/external PA mode.

## Purpose

The data in this chunk gives the Broadcom `brcmsmac` N-PHY driver the hard-coded radio initialization, per-channel tuning, TX power control, IQ calibration, and PAPD compensation values needed for BCM2055/2056/2057-family radios. These tables bridge high-level channel and calibration decisions to concrete PHY table words and RF register values. They are used during radio power-on, channel changes, TX power table programming, IQ calibration, LNA gain adjustment, and PAPD setup.

## Important Types And Tables

- `struct chan_info_nphy_radio2057` and `struct chan_info_nphy_radio2057_rev5` map channel numbers to frequency, RFPLL/VCO/logen/TX/RX/LNA tuning values, and six PHY bandwidth-control values (`PHY_BW1a` through `PHY_BW6`). The rev5 structure is smaller because it only carries the fields needed for that radio variant.
- `chan_info_nphyrev7_2057_rev4`, `chan_info_nphyrev8_2057_rev5`, `chan_info_nphyrev9_2057_rev5v1`, `chan_info_nphyrev8_2057_rev7`, and `chan_info_nphyrev8_2057_rev8` are the 2057 channel tables for N-PHY revisions 7, 8, 9, and 16 with radio revisions 4/5/7/8. They cover 2.4 GHz channels and 5 GHz channel/frequency entries with per-channel PLL and RF path settings.
- `struct radio_regs` tables (`regs_2055`, `regs_SYN_2056*`, `regs_TX_2056*`, `regs_RX_2056*`) describe default radio-register initialization for 2055 and 2056 radios. Each row has an address, A-band and G-band init values, and per-band enable flags.
- `struct radio_20xx_regs` tables (`regs_2057_rev4`, `regs_2057_rev5`, `regs_2057_rev5v1`, `regs_2057_rev7`, `regs_2057_rev8`) provide compact address/value/default-enable rows for 2057 radio revisions.
- `nphy_def_lnagains`, `nphy_lnagain_est0`, and `nphy_lnagain_est1` are LNA gain baselines and estimation constants used by later gain-table adjustment code.
- `tbl_iqcal_gainparams_nphy[2][NPHY_IQCAL_NUMGAINS][8]` defines 2 GHz and 5 GHz IQ calibration gain parameter rows. Later code matches a requested calibration gain against column 0, then fills TXGM/PGA/PAD and noise-correlation fields from the remaining columns.
- `nphy_tpc_txgain`, `nphy_tpc_loscale`, and the many `nphy_tpc_txgain_ipa*` arrays encode TX power-control gain ladders for non-IPA, IPA, band-specific, and 2057-revision-specific cases.
- `nphy_papd_*` delta tables, `pad_gain_codes_used_2057rev*`, `pad_all_gain_codes_2057`, `pga_all_gain_codes_2057`, and `nphy_papd_scaltbl` support PAPD gain selection, RF power offset calculation, and scale-table download.

## Control Flow And Consumers

- Radio initialization uses the register tables through `wlc_phy_radio_init_2057()`, `wlc_phy_radio_init_2056()`, and `wlc_phy_radio_init_2055()`. Those functions choose a table based on `pi->pubpi.phy_rev` and `pi->pubpi.radiorev`, then call `wlc_phy_init_radio_regs_allbands()` or `wlc_phy_init_radio_regs()` from common PHY code.
- Channel lookup uses `wlc_phy_chan2freq_nphy()`. For N-PHY rev >= 7, it selects one of the 2057 channel tables in this chunk, scans for `chan == channel`, returns the matched frequency, and returns a pointer to either the full 2057 row or the rev5 row.
- Channel programming uses `wlc_phy_chanspec_set_nphy()`. After lookup, it calls `wlc_phy_chanspec_radio2057_setup()` for 2057 radios, which writes the selected row's VCO, RFPLL, logen, TX mixer/PAD/PGA, and LNA fields into radio registers, applies revision/band-specific loop filter overrides, applies some IPA/non-IPA 2 GHz overrides, delays, and triggers VCO calibration.
- The same channel-change flow casts the row's `PHY_BW1a` tail to `struct nphy_sfo_cfg` and passes it to `wlc_phy_chanspec_nphy_setup()`, which writes the six bandwidth-control values to PHY registers `0x1ce` through `0x1d3`, toggles current-band state, adjusts channel-14 OFDM classification, handles fixed-power mode, updates TX LPF bandwidth, and may run spur-avoid PLL updates.
- TX power-control table selection happens later in the file around TX power setup paths. The code chooses among the `nphy_tpc_txgain_ipa*` arrays according to `PHY_IPA(pi)`, channel band, PHY revision, and radio revision, then writes the chosen gain ladder to N-PHY tables. External-PA paths use the related non-IPA/EPA tables just after this chunk.
- IQ calibration uses `tbl_iqcal_gainparams_nphy` in a later helper that searches by requested `cal_gain`, then populates an `nphy_iqcal_params` instance with gain and `ncorr` values.
- PAPD setup uses this chunk's delta/code/scale tables to derive RF power offsets, select legal PAD/PGA gain code ranges by radio revision, and write `nphy_papd_scaltbl` into PAPD scale PHY tables.

## State And Persistence Behavior

The chunk itself defines static in-kernel data only. Most arrays are file-local `static` objects, so their contents persist for the lifetime of the module and are shared by all N-PHY instances. Tables declared `const` should be immutable. Several `u32`, `u8`, and `s8/s16` arrays are not declared `const` even though they appear to be used as read-only calibration data; accidental mutation would affect every later use in the driver.

Runtime state affected by consumers includes:

- Hardware radio registers for PLL, VCO, logen, mixer, PAD/PGA, LNA, and band-specific tune values.
- PHY registers for SFO/bandwidth configuration and current-band/classifier behavior.
- PHY table memory for TX power gain ladders, IQ calibration parameters, PAPD scale tables, and antenna/gain calibration data.
- `brcms_phy` state such as `radio_is_on`, `radio_chanspec`, `bw`, `phy_isspuravoid`, power-control mode, and calibration/gain fields updated by later code using these tables.

## Dependencies And Integration Points

- Hardware register access is through `read_radio_reg()`, `write_radio_reg()`, `mod_radio_reg()`, `write_phy_reg()`, `mod_phy_reg()`, and PHY table wrappers such as `wlc_phy_table_write_nphy()`.
- Common PHY helpers in `phy_cmn.c` consume `struct radio_regs` and `struct radio_20xx_regs` rows through `wlc_phy_init_radio_regs()` and `wlc_phy_init_radio_regs_allbands()`.
- Register and table IDs come from `phyreg_n.h`, `phytbl_n.h`, `phy_radio.h`, and related Broadcom hardware headers.
- Board and device inputs come from `struct brcms_phy`, including `pubpi.phy_rev`, `pubpi.radiorev`, `pubpi.radiover`, `radio_chanspec`, `srom_fem2g/srom_fem5g`, `sh->chip`, `sh->boardflags2`, and `d11core`.
- Channel macros (`CHSPEC_CHANNEL`, `CHSPEC_IS2G`, `CHSPEC_IS5G`, `CHSPEC_IS40`, `CHSPEC_SB_UPPER`) and band range constants decide which table row and follow-up programming path are valid.

## Risks And Edge Cases

- The channel tables are manually aligned with structure field order. A missing value, wrong field order, or wrong table selected for a PHY/radio revision will silently program incorrect RF registers.
- `wlc_phy_chan2freq_nphy()` linearly searches these tables and falls back to a failed lookup if a channel is absent. Missing regulatory/channel entries can make channel changes no-op after `wlc_phy_chanspec_set_nphy()` returns early.
- Rev5 radio rows use a different struct and lack 5 GHz fields carried by the full 2057 struct. Consumer code branches on `radiorev == 5`; any future caller that treats the two table types interchangeably can read invalid layout.
- Many tables are non-`const` despite acting as static calibration constants. That increases the blast radius of accidental writes and makes it harder to reason about data immutability.
- TX gain ladder array lengths are assumed by later table writes and index calculations. Array-size drift or selecting a table with the wrong ladder shape could misprogram TX gain indexes or overrun table expectations.
- PAPD delta arrays are indexed by gain-code values. Later code must clamp or select only supported PAD/PGA codes, especially across radio revisions 3/4/5/7/8.
- Hardware validation is difficult from code inspection: the literals are vendor calibration data, so regressions usually surface as RF bring-up failure, bad EVM, bad TX power, poor sensitivity, or calibration timeout rather than compile-time errors.

## Test Signals

- Boot/radio-on smoke tests across N-PHY rev 7, 8, 9, and 16 devices with 2057 radio revs 4, 5, 7, and 8 should verify radio initialization completes and `radio_is_on` transitions correctly.
- Channel-change tests should cover 2.4 GHz channel 14, 20/40 MHz operation, low/mid/high 5 GHz channels, and rev5/v5v1 hardware, checking that the expected channel table row is selected and VCO calibration completes.
- RF calibration tests should watch for `radio calib` warnings/timeouts, IQ calibration success, stable RSSI/LNA behavior, and PAPD convergence after channel changes and temperature changes.
- TX power tests should validate table selection for IPA/non-IPA, 2 GHz vs 5 GHz, and 2057 rev-specific cases by comparing programmed TX gain table contents and measured conducted power.
- Regulatory/rate-throughput tests should look for degraded sensitivity, excessive EVM, spur issues, or band-edge failures after any table edit.
- Static checks can confirm that table sizes match consumer expectations, all supported channels are represented for each selected radio revision, and read-only tables can safely be made `const`.
