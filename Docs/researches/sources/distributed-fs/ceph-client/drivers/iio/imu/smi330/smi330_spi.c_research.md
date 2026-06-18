<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c

Purpose: Bosch SMI330 SPI transport frontend. It provides custom regmap bus operations for SPI framing and delegates sensor setup to the shared SMI330 core.

Important APIs/functions: `smi330_regmap_spi_read()` inserts one pad byte after the register address and uses `spi_write_then_read()`. `smi330_regmap_spi_write()` writes the regmap frame directly. `smi330_spi_probe()` creates the regmap with `read_flag_mask = 0x80` and calls `smi330_core_probe()`.

Control flow: SPI probe initializes regmap over the SPI device, then shared core handles reset, validation, IRQ, buffer, and IIO registration. Reads require a one-byte regmap register buffer, add a dummy byte, and read the requested value bytes.

State and persistence: no transport-private persistent state beyond the SPI device/regmap.

Dependencies and integration: depends on SPI, regmap custom bus, OF compatible `bosch,smi330`, SPI ID `smi330`, and namespace import `IIO_SMI330`.

Risks: read path rejects unexpected register-buffer sizes and logs through the SPI device. Protocol correctness depends on the read flag mask and dummy-byte behavior matching the hardware.

Test signals: SPI modalias/OF matching, read/write regmap traces, core probe via SPI, bulk data read, and module namespace resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c -->
