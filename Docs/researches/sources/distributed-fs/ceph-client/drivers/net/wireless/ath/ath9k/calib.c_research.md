# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.c

Purpose: Provides common ath9k calibration support, centered on noise-floor calibration history, NF loading into baseband, calibration validity reset, and stuck-beacon interference handling.

Important APIs/functions: Exported APIs are `ath9k_hw_getchan_noise()`, `ath9k_hw_reset_calibration()`, `ath9k_hw_reset_calvalid()`, `ath9k_hw_start_nfcal()`, `ath9k_hw_loadnf()`, `ath9k_hw_getnf()`, `ath9k_init_nfcal_hist_buffer()`, and `ath9k_hw_bstuck_nfcal()`. Internal helpers compute median NF history (`ath9k_hw_get_nf_hist_mid()`), choose 2 GHz/5 GHz NF limits, read EEPROM NF thresholds, update history buffers, and sanitize raw readings.

Control flow: Calibration reset calls hardware setup, marks current calibration running, clears measurement signs, and resets sample count. NF start sets pending state, enables/disables baseband NF update, and triggers AGC NF. NF load writes cached/default/override NF values to `ah->nf_regs`, forces baseband load, waits up to 22.2 ms, optionally restarts an interrupted NF calibration, and restores max CCA power to `-50`. NF get refuses incomplete AGC NF, reads raw NF through hardware ops, clamps against per-band limits, warns on EEPROM threshold failures, updates per-chain median history, stores channel noisefloor, and updates `ah->noise`.

State/persistence: State lives in `ah->caldata`, `nfCalHist[]`, `cal_flags` (`NFCAL_PENDING`, `NFCAL_INTF`), `ah->cal_list*`, `ah->meas*`, `ah->cal_samples`, `ah->noise`, `chan->noisefloor`, `ah->nf_override`, and hardware AGC/NF registers. NF history persists per channel calibration data and smooths transient readings.

Dependencies/integration: Uses `hw.h`, `hw-ops.h`, Linux sort/export, EEPROM ops, ath debug categories, channel width helpers, register RMW buffering, and beacon stuck handling from `beacon.c`.

Risks: NF load timeout handling intentionally returns before restoring `-50` to avoid RX deafness from overlapping loads. Incorrect chainmask or HT40 gating can touch wrong NF registers. Interference mode bypasses max NF clamping after stuck beacons; failure to clear it would keep elevated NF. `nf_override` from debugfs directly affects baseband NF programming.

Test signals: Verify NF median updates, invalid-count warmup behavior, 2 GHz/5 GHz limits, HT20/HT40 chain handling, NF timeout path, forced override, stuck-beacon NF recalibration, calibration-valid reset on supported revisions, and stable RX sensitivity after repeated channel resets.
