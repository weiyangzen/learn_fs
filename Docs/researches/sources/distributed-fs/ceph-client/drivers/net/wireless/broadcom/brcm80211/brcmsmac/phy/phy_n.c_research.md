# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004802`: lines 1-4811, `Docs/researches/chunks/subset-b-004802_research.md`
- `subset-b-004803`: lines 4812-13824, `Docs/researches/chunks/subset-b-004803_research.md`
- `subset-b-004804`: lines 13825-22851, `Docs/researches/chunks/subset-b-004804_research.md`
- `subset-b-004805`: lines 22852-28571, `Docs/researches/chunks/subset-b-004805_research.md`

## Chunk Research

### subset-b-004802: lines 1-4811

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c lines 1-4811

## Scope

This chunk covers the opening of the Broadcom `brcmsmac` N-PHY implementation. It contains the module/license header, include dependencies, local register-access macros, calibration/control constants, local helper data types, gain/filter tables, and the first large set of static channel tuning tables. No executable function body is present in lines 1-4811; the chunk is a static configuration and data-definition layer consumed by later N-PHY initialization, channel selection, calibration, and radio programming code in the same file.

The source file continues well beyond this chunk. In particular, the table `chan_info_nphyrev6_2056v11[]` begins at line 4675 and is still open at line 4811, so later chunk(s) must complete that table before whole-file conclusions about all radio 2056v11 channel entries are final.

## Purpose

The visible code establishes the constants and lookup tables needed to translate an 802.11 channel/frequency and radio/PHY revision into concrete RF synthesizer, RX/TX front-end, and PHY bandwidth register values. The data is revision-specific because N-PHY devices use several radio blocks (`2055`, `2056`, later `2057`) with different register naming and tuning values.

The table rows are hardware programming payloads. Each row is keyed by channel number and frequency and then stores the values later routines write into radio registers and N-PHY registers when switching channel, calibrating RX/TX, setting bandwidth, or applying workarounds.

## Dependencies

The chunk includes Linux and driver-local headers:

- Linux helpers: `linux/kernel.h`, `linux/delay.h`, and `linux/cordic.h`.
- Broadcom bus/chip headers: `brcm_hw_ids.h`, `aiutils.h`, `chipcommon.h`, `pmu.h`, and `soc.h`.
- MAC/PHY integration headers: `d11.h`, `phy_shim.h`, `phy_int.h`, `phy_hal.h`, `phy_radio.h`, `phyreg_n.h`, and `phytbl_n.h`.

The macro and table definitions depend heavily on symbols defined elsewhere:

- `read_radio_reg()`, `write_radio_reg()`, and `read_phy_reg()` are used by macros but implemented outside this chunk.
- Register token names such as `radio_type##_##jspace##_##reg_name` and `radio_type##_##SYN##_##reg_name` come from radio register headers.
- PHY revision helpers such as `NREV_GE()` and fields under `pi->pubpi.phy_rev` come from the PHY core structures.
- `struct brcms_phy`, `struct brcms_phy_pub`, and `struct nphy_txgains` are referenced or embedded but defined outside this chunk.

## Important APIs, Types, and Data

### Register Access Macros

Lines 25-60 define token-pasting helpers for multi-core radio register addressing:

- `READ_RADIO_REG2()` and `WRITE_RADIO_REG2()` build register addresses using a radio type, register-space name, core selector, and register name. They OR the selected core namespace into a common register token.
- `WRITE_RADIO_SYN()` writes synthesizer-space registers.
- `READ_RADIO_REG3()` / `WRITE_RADIO_REG3()` and `READ_RADIO_REG4()` / `WRITE_RADIO_REG4()` support alternate radio register naming layouts where the core number appears in a different token position.

These are not public APIs, but later code likely uses them to hide radio-family register naming differences while programming core 0/core 1 paths.

### Calibration and Control Constants

Lines 62-168 define N-PHY constants for:

- Adjacent-channel interference detection windows and channel skip/delta thresholds.
- Noise and glitch thresholds for associated and unassociated states.
- RSSI calibration limits, sign extension, and violation checks.
- IQ calibration gain count, PAPD table sizes, and digital filter coefficient count.
- SROM temperature offset interpretation and maximum calibration temperature delta.
- Noise variance table lengths for 20 MHz and 40 MHz modes.
- RX/TX calibration tone frequency and amplitude constants.
- TX filter mode identifiers for OFDM20, OFDM40, CCK, and default filters.
- 5357 chip-control bits for external PA and antenna mux behavior.

These constants are part of the persistent hardware policy for later runtime decisions. Changing them changes calibration acceptance, noise mitigation, and RF programming behavior.

### Local Structs

The chunk defines several local table/restore-state shapes:

- `struct nphy_iqcal_params`: TX low-pass filter, TX gain mixer, PGA, PAD, IPA, calibration gain, and five correction values for IQ calibration.
- `struct nphy_txiqcal_ladder`: compact TX IQ calibration ladder row with percentage and envelope gain.
- `struct nphy_ipa_txcalgains`: wraps `struct nphy_txgains` with a flag/index pair for table-indexed IPA TX calibration.
- `struct nphy_papd_restore_state`: per-core and shared state snapshot for PAPD restoration, including feedback mixer, VGA, internal PA, AFE control/override, power-up, attenuation, and multiplier state.
- `struct nphy_ipa_txrxgain`: RX calibration gain tuple with HPVGA, LPF BIQ stages, LNA2/LNA1, and TX power index.
- `struct chan_info_nphy_2055`: channel/frequency row for radio 2055, including PLL values, local-generator tuning, per-core RX/TX values, and six PHY bandwidth values.
- `struct chan_info_nphy_radio205x`: channel/frequency row for radio 2056-class programming, including synthesizer PLL fields, reserved synthesizer addresses, logen fields, per-core RX/TX tune/boost values, and six PHY bandwidth values.
- `struct chan_info_nphy_radio2057` and `struct chan_info_nphy_radio2057_rev5`: alternate row layouts for later 2057 tables, defined here but not populated in this chunk.
- `struct nphy_sfo_cfg`: a smaller PHY bandwidth-only row.

### Static Tables Present in This Chunk

The chunk includes several static tables:

