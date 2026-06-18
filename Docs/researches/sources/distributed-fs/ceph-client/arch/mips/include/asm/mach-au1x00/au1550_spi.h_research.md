# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1550_spi.h

**Purpose:** Defines board/platform data for the Au1550 PSC SPI controller driver.

**Important APIs/types/functions:** Exports `struct au1550_spi_info` with `mainclk_hz`, `num_chipselect`, and board-provided `activate_cs()`/`deactivate_cs()` callbacks that receive the SPI info object, chip-select index, and polarity.

**Control flow:** SPI controller setup reads the input clock and number of chipselects, then invokes activate/deactivate callbacks around transfers to drive board-specific CS GPIOs or glue logic while PSC SPI registers are managed elsewhere.

**State and persistence behavior:** No local storage. Board callbacks mutate chip-select hardware state. `mainclk_hz` is persistent configuration supplied during platform registration.

**Dependencies and integration points:** Integrated by Au1550 PSC SPI driver, board files, and `au1xxx_psc.h` register definitions. Uses Linux fixed-width integer types through normal include context.

**Risks:** Bad clock values break SPI timing; wrong CS polarity or callback sequencing can corrupt flash/peripheral transactions. The header does not bound `num_chipselect` or validate callback presence.

**Test signals:** Probe SPI devices, test each CS line and polarity, verify transfer speed calculations against scope/logic analyzer, and test concurrent SPI messages if the driver serializes correctly.
