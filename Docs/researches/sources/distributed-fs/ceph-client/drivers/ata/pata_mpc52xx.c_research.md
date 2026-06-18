# sources/distributed-fs/ceph-client/drivers/ata/pata_mpc52xx.c

`pata_mpc52xx.c` is the OF platform libata driver for the Freescale MPC52xx on-chip ATA controller. It supports PIO and optional MWDMA/UDMA via BestComm DMA tasks, with DMA masks controlled by device-tree properties because board routing and MPC5200B errata can make DMA unsafe.

`struct mpc52xx_ata` maps controller registers. `struct mpc52xx_ata_timings` caches per-device PIO/MDMA/UDMA registers, and `struct mpc52xx_ata_priv` stores clock period, register base/PA, IRQ, timings, selected device, BestComm task/specs, last DMA direction, and DMA status. Timing is computed by `mpc52xx_ata_compute_pio_timings()`, `mpc52xx_ata_compute_mdma_timings()`, and `mpc52xx_ata_compute_udma_timings()`, then applied by `mpc52xx_ata_apply_timings()`. `mpc52xx_ata_hw_init()` resets host/FIFO and initializes PIO0.

DMA flow builds BestComm ATA buffer descriptors in `mpc52xx_ata_build_dmatable()`, configures FIFO and DMA mode in `mpc52xx_bmdma_setup()`, starts/stops BestComm tasks, and reports status through `waiting_for_dma`. `mpc52xx_ata_task_irq()` drains completed BestComm buffers and sets `ATA_DMA_INTR`.

Probe reads IPB frequency, maps OF resources, builds DMA masks from `mwdma-mode`/`udma-mode`, maps ATA IRQ, allocates private state, selects 66 or 132 MHz spec tables, allocates BestComm task and IRQ, initializes hardware, and registers a one-port host with taskfile pointers into the MMIO struct. Risks include unsafe DMA enablement, descriptor overflow, FIFO errors, clock miscalculation, and UDMA mode limits. Tests should cover no-DMA DT, DMA masks, BestComm failure unwind, large scatterlists, FIFO error paths, direction changes, timing reapply, and PM reinitialization.