- `nphy_ipa_rxcal_gaintbl_5GHz[]`, `nphy_ipa_rxcal_gaintbl_2GHz[]`, `nphy_ipa_rxcal_gaintbl_5GHz_rev7[]`, and `nphy_ipa_rxcal_gaintbl_2GHz_rev7[]`: IPA RX calibration gain ladders for band and revision combinations.
- `NPHY_IPA_REV4_txdigi_filtcoeffs[][15]`: seven sets of TX digital filter coefficients for IPA rev4 paths.
- `chan_info_nphy_2055[]`: complete channel tuning table for radio 2055, covering 5 GHz channels from 184 through 228 and 32 through 182, plus 2.4 GHz channels 1 through 14.
- `chan_info_nphyrev3_2056[]`: complete radio 2056 table for N-PHY rev3.
- `chan_info_nphyrev4_2056_A1[]`: complete radio 2056 A1 table for N-PHY rev4.
- `chan_info_nphyrev5_2056v5[]`: complete radio 2056v5 table for N-PHY rev5.
- `chan_info_nphyrev6_2056v6[]`: complete radio 2056v6 table for N-PHY rev6.
- `chan_info_nphyrev5n6_2056v7[]`: complete radio 2056v7 table shared by rev5/rev6 paths.
- `chan_info_nphyrev6_2056v8[]`: complete radio 2056v8 table for rev6.
- `chan_info_nphyrev6_2056v11[]`: begins in this chunk but is incomplete at line 4811.

The `chan_info_*` tables are mostly dense numeric literals. The semantic contract is carried by the struct field order, so row/field alignment is critical.

## Control Flow

There is no direct executable control flow in lines 1-4811. The only conditional logic is in macro expansion:

- Core selection in `READ_RADIO_REG2()`/`WRITE_RADIO_REG2()` chooses core 0 or core 1 register namespaces.
- The RSSI violation macros compare calibrated RSSI values against upper/lower tolerances.
- `NPHY_IS_SROM_REINTERPRET` expands to a PHY revision check.

The runtime control flow using this chunk is expected to happen later in the file:

1. A channel set or initialization routine identifies radio type/revision and channel.
2. It selects the matching `chan_info_*` table.
3. It searches for the matching `chan`/`freq` row.
4. It writes synthesizer, RX/TX, and PHY bandwidth values from that row through radio/PHY register helpers.
5. Calibration routines select gain/filter tables based on band, revision, IPA presence, and calibration mode.

## State and Persistence Behavior

The chunk itself defines no mutable global state. Most objects are `static const`, so they are read-only kernel text/data inputs after compilation.

Persistence is hardware-facing rather than file-backed:

- Register macros write values into radio/PHY hardware state through driver helpers.
- The table values represent stable default hardware programming for channel changes and calibration.
- `struct nphy_papd_restore_state` is a transient in-memory snapshot type used later to restore PAPD-related register state after calibration or measurement changes.

Any future edit to the numeric tables effectively changes persistent device behavior across boots because these constants are compiled into the driver.

## Integration Points

This chunk integrates with:

- The Linux wireless driver build via `pr_fmt()` and kernel headers.
- Broadcom chip/bus helpers for chip IDs, PMU, chipcommon, and AI backplane access.
- The brcmsmac PHY abstraction through `phy_int.h`, `phy_hal.h`, `phy_radio.h`, `phyreg_n.h`, and `phytbl_n.h`.
- Later N-PHY routines in this same file that likely implement attach/init, channel switching, radio initialization, calibration, TX power control, RSSI calibration, PAPD, and workarounds.
- Register definition headers that must match the token-pasting macro naming schemes.

The line-anchored table starts show the intended revision split: radio 2055 data starts at line 438, radio 2056 rev3 at 937, rev4 A1 at 1560, rev5/v5 at 2183, rev6/v6 at 2806, rev5/6 v7 at 3429, rev6/v8 at 4052, and rev6/v11 at 4675.

## Risks and Edge Cases

- Numeric table field order is fragile. A missing value, extra value, or wrong field alignment will silently program the wrong hardware register.
- The register macros rely on token pasting against names defined in headers. Register renames or new radio layouts can fail at compile time or, worse, select the wrong token pattern if reused incorrectly.
- The `u16` filter coefficient table stores negative literals in unsigned elements. This likely relies on two's-complement wraparound for hardware coefficient encoding; readers must not "fix" these to signed types without checking the downstream table writer.
- Channel tables duplicate many rows across revisions with small differences. Manual edits are high risk because a one-nibble change can affect a narrow channel/revision only.
- The chunk boundary cuts `chan_info_nphyrev6_2056v11[]` mid-table. Whole-file reconciliation must verify the final table closes correctly in the next chunk and that consumers never see a partially documented revision map.
- The constants include regulatory-adjacent and RF-behavior-affecting values such as TX power calibration, external PA, noise thresholds, and channel tuning. Behavioral validation needs actual hardware or a trusted golden register trace.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel build catches struct initializer arity/type errors, token-pasting register name mismatches, and missing external symbols.
- Static checks can verify each complete `chan_info_*` array has expected channel coverage, especially 2.4 GHz channels 1-14 and the 5 GHz channel list used by this driver.
- Channel-switch tests on supported Broadcom N-PHY hardware should compare programmed radio/PHY registers against known-good traces for each radio revision.
- Calibration smoke tests should exercise IPA RX gain tables, TX digital filter coefficient loading, RSSI calibration limits, and PAPD restore behavior.
- Regression tests should specifically cover radio 2055, 2056 rev3/rev4/rev5/rev6/v7/v8/v11 paths because this chunk encodes distinct table families for them.

## Cross-Chunk Notes

Later chunks need to identify the functions that consume these tables and constants. In particular, look for channel lookup and radio-programming routines that reference `chan_info_nphy_2055`, `chan_info_nphyrev3_2056`, `chan_info_nphyrev4_2056_A1`, `chan_info_nphyrev5_2056v5`, `chan_info_nphyrev6_2056v6`, `chan_info_nphyrev5n6_2056v7`, `chan_info_nphyrev6_2056v8`, and `chan_info_nphyrev6_2056v11`. The final per-file synthesis should connect those consumers to `wlc_phy_chanspec_set_nphy()` and radio init/calibration paths if confirmed in later lines.

### subset-b-004803: lines 4812-13824

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

### subset-b-004804: lines 13825-22851

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c lines 13825-22851

