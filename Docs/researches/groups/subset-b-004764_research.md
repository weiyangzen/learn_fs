# subset-b-004764 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_2p2_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_2p2_initvals.h

## Purpose
`ar9003_2p2_initvals.h` is a static hardware initialization data header for the ath9k AR9003 2.2 family. It contains register/value tables consumed by the AR9003 hardware setup path to program MAC, baseband, radio, SoC, PCIe SERDES, fast-clock, CCK Japan 2484 MHz, DFS, RX gain, and multiple TX gain profiles.

The file has no executable code. Its behavior is entirely in the shape and values of `static const u32` INI arrays. `ar9003_hw.c` includes the header and registers these arrays with `INIT_INI_ARRAY()` for the fallback AR9300/AR9003 2.2 path and as shared tables for later chips that `#define` their own names to these arrays.

## Important APIs, Types, And Data
- Include guard: `INITVALS_9003_2P2_H`.
- Table row conventions:
  - `[][2]`: address plus one value, usually non-modal core/preamble tables.
  - `[][3]`: address plus two modal values, used for fast-clock/DFS variants.
  - `[][5]`: address plus `5G_HT20`, `5G_HT40`, `2G_HT40`, `2G_HT20` values.
- Key tables and coverage:
  - `ar9300_2p2_radio_postamble` has 9 rows over radio-chain addresses `0x0001609c` through `0x00016940`.
  - `ar9300_2p2_radio_core` has 140 rows over radio core addresses `0x00016000` through `0x00016bd4`.
  - `ar9300_2p2_mac_core` has 153 rows over MAC addresses `0x00000008` through `0x000083d0`.
  - `ar9300_2p2_mac_postamble` has 8 modal rows.
  - `ar9300_2p2_soc_preamble` has 6 rows and `ar9300_2p2_soc_postamble` has 1 row.
  - `ar9300_2p2_baseband_core` has 159 rows and `ar9300_2p2_baseband_postamble` has 52 modal rows.
  - `ar9300Common_rx_gain_table_2p2` and `ar9300Common_wo_xlna_rx_gain_table_2p2` each have 256 RX gain rows.
  - TX gain profiles include `lowest_ob_db`, `low_ob_db`, `high_ob_db`, `high_power`, `mixed_ob_db`, and `type5`. Most have 102 modal rows; `type5` has 70 rows.
  - Special-purpose tables are `ar9300Modes_fast_clock_2p2`, `ar9300PciePhy_pll_on_clkreq_disable_L1_2p2`, `ar9300_2p2_baseband_core_txfir_coeff_japan_2484`, and `ar9300_2p2_baseband_postamble_dfs_channel`.

## Control Flow
The header itself has no branches or functions. Runtime control flow lives in `ar9003_hw_init_mode_regs()` and TX-gain mode selectors in `ar9003_hw.c`:
- For the generic AR9300/AR9003 2.2 branch, `iniMac`, `iniBB`, `iniRadio`, `iniSOC`, `iniModesRxGain`, `iniModesTxGain`, `iniPcieSerdes`, `iniPcieSerdesLowPower`, `iniModesFastClock`, `iniCckfirJapan2484`, and `ini_dfs` are bound to this file's arrays.
- `ar9003_tx_gain_table_mode0()` through mode 5 select the appropriate TX gain table. Fallback cases use this file's AR9300 2.2 tables when no newer chip-specific override is selected.
- Other initval headers alias selected shared tables, especially Japan CCK FIR and DFS/SoC postamble data, through preprocessor `#define`s.

## State And Persistence Behavior
The arrays are compile-time constant data stored in the kernel image. They do not persist state, allocate memory, or mutate. Their values become device state only when the ath9k register programming code writes them to hardware registers during reset/channel setup. Any persistent effect is in `struct ath_hw` INI array pointers and hardware registers, not in this header.

## Dependencies And Integration Points
- Depends on the ath9k INI-table convention and the `u32` type supplied by surrounding kernel headers.
- Integrated by `ar9003_hw.c` through `#include "ar9003_2p2_initvals.h"` and `INIT_INI_ARRAY()`.
- Register addresses and value semantics must match definitions in AR9003 PHY/MAC register headers such as `ar9003_phy.h` and related ath9k hardware code.
- Several later chip initval headers depend on these arrays by aliasing compatible shared tables.

## Risks
- A single incorrect literal can cause failed device bring-up, low RF performance, regulatory-channel malfunction, PCIe power-save instability, or calibration failures.
- Modal table width and row order are part of the ABI expected by ath9k INI writers. Changing a `[][5]` table to the wrong shape or reordering columns would silently program incorrect mode-specific values.
- RX/TX gain tables are tightly coupled to EEPROM/board configuration and power-control assumptions. Using a profile on the wrong board variant can affect transmit power, sensitivity, or compliance.
- Shared aliases from other chip headers mean changes here can affect devices beyond AR9300 2.2.

