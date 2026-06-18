
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.c

## Purpose
`st_sensors_core.c` is the central common library for STMicroelectronics IIO sensor drivers. It provides register field writes, debugfs register access, output-data-rate and full-scale configuration, power/regulator setup, data-ready interrupt routing, raw direct reads, device-name matching, Who-Am-I verification, and sysfs available-value formatting.

## Important APIs, types, and functions
- `st_sensors_write_data_with_mask()` wraps `regmap_update_bits()` with mask shifting.
- `st_sensors_debugfs_reg_access()` supports generic IIO debugfs register read/write.
- `st_sensors_set_odr()`, `st_sensors_set_enable()`, `st_sensors_set_axis_enable()`, `st_sensors_set_fullscale_by_gain()`, and internal full-scale helpers program common sensor settings tables.
- `st_sensors_power_enable()` enables optional `vdd` and `vddio` supplies.
- `st_sensors_init_sensor()` applies platform/firmware data, powers down the device, disables DRDY, sets full scale, ODR, BDU/DAS, open-drain interrupt mode, and all-axis enable.
- `st_sensors_set_dataready_irq()` controls DRDY routing and `hw_irq_trigger` state.
- `st_sensors_read_info_raw()` claims direct mode, powers the sensor, waits boot time, reads an axis, and powers down.
- `st_sensors_get_settings_index()`, `st_sensors_verify_id()`, `st_sensors_sysfs_sampling_frequency_avail()`, and `st_sensors_sysfs_scale_avail()` are exported helpers.

## Control flow
Sensor-specific probe code typically configures bus regmap, selects `sensor_settings`, then calls `st_sensors_init_sensor()`. Initialization parses `st,drdy-int-pin` and `drive-open-drain` firmware properties, validates DRDY pin support, disables the sensor and data-ready IRQ, programs current full-scale and ODR settings, enables BDU/DAS where available, configures open drain, and enables all axes. Runtime sysfs writes call ODR/full-scale/power helpers; direct raw reads temporarily enable the sensor under `odr_lock`.

## State and persistence behavior
State is stored in `struct st_sensor_data`: `regmap`, `sensor_settings`, `current_fullscale`, `enabled`, `odr`, `drdy_int_pin`, `int_pin_open_drain`, `edge_irq`, `hw_irq_trigger`, `hw_timestamp`, `buffer_data`, and `odr_lock`. Register writes persist in the sensor hardware until reset. No filesystem persistence is used.

## Dependencies and integration points
The file depends on IIO core, regmap, firmware/property APIs, regulators, mutexes, and ST shared structs from `linux/iio/common/st_sensors.h`. It is used by many ST accelerometer, gyro, magnetometer, pressure, and IMU drivers. Bus setup comes from the sibling I2C/SPI helper files, and trigger/buffer behavior comes from optional sibling files.

## Risks and edge cases
- `st_sensors_verify_id()` only warns on Who-Am-I mismatch and still returns success; this permits continued probing on unexpected silicon.
- `st_sensors_sysfs_sampling_frequency_avail()` and `st_sensors_sysfs_scale_avail()` write `buf[len - 1] = '\n'`; if no values are available, `len` is zero and this underwrites the buffer.
- `st_sensors_read_info_raw()` may leave the sensor enabled if `st_sensors_read_axis_data()` fails after enabling; the error path jumps to unlock without disabling.
- ODR and power registers can share the same field; `st_sensors_set_odr()` defers writes while disabled in that case, so tests must cover enable-after-ODR-change behavior.
- Firmware property `st,drdy-int-pin` values greater than 2 silently fall back to defaults rather than reporting invalid firmware.

## Test signals
Probe tests should cover regulator enable, name matching, Who-Am-I mismatch warning, init register writes, DRDY pin selection and open-drain configuration. Runtime tests should cover ODR changes while enabled/disabled, direct raw read cleanup on read errors, sysfs available strings for empty/non-empty tables, and data-ready IRQ enable/disable register writes.
