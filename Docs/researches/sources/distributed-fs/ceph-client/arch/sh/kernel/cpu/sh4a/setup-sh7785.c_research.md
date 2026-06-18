# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/setup-sh7785.c

Purpose: provides SH7785 device and interrupt setup for six SCIF ports, two TMU blocks, two DMA engines, and an optional URAM node.

Important APIs, types, and functions: `sh7785_devices_setup()` registers SCIF0-5, TMU0-1, and DMA0-1. `plat_early_device_setup()` exposes serial/timers early. `plat_irq_setup()` and `plat_irq_setup_pins()` configure main and external interrupt descriptors. `plat_mem_setup()` registers URAM as Node 1.

Control flow: SCIF resources use `SCIx_SH4_SCIF_FIFODATA_REGTYPE` and `SCSCR_REIE | SCSCR_CKE1`. DMA0 has DMARS resources, while DMA1 does not. Interrupt setup supports separate IRQ0123/IRQ4567 and IRL0123/IRL4567 descriptors.

State and persistence: device metadata is static; `plat_mem_setup()` registers `0xe55f0000-0xe5610000` as bootmem node 1. INTC and DMA runtime state lives in hardware.

Dependencies and integration points: integrates with `sh-sci`, `sh-tmu`, `sh-dma-engine`, PFC/board external pin setup, and SuperH INTC.

Risks: DMA1 lacking DMARS must match driver expectations. URAM registration must align with memory maps. External pin mode setup directly toggles ICR0 and mask registers.

Test signals: SCIF0-5 console/TTY tests, DMA transfer tests on both engines, timer interrupts, `/proc/iomem` node visibility for URAM, and external IRQ/IRL mode tests.
