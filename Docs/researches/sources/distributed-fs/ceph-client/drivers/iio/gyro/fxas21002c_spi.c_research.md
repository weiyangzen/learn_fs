# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_spi.c

## Purpose
SPI transport driver for FXAS21002C.

## Important APIs, Types, And Functions
Defines SPI regmap config, `fxas21002c_spi_probe`, `fxas21002c_spi_remove`, SPI/OF match tables, and a `spi_driver` importing `IIO_FXAS21002C`.

## Control Flow
Probe initializes SPI regmap, obtains SPI ID name, and delegates to `fxas21002c_core_probe`; remove calls `fxas21002c_core_remove`.

## State And Persistence
No local runtime state except regmap allocation and binding.

## Dependencies And Integration Points
Depends on SPI, REGMAP_SPI, shared PM ops, `nxp,fxas21002c` compatible, and core namespace exports.

## Risks
Probe assumes a non-NULL SPI ID. SPI-specific read/write flags are not customized in regmap config, so future protocol quirks need explicit config changes.

## Test Signals
Build/probe via SPI ID and OF compatible, verify IRQ forwarding, PM ops, and core raw/buffer sysfs behavior over SPI.
