# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.c

## Purpose

`adxl380.c` is the shared IIO core for ADXL318, ADXL319, ADXL380, and ADXL382 accelerometers. It exposes accelerometer and temperature channels, configurable scale/sample rate/LPF/HPF/calibration bias, hardware FIFO buffering, threshold events, tap/double-tap gesture events, and chip-specific feature surfaces.

## Important APIs, Types, and Functions

`struct adxl380_chip_info` instances describe chip name, part ID family, scale table, sample-frequency table, temperature offset, low-power capability, and the IIO info table to expose. ADXL318/319 use `adxl318_info` without event callbacks; ADXL380/382 use `adxl380_info` with threshold and gesture events. `struct adxl380_state` stores regmap, device/chip info, lock, tap axis, range/ODR, FIFO set size/watermark, cached thresholds/timers/tap settings, IRQ/int-map selection, and dynamic LPF/HPF availability tables.

Major functions include measurement enable/disable, ODR/filter/range setters, activity/inactivity threshold and timer setters, tap configuration, FIFO sample programming, IRQ handler, raw/event callbacks, chip-info declarations, IRQ configuration, setup, and exported `adxl380_probe()`.

## Control Flow

Probe allocates the IIO device, defaults ODR to DSM, enables `vddio` and `vsupply`, calls setup, registers a kfifo buffer with FIFO attributes, then registers the device. Setup checks the AD vendor ID and part ID, differentiates ADXL380/382 through `MISC_0`, issues soft reset, enables all channels, selects streamed FIFO mode, enables all axes for activity/inactivity, configures a named INT0 or INT1 level-triggered interrupt, fills filter availability tables, and enters measurement mode.

Direct reads claim direct mode and bulk-read channel data. Writes update ODR, calibration bias, LPF, HPF, scale, thresholds, timers, and tap settings, usually by entering standby, writing registers, updating cached fields, and returning to measure mode. Buffer enable disables unselected channels, computes FIFO set size, clamps watermark, writes FIFO sample count, enables FIFO and watermark interrupt, and resumes measurement. The IRQ handler serializes status reads, pushes threshold/tap events, checks FIFO watermark, drains rounded FIFO entries with `regmap_noinc_read()`, and pushes samples to IIO buffers.

## State and Persistence Behavior

The mutex protects multi-register transactions and cached state. Activity/inactivity events can force ODR to VLP on low-power-capable chips when measurement is re-enabled. Range changes rescale cached thresholds and rewrite hardware threshold registers. LPF/HPF availability is derived from the current ODR and refreshed on ODR changes. Interrupt register addresses are selected at runtime from firmware-named `INT0` or `INT1`.

## Dependencies and Integration Points

The core depends on regmap, firmware properties for named IRQs, regulators, level-triggered threaded IRQs, IIO kfifo buffers, event sysfs attributes, no-increment FIFO reads, and chip info supplied by I2C/SPI wrappers. `adxl380_readable_noinc_reg()` is exported for bus regmap configs.

## Risks

`adxl380_write_tap_dur_us()` lacks the same explicit mutex guard used by nearby tap setters and can be called while its caller already holds the lock from the sysfs store path, making lock sequencing worth review. `adxl380_get_fifo_entries()` shifts the masked high bit expression and should be validated for correct 9-bit count extraction. `adxl380_samp_freq_avail()` returns success even if `adxl380_act_inact_enabled()` fails, which can hide register-read errors. Setup warns rather than fails on several ID mismatches, so the driver can bind to unexpected silicon. Interrupt configuration rejects edge-triggered IRQs and requires firmware names.

## Test Signals

Validation should cover all four chip compatibles, chip-info-specific event availability, regulator failures, missing/invalid INT0/INT1 firmware IRQs, level-high and level-low polarity programming, raw accel/temp reads, calibration bias sign extension, ODR-dependent LPF/HPF tables, low-power activity mode ODR restrictions, tap timing/value attributes, FIFO watermark and selected-channel buffering, and IRQ event plus FIFO delivery.
