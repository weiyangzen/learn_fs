# sources/distributed-fs/ceph-client/drivers/mfd/ocelot.h

Purpose: Private header shared by Ocelot MFD core and SPI front end. It defines the parent private data, exported core/SPI helper prototypes, and compile-time SPI byte-order constants.

Important APIs, types, and functions: `struct ocelot_ddata` stores GCB and CPUORG regmaps, SPI padding byte count, and dummy buffer pointer. Prototypes declare `ocelot_chip_reset()`, `ocelot_core_init()`, and `ocelot_spi_init_regmap()`. `OCELOT_SPI_BYTE_ORDER_LE`, `OCELOT_SPI_BYTE_ORDER_BE`, and `OCELOT_SPI_BYTE_ORDER` encode payload ordering based on host endianness.

Control flow: `ocelot-spi.c` fills `ocelot_ddata` and uses the byte-order macro during interface initialization. `ocelot-core.c` retrieves the same data with `dev_get_drvdata()` and calls the SPI regmap helper when creating child resource regmaps.

State and persistence: the header describes in-memory parent state only. The byte-order macro determines persistent hardware interface configuration written by the SPI driver.

Dependencies and integration points: includes `linux/kconfig.h` for endianness checks and forward-declares device/regmap/resource types to keep compile dependencies light. It is local to the Ocelot MFD implementation and namespace exports.

Risks: this private header currently bakes SPI-specific fields into the shared data structure, limiting the bus-agnostic goal of the core. Endianness macro correctness is critical because a wrong value makes all register payloads decode incorrectly. Test signals are compile-time for little- and big-endian builds plus runtime verification that SPI register reads match expected values after initialization.
