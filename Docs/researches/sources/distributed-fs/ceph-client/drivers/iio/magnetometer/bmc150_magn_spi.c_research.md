<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c

Purpose: SPI bus front-end for the Bosch BMC150/BMC156/BMM150 magnetometer core.

Important APIs/types/functions: `bmc150_magn_spi_probe()` initializes a SPI regmap with the shared `bmc150_magn_regmap_config`, gets the SPI device id, and calls `bmc150_magn_probe()`. `bmc150_magn_spi_remove()` calls `bmc150_magn_remove()`. The SPI id table supports `bmc150_magn`, `bmc156_magn`, and `bmm150_magn`.

Control flow: module registration installs a `spi_driver`; probe sets up transport and delegates all functional behavior to the shared core; remove delegates teardown. Unlike the I2C wrapper, this driver table does not attach the shared PM ops directly.

State/persistence: no independent runtime state beyond devm regmap; core state is attached to the SPI device.

Dependencies/integration: depends on SPI, regmap-SPI, BMC150 common core, and namespace import `IIO_BMC150_MAGN`. It is built by `CONFIG_BMC150_MAGN_SPI`.

Risks: no OF match table is present in this wrapper, so SPI devices need board/device-id enumeration unless another mechanism supplies ids. The shared regmap config has no SPI read flag override here; correctness depends on regmap-SPI framing matching the device protocol. `MODULE_AUTHOR` metadata is missing a closing angle bracket.

Test signals: compile and modpost namespace checks, instantiate SPI ids, verify regmap read/write over SPI, confirm core probe receives IRQ/name, and exercise remove cleanup after triggered-buffer use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c -->
