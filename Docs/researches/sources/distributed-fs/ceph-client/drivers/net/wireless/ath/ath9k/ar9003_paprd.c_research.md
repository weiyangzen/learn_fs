# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_paprd.c

## Purpose
`ar9003_paprd.c` implements peak-to-average power ratio distortion correction for AR9003 transmit chains. It configures PAPRD training, chooses training power, forces TX gain for training frames, reads hardware channel-info bins, builds the PA predistortion curve, stores the curve in calibration data, and writes the final PAPRD table into PHY registers.

## Important APIs, Types, and Functions
Exported APIs are `ar9003_paprd_enable()`, `ar9003_paprd_populate_single_table()`, `ar9003_paprd_setup_gain_table()`, `ar9003_paprd_create_curve()`, `ar9003_paprd_init_table()`, `ar9003_paprd_is_done()`, and `ar9003_is_paprd_enabled()`. The main internal helpers are `ar9003_get_training_power_2g()`, `ar9003_get_training_power_5g()`, `ar9003_paprd_setup_single_table()`, `ar9003_paprd_get_gain_table()`, `ar9003_get_desired_gain()`, `ar9003_tx_force_gain()`, `create_pa_curve()`, and `ar9003_paprd_retrain_pa_in()`.

The file uses `ah->paprd_target_power`, `ah->paprd_training_power`, `ah->paprd_ratemask`, `ah->paprd_ratemask_ht40`, `ah->paprd_table_write_done`, `ah->paprd_gain_table_entries`, and `ah->paprd_gain_table_index`. Per-channel persistent calibration data is stored in `struct ath9k_hw_cal_data`, especially `pa_table[chain]` and `small_signal_gain[chain]`.

## Control Flow
PAPRD setup begins with `ar9003_paprd_init_table()`, which calls `ar9003_paprd_setup_single_table()` and then snapshots the TX gain table. Setup selects 2 GHz or 5 GHz training power from current transmit power registers, target power, eeprom-derived scale factors, channel width, and chip revision. It writes AM2AM/AM2PM/HT40 masks, configures per-chain single-table mode and adaptive correction fields, disables PAPRD while training, and programs trainer control registers with chip-specific loopback, gain, quick-drop, ADC desired size, correction length, sample count, and pre/post scale settings.

For each chain, the upper driver calls `ar9003_paprd_setup_gain_table()` before sending a training frame. That function computes desired gain from target power, OLPC gain delta, thermal/voltage correction, desired scale, and closed-loop gain modifier, finds the first TX gain table index that satisfies the desired gain, and writes the decomposed gain fields into forced-gain registers.

After a training frame completes, `ar9003_paprd_create_curve()` reads two banks of 48 channel-info words from hardware, invokes `create_pa_curve()` to derive PA input and angle correction values, optionally requests retraining through `ar9003_paprd_retrain_pa_in()`, clears the train-done bit, and returns `0`, `-2`, `-EINPROGRESS`, or `-ENOMEM`. Successful curves are activated by `ar9003_paprd_populate_single_table()`, which writes `PAPRD_TABLE_SZ` values to the per-chain PAPRD memory table, writes small-signal gain, and programs training power into PAPRD control registers. `ar9003_paprd_enable()` then enables correction for active TX chains unless eeprom sub-band bits disable it.

## State and Persistence Behavior
PAPRD results persist in the in-memory `caldata` for the channel and in hardware PAPRD memory/control registers after activation. `ah->paprd_table_write_done` prevents repeated eeprom txpower/PAPRD table programming until reset code clears it. Gain-table snapshots persist in `ath_hw` between setup and per-chain training. No filesystem or firmware persistence is performed.

## Dependencies and Integration Points
`link.c` owns the workqueue flow (`ath_paprd_calibrate()`): initialize table, allocate/send PAPRD frames, wait for completion from TX status, call `ar9003_paprd_is_done()`, call `ar9003_paprd_create_curve()`, retry if requested, then activate tables. `xmit.c` marks PAPRD training frames and completes the PAPRD completion. `ar9003_eeprom.c` computes PAPRD target power and rate masks and disables rates whose target delta exceeds the scale factor. Register definitions come from `ar9003_phy.h`.

## Risks
`create_pa_curve()` is numerically dense fixed-point code with many division points and scale shifts; it has explicit zero guards but remains sensitive to sparse or noisy training bins. `ar9003_paprd_setup_gain_table()` does not clamp `gain_index` after scanning the gain table, so an unexpected desired gain above all entries risks indexing past the cached table in `ar9003_tx_force_gain()`. Some chip-specific quick-drop/capdiv adjustment paths can return `-EINPROGRESS` indefinitely if hardware measurements sit at the boundary. A source comment questions whether the B2 training-power field is correct, marking a maintenance risk.

## Test Signals
Strong signals are successful `ath_paprd_calibrate()` completion, `PAPRD_TRAIN_DONE` with acceptable AGC2 power, no repeated `-EINPROGRESS` loops, populated nonzero `caldata->pa_table` and `small_signal_gain`, correct per-chain PAPRD memory writes, and stable throughput/EVM improvements without transmit power regressions. Regression tests should cover 2 GHz/5 GHz, HT20/HT40, one/two/three-chain masks, AR9330/9485/9462/9565 revision branches, and eeprom sub-band PAPRD disable bits.
