# sources/distributed-fs/ceph-client/drivers/misc/lis3lv02d/Makefile

## Purpose
The Makefile connects LIS3 accelerometer Kconfig options to Kbuild objects.

## Important APIs, types, and functions
`obj-$(CONFIG_SENSORS_LIS3LV02D) += lis3lv02d.o` builds the shared core. `obj-$(CONFIG_SENSORS_LIS3_SPI) += lis3lv02d_spi.o` builds SPI glue. `obj-$(CONFIG_SENSORS_LIS3_I2C) += lis3lv02d_i2c.o` builds I2C glue.

## Control flow
Kbuild includes the core when selected by either transport and includes each transport object according to its tristate value.

## State and persistence
No runtime state exists. Build output determines which module or built-in objects provide the common exported symbols and bus drivers.

## Dependencies and integration points
The Makefile relies on Kconfig to select `SENSORS_LIS3LV02D` when a transport is enabled, ensuring the transport modules can resolve common symbols such as `lis3lv02d_init_device`.

## Risks
Object ordering and option names must stay aligned with exported symbols and transport module names. A missing core object would break transport linking.

## Test signals
Build tests should confirm `lis3lv02d.ko`, `lis3lv02d_spi.ko`, and `lis3lv02d_i2c.ko` are produced under module configurations and link correctly under built-in configurations.
