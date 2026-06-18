
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Makefile

## Purpose
This Makefile maps ST common Kconfig symbols to kernel objects and composes the core `st_sensors` module from mandatory core code plus optional buffer and trigger helpers.

## Important APIs, types, and functions
- `obj-$(CONFIG_IIO_ST_SENSORS_I2C) += st_sensors_i2c.o`
- `obj-$(CONFIG_IIO_ST_SENSORS_SPI) += st_sensors_spi.o`
- `obj-$(CONFIG_IIO_ST_SENSORS_CORE) += st_sensors.o`
- `st_sensors-y := st_sensors_core.o`
- `st_sensors-$(CONFIG_IIO_BUFFER) += st_sensors_buffer.o`
- `st_sensors-$(CONFIG_IIO_TRIGGER) += st_sensors_trigger.o`

## Control flow
There is no runtime control flow. The build system includes buffer and trigger helper code only when the corresponding IIO framework features are enabled.

## State and persistence behavior
This file controls build artifacts only.

## Dependencies and integration points
It ties the Kconfig symbols to the common helper C files. Sensor-specific drivers depend on the exported namespace `IIO_ST_SENSORS` from the resulting modules.

## Risks and edge cases
If a sensor driver uses trigger or buffer helpers without depending on the matching IIO feature, symbols can be absent. Ordering is mostly conventional; comments ask that DAC entries elsewhere remain alphabetical, but this ST Makefile is small and direct.

## Test signals
Compile representative ST IIO drivers with `IIO_BUFFER=n/y` and `IIO_TRIGGER=n/y` to ensure optional helper symbols match feature availability.
