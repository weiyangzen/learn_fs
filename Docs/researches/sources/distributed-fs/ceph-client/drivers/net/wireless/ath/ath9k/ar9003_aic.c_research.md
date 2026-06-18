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