## Scope

This chunk covers the middle-to-late N-PHY implementation for the Broadcom `brcmsmac` wireless driver. It starts in the static transmit-power gain table area and ends inside the older revision-2 RSSI calibration routine. The code is not a standalone module; it is a large slice of `phy_n.c` that provides initialization, radio setup, channel programming, transmit-power control, workarounds, calibration save/restore, RSSI routing, temperature sensing, and RSSI calibration for N-PHY hardware using 2055, 2056, and 2057 radio blocks.

The chunk includes public driver entry points such as `wlc_phy_attach_nphy`, `wlc_phy_init_nphy`, `wlc_phy_switch_radio_nphy`, `wlc_phy_chanspec_set_nphy`, `wlc_phy_rxcore_setstate_nphy`, `wlc_phy_rssisel_nphy`, `wlc_phy_poll_rssi_nphy`, `wlc_phy_tempsense_nphy`, and RF-sequence helpers. It also contains many static helpers for revision-specific register programming and calibration sequencing.

The range ends partway through `wlc_phy_rssi_cal_nphy_rev2`; its complete behavior must be reconciled with the following chunk.

## Purpose

The code programs the N-PHY and associated radio hardware into a usable operating state for the current channel, band, bandwidth, board flags, SROM contents, PHY revision, and radio revision. Its main responsibilities are:

- Load N-PHY static and volatile tables, including antenna-switch control LUTs, RF-sequence tables, gain tables, noise variance tables, AFE control tables, and transmit-power control tables.
- Read board/SROM power and front-end-module parameters into `struct brcms_phy`, including antenna availability, FEM TSSI position, external PA gain, detector range, TR isolation, temperature limits, power offsets, per-core power detector coefficients, and MCS/OFDM/CCK power-offset fields.
- Select revision-specific hardware workarounds for N-PHY revs before 3, revs 3 through 6, and revs 7 and later.
- Initialize and switch 2055, 2056, and 2057 radio blocks, run RC/RCCAL/VCO calibrations, and program channel tables.
- Set up hardware transmit-power control, including idle TSSI measurement, detector polynomial tables, per-rate power offsets, transmit-gain tables, RF power offsets, and IQ/LO compensation tables.
- Save and restore RSSI and IQ/LO calibration caches by band so later PHY inits can avoid repeating full calibration.
- Route RSSI/TSSI/temperature measurement paths, poll signed RSSI values, and calibrate RSSI offsets.

This is hardware bring-up and calibration code. Most functions are sequences of PHY register writes, radio register writes, PHY table writes, delays, polling loops, and state-cache updates.

## Important APIs, Types, and Data

The primary software object is `struct brcms_phy *pi`. This chunk uses `pi->pubpi.phy_rev`, `pi->pubpi.radiorev`, `pi->pubpi.radioid`, `pi->pubpi.phy_corenum`, `pi->radio_chanspec`, `pi->bw`, SROM-derived FEM fields, board flags, chip IDs, and many persistent calibration fields to select hardware sequences.

Important public or cross-file functions in this chunk include:

- `wlc_phy_bist_check_phy()` validates a small set of BIST/status registers for older N-PHY revisions and treats rev 16+ as passing.
- `wlc_phy_table_write_nphy()` and `wlc_phy_table_read_nphy()` wrap `struct phytbl_info` construction around lower-level N-PHY table access.
- `wlc_phy_attach_nphy()` initializes N-PHY software defaults, enables workaround flags, installs function pointers, configures hardware TPC capability, and reads SROM data.
- `wlc_phy_init_nphy()` is the central PHY initialization path. It loads tables, clears overrides, programs workarounds, resets CCA, forces RF sequences, configures transmit power, sets gain tables, runs or restores RSSI/IQ calibration, enables TPC, restores RIFS timing, applies LPF bandwidth and spur workarounds.
- `wlc_phy_switch_radio_nphy()` powers radio blocks on or off and dispatches to 2055/2056/2057 preinit/init/postinit paths.
- `wlc_phy_chanspec_set_nphy()` resolves a channel to a radio table entry, updates bandwidth and sideband selection, programs the radio and PHY SFO/bandwidth registers, and applies spur avoidance.
- `wlc_phy_rxcore_setstate_nphy()` and `wlc_phy_rxcore_getstate_nphy()` control active RX chains and patch RF-sequence RX-to-TX behavior when only one RX core is enabled.
- `wlc_phy_classifier_nphy()` updates classifier enable bits, suspending MAC for D11 core rev 16 when required.
- `wlc_phy_force_rfseq_nphy()` triggers hardware RF sequence commands and waits for completion.
- `wlc_phy_rssisel_nphy()`, `wlc_phy_poll_rssi_nphy()`, and `wlc_phy_tempsense_nphy()` select measurement sources, read RSSI samples, and compute temperature.

Important static data in this range includes several 128-entry transmit-gain tables: `nphy_tpc_txgain_HiPwrEPA`, `nphy_tpc_txgain_epa_2057rev3`, `nphy_tpc_txgain_epa_2057rev5`, `nphy_tpc_5GHz_txgain_rev3`, `nphy_tpc_5GHz_txgain_rev4`, `nphy_tpc_5GHz_txgain_rev5`, and `nphy_tpc_5GHz_txgain_HiPwrEPA`. These tables are copied into core transmit-power-control tables based on band, PHY/radio revision, IPA status, and external PA gain. The chunk also defines small antenna switch control LUT fragments for rev 8/2057 variants.

Key external dependencies include register helpers (`read_phy_reg`, `write_phy_reg`, `mod_phy_reg`, `or_phy_reg`, `and_phy_reg`, radio equivalents, and `WRITE_RADIO_REG*` macros), channel macros (`CHSPEC_IS2G`, `CHSPEC_IS5G`, `CHSPEC_IS40`, `CHSPEC_CHANNEL`, `CHSPEC_BW`, `CHSPEC_SB_UPPER`), revision macros (`NREV_GE`, `NREV_LT`, `NREV_IS`), board flags (`BFL2_TXPWRCTRL_EN`, `BFL_EXTLNA`, `BFL2_SPUR_WAR`, `BFL2_GPLL_WAR`, etc.), SSB SPROM data, BCMA core/chipcommon accessors, and BMAC shim calls.

## Control Flow

