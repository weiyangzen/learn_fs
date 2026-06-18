# sources/distributed-fs/ceph-client/drivers/iio/light/ltrf216a.c

## Purpose
`ltrf216a.c` is an IIO I2C/regmap driver for Lite-On LTRF216A and LTR308 ambient light sensors. It provides raw ALS counts, processed lux, integration-time selection, runtime PM, and chip-specific handling for optional clear-data registers and lux multipliers.

## Important APIs, types, and functions
`struct ltr_chip_info` indicates whether clear-data registers exist and which lux multiplier to use. `struct ltrf216a_data` stores regmap, client, chip info, current integration time/factors, gain factor, and a mutex. `ltrf216a_reset()`, `ltrf216a_enable()`, `ltrf216a_disable()`, and `ltrf216a_cleanup()` manage power state. `ltrf216a_set_int_time()` programs `ALS_MEAS_RES` and updates conversion factors. `ltrf216a_set_power_state()` wraps runtime PM references. `ltrf216a_read_data()` polls data-ready and reads 24-bit little-endian samples. `ltrf216a_get_lux()` combines PM, raw green data, and chip multiplier.

## Control flow
Probe allocates IIO state, initializes regmap with custom readable/writeable/volatile/precious callbacks, stores match data, resets the sensor, reinitializes the regmap cache, enables ALS, registers a cleanup action, enables runtime PM autosuspend, seeds default integration/gain factors, and registers IIO. Raw reads runtime-resume the device, lock around data read, then autosuspend. Processed reads lock, call the lux helper, and return a fractional value using gain and integration factors. Runtime suspend disables the sensor and switches regmap to cache-only; runtime resume syncs the cache and re-enables ALS.

## State and persistence
Integration time, integration factor, and gain factor are cached in RAM. Register settings are preserved by regmap cache while runtime-suspended and synchronized on resume. Hardware state is disabled during autosuspend and on cleanup. `MAIN_STATUS` is marked precious, preventing debug-style reads from accidentally clearing or altering status semantics.

## Dependencies and integration points
The driver integrates with I2C IDs, OF compatibles `liteon,ltr308`, `liteon,ltrf216a`, and `ltr,ltrf216a`, regmap cache-only runtime PM, IIO direct-mode attributes, and unaligned 24-bit helpers.

## Risks
`ltrf216a_get_lux()` does not call `ltrf216a_set_power_state(false)` if `ltrf216a_read_data()` fails, which can leak a runtime PM reference and leave the device active. The processed path nests PM control inside the mutex, while raw path takes PM before locking. Regmap callbacks consult `i2c_get_clientdata()` and chip info, so callback timing before clientdata initialization is important. The reset write intentionally ignores errors.

## Test signals
Compile with runtime PM and regmap. Runtime tests should cover LTR308 versus LTRF216A register visibility, all integration-time writes, raw and processed reads, data-ready timeout, runtime suspend/resume cache sync, cleanup disable, and the error path in `ltrf216a_get_lux()` for PM reference balance.
