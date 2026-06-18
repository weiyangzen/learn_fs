# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_64xx.c

Purpose: provides the Marvell 88SE64xx/SoC hardware implementation behind the shared `mvs_dispatch` interface. It initializes registers and DMA rings, controls phys, handles interrupts, manages SATA register sets, builds PRDs, and implements SPI and interrupt-coalescing hooks for 3 Gb/s-era chips.

Important APIs/types/functions: the exported `mvs_64xx_dispatch` binds chip operations such as `mvs_64xx_init()`, `mvs_64xx_ioremap()`, `mvs_64xx_isr()`, `mvs_64xx_phy_reset()`, `mvs_64xx_phy_disable()/enable()`, `mvs_64xx_assign_reg_set()/free_reg_set()`, `mvs_64xx_make_prd()`, `mvs_64xx_fix_phy_info()`, `mvs_64xx_phy_set_link_rate()`, SPI helpers, `mvs_64xx_fix_dma()`, and `mvs_64xx_tune_interrupt()`.

Control flow: init optionally performs PCI global reset, powers/enables phys, configures PRD request size, applies vendor phy workarounds, programs SAS addresses and DMA ring base addresses, resets each phy, detects SAS/SATA port type, clears and unmasks per-phy interrupts, sets endian mode, resets command queues, configures coalescing, enables TX/RX rings, and unmasks central/SRS interrupts. ISR status filters invalid or absent interrupts; the ISR clears completion, takes `mvi->lock`, and calls common `mvs_int_full()`. SATA register sets are allocated by scanning PCS/MVS_CTL enable bits and freed by clearing those bits.

State and persistence: all state is runtime in `struct mvs_info`, hardware registers, DMA rings, SATA register-set mapping bytes, and phy structures. Link-rate changes and phy disable/enable write hardware control registers but are not driver-persisted.

Dependencies and integration points: depends on `mv_sas.h`, `mv_64xx.h`, `mv_chips.h`, PCI config space, MMIO/I/O port helpers, common interrupt functions, and libsas-facing code in `mv_sas.c`. Selected by `mv_init.c` for chip flavors 6320, 6440, 6485, Areca 1300, and compatible IDs.

Risks and test signals: reset loops and register polling lack broad timeout coverage in several paths. SoC and PCI branches manipulate different register spaces and are easy to regress independently. `mvs_64xx_init()` has dense hardware sequencing with fixed sleeps. Tests should include probe/remove on representative 64xx and SoC devices, phy reset/disable/rate changes, SATA NCQ/SRS stop recovery, PRD generation with max scatterlists, interrupt coalescing sysfs writes, and fault injection for ioremap/DMA allocation failures.