Attach-time flow starts in `wlc_phy_attach_nphy()`. It sets workaround booleans by revision and board flags, chooses default preamble and chain policy, initializes calibration mode to multiphase, marks gain boost/radio state defaults, configures TPC mode, installs N-PHY function pointers into `pi->pi_fptr`, and calls `wlc_phy_txpwr_srom_read_nphy()` to persist SROM/FEM/power data in `pi`.

Initialization flow is concentrated in `wlc_phy_init_nphy()`:

1. Set measurement hold defaults and chip-specific chipcommon controls.
2. Determine whether internal TX IQ/LO calibration is available, clear deaf and spur-adjustment state, then call `wlc_phy_tbl_init_nphy()` to download static/volatile tables.
3. Clear RF control overrides and core override registers, initialize basic PHY thresholds, update MIMO preamble behavior for older revisions, and call `wlc_phy_stf_chain_upd_nphy()`.
4. Apply digital transmit filters for internal PA or external PA cases, then run `wlc_phy_workarounds_nphy()`, which dispatches to rev7, rev3, or rev1 workaround suites.
5. Toggle PHY clock/reset CCA, force RX2TX and RESET2RX RF sequences with PA override disabled/enabled, disable classifier bits, and snapshot clip-detector thresholds.
6. Initialize BPHY state in 2 GHz, disable hardware TPC temporarily, program fixed power, measure idle TSSI, and set up transmit-power detector and rate-offset tables.
7. Select and write the correct transmit gain table, compute RF power offsets, adjust RX core state, run or restore RSSI calibration, and run or restore IQ/LO calibration.
8. Write TX power compensation coefficient tables, restore the previous TPC state, apply RIFS timing, LPF bandwidth, and spur workarounds.

Radio control flow is split by radio generation. `wlc_phy_switch_radio_nphy()` uses 2057 paths for rev 7+, 2056 paths for rev 3-6, and 2055 paths for older revisions. Post-init paths run RC/RCCAL when `pi->phy_init_por` is set. Channel setting first resolves channel metadata through `wlc_phy_chan2freq_nphy()`, then calls `wlc_phy_chanspec_radio2055_setup()`, `wlc_phy_chanspec_radio2056_setup()`, or `wlc_phy_chanspec_radio2057_setup()`, followed by `wlc_phy_chanspec_nphy_setup()` for PHY bandwidth/SFO, BPHY reset, spur avoidance, CCA reset, and spur workaround handling.

Workaround control flow is heavily revision- and board-dependent. Rev7 code programs AFE control, RF sequence LPF/RCCAL entries, IPA bias workarounds, ADC VMID/gain by detector range, 2057-specific overrides, and gain-control tables. Rev3 code adjusts RF sequence RX2TX/TX2RX ordering, data weights, noise variance floors, detector ADC tables, mixer/radio biases, PLL workaround data weights, EDCRS thresholds, and single-antenna CCK behavior. Rev1 code configures 2055 RF sequences, table entries, MLADV workarounds, and older alpha/beta coefficients. All are called under optional carrier-search hold when `pi->phyhang_avoid` is set.

Calibration flow is stateful. `wlc_phy_precal_txgain_nphy()` chooses calibration TX gain based on PHY/radio revision and IPA support, optionally saving BB multiplier. `wlc_phy_cal_txgainctrl_nphy()` forces PA/TRSW overrides, emits calibration tones, estimates tone power, iteratively adjusts per-core power indexes, then restores saved register state. `wlc_phy_savecal_nphy()` stores RX IQ coefficients, TX LOFT radio registers, and IQLOCAL table values into band-specific caches. `wlc_phy_restorecal_nphy()` writes those caches back when a valid band-specific chanspec is present.

The RSSI flow routes hardware sources through `wlc_phy_rssisel_nphy()`, samples signed six-bit RSSI words in `wlc_phy_poll_rssi_nphy()`, and uses `wlc_phy_scale_offset_rssi_nphy()` to write per-core/per-rail scale and offset registers. `wlc_phy_rssi_cal_nphy_rev3()` disables normal RF state, powers selected RX paths, sweeps VCM values, computes minimum-error VCM, writes fine digital offsets for NB/W1/W2 RSSI, restores saved registers, and caches final radio/PHY RSSI settings by band. The chunk then starts `wlc_phy_rssi_cal_nphy_rev2()`, which performs a similar older-radio calibration for 2055 RSSI paths but continues past the chunk boundary.

## State and Persistence

This chunk persists board and calibration state in `struct brcms_phy`:

- SROM-derived fields: `antswitch`, `aa2g`, `aa5g`, `srom_fem2g`, `srom_fem5g`, temperature thresholds and offsets, per-band/per-core detector coefficients, idle targets, and power offset arrays.
- Capability and policy flags: `nphy_txpwrctrl`, `phy_5g_pwrgain`, `hwpwrctrl_capable`, `phyhang_avoid`, spur workaround booleans, `nphy_gain_boost`, `nphy_elna_gain_config`, `radio_is_on`, and internal calibration flags.
- Calibration caches: `calibration_cache` stores TX/RX IQ/LO coefficients and radio LOFT registers by 2G/5G; `rssical_cache` stores RSSI radio and PHY register settings by 2G/5G; `nphy_iqcal_chanspec_*` and `nphy_rssical_chanspec_*` mark cache validity.
- Runtime adjustment state: `nphy_anarxlpf_adjusted`, `nphy_noisevars_adjusted`, `nphy_saved_noisevars`, `nphy_crsminpwr_adjusted`, `nphy_crsminpwr`, `rx2tx_biasentry`, `rfctrlIntc*_save`, `nphy_txcal_pwr_idx`, `nphy_txcal_bbmult`, and `nphy_gmval`.

Most hardware writes are persistent until another channel change, PHY init, calibration restore, RF sequence, radio switch, or reset changes them. Several routines explicitly save and restore registers around temporary measurement state (`wlc_phy_poll_rssi_nphy`, `wlc_phy_tempsense_nphy`, `wlc_phy_cal_txgainctrl_nphy`, `wlc_phy_rssi_cal_nphy_rev3`). Spur workaround helpers persistently modify noise variance table entries, analog RX LPF calibration, and CRS minimum power, but keep old values in `pi` so later calls can restore them when the channel no longer requires the workaround.

