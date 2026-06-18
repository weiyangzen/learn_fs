# sources/distributed-fs/ceph-client/drivers/staging/iio/impedance-analyzer/Kconfig

## Purpose
Defines the staging impedance converter/network analyzer menu and AD5933/AD5934 driver option.

## Important Entries and Integration
`config AD5933` is tristate, depends on `I2C`, and selects `IIO_BUFFER` plus `IIO_KFIFO_BUF`. The help text names the module `ad5933`.

## Risks and Test Signals
The selected buffer dependencies match the driver's kfifo buffered sweep implementation. Kconfig tests should verify buffer support is selected automatically.
