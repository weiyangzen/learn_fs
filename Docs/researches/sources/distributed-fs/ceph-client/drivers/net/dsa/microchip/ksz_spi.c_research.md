# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_spi.c

## Purpose
`ksz_spi.c` is the SPI bus glue for Microchip KSZ/LAN937x DSA switches. It creates width-specific regmaps over SPI, handles KSZ8463's nonstandard SPI command encoding, matches OF/SPI IDs to chip data, and invokes the common switch lifecycle.

## Important APIs, Types, and Functions
The module defines regmap tables with `KSZ_REGMAP_TABLE()` for KSZ8795, KSZ8863/88x3, and KSZ9477-like protocols, and `KSZ8463_REGMAP_TABLE()` with custom `ksz8463_spi_read()` and `ksz8463_spi_write()` callbacks. The driver entry points are `ksz_spi_probe()`, `ksz_spi_remove()`, and `ksz_spi_shutdown()`. OF match data points to entries in `ksz_switch_chips[]` for KSZ8463, KSZ87xx, KSZ88xx, KSZ9xxx, LAN937x, and LAN9646.

## Control Flow
On probe, the driver allocates a `ksz_device`, retrieves match data, stores the expected chip ID for special initialization, chooses the regmap config family, initializes the 8/16/32-bit regmaps with the shared regmap mutex and chip access tables, copies optional platform data, configures SPI mode 3, records the SPI IRQ, and calls `ksz_switch_register()`. Remove calls `ksz_switch_remove()`. Shutdown calls `ksz_switch_shutdown()` and clears driver data.

## State and Persistence
State consists of the SPI device, the allocated `ksz_device`, three regmaps, optional platform data, and the IRQ number. No disk state exists. Register caching is disabled; all access goes to hardware. The KSZ8463 read/write helpers perform endian conversion on big-endian hosts.

## Dependencies and Integration Points
The file depends on Linux SPI, regmap, module infrastructure, unaligned access helpers, OF match tables, and the common KSZ driver API. It exports no symbols; integration is through `module_spi_driver()` and common lifecycle calls.

## Risks and Edge Cases
Choosing the wrong regmap config breaks every register access. KSZ8463 command encoding depends on access width and address alignment and is easy to regress. The SPI ID table names do not carry driver data, so non-OF users rely on platform data and detection. Probe sets `spi->mode` and calls `spi_setup()` after regmaps are initialized, so controller mode assumptions should be tested. Regmap access tables from chip data restrict valid addresses on some chips.

## Test Signals
Probe each compatible over SPI, verify 8/16/32-bit register reads and writes, exercise KSZ8463 byte/word/dword accesses and big-endian conversions, confirm SPI mode 3 is accepted by controllers, validate IRQ propagation into common setup, test remove/shutdown paths, and check module alias matching for `spi:lan937x` and listed device IDs.