`wlc_phy_rxcore_setstate_nphy()` persists the requested RX chain in `pi->sh->phyrxchain`, writes the active-core register, and edits the RF sequence table by replacing `CLR_RXRX_BIAS` with NOP when a single RX core is active. It remembers the entry index in `pi->rx2tx_biasentry` and restores the opcode when both RX cores are enabled.

## Dependencies and Integration Points

This code integrates directly with the Linux staging `brcmsmac` PHY stack:

- The attach path installs N-PHY callbacks in `pi->pi_fptr`, so higher-level PHY code calls these routines through the generic PHY interface for init, calibration init, channel set, and target-power recalculation.
- `wlapi_bmac_*` shim calls coordinate MAC suspension, PHY clock forcing, bandwidth changes, shared-memory writes, core PHY PLL control, and MAC control register updates. These calls prevent register sequences from racing the MAC or PSM.
- BCMA and chipcommon helpers adjust chip-level clocks, PLL spur avoidance, chip-control bits, and D11 core registers.
- SSB SPROM data under `pi->d11core->bus->sprom` provides board-specific power, FEM, temperature, and antenna values. Incorrect SROM interpretation directly changes power limits, TSSI setup, detector tables, and antenna LUTs.
- Radio register table arrays such as `regs_2055`, `regs_SYN_2056_rev*`, `regs_TX_2056_rev*`, `regs_RX_2056_rev*`, and `regs_2057_rev*` provide reset/init values for radio blocks.
- Channel metadata arrays such as `chan_info_nphyrev*_205*` provide per-channel synthesizer, tuning, and PHY bandwidth values.
- Calibration functions outside this chunk, including TX power index/gain helpers, tone generation, tone power estimation, TX IQ/LO calibration, RX IQ calibration, and perical multiphase logic, are orchestrated here.

Hardware integration is sensitive to revision gates. The same logical operation frequently uses different registers for 2055, 2056, and 2057 radios, and even 2057 rev 5 uses a different channel table shape (`chan_info_nphy_radio2057_rev5`) from other 2057 revisions.

## Risks

- Register sequencing risk is high. Many functions rely on specific ordering, delays, and RF sequence triggers. Reordering writes, omitting `udelay`/`mdelay`, or removing MAC/PHY clock coordination can leave the radio in an invalid state.
- Revision gating is fragile. A wrong `NREV_*`, `radiorev`, `radiover`, chip ID, package ID, or board flag condition can program a 2055/2056/2057 register layout with the wrong constants.
- Power-control code affects regulatory and thermal behavior. SROM-derived coefficients, transmit-gain table selection, idle TSSI measurement, target power, and per-rate offsets feed hardware TPC; bad values can cause underpowered links, excessive power, or thermal shutdown behavior.
- Calibration caches must be valid for the current band/channel context. Restoring stale 2G/5G IQ/RSSI state or failing to set `nphy_*_chanspec_*` validity markers can corrupt RSSI reporting and IQ/LO correction.
- Temporary override paths must restore state. RSSI polling, temperature sensing, TX gain calibration, and RSSI calibration save many PHY/radio registers. Early returns or WARN paths can leave overrides active.
- Spur workaround state is persistent and conditional. Noise variance, analog RX LPF, and CRS minimum power adjustments must be undone when leaving affected channels; otherwise sensitivity or false detection behavior can regress on unrelated channels.
- RF-sequence table patching in `wlc_phy_rxcore_setstate_nphy()` depends on finding expected opcodes and restoring the same slot later. Failed discovery or stale `rx2tx_biasentry` can alter RX/TX transitions.
- The chunk contains probable bug-prone patterns inherited from old driver code, such as the temperature-sense rev7 restore writing `RfctrlMiscReg5_save` to both `0x344` and `0x345` after reading `0x345` without storing it.
- The chunk boundary cuts through `wlc_phy_rssi_cal_nphy_rev2`; the final per-file report must combine the next chunk before describing old-revision RSSI calibration completely.

## Test and Validation Signals

Useful validation for this code is hardware-oriented:

- Probe/init tests on supported N-PHY devices should confirm `wlc_phy_attach_nphy()`, radio switch-on, and `wlc_phy_init_nphy()` complete without RF sequence timeout WARNs or radio calibration WARNs.
- Channel-change tests across 2.4 GHz, low/mid/high 5 GHz, 20 MHz, and 40 MHz modes should verify `wlc_phy_chanspec_set_nphy()` programs correct channel tables, bandwidth, sideband, spur avoidance, and CCA reset behavior.
- Transmit-power validation should compare requested target power, measured conducted power, idle TSSI, temperature compensation, and per-rate offsets across SROM revisions and external/internal PA boards.
- RSSI calibration validation should confirm NB/W1/W2 RSSI readings are near target after calibration and that cached RSSI settings restore on later PHY init without recalibrating unnecessarily.
- IQ/LO calibration tests should verify `wlc_phy_savecal_nphy()` and `wlc_phy_restorecal_nphy()` preserve TX/RX calibration quality across band changes and reinitialization.
- RX-chain state tests should switch one-core and two-core RX modes and verify RF sequence restoration, receive sensitivity, and no stuck MAC suspension.
- Temperature-sense tests should compare reported temperature against known board temperature over rev7+, rev3-6, and older 2055 hardware, including SROM offset handling.
- Spur workaround tests should exercise affected channels, especially 2 GHz 40 MHz channels 3-11 and listed 5 GHz channels, then leave those channels and confirm noise variance/CRS/LPF state is restored.
- Negative-path tests should watch for `WARN` messages from RF sequence waits and radio calibration loops; these are the main built-in signals of hardware sequencing failure in this chunk.

### subset-b-004805: lines 22852-28571

# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c lines 22852-28571

## Scope

This chunk covers the final 5,720 lines of `drivers/net/wireless/broadcom/brcm80211/brcmsmac/phy/phy_n.c`. It begins in the tail of the N-PHY RSSI calibration path and then contains the N-PHY sample-playback helpers, transmit gain extraction, TX IQ/LO calibration setup and execution, IPA/PAPD calibration, periodic calibration orchestration, RX IQ calibration, SROM transmit-power limit expansion, transmit-power-control toggling, manual transmit power index application, SROM limit lookup, and the carrier-search/deaf-mode nesting helper.

