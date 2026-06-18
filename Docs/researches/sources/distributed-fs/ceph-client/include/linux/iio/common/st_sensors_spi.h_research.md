# `sources/distributed-fs/ceph-client/include/linux/iio/common/st_sensors_spi.h`

Purpose: SPI transport configuration entry point for ST common IIO sensor drivers.

Important APIs/types/functions: `st_sensors_spi_configure(struct iio_dev *, struct spi_device *)`.

Control flow and state: implementation configures SPI-specific regmap/read flags and binds transport state to the shared ST sensor core.

Dependencies/integration: depends on SPI and `st_sensors.h`; used by ST sensor SPI drivers.

Risks: SPI read/write and multi-read bits vary by chip; mode/word size must match hardware; bus setup must be complete before common probe accesses registers.

Test signals: SPI probe/configure, WAI register read, buffered multi-byte sample reads, debugfs reg access, and compare behavior against I2C variants.