## Test Signals
- Build coverage should compile ath9k with this header included and catch syntax/shape errors.
- Hardware smoke tests should cover AR9300/AR9003 reset, channel changes, 2.4/5 GHz operation, HT20/HT40, DFS channels, and Japan channel 14 CCK behavior.
- Runtime signals include successful `INIT_INI_ARRAY()` programming, no reset timeouts, stable PCIe suspend/resume when SERDES tables are used, expected noise-floor/calibration completion, and throughput/RSSI sanity across bands.
- Regression checks should compare selected table row counts and modal widths against known-good upstream values before and after any edit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_2p2_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.c

## Purpose
`ar9003_aic.c` implements AR9003 Adaptive Interference Cancellation support for Bluetooth coexistence. It programs AIC gain/calibration SRAM, drives a calibration state machine, post-processes sparse measured BT-channel data into a full SRAM table, and exposes a small set of AIC operations used by the MCI coexistence path.

The current `ar9003_hw_is_aic_enabled()` unconditionally returns `false`, with a comment saying AIC is disabled until full hardware and driver-layer support are ready. The rest of the implementation remains present and is called only if that gate is changed or bypassed.

## Important APIs, Types, And Functions
- Static lookup tables:
  - `com_att_db_table[6]`: common attenuation dB choices `{0, 3, 9, 15, 21, 27}`.
  - `aic_lin_table[69]`: decreasing linear gain magnitudes used to convert dB-indexed SRAM values to interpolation-friendly signed linear values.
- Helpers:
  - `ar9003_hw_is_aic_enabled()` supplies `priv_ops->is_aic_enabled`.
  - `ar9003_aic_find_valid()` scans up or down for the next calibrated BT channel.
  - `ar9003_aic_find_index()` maps linear magnitude or common attenuation back to table indices.
  - `ar9003_aic_gain_table()` writes a 19-word attenuation table into AIC SRAM using auto-increment.
- Calibration control:
  - `ar9003_aic_cal_start()` clears SRAM, programs AIC control registers, enables BT AIC reference signaling, records TSF start time, and moves state to `AIC_CAL_STATE_STARTED`.
  - `ar9003_aic_cal_continue()` polls or samples hardware calibration progress, reads valid SRAM entries, either restarts calibration for more channels or finalizes.
  - `ar9003_aic_cal_post_process()` interpolates/extrapolates missing BT-channel coefficients and repacks final SRAM words.
  - `ar9003_aic_cal_done()` disables the BT reference signal and marks state `DONE` or `ERROR`.
- Exported functions:
  - `ar9003_aic_calibration()`: multi-step state-machine entry used by MCI messages.
  - `ar9003_aic_start_normal()`: loads processed AIC SRAM and enables normal AIC hardware operation.
  - `ar9003_aic_cal_reset()`: returns state to idle.
  - `ar9003_aic_calibration_single()`: start and complete calibration in one blocking flow.
  - `ar9003_hw_attach_aic_ops()`: installs the `is_aic_enabled` private op.

## Control Flow
Normal multi-step flow is:
1. MCI/coexistence code checks `ath9k_hw_is_aic_enabled()`. With the current hard-disabled implementation, no AIC calibration is run.
2. If enabled, `ar9003_aic_calibration()` dispatches by `aic->aic_cal_state`.
3. `IDLE` calls `ar9003_aic_cal_start(ah, 1)`, which clears `aic->aic_sram`, configures AIC control registers, writes gain tables, enables the BT reference signal, and starts calibration.
4. `STARTED` calls `ar9003_aic_cal_continue(ah, false)`. It reads `ATH_MCI_CONFIG_AIC_CAL_NUM_CHAN`, checks `AR_PHY_AIC_CAL_ENABLE` rather than `CAL_DONE`, reads SRAM entries from chain B1, and counts newly calibrated BT channels.
5. Once enough channels are seen, `ar9003_aic_cal_done()` runs post-processing. Missing channels are filled from neighboring valid data using interpolation or edge extrapolation; failure to find sufficient anchors returns `ERROR`.
6. MCI can then call `ar9003_aic_start_normal()`, which writes the full processed SRAM table back to hardware and sets raw AIC enable registers.

The single-shot flow uses `ar9003_aic_calibration_single()`, passing the configured channel count as `min_valid_count` and letting `ar9003_aic_cal_continue()` busy-wait up to 10,000 iterations of 100 microseconds.

## State And Persistence Behavior
- Persistent software state is in `ah->btcoex_hw.aic`:
  - `aic_cal_state`
  - `aic_caled_chan`
  - `aic_sram[ATH_AIC_MAX_BT_CHANNEL]`
  - `aic_cal_start_time`
  - `aic_enabled`
