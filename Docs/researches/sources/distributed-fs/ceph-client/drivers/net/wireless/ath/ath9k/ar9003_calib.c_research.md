# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_calib.c

## Purpose
`ar9003_calib.c` implements AR9003-family PHY calibration for ath9k. It covers periodic IQ mismatch/noise-floor calibration and reset-time calibration sequences for SoC and PCIe/OEM variants. It computes RX and TX IQ correction coefficients, runs AGC/offset/filter/peak-detect/carrier-leak related calibrations, handles reusable calibration state, integrates with MCI/RTT, and attaches the calibration operations into ath9k hardware op tables.

## Important APIs, Types, And Functions
- Constants:
  - `MAX_MEASUREMENT`, `MAX_MAG_DELTA`, `MAX_PHS_DELTA`, `MAXIQCAL`.
  - `OFF_UPPER_LT`, `OFF_LOWER_LT` for dynamic OSDAC selection.
  - `DELPT` for TX IQ phase delta.
- Types:
  - `struct coeff` stores per-chain/per-measurement magnitude and phase coefficients plus current IQ correction words.
  - `enum ar9003_cal_types` currently defines `IQ_MISMATCH_CAL`.
- Periodic calibration:
  - `ar9003_hw_setup_calibration()` programs IQ calibration mode and starts PHY calibration.
  - `ar9003_hw_per_calibration()` checks completion, collects samples, post-processes, and marks `caldata->CalValid`.
  - `ar9003_hw_calibrate()` runs the current calibration list and handles long-interval noise-floor calibration through common ath9k NF helpers.
  - `ar9003_hw_iqcal_collect()` accumulates measurement registers.
  - `ar9003_hw_iqcalibrate()` computes and writes RX IQ coefficients.
- TX IQ calibration:
  - `ar9003_hw_solve_iq_cal()`, `ar9003_hw_find_mag_approx()`, and `ar9003_hw_calc_iq_corr()` parse channel-info results and solve/quantize correction coefficients.
  - `ar9003_hw_detect_outlier()` and `ar9003_hw_tx_iq_cal_outlier_detection()` filter unstable measurements and write coefficient tables.
  - `ar9003_hw_tx_iq_cal_run()` starts standalone TX IQ calibration.
  - `ar955x_tx_iq_cal_median()` handles AR9550 median selection over three runs.
  - `ar9003_hw_tx_iq_cal_post_proc()` reads calibration results and stores coefficients in `caldata`.
  - `ar9003_hw_tx_iq_cal_reload()` reloads reusable coefficients.
- Reset-time calibration:
  - `ar9003_hw_manual_peak_cal()` performs a binary-search-like manual peak detector calibration per chain.
  - `ar9003_hw_do_pcoem_manual_peak_cal()` runs manual peak calibration and persists caldac values for RTT.
  - `ar9003_hw_cl_cal_post_proc()` saves or restores carrier-leak calibration tables.
  - `ar9003_hw_init_cal_common()` initializes calibration list state.
  - `ar9003_hw_init_cal_pcoem()` is the PCIe/OEM reset calibration path.
  - `ar9003_hw_init_cal_soc()` is the SoC reset calibration path.
  - `ar9003_hw_attach_calib_ops()` wires the private and public calibration ops.

## Control Flow
Attach-time flow:
1. `ar9003_hw_attach_calib_ops()` selects `priv_ops->init_cal` based on `AR_SREV_9003_PCOEM(ah)`.
2. It also installs `init_cal_settings`, `setup_calibration`, and `ops->calibrate`.
3. `ar9003_hw_init_cal_settings()` enables supported calibration flags based on silicon revision, including TX IQ and TX IQ-on-AGC for AR9485-or-later except AR9340.

Periodic flow:
1. Higher ath9k code calls `ops->calibrate`.
2. `ar9003_hw_calibrate()` advances `ah->cal_list_curr` if a calibration is waiting or running.
3. `ar9003_hw_per_calibration()` either waits for `AR_PHY_TIMING4_DO_CAL` to clear, collects a sample, restarts for more samples, or post-processes when enough samples are collected.
4. On long calibration intervals, `ar9003_hw_calibrate()` reads noise-floor results, loads historical NF, and starts a new NF calibration.

Reset-time PCIe/OEM flow:
1. `ar9003_hw_init_cal_pcoem()` temporarily uses chip chainmasks, optionally restores/runs RTT, decides whether AGC must run, and handles reusable TXCL/TXIQ state in `caldata`.
2. It may coordinate with MCI on 2 GHz before and after AGC calibration.
3. It runs AGC calibration when needed, performs manual peak calibration, post-processes or reloads TX IQ, saves/restores carrier-leak tables, fills RTT history when reusable, restores runtime chainmasks, and initializes periodic calibration state.

