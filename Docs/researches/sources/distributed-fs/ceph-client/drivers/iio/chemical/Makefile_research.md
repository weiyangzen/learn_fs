# sources/distributed-fs/ceph-client/drivers/iio/chemical/Makefile

## Purpose
This Makefile maps chemical sensor Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
It builds the subset objects `ags02ma.o`, `atlas-sensor.o`, `atlas-ezo-sensor.o`, `bme680_core.o`, `bme680_i2c.o`, `bme680_spi.o`, `ccs811.o`, `ens160_core.o`, `ens160_i2c.o`, `ens160_spi.o`, `ams-iaq-core.o`, `mhz19b.o`, `pms7003.o`, and SCD30 transport/core objects, plus additional chemical drivers.

## Control Flow
No runtime behavior exists. Kbuild includes objects based on `CONFIG_*` selections from `Kconfig`.

## State And Persistence
The file stores build mappings only. It has no runtime state.

## Dependencies And Integration Points
It must stay aligned with `drivers/iio/chemical/Kconfig`, module names in help text, and source file names. The comment requests alphabetical insertion for new entries.

## Risks
Core/transport split drivers can build incorrectly if core and bus objects are mapped to the wrong symbols. Missing object rules are caught by build tests only when the corresponding symbol is enabled.

## Test Signals
Targeted module builds for every chemical sensor symbol and all bus combinations are the main validation signal.