- Hardware state is stored in AIC SRAM and AIC/BT coexistence registers. `ATH_AIC_SRAM_AUTO_INCREMENT` is used when streaming tables.
- Calibration data is not stored in EEPROM or files. It is runtime state that must be regenerated after reset unless higher layers preserve it.

## Dependencies And Integration Points
- Includes `hw.h`, `hw-ops.h`, `ar9003_mci.h`, `ar9003_aic.h`, `ar9003_phy.h`, and `reg_aic.h`.
- Uses ath9k register helpers `REG_READ`, `REG_WRITE`, `REG_SET_BIT`, `REG_CLR_BIT`, `REG_RMW_FIELD`, `SM`, and `MS`.
- Reads MCI configuration from `ah->btcoex_hw.mci.config`, especially `ATH_MCI_CONFIG_DISABLE_AIC` and `ATH_MCI_CONFIG_AIC_CAL_NUM_CHAN`.
- MCI integration appears in `ar9003_mci.c`, which calls AIC calibration/start/reset commands when `ath9k_hw_is_aic_enabled()` is true.
- Installs only `priv_ops->is_aic_enabled`; the other exported AIC functions are called directly by MCI code, not through attached ops.

## Risks
- The hardcoded `return false` means this file is effectively dormant; enabling it would expose untested paths.
- `ar9003_aic_start_normal()` contains FIXME raw register writes (`0xa6b0` and related addresses), which are fragile and harder to audit than named fields.
- Post-processing relies on at least two valid calibration anchors for extrapolation and sensible linear-gain indexes. Bad SRAM data can produce clamped but degraded coefficients.
- The single-shot path can busy-wait for about one second, which is inappropriate in some contexts if called under locks or timing-sensitive paths.
- Table index math uses signed 16-bit intermediates and assumes SRAM field values keep `dir_path_gain_idx`/`quad_path_gain_idx` inside `aic_lin_table`.

## Test Signals
- Unit-style hardware mocks should cover `ar9003_aic_find_valid()`, `ar9003_aic_find_index()`, and interpolation/extrapolation edge cases in `ar9003_aic_cal_post_process()`.
- On hardware, useful signals are AIC state transitions `IDLE -> STARTED -> DONE`, expected `aic_caled_chan`, nonzero valid SRAM words, BT coexistence stability, and no MCI calibration timeouts.
- Regression tests should verify that disabling AIC via `ATH_MCI_CONFIG_DISABLE_AIC` still gates operation if the current early return is removed.
- Register traces should confirm BT reference enable/disable symmetry and correct SRAM auto-increment writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.h

## Purpose
`ar9003_aic.h` declares constants, state types, packed SRAM helper structures, and public function prototypes for AR9003 Adaptive Interference Cancellation. It is the local contract between the AIC implementation, MCI Bluetooth coexistence code, and hardware attach paths.

## Important APIs, Types, And Constants
- Include guard: `AR9003_AIC_H`.
- Table/limit constants:
  - `ATH_AIC_MAX_COM_ATT_DB_TABLE` = 6.
  - `ATH_AIC_MAX_AIC_LIN_TABLE` = 69.
  - Rotation attenuation min/max constants cover 0 through 37 dB.
- SRAM/register constants:
  - `ATH_AIC_SRAM_AUTO_INCREMENT` = `0x80000000`.
  - `ATH_AIC_SRAM_GAIN_TABLE_OFFSET` = `0x280`.
  - `ATH_AIC_SRAM_CAL_OFFSET` = `0x140`.
  - `ATH_AIC_SRAM_OFFSET` = `0x00`.
  - `ATH_AIC_BT_JUPITER_CTRL` = `0x66820`.
  - `ATH_AIC_BT_AIC_ENABLE` = `0x02`.
- `enum aic_cal_state` defines the lifecycle states `IDLE`, `STARTED`, `DONE`, and `ERROR`.
- `struct ath_aic_sram_info` models decoded SRAM fields: valid bit, VGA signs, direct/quadrature rotation attenuation, and common attenuation index.
- `struct ath_aic_out_info` holds signed linear direct/quadrature gain values used during interpolation.
- Public functions:
  - `ar9003_aic_calibration()`
  - `ar9003_aic_start_normal()`
  - `ar9003_aic_cal_reset()`
  - `ar9003_aic_calibration_single()`

## Control Flow
This header does not implement control flow, but its declarations define the legal transitions used by `ar9003_aic.c`:
- `AIC_CAL_STATE_IDLE` starts calibration.
- `AIC_CAL_STATE_STARTED` continues calibration.
- `AIC_CAL_STATE_DONE` allows `ar9003_aic_start_normal()` to load normal AIC operation.
- `AIC_CAL_STATE_ERROR` reports unusable calibration state until reset.

