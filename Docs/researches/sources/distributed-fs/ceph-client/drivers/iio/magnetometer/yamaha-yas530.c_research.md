# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/yamaha-yas530.c

## Purpose
I2C IIO driver for Yamaha YAS530/YAS532/YAS533/YAS537 3-axis magnetometers. It implements device-specific calibration extraction, measurement conversion, runtime PM, mount matrix, and triggered-buffer capture.

## Important APIs, Types, And Functions
`struct yas5xx_chip_info` defines per-variant IDs, scale, temperature reference, volatile registers, and function pointers for measurement, calibration, offset measurement, and power-on. `struct yas5xx` stores chip info, calibration, hard offsets, mount matrix, regmap, regulators, optional reset GPIO, mutex, and scan buffer. `yas530_measure()` and `yas537_measure()` perform low-level conversions. `yas530_get_measure()` and `yas537_get_measure()` produce IIO-facing temperature and X/Y/Z values. Calibration readers decode OTP bitfields and program YAS537 trims. `yas5xx_probe()` orchestrates regulators, reset, ID check, calibration, power-on, offset discovery, buffer setup, IIO registration, and PM.

## Control Flow
Probe powers rails, waits for startup, releases optional reset, creates regmap, checks device ID, reads calibration, powers on with variant logic, measures hard offsets where applicable, sets up channels and triggered buffer, then enables runtime PM. Reads and trigger fills resume the device, call the selected `get_measure`, then autosuspend. Removal unregisters IIO/buffer resources, disables PM, asserts reset, and disables regulators.

## State And Persistence
Calibration is read from device OTP and retained in RAM; YAS537 trim registers are programmed from OTP. YAS530/YAS532 hard offsets are discovered by a binary-search-like coil measurement and stored in RAM/registers. Runtime PM resets power and re-runs `power_on()` on resume.

## Dependencies And Integration Points
Uses I2C regmap, regulator bulk APIs, optional GPIO reset, runtime PM, random input from calibration bytes, IIO mount matrix, triggered buffers, and OF/I2C match data.

## Risks And Test Signals
This file is calibration-heavy: bitfield extraction, version-specific math, and offset search are the main risk areas. Runtime resume does not re-read OTP or remeasure offsets, so verify register state after power cycling. Test all supported IDs, calibration blank warnings, direct reads, buffer scans, reset/regulator failure unwinds, mount matrix exposure, and PM suspend/resume correctness.
