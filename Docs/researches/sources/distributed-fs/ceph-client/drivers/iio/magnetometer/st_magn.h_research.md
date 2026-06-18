# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn.h

## Purpose
Shared ST magnetometer header that names supported devices and declares buffer/trigger helpers used by the ST magnetometer core and bus glue.

## Important APIs, Types, And Functions
Defines public device-name strings such as `LSM303DLH_MAGN_DEV_NAME`, `LIS3MDL_MAGN_DEV_NAME`, `LIS2MDL_MAGN_DEV_NAME`, `IIS2MDC_MAGN_DEV_NAME`, and `LSM303C_MAGN_DEV_NAME`. Declares `st_magn_allocate_ring()` and `st_magn_trig_set_state()` when `CONFIG_IIO_BUFFER` is enabled. Provides a no-op `st_magn_allocate_ring()` and `NULL` trigger setter macro when buffering is disabled.

## Control Flow
This header contributes compile-time selection: buffered builds wire the core to real triggered-buffer setup, while non-buffered builds keep common probe working by returning success from the inline stub.

## State And Persistence
No runtime state. Its constants are the stable linkage between device-tree/modalias names and `st_magn_get_settings()` in the core.

## Dependencies And Integration Points
Includes `linux/iio/common/st_sensors.h` and is consumed by `st_magn_core.c`, `st_magn_buffer.c`, `st_magn_i2c.c`, and `st_magn_spi.c`.

## Risks And Test Signals
Adding a new ST magnetometer requires synchronized name additions here, bus ID tables, OF match tables, and core settings. Build coverage should include both buffered and non-buffered configurations.
