# sources/distributed-fs/ceph-client/drivers/staging/iio/accel/Kconfig

## Purpose
Defines the staging accelerometer menu and the `ADIS16203` driver option.

## Important Entries and Integration
`config ADIS16203` is tristate, depends on `SPI`, selects `IIO_ADIS_LIB`, and selects `IIO_ADIS_LIB_BUFFER` when `IIO_BUFFER` is enabled. The help text names the module `adis16203`.

## Risks and Test Signals
Dependencies must match the source driver's use of SPI and ADIS library helpers. Kconfig tests should confirm buffer support is selected only when the IIO buffer core is available.
