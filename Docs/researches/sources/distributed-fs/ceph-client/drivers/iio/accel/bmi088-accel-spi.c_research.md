# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-spi.c

Purpose: SPI wrapper for BMI085/BMI088/BMI090L accelerometer core, including the custom SPI read behavior required by the chip protocol.

Important APIs and flow: implements a `struct regmap_bus` with `bmi088_regmap_spi_write()` and `bmi088_regmap_spi_read()`. Writes use `spi_write()`. Reads set bit 7 in the register address and insert a dummy byte before reading the value payload. Probe creates the regmap with `devm_regmap_init()`, passes SPI IRQ and ID driver data to `bmi088_accel_core_probe()`, and remove delegates to the core. OF and SPI ID tables cover the three chip variants.

State, dependencies, risks, and tests: the bus wrapper stores no persistent state, but the custom regmap bus is critical because generic SPI register reads would not satisfy the dummy-byte protocol. It depends on SPI, regmap, OF matching, PM ops, and namespace `IIO_BMI088`. Risks include read framing errors, incorrect ID match data, and absent IRQ being unused by this core today but still passed through. Test signals are regmap bus read/write transactions on SPI, dummy-read compatibility with core init, chip-ID reads after reset, and runtime PM callbacks through the SPI driver.
