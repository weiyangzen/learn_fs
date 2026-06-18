# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Kconfig

## Purpose
This Kconfig file defines the IIO amplifier submenu and build symbols for SPI and GPIO-controlled amplifier/attenuator drivers.

## Important APIs, Types, And Functions
`CONFIG_AD8366` enables the AD8366-and-similar SPI gain amplifier/attenuator driver, depends on SPI and GPIOLIB, and selects BITREVERSE. `CONFIG_ADA4250` enables an Analog Devices SPI instrumentation amplifier and selects REGMAP_SPI. `CONFIG_ADL8113` enables a GPIO-controlled low-noise amplifier. `CONFIG_HMC425` enables GPIO-controlled gain amplifier/attenuator support. The AD8366 help text enumerates the supported devices and states module name `ad8366`.

## Control Flow
Kconfig gates which amplifier object rules in the Makefile become active. Dependency evaluation prevents selecting drivers without required buses or GPIO support.

## State And Persistence
The file controls only build-time configuration. Runtime state belongs to the selected C drivers.

## Dependencies And Integration Points
It integrates with kbuild, the amplifier Makefile, SPI, GPIOLIB, BITREVERSE, and REGMAP_SPI. Help text is part of the user-facing configuration documentation.

## Risks And Test Signals
Risks include missing dependency/select lines when drivers change, inaccurate supported-device lists, and symbol/object mismatches. Test signals are `allmodconfig` and per-symbol builds, especially `AD8366=m` with BITREVERSE availability, plus config visibility checks on kernels without SPI or GPIOLIB.
