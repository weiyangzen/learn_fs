# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_spi.c

Purpose: SPI transport wrapper for the BMI160/BMI120 core driver.

Important APIs, types, and functions: `bmi160_spi_probe()` initializes SPI regmap with `bmi160_regmap_config`, chooses a name from SPI ID or device name, and calls `bmi160_core_probe(..., use_spi=true)`. It declares SPI IDs, ACPI IDs, OF compatibles, and a `spi_driver` with core PM ops.

Control flow: SPI match triggers probe, regmap is created, then core handles reset, the SPI-specific dummy read, chip init, buffers, triggers, and registration.

State and persistence: no transport-private persistent state; `use_spi=true` affects core initialization by causing a post-reset dummy read.

Dependencies and integration: depends on SPI, regmap SPI, BMI160 core namespace, ACPI IDs `BMI0120`/`BMI0160`, and OF compatibles.

Risks: the `MODULE_AUTHOR` string is missing a closing `>` in the source, cosmetic but visible in module metadata. SPI read semantics rely on generic regmap SPI being adequate for this device after the dummy read.

Test signals: SPI probe, regmap failure handling, dummy-read path, OF/ACPI/SPI ID matching, PM callbacks, and module metadata sanity.
