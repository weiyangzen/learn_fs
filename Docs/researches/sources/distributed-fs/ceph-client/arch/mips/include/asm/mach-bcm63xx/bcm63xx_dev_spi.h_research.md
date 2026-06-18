# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_spi.h

**Purpose:** Declares registration for the legacy BCM63xx SPI controller.

**Important APIs/types/functions:** Includes Linux types, `bcm63xx_io.h`, and `bcm63xx_regs.h`, and exports `bcm63xx_spi_register()`.

**Control flow:** Board setup calls the registration helper for SoCs using the legacy SPI block. The implementation obtains resources through CPU register-set helpers and registers the SPI controller.

**State and persistence behavior:** No local state. Registration creates platform device state and exposes SPI flash/peripherals.

**Dependencies and integration points:** Integrated with CPU register maps, raw IO helpers, SPI core, flash registration, and board-selected chip-selects.

**Risks:** Confusing legacy SPI with HSSPI can map the wrong controller. Including IO/register headers from this small declaration header increases coupling and can hide missing includes in users.

**Test signals:** Boot legacy-SPI boards, verify controller probe, SPI flash reads, chip-select operation, IRQ/polling path, and no registration on HSSPI-only SoCs.
