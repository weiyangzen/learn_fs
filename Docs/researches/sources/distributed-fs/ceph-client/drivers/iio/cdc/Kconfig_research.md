# sources/distributed-fs/ceph-client/drivers/iio/cdc/Kconfig

## Purpose
This Kconfig menu defines capacitance-to-digital converter drivers for Analog Devices AD7150-family and AD7745/AD7746/AD7747 sensors.

## Important APIs, Types, And Functions
It defines `AD7150` and `AD7746`, both tristate and dependent on I2C. Help text identifies supported chips and module names.

## Control Flow
No runtime control flow exists; Kconfig controls whether corresponding I2C IIO drivers are built.

## State And Persistence
State is the kernel build configuration. The selected symbols persist in `.config` and determine compiled objects.

## Dependencies And Integration Points
The menu integrates with `drivers/iio/cdc/Makefile`, where `CONFIG_AD7150` maps to `ad7150.o` and `CONFIG_AD7746` maps to `ad7746.o`.

## Risks
Dependencies are minimal; if future code adds regulators, events, or buffers with extra config dependencies, this file must be updated. Help text says direct sysfs access, matching the direct-mode drivers.

## Test Signals
Build each driver as built-in and module, and verify I2C dependency hides options when I2C is disabled.