The code is hardware-facing driver code for Broadcom N-PHY radios. Most operations read and write PHY registers, radio registers, and N-PHY tables directly through helpers such as `read_phy_reg()`, `write_phy_reg()`, `mod_phy_reg()`, `read_radio_reg()`, `write_radio_reg()`, `wlc_phy_table_read_nphy()`, and `wlc_phy_table_write_nphy()`.

## Purpose

This chunk provides the calibration and transmit-power-control back end for the brcmsmac N-PHY implementation. It measures and compensates RSSI, generates calibration tones, runs sample playback through the PHY sample table, calibrates TX IQ/LO coefficients, calibrates RX IQ and RX LPF RC values, derives PAPD compensation tables for internal-PA devices, expands board/SROM power-offset data into per-rate power arrays, and switches hardware TX power control on and off.

The routines are tightly coupled to PHY revision, radio revision, band, channel width, board SROM contents, internal/external PA mode, and current MAC state. Revision branches split behavior among 2055-era rev0-2 paths, 2056 rev3-6 paths, and 2057 rev7+ paths.

## Important APIs and Functions

- `wlc_phy_rssi_cal_nphy()` dispatches RSSI calibration to rev3+ or rev2-era implementations. The visible rev2 tail sweeps VCM settings, polls RSSI, computes fine digital offsets per core/rail, writes RSSI scale/offset state, and restores classifier/clip/radio state.
- `wlc_phy_rssi_compute_nphy()` decodes signed per-chain RSSI fields from `struct d11rxhdr`, handles special remapping when power fields contain sentinel values, and merges antennas by `pi->sh->rssi_mode` using max, min, or average.
- `wlc_phy_loadsampletable_nphy()`, `wlc_phy_gen_load_samples_nphy()`, `wlc_phy_runsamples_nphy()`, `wlc_phy_tx_tone_nphy()`, and `wlc_phy_stopplayback_nphy()` implement the sample-playback engine used by calibration. They allocate CORDIC IQ buffers, write `NPHY_TBL_ID_SAMPLEPLAY`, configure sample count/loop/wait registers, optionally adjust baseband multiplier table entry 87, start/stop playback, and restore saved multipliers and LPF overrides.
- `brcms_phy_get_tx_pwrctrl_tbl()` and `wlc_phy_get_tx_gain_nphy()` select and decode the active TX gain table based on IPA mode, band, PHY revision, radio revision, and external PA SROM flags.
- `wlc_phy_iqcal_gainparams_nphy()` maps a `struct nphy_txgains` value into `struct nphy_iqcal_params`, including packed RFSEQ calibration gain and per-calibration `ncorr[]` values.
- `wlc_phy_txcal_radio_setup_nphy()` / `wlc_phy_txcal_radio_cleanup_nphy()` and `wlc_phy_txcal_physetup_nphy()` / `wlc_phy_txcal_phycleanup_nphy()` save and restore calibration-specific radio/PHY register state for TX IQ/LO calibration.
- `wlc_phy_est_tonepwr_nphy()` polls TSSI, subtracts idle TSSI, maps resulting power indexes through core TX power control tables, and returns qdBm power estimates.
- `wlc_phy_cal_txiqlo_nphy()` is the TX IQ/LO calibration worker. It prepares RFSEQ gains, writes IQLOCAL ladders and starting coefficients, plays a calibration tone, runs a command sequence, copies hardware-result coefficients from IQLOCAL result rows to active rows, saves best coefficients into `pi->nphy_txiqlocal_bestc` or `pi->mphase_txcal_bestcoeffs`, and restores hardware state.
- `wlc_phy_a4()` is the PAPD calibration coordinator for IPA devices. It disables HW power control, loads scalar/epsilon tables, calibrates each core with `wlc_phy_papd_cal_setup_nphy()`, `wlc_phy_a3_nphy()`, and `wlc_phy_a2_nphy()`, computes per-core epsilon offsets, enables PAPD compensation, restores TX filters, and restores MAC/PHY state.
- `wlc_phy_cal_perical_nphy_run()` orchestrates full or partial periodic calibration. In single-pass mode it runs TX IQ/LO, optional PAPD, RX IQ, save-cal, TX power coefficients, RSSI, idle TSSI, and VCO calibration. In multiphase mode it advances `pi->mphase_cal_phase_id` through TX phases, PAPD, RX, RSSI, and idle-TSSI phases.
- `wlc_phy_rx_iq_coeffs_nphy()`, `wlc_phy_rx_iq_est_nphy()`, and `wlc_phy_calc_rx_iq_comp_nphy()` read/write RX IQ compensation registers, trigger IQ estimates, compute compensation from I/Q power and IQ product, retry low-quality estimates, and restore previous coefficients on failure.
- `wlc_phy_cal_rxiq_nphy()` dispatches RX IQ calibration to rev3+ or rev2-era workers. Rev3+ setup uses TX/RX loopback coupling, gain control, optional RC sweep, and RX IQ compensation. Rev2 performs paired TX/RX core loopback with gain passes and compensation.
- `wlc_phy_txpwr_fixpower_nphy()`, `wlc_phy_txpwr_apply_nphy()`, `wlc_phy_txpower_recalc_target_nphy()`, `wlc_phy_txpwrctrl_enable_nphy()`, `wlc_phy_txpwr_index_nphy()`, and `wlc_phy_txpower_sromlimit_get_nphy()` handle TX power table materialization, HW power-control state, manual gain index programming, and per-rate SROM power limits.
- `wlc_phy_stay_in_carriersearch_nphy()` is a nested deaf-mode helper. It saves classifier and clip-detection state on the first enable, disables normal packet detection, resets CCA, increments `pi->nphy_deaf_count`, and restores state when the nesting count returns to zero.

## Important Types and State

