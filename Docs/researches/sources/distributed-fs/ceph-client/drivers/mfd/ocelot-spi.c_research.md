# sources/distributed-fs/ceph-client/drivers/mfd/ocelot-spi.c

Purpose: SPI front end for externally controlled Ocelot/VSC7512 chips. It calculates SPI read padding, configures byte order and interface timing, creates regmaps over SPI register windows, resets and reinitializes the chip, then delegates child creation to `ocelot-core.c`.

Important APIs, types, and functions: `ocelot_spi_initialize()` writes CPUORG interface control and padding configuration, then verifies padding, interface status, and serial-interface selection. `ocelot_spi_regmap_config` defines 24-bit big-endian addresses, 32-bit native-endian values, stride/downshift, and single read/write behavior. `ocelot_spi_regmap_bus_read()` emits address, optional dummy padding, and data receive transfers. `ocelot_spi_init_regmap()` exports named regmap construction for any resource. `ocelot_spi_probe()` allocates `struct ocelot_ddata`, calculates padding from bus speed, initializes CPUORG/GCB regmaps, configures SPI, resets the chip, configures SPI again, and calls `ocelot_core_init()`.

Control flow: probe must configure the serial interface before any broad register access. Because chip reset clears SPI interface configuration, initialization is performed before and after `ocelot_chip_reset()`. Child registration only happens after the second successful initialization.

State and persistence: `ocelot_ddata` stores padding count, dummy buffer, and core regmaps. SPI interface configuration is hardware state and is lost on chip reset. Devm regmaps persist for child use until device removal.

Dependencies and integration points: depends on SPI core, custom regmap bus, Ocelot private header, `ocelot-core.c` exports, DT compatible `mscc,vsc7512`, and namespace imports/exports.

Risks: padding calculation is integer approximation and incorrect values cause `ocelot_spi_initialize()` to reject the interface or reads to fail. `ocelot_spi_regmap_bus_read()` relies on `dummy_data` support in SPI transfers. The regmap bus has no locking beyond regmap/SPI core behavior. Test signals include low-speed zero-padding path, high-speed padding verification, reset reinitialization, endian correctness, named resource regmap creation, and SPI transfer failure propagation.
