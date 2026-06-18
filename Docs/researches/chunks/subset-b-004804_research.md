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