- `struct brcms_phy` is the main mutable state container. This chunk reads or writes calibration state such as `nphy_txpwrctrl`, `nphy_txpwrindex[]`, `nphy_txpwr_idx[]`, `nphy_txiqlocal_bestc[]`, `nphy_txiqlocal_coeffsvalid`, `nphy_txiqlocal_chanspec`, `mphase_cal_phase_id`, `mphase_txcal_cmdidx`, `mphase_txcal_bestcoeffs[]`, `nphy_papd_*`, `nphy_rccal_value`, `nphy_rxcal_pwr_idx[]`, `tx_srom_max_rate_*`, `classifier_state`, `clip_state[]`, and `nphy_deaf_count`.
- `struct nphy_txgains` carries per-core `txlpf`, `txgm`, `pga`, `pad`, and `ipa` gain components.
- `struct nphy_iqcal_params` stores packed calibration gain and `ncorr[]` settings for TX IQ/LO commands.
- `struct nphy_papd_restore_state` stores PAPD setup state for AFE override, feedback mixer, VGA, internal PA, coupling power-up/attenuation, and saved baseband multipliers.
- `struct nphy_ipa_txcalgains` carries either a table index or explicit gain fields for IPA/PAPD calibration.
- `struct phy_iq_est` and `struct nphy_iq_comp` are the estimate/compensation data exchanged between RX IQ estimation and RX IQ coefficient registers.
- `struct nphy_txpwrindex` stores manual TX power index save/restore state, including AFE override, DAC gain, RF gain, bbmult, IQ compensation, LO compensation, and internal index bookkeeping.

## Control Flow

RSSI processing has two paths. Runtime packet RSSI goes through `wlc_phy_rssi_compute_nphy()`, which is pure header decoding plus merge-policy selection. Calibration RSSI enters `wlc_phy_rssi_cal_nphy()`, then either rev3+ code from the previous chunk or the rev2 path ending here. The rev2 path temporarily forces RSSI selection, powers RSSI blocks, disables classifiers and clipping, sweeps VCM, polls RSSI samples, picks the nearest VCM for each core/rail, writes fine offsets, then restores all saved state.

Sample playback is the shared tone source. `wlc_phy_tx_tone_nphy()` calls `wlc_phy_gen_load_samples_nphy()` to create a CORDIC sine/cosine table sized by channel width and DAC-test mode, then `wlc_phy_runsamples_nphy()` to program playback registers and trigger playback. `wlc_phy_stopplayback_nphy()` stops the active mode, restores saved bbmult and rev7+ LPF overrides, and unwinds deaf-mode state.

Periodic calibration starts in `wlc_phy_cal_perical_nphy_run()`. It suspends the MAC, enters PHY-reg access mode, snapshots original power indexes and gains, disables HW TX power control, optionally precalibrates TX gain, then runs TX IQ/LO calibration. On success it may run PAPD for IPA devices, briefly exits/re-enters PHY access, runs RX IQ calibration, saves calibration results, updates TX power coefficients, and updates timestamps. Multiphase mode executes the same logical work across phase IDs and preserves intermediate TX coefficients between calls.

TX IQ/LO calibration programs RFSEQ calibration gains, configures radio and PHY loopback, writes IQLOCAL ladder/start rows, plays a tone, and executes a list of encoded calibration commands. Each command selects a core and calibration type, writes gain-control/ncorr state, starts hardware calibration through register `0xc0`, waits for completion, and copies result rows back to active coefficient rows. Final phases persist the best coefficients and mark the channel as valid.

PAPD calibration is a nested sub-flow for IPA devices. Setup selects loopback/coupling state and starts a 4 MHz tone. Gain search (`wlc_phy_a3_nphy()`) repeatedly runs `wlc_phy_a2_nphy()` and checks epsilon table saturation to find a usable PAD/PGA/index. The final pass writes epsilon tables and scalar tables, computes an epsilon offset from band/radio-specific gain-delta arrays, enables PAPD compensation bits, restores TX digital filters, and restores TX power control.

RX IQ calibration has revision-specific setup. Rev3+ loops over RX cores, configures the appropriate TX/RX coupling and RFSEQ state, does gain control, plays a loopback tone, computes RX IQ compensation, optionally runs an RC sweep on older revs, then restores radio/PHY state. Rev2 performs a four-pass gain search per RX/TX core pair before computing compensation.

TX power control applies SROM-derived policy in two layers. `wlc_phy_txpwr_apply_nphy()` expands CCK/OFDM/MCS offsets into `tx_srom_max_rate_*` arrays for 2G and low/mid/high 5G bands. Runtime control then uses `wlc_phy_txpwrctrl_enable_nphy()` to write adjusted power tables into core tables 26/27 and set control bits, or clear hardware control and zero adjustment rows. `wlc_phy_txpwr_index_nphy()` temporarily or permanently programs manual gain indexes by reading gain, IQ, and LO rows from the selected per-core table.

## State and Persistence Behavior

Most setup helpers save hardware state into `pi->tx_rx_cal_radio_saveregs[]` or `pi->tx_rx_cal_phy_saveregs[]` and restore it before return. This save/restore pattern is essential because calibration deliberately changes RF paths, PA overrides, AFE controls, coupling attenuators, LPF settings, RFSEQ gains, IQLOCAL table rows, and sample-playback state.

Persistent calibration results are stored in both `struct brcms_phy` and hardware tables/registers:

- TX IQ/LO best coefficients persist in `pi->nphy_txiqlocal_bestc[]`, `pi->nphy_txiqlocal_coeffsvalid`, and `pi->nphy_txiqlocal_chanspec`; active coefficients persist in IQLOCAL table rows 80/85/88/93 until changed.
- Multiphase TX calibration persists intermediate command index and best coefficients in `pi->mphase_txcal_cmdidx` and `pi->mphase_txcal_bestcoeffs[]`.
- PAPD calibration persists last-cal timestamp/counter, gain-at-last-cal, selected PAPD gain indexes, epsilon offsets, `pi->nphy_papdcomp`, epsilon/scalar table contents, and PAPD enable bits.
- RX IQ calibration persists compensation registers `0x9a`-`0x9d`; older rev3 RC calibration persists `pi->nphy_rccal_value` and writes radio LPF RC override values.
- TX power configuration persists SROM-expanded rate arrays, `pi->nphy_txpwrctrl`, saved manual power indexes, `pi->nphy_txpwrindex[]`, core TX power table rows, AFE override bits, RFSEQ gain rows, IQ/LO compensation rows, and IPA RF power offsets.
- `wlc_phy_stay_in_carriersearch_nphy()` persists a nesting count. A mismatched enable/disable sequence can leave the PHY deaf or underflow the count.

Temporary allocations use `GFP_ATOMIC` in sample and PAPD smoothing helpers because calibration code may run in constrained driver contexts. Allocation failure returns early in helper paths; for sample generation it propagates as `-EBADE` from `wlc_phy_tx_tone_nphy()`.