Reset-time SoC flow:
1. `ar9003_hw_init_cal_soc()` enables TXCL and TXIQ paths according to feature flags and channel width.
2. It may run standalone TX IQ calibration, dynamic OSDAC selection for AR9550 2 GHz, manual peak calibration, and AGC calibration.
3. AR9550 with TXIQ uses three AGC/TXIQ passes and median coefficient selection; other chips usually use a single post-process pass.
4. It restores runtime chainmasks and initializes periodic calibration state.

## State And Persistence Behavior
- Uses mutable fields in `struct ath_hw`: calibration lists, `cal_samples`, total IQ measurement accumulators, chainmasks, enabled/supported calibration bitmasks, current channel, flags such as `AH_FASTCC`, and `ah->caldata`.
- Uses `struct ath9k_hw_cal_data` to persist per-channel reusable calibration state:
  - `CalValid`
  - `cal_flags` bits such as `TXIQCAL_DONE`, `TXCLCAL_DONE`, `SW_PKDET_DONE`, and RTT-related flags from other files.
  - `tx_corr_coeff`, `num_measures`, `tx_clcal`, and `caldac`.
- Writes many PHY registers directly. Hardware state includes IQ correction enable bits, TX coefficient tables, AGC control bits, CL tables, RX/TX gain-stage overrides, OSDAC values, and RTT history registers.
- Calibration persistence is runtime/per-channel, not filesystem-backed. It survives fast channel changes only through `caldata`.

## Dependencies And Integration Points
- Includes `hw.h`, `hw-ops.h`, `ar9003_phy.h`, `ar9003_rtt.h`, and `ar9003_mci.h`.
- Uses common ath9k calibration helpers from `calib.c`, including reset/list handling and noise-floor APIs.
- Relies on register macros from AR9003 PHY headers and silicon revision predicates such as `AR_SREV_9550`, `AR_SREV_9565`, `AR_SREV_9003_PCOEM`, `AR_SREV_9485_OR_LATER`, and `AR_SREV_9340`.
- MCI integration uses `ath9k_hw_mci_is_enabled()`, `ar9003_mci_init_cal_req()`, and `ar9003_mci_init_cal_done()` to coordinate calibration with Bluetooth coexistence.
- RTT integration uses `ar9003_hw_rtt_restore()`, `ar9003_hw_rtt_enable()`, `ar9003_hw_rtt_set_mask()`, `ar9003_hw_rtt_clear_hist()`, `ar9003_hw_rtt_fill_hist()`, `ar9003_hw_rtt_load_hist()`, and `ar9003_hw_rtt_disable()`.
- The public integration point is `ath_hw_ops.calibrate` and private ops used by reset/channel setup.

## Risks
- This code is register- and silicon-revision-sensitive. A wrong revision predicate or field write can break calibration on a subset of chips.
- Several coefficient calculations guard divide-by-zero and bounds, but invalid channel-info readings still lead to failed TX IQ post-processing with limited recovery beyond debug logs.
- `ar9003_hw_tx_iq_cal_post_proc()` uses a static `struct coeff`; this is acceptable for serialized hardware calibration but would be unsafe if concurrent calibrations on different devices entered the function simultaneously.
- Manual peak calibration temporarily overrides RX/LNA/AGC paths. Early returns or missed restore writes can leave hardware in a bad receive state.
- Reusable `caldata` is performance-critical. Incorrectly setting or clearing `TXIQCAL_DONE`, `TXCLCAL_DONE`, or `SW_PKDET_DONE` can skip needed calibration or discard useful cached state.
- MCI/RTT paths add coordination risk: calibration can be marked non-reusable or require RF bus access, and failures can leave coexistence or RTT history stale.
- Half/quarter-rate channels skip TX IQ calibration, so changes must preserve that behavior.

## Test Signals
- Build and static-analysis coverage should catch register macro drift, type issues, and missing prototypes.
- Hardware reset/channel-change tests should cover PCIe/OEM and SoC families, at least AR9300, AR9485, AR9550, AR9565, AR9531/9561 if available, with 2.4/5 GHz and HT20/HT40/half/quarter-rate channels.
- Periodic calibration signals include `CalValid` being set, calibration list state reaching `CAL_DONE`, successful noise-floor load/start, and no repeated timeout logs.
- TX IQ signals include successful `AR_PHY_TX_IQCAL_START_DO_CAL` completion, coefficient values within expected signed 7-bit ranges, `TXIQCAL_DONE` persistence when reusable, and stable EVM/throughput.
- Peak/AGC signals include `ath9k_hw_wait()` completion, expected AGC/offset/peak flags, restored chainmasks, and no degraded RX sensitivity after calibration.
- MCI/RTT test cases should verify calibration request/done pairing, RTT history restore/fill, and behavior when calibration is not reusable.
