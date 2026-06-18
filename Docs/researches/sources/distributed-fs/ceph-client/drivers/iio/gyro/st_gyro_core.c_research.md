# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_core.c

## Purpose
Common STMicroelectronics 3-axis gyroscope IIO core supporting several L3G/LSM devices with shared channel definitions, per-chip settings, raw reads, scale/ODR writes, mount matrix, buffers, triggers, and debugfs register access.

## Important APIs, Types, And Functions
Important data includes `st_gyro_16bit_channels`, `st_gyro_sensors_settings`, and `gyro_pdata`. Key functions are `st_gyro_read_raw`, `st_gyro_write_raw`, `st_gyro_get_settings`, and `st_gyro_common_probe`. Trigger ops use ST common validation and optional buffer trigger set-state.

## Control Flow
Bus driver selects settings by device name, configures transport, powers the sensor, then calls common probe. Common probe verifies WHOAMI, sets channel count/table, reads mount matrix, initializes default fullscale/ODR, calls ST common sensor initialization, allocates ring buffer, optionally allocates trigger, and registers IIO.

## State And Persistence
State is mostly in `struct st_sensor_data`: sensor settings, current fullscale, ODR, mount matrix, IRQ, and transport-specific transfer functions. Hardware registers persist ODR, power, axis enable, fullscale, BDU, data-ready IRQ, SPI mode, and supported WHOAMI.

## Dependencies And Integration Points
Depends on `IIO_ST_SENSORS_CORE`, optional triggered buffers, ST common sensor helpers, bus-specific ST I2C/SPI configuration modules, sysfs attributes, and debugfs register access.

## Risks
Settings table entries are dense and must match actual device register maps; a bad WHOAMI/name mapping causes wrong ODR/fullscale programming. DRDY is fixed to INT2. Adding a device requires updating names, settings, and bus match tables together.

## Test Signals
Probe each supported name/WHOAMI, read raw axes and scale/ODR, write fullscale and sample frequency, inspect available sysfs attributes, enable buffers/triggers with IRQ, verify mount matrix, and test debugfs register access.
