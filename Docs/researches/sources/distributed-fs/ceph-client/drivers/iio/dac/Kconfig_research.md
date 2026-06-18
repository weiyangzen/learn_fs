
# sources/distributed-fs/ceph-client/drivers/iio/dac/Kconfig

## Purpose
This Kconfig menu declares build-time options for Linux IIO digital-to-analog converter drivers. The researched entries include AD3530R, AD3552R regular/high-speed/library, AD5064, AD5360, AD5380, AD5421, AD5446 SPI/I2C/common, and AD5449, plus many neighboring DAC options.

## Important APIs, types, and functions
- `AD3530R` depends on SPI and selects `REGMAP_SPI`.
- `AD3552R_HS` selects `AD3552R_LIB` and `IIO_BACKEND`.
- `AD3552R_LIB` is an internal shared-library symbol.
- `AD3552R` depends on `SPI_MASTER`, selects `AD3552R_LIB`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.
- `AD5064` supports SPI/I2C combinations through a compound dependency.
- `AD5360`, `AD5421`, and `AD5449` are SPI/SPI_MASTER drivers.
- `AD5380` supports SPI and I2C through regmap selections.
- `AD5446`, `AD5446_SPI`, and `AD5446_I2C` split common core from transport drivers.

## Control flow
There is no runtime control flow. User or defconfig choices select which DAC drivers and support libraries are compiled.

## State and persistence behavior
Only kernel build configuration state is represented.

## Dependencies and integration points
The symbols connect to `drivers/iio/dac/Makefile`, transport frameworks, regmap backends, IIO buffers, IIO backend, SPI offload, DMA buffers, regulators, GPIO, and platform architecture dependencies for other DACs in the menu.

## Risks and edge cases
- Compound dependencies such as `AD5064` and `AD5380` must avoid impossible module combinations when common code registers both SPI and I2C subdrivers.
- Internal library symbols (`AD3552R_LIB`, `AD5446`) are selected by front-end drivers; enabling code that imports their namespaces without the select will fail at link/load time.
- Comments require alphabetical ordering, but the Makefile has some historical ordering differences; new entries should be checked in both places.

## Test signals
Run build matrix coverage for selected drivers as built-in and modules, including `AD3552R_HS` with backend support, `AD3552R` with triggered buffers, `AD5064` with only SPI or I2C enabled, and `AD5446_SPI/I2C` namespace imports.
