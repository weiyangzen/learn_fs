# sources/distributed-fs/ceph-client/drivers/iio/accel/dmard06.c

Purpose: direct-mode I2C IIO driver for Domintech DMARD05/DMARD06/DMARD07 accelerometers with a temperature channel. It validates chip IDs, exposes byte-sized axis and temperature reads, and supports system sleep powerdown/normal modes.

Important APIs and flow: probe checks full I2C functionality, allocates the IIO device, reads `DMARD06_CHIP_ID_REG`, validates one of three IDs, stores the chip ID, sets channel metadata, and registers via devm. `dmard06_read_raw()` reads a byte from the channel address, sign-extends bit 7, applies chip-specific shifts or halves, returns accel scale depending on chip generation, and returns a fixed temperature offset. PM suspend writes `DMARD06_MODE_POWERDOWN`; resume writes `DMARD06_MODE_NORMAL`.

State, dependencies, risks, and tests: state contains the I2C client and chip ID. Dependencies are I2C SMBus byte operations, OF/I2C matching, and IIO direct mode. Risks include very compact 8-bit data precision, chip-specific scaling branches that must match hardware, probe not explicitly setting normal mode before first read, and no runtime PM or buffering. Test signals are chip ID validation for all three IDs, raw axis/temp sysfs reads, scale/offset values, suspend/resume register writes, and OF/I2C module matching.
