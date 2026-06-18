## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Kconfig

Purpose: defines BCM47XX bus-family support options for old SSB-based and newer BCMA-based Broadcom router SoCs.

Important symbols: `BCM47XX_SSB` selects BMIPS32 3300 CPU support, SSB host/embedded/MIPS/extif/GPIO support, and optional SSB PCI host/bridge pieces when PCI is enabled. `BCM47XX_BCMA` selects MIPS32 R2/highmem/vector IRQ support, BCMA host/MIPS/GPIO support, and optional BCMA PCI hostmode. Both default to `y` under `BCM47XX`.

Control flow: none directly. These options control which bus framework and CPU/IRQ capabilities are available to the platform.

State and persistence: none.

Dependencies and integration: integrates with parent `BCM47XX`, SSB, BCMA, PCI, CPU, and IRQ subsystem Kconfig symbols. The runtime code in this subset, especially `irq.c`, branches on `CONFIG_BCM47XX_BCMA`.

Risks: both default on for broad images, increasing binary surface. Selecting the wrong bus support for a board can remove required bus setup, GPIO, PCI, or IRQ behavior. BCMA changes `cp0_compare_irq` routing in `irq.c`.

Test signals: SSB and BCMA target builds should include their bus drivers and boot on representative routers. PCI enumeration and GPIO-backed buttons/LEDs validate the selected support.