## State And Persistence Behavior
The header's structures are temporary decoded forms, not persistent storage. Persistent runtime AIC state is held in `struct ath9k_hw_aic` in `btcoex.h`, while these definitions describe the interpretation of SRAM words and function return values. The constants define hardware offsets and bit values that remain fixed at compile time.

## Dependencies And Integration Points
- Requires `struct ath_hw`, `u8`, `u32`, `int16_t`, and `bool` to be visible from including ath9k/kernel headers.
- Used by `ar9003_aic.c` for implementation and by `ar9003_mci.c` for command handling around calibration/start/reset/single-shot calibration.
- Related state storage lives in `btcoex.h`, which contains `aic_enabled`, `aic_cal_state`, `aic_caled_chan`, `aic_sram`, and `aic_cal_start_time`.
- Hardware field names are in `reg_aic.h`; this header carries only local limits and a few raw offsets.

## Risks
- Constants must match the hardware SRAM layout. A wrong offset or table size causes incorrect SRAM streaming and can corrupt unrelated AIC memory.
- `struct ath_aic_sram_info` uses bitfields only as a decoded software container; it is not safe as a direct packed hardware overlay.
- Return type `u8` for state functions assumes enum values stay small and compatible with MCI message expectations.
- Raw register constants duplicate knowledge that would be safer as named register definitions.

## Test Signals
- Compile tests catch declaration drift between this header and `ar9003_aic.c`.
- Static checks should confirm constants stay consistent with `ATH_AIC_MAX_BT_CHANNEL` and `reg_aic.h` SRAM fields.
- Runtime tests should assert state-return values match `enum aic_cal_state` and that callers handle `ERROR` distinctly from in-progress states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_aic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_buffalo_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_buffalo_initvals.h

## Purpose
`ar9003_buffalo_initvals.h` provides a board/vendor-specific high-power TX gain table for AR9300/AR9003 hardware used when `ah->config.tx_gain_buffalo` is selected. It overrides the generic AR9300 2.2 high-power TX gain profile without changing the rest of the chip initialization tables.

## Important APIs, Types, And Data
- Include guard: `INITVALS_9003_BUFFALO_H`.
- Exports one table: `ar9300Modes_high_power_tx_gain_table_buffalo[][5]`.
- The table has 102 rows and follows the standard modal TX-gain layout:
  - column 0: register address
  - columns 1-4: `5G_HT20`, `5G_HT40`, `2G_HT40`, `2G_HT20`
- Address coverage starts at `0x0000a2dc` and ends at `0x00016868`, matching the generic high-power table shape.
- The table includes primary TX gain ladder rows around `0x0000a500`-`0x0000a63c`, duplicated chain-specific rows at `0x0000b2dc`/`0x0000c2dc` ranges, and radio/chain calibration values around `0x00016044`, `0x00016444`, and `0x00016844`.

## Control Flow
The header has no executable control flow. Runtime selection happens in `ar9003_tx_gain_table_mode3()` in `ar9003_hw.c`:
- For newer chip revisions, chip-specific high-power tables are selected first.
- In the generic fallback branch, `ah->config.tx_gain_buffalo` selects `ar9300Modes_high_power_tx_gain_table_buffalo`.
- If the flag is not set, the generic `ar9300Modes_high_power_tx_gain_table_2p2` is used instead.

## State And Persistence Behavior
The table is immutable compile-time data. It affects runtime state only when ath9k binds it to `ah->iniModesTxGain` and later writes its entries into device registers during hardware initialization or channel reset. The selection flag is in `struct ath_hw` configuration; this header stores no mutable state.

## Dependencies And Integration Points
- Included by `ar9003_hw.c` alongside the generic AR9003 initvals.
- Depends on the same ath9k modal INI writer assumptions as other `[][5]` TX gain tables.
- Integrated with board configuration through `ah->config.tx_gain_buffalo`, declared in `hw.h`.
- Must remain row-compatible with generic AR9300 high-power TX gain tables so selection can be swapped by pointer without custom programming logic.

## Risks
- Vendor-specific transmit gain values have regulatory and RF-performance implications. Incorrect values may overdrive power, degrade EVM, or violate board limits.
- If row count or register order diverges unexpectedly from the generic high-power table, shared INI programming assumptions may break.
- Because the table is selected by a configuration flag, misdetecting Buffalo hardware can apply this profile to an incompatible board.

## Test Signals
- Build tests should confirm the table compiles and is visible to `ar9003_hw.c`.
- Configuration tests should verify `tx_gain_buffalo` selects this table only in mode 3 fallback paths.
- Hardware validation should measure conducted TX power, EVM, spectral mask, per-rate power limits, and throughput on the target Buffalo boards across 2.4/5 GHz and HT20/HT40.
- Register-dump comparisons against vendor-known init sequences are the strongest regression signal for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_buffalo_initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_calib.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_calib.c -->
