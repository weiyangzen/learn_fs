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
