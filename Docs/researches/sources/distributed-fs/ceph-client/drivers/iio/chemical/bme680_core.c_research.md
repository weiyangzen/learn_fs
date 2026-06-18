# sources/distributed-fs/ceph-client/drivers/iio/chemical/bme680_core.c

## Purpose
`bme680_core.c` implements the Bosch BME680 IIO core for temperature, pressure, humidity, and gas resistance. Bus-specific drivers supply regmap access; the core handles calibration, compensation, forced conversions, triggered buffering, heater setup, regulators, and runtime PM.

## Important APIs, Types, And Functions
`struct bme680_calib` stores factory calibration coefficients. `struct bme680_data` stores regmap, calibration cache, mutex, oversampling settings, heater settings, scan buffer, and transfer scratch union. `bme680_read_calib()` reads and decodes three calibration ranges. Compensation helpers compute temperature, pressure, humidity, gas resistance, heater resistance, heater duration, and preheat current. `bme680_chip_config()`, `bme680_gas_config()`, `bme680_set_mode()`, and `bme680_wait_for_eoc()` control conversions. IIO access is via `bme680_read_raw()`, `bme680_write_raw()`, and `bme680_trigger_handler()`. `bme680_core_probe()` is exported.

## Control Flow
Probe enables `vdd`/`vddio`, resets the chip, checks chip ID, reads calibration, programs default oversampling and gas heater settings, sets up a triggered buffer, enables runtime PM, and registers the IIO device. Direct reads resume PM, force one conversion, wait for end-of-conversion, then read and compensate the requested channel. Buffered reads force one conversion and bulk-read all measurement registers before pushing a timestamped scan.

## State And Persistence
Calibration, oversampling ratios, heater temperature/duration/current, and scan scratch are in-memory state protected by a mutex. Hardware registers mirror oversampling and heater settings and are reprogrammed on runtime resume. Sensor measurements are not cached; reads trigger fresh forced conversions.

## Dependencies And Integration Points
The core uses regmap with Maple cache, regulator bulk enable, runtime PM, IIO direct and triggered-buffer APIs, unaligned endian helpers, and namespaces for transport modules.

## Risks
Compensation math is integer-heavy and sensitive to calibration endian/bitfield extraction. `bme680_read_gas()` reads status but does not check the regmap read return before testing `data->check`. Raw read paths for pressure/humidity return compensated values under `RAW`, preserving legacy behavior but potentially confusing. Wait time depends on oversampling and heater duration; wrong formulas cause stale or busy data. `preheat_curr_mA` state is not updated when writing current, only the hardware register is written.

## Test Signals
Test chip ID/reset failures, calibration decoding with known vectors, compensation vectors from Bosch API, runtime suspend/resume reconfiguration, direct versus buffered scan values, oversampling validation, gas heater stabilization failures, and regmap read error injection.
