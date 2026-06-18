<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c

Purpose: SPI frontend for the ST LSM6DSx family. It matches OF/SPI IDs, creates an 8-bit SPI regmap, and delegates device handling to the shared core.

Important APIs/functions: `st_lsm6dsx_spi_probe()` gets `spi_device_id` driver data, initializes `devm_regmap_init_spi()`, and calls `st_lsm6dsx_probe(&spi->dev, spi->irq, hw_id, regmap)`. OF and SPI ID tables mirror the supported core device names.

Control flow: SPI device match selects a hardware ID, regmap abstracts bus access, and the core handles reset, registration, IRQ/FIFO, shub, and PM.

State and persistence: no transport-private runtime state beyond SPI/regmap/core state.

Dependencies and integration: depends on SPI master, regmap SPI, OF matching, core PM ops, and namespace import `IIO_LSM6DSX`.

Risks: the probe uses SPI ID driver data directly; OF-only devices still need modalias/ID association to provide the correct driver data in this implementation. Match tables must remain synchronized with core settings.

Test signals: SPI modalias and OF matching for each supported name, regmap read/write, IRQ forwarding, PM ops, and core probe over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c -->
