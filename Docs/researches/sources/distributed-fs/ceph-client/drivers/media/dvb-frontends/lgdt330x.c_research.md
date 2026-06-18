# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt330x.c

## Purpose
`lgdt330x.c` supports LGDT3302 and LGDT3303 ATSC 8VSB / Annex B QAM demodulators. It provides an I2C-client-backed DVB frontend with legacy attach wrapping, chip-specific init/reset sequences, modulation switching, SNR/status/statistics reporting, and tuner integration.

## Important APIs, Types, and Functions
`struct lgdt330x_state` stores the I2C client, copied config, frontend, cached modulation/frequency, SNR, uncorrected-block count, and throttled-stat timestamp. I2C helpers are `i2c_write_demod_bytes()` and `i2c_read_demod_bytes()`. Reset/init paths are `lgdt3302_sw_reset()`, `lgdt3303_sw_reset()`, `lgdt330x_sw_reset()`, and `lgdt330x_init()`. Tuning uses `lgdt330x_set_parameters()` and `lgdt330x_get_frontend()`. Metrics use `calculate_snr()`, `lgdt3302_read_snr()`, `lgdt3303_read_snr()`, `lgdt330x_read_snr()`, `lgdt330x_read_signal_strength()`, `lgdt3302_read_status()`, `lgdt3303_read_status()`, and `lgdt330x_read_ucblocks()`. Driver entry points are `lgdt330x_probe()`, legacy `lgdt330x_attach()`, and `lgdt330x_remove()`.

## Control Flow
Probe allocates state, copies platform config, chooses LGDT3302 or LGDT3303 frontend ops, and verifies I2C communication by reading register 2. Init writes chip-specific register tables, applies LGDT3303 clock-polarity variants, initializes DVB statistic property scales, resets the demodulator, and clears the stat throttle. Set-frontend changes demod mode only when modulation changes, optionally switches an RF input through `pll_rf_set()`, writes LGDT3303 VSB/QAM register tables, combines serial/parallel MPEG output bits, invokes `set_ts_params()`, then asks the tuner to tune and resets the demod. Status callbacks read AGC/carrier/sync/FEC lock registers, update FE_HAS_* flags, and when locked refresh CNR and block counters at most once per second.

## State and Persistence
State is in the I2C chip registers plus software caches for current modulation/frequency, last SNR, `ucblocks`, and `last_stats_time`. The driver has no suspend cache or persistent storage. `release()` unregisters the I2C client for legacy attach users; remove frees the state.

## Dependencies and Integration Points
The driver depends on I2C, DVB frontend core, `intlog10()` fixed-point math, and board callbacks from `struct lgdt330x_config` for RF connector selection and TS parameter setup. It registers I2C id `"lgdt330x"` and exports `lgdt330x_attach()`. The frontends advertise `SYS_ATSC` and `SYS_DVBC_ANNEX_B`.

## Risks and Edge Cases
Several I2C reads in status/SNR paths do not fully propagate errors before consuming buffers. The legacy `lgdt330x_attach()` creates an I2C client from a stack-copied platform-data object; probe copies the data immediately, which is required for correctness. Cached modulation avoids reprogramming mode but frequency is always tracked with a FIXME noting tuner sharing with analog APIs. Block count increments use a fixed placeholder of 10000 and are not true hardware totals.

## Test Signals
Validate both LGDT3302 and LGDT3303 ops, LGDT3303 clock-polarity variants, VSB/QAM64/QAM256 switching, serial and parallel MPEG output, RF-selector callback use, tuner gate close after tuner writes, lock/status mapping, CNR decibel counters after lock, once-per-second stats throttling, and I2C client unregister/free behavior.
