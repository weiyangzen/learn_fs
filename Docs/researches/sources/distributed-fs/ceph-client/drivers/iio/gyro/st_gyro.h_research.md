# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro.h

## Purpose
Shared header for STMicroelectronics IIO gyroscope core, buffer code, and I2C/SPI bus drivers.

## Important APIs, Types, And Functions
Defines device-name constants for supported ST gyro variants and declares buffer/trigger functions when `CONFIG_IIO_BUFFER` is enabled. Provides no-op ring allocation and NULL trigger state macro when buffers are disabled.

## Control Flow
Core and bus files use the constants for settings lookup and match tables. Buffer-enabled builds call `st_gyro_allocate_ring` and use `ST_GYRO_TRIGGER_SET_STATE`; non-buffer builds compile out those paths.

## State And Persistence
No stored state; it defines compile-time contracts and supported device names.

## Dependencies And Integration Points
Depends on ST sensor common types and IIO trigger declarations. Integrates `st_gyro_core.c`, `st_gyro_buffer.c`, `st_gyro_i2c.c`, and `st_gyro_spi.c`.

## Risks
Name constants must match Kconfig, bus ID tables, OF data, and settings table entries. Buffer guards must stay synchronized with Makefile conditional object inclusion.

## Test Signals
Compile with and without `CONFIG_IIO_BUFFER`; verify all device names resolve through settings lookup.