## Dependencies

- `phy_int.h` supplies exported prototypes, `struct brcms_phy`, `struct nphy_txgains`, `struct nphy_txpwrindex`, RSSI/PAPD/power-control state fields, and PHY revision macros.
- Register definitions and table IDs come from the brcmsmac PHY/radio header set, including N-PHY table IDs such as `NPHY_TBL_ID_IQLOCAL`, `NPHY_TBL_ID_RFSEQ`, `NPHY_TBL_ID_SAMPLEPLAY`, `NPHY_TBL_ID_CORE1TXPWRCTL`, `NPHY_TBL_ID_CORE2TXPWRCTL`, `NPHY_TBL_ID_EPSILONTBL0/1`, and `NPHY_TBL_ID_SCALARTBL0/1`.
- Static calibration and gain data from earlier `phy_n.c` sections are consumed here: TX gain tables, IQ calibration gain tables, PAPD scalar and gain-delta tables, PAD/PGA gain-code arrays, and RX calibration gain tables.
- MAC/PHY integration helpers include `wlapi_suspend_mac_and_wait()`, `wlapi_enable_mac()`, `wlapi_bmac_write_shm()`, `wlapi_bmac_mctrl()`, `wlapi_bmac_mhf()`, `bcma_read32()`, `wlc_phyreg_enter()`, and `wlc_phyreg_exit()`.
- Math and kernel helpers include `cordic_calc_iq()`, `CORDIC_FLOAT()`, `int_sqrt()`, `DIV_ROUND_CLOSEST()`, `kmalloc_array()`, `kmalloc_objs()`, `kfree()`, `SPINWAIT()`, `WARN()`, and `WARN_ON()`.

## Integration Points

- `phy_cmn.c` calls `wlc_phy_cal_perical_nphy_run()` for periodic, forced, and watchdog-triggered calibration paths.
- `phy_cmn.c` calls `wlc_phy_rssi_compute_nphy()` when converting receive headers into RSSI values.
- `phy_cmn.c` calls `wlc_phy_txpower_sromlimit_get_nphy()` when common power-limit logic needs per-rate N-PHY SROM limits.
- Earlier N-PHY initialization calls `wlc_phy_txpwr_apply_nphy()` after SROM parsing so later rate-limit lookup and power table setup have populated arrays.
- Calibration code in this chunk calls earlier N-PHY helpers for RSSI polling, RF control overrides, RF sequences, RX core state, TX digital filters, TX power setup, save-cal handling, VCO calibration, antenna selection, and PAPD epsilon encode/decode.
- The sample-playback helpers are shared by TX calibration, RX calibration, RC sweep, PAPD calibration, and test-tone/debug paths elsewhere in `phy_n.c`.

## Risks and Sharp Edges

- Hardware state restoration is fragile. Many helpers share `pi->tx_rx_cal_radio_saveregs[]` and `pi->tx_rx_cal_phy_saveregs[]`; an early return after setup, nested calibration misuse, or wrong revision branch can leave RF paths, AFE overrides, LPF settings, or coupling registers in calibration mode.
- `wlc_phy_stay_in_carriersearch_nphy()` decrements without an explicit underflow guard. Call imbalance can permanently alter classifier/clip state or drive `nphy_deaf_count` below zero.
- Several functions return early on hardware timeouts or allocation failures after modifying state. For example, `wlc_phy_cal_txiqlo_nphy()` returns `-EIO` directly on TX IQ calibration timeout inside the command loop, which can bypass some cleanup in that path.
- Revision and band branches are dense. A change intended for 2057 rev7+ can accidentally affect 2056 or 2055 paths, and SROM external-PA flags select different TX gain tables.
- Manual TX power indexing saves original state only when `pi->nphy_txpwrindex[core].index < 0`. Repeated calls with mixed restore flags can produce surprising saved-state and calibration-coefficient behavior.
- Power-offset arithmetic uses unsigned `u8` arrays and subtracts twice the SROM offsets. Bad SROM data, missing bounds checks, or reinterpretation mistakes can underflow per-rate limits.
- PAPD gain search indexes band/radio-specific gain-code arrays. Off-by-one changes or wrong radio-revision selection can pick invalid gain codes or compute incorrect epsilon offsets.
- Many hardware waits use fixed `SPINWAIT()` budgets and only weak failure reporting. RF conditions, MAC state, or a hung PHY may produce silent bad coefficients or timeout warnings.
- Calibration suppresses normal receive behavior by suspending MAC and entering carrier-search/deaf mode. Latency-sensitive paths must not call these routines casually.

## Test Signals

- Build with brcmsmac and N-PHY enabled to catch prototype, table ID, register macro, and struct-field regressions.
- Exercise periodic calibration in both `PHY_PERICAL_AUTO` and forced/full modes on N-PHY hardware, checking that MAC suspend/resume happens and traffic resumes afterward.
- Validate both single-pass and multiphase calibration by tracing `pi->mphase_cal_phase_id`, `mphase_txcal_cmdidx`, `nphy_txiqlocal_coeffsvalid`, and `nphy_txiqlocal_chanspec`.
- For RSSI, compare reported RSSI across antenna merge modes and confirm calibration does not leave classifier/clip state disabled.
- For sample playback, verify test tone start/stop, nonzero sample table programming, bbmult restoration, and rev7+ LPF override cleanup.
- For TX IQ/LO and RX IQ, inspect IQLOCAL table rows and RX IQ registers before/after calibration; hardware timeout warnings from `"HW error: txiq calib"` or `"HW error: rxiq est"` are failure signals.
- For PAPD, verify IPA devices update epsilon/scalar tables, `nphy_papd_epsilon_offset[]`, `nphy_papd_tx_gain_at_last_cal[]`, and `nphy_papdcomp`, and that recalibration triggers when TX power index shifts by at least four steps.
- For TX power control, compare SROM-derived `tx_srom_max_rate_*` arrays against board data, verify HW on/off bit transitions in register `0x1e7`, and confirm manual `wlc_phy_txpwr_index_nphy()` restores prior gain and calibration rows.
- Run RF functional checks on 2.4 GHz, 5 GHz low/mid/high, 20 MHz, and 40 MHz channels because almost every path branches on band, bandwidth, PHY revision, radio revision, and IPA mode.
