# sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-spi.c

Purpose: SPI transport wrapper for BMC150-family accelerometers. It initializes a SPI regmap using the shared BMC150 regmap config and delegates probe/remove/PM behavior to the core.

Important APIs and flow: `bmc150_accel_probe()` obtains the SPI device ID when present, derives optional name and `enum bmc150_type`, initializes `devm_regmap_init_spi()`, then calls `bmc150_accel_core_probe(&spi->dev, regmap, spi->irq, type, name, true)`. The SPI wrapper always declares block/FIFO-style reads supported. Remove calls `bmc150_accel_core_remove()`. It provides ACPI and SPI ID tables and binds the core PM ops in `struct spi_driver`.

State, dependencies, risks, and tests: all meaningful sensor state belongs to the core, while this file owns only bus binding and match metadata. It depends on SPI, regmap, module SPI registration, ACPI matching, and namespace import `IIO_BMC150`. Risks are limited to incorrect ID driver data, regmap setup failure, and SPI boards without an IRQ losing trigger/event/FIFO interrupt features. Test signals are module autoload from SPI/ACPI IDs, regmap initialization, core probe success, IRQ propagation, and core remove on driver unbind.
