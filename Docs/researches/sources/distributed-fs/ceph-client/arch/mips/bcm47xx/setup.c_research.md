# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/setup.c

Purpose: BCM47xx platform setup for reboot, halt, bus registration, Ethernet defaults, fixed PHYs, LED/buttons/workarounds, and CPU quirks.

Important APIs and functions: `plat_mem_setup()` installs restart/halt callbacks, initializes CFE, chooses idle behavior, and registers SSB or BCMA buses. `bcm47xx_bus_setup()` performs post-bus board setup including SPROM, Ethernet MAC/MDIO defaults, fixed PHY registration, LED/button registration, workarounds, and optional mtd initialization. `bcm47xx_cpu_fixes()` applies BMIPS quirks, while `bcm47xx_register_bus_complete()` finalizes bus registration late.

Control flow: platform setup runs in layers: memory/reboot setup first, bus probing next, board-specific devices after the bus is available, and late bus completion via initcall. Restart writes watchdog or chipcommon reset registers; halt loops after disabling interrupts.

State and persistence: changes global machine callbacks, bus state, fixed PHY registration, board platform devices, and chip registers. It reads firmware/SPROM data but does not persist changes.

Dependencies and integration points: integrates CFE, SSB/BCMA, BMIPS, fixed PHY, MTD, LED/button/workaround helpers, and MIPS platform hooks.

Risks and test signals: bus-type assumptions and reset register handling are board-sensitive. Test signals are clean reboot/halt, bus enumeration, Ethernet MAC/PHY availability, LED/button devices, MTD registration, and absence of CPU quirk regressions on BMIPS devices.
