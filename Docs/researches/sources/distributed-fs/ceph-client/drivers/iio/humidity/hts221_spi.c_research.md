# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_spi.c

Purpose: SPI transport wrapper for the HTS221 core driver.

Important APIs/types/functions: `hts221_spi_regmap_config` sets 8-bit registers/values, write auto-increment flag, and read flag combining SPI read plus auto-increment. `hts221_spi_probe()` initializes an SPI regmap and delegates to `hts221_probe()`. Match tables include OF `st,hts221` and SPI id `hts221`.

Control flow: SPI probe creates a regmap; all identity, calibration, IIO, and optional trigger setup is handled by core. Module registration is via `module_spi_driver`.

State and persistence: No SPI-private runtime state is stored; devm regmap and core-owned `struct hts221_hw` hold state.

Dependencies and integration points: Depends on SPI, `REGMAP_SPI`, shared HTS221 core symbols and PM ops, and namespace `IIO_HTS221`.

Risks: Correct SPI operation depends on read and auto-increment flags matching HTS221 protocol. The transport leaves mode/bits-per-word to SPI core/device setup and does not validate them.

Test signals: Probe over SPI with compatible/id match, verify multi-byte reads for calibration and buffer samples, and run suspend/resume with core PM callbacks.
