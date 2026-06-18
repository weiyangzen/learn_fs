# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_core.c

## Purpose
Common STMicroelectronics magnetometer implementation for multiple LSM/LIS/IIS devices. It centralizes channel definitions, per-chip register settings, raw/scale/sample-frequency IIO operations, trigger configuration, and common probe.

## Important APIs, Types, And Functions
`st_magn_sensors_settings[]` is the key table, mapping supported device names to WAI IDs, channels, ODR registers, power bits, full-scale ranges, BDU, DRDY, SPI mode, multi-read behavior, and boot time. `st_magn_get_settings()` exports lookup by name. `st_magn_common_probe()` verifies the ID, assigns channels, reads mount matrix, initializes ST common sensor state, allocates ring/trigger resources, and registers the IIO device. `st_magn_read_raw()` and `st_magn_write_raw()` bridge IIO raw/scale/sample-frequency access to common ST helpers.

## Control Flow
Bus-specific drivers allocate an IIO device, set `sensor_settings`, configure I2C/SPI transport, enable power, then call `st_magn_common_probe()`. Common probe verifies WAI, picks the channel table, sets default full-scale and ODR, initializes the sensor using platform data/default DRDY pin, optionally allocates buffer and trigger, then registers with IIO.

## State And Persistence
State lives in `struct st_sensor_data`: current full scale, ODR, IRQ, mount matrix, and common transport fields. Hardware settings are volatile register programming; no nonvolatile writes.

## Dependencies And Integration Points
Depends heavily on `IIO_ST_SENSORS` helpers, IIO triggers, mount matrix parsing, and bus glue in `st_magn_i2c.c` and `st_magn_spi.c`. Exports symbols in namespace `IIO_ST_SENSORS`.

## Risks And Test Signals
Risks are table correctness: wrong endianness, output addresses, gain/gain2, WAI, or DRDY masks silently break specific parts. Test each supported family for ID verification, raw axis reads, Z-axis special gain where applicable, ODR/scale sysfs writes, mount-matrix exposure, and buffer trigger operation.
