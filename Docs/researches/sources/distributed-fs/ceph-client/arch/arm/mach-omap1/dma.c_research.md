<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c

Purpose: OMAP1 system DMA platform setup. It maps DMA registers, defines register layout/resources, supplies low-level read/write/clear/capability callbacks, describes slave request mappings, and registers legacy system DMA plus dmaengine devices.

Important APIs/types/functions: Important routines are `dma_write`, `dma_read`, `omap1_clear_lch_regs`, `omap1_clear_dma`, `omap1_show_dma_caps`, `configure_dma_errata`, and `omap1_system_dma_init`.

Control flow, state, and persistence: State includes mapped `dma_base`, `enable_1510_mode`, DMA attributes, errata flags, logical channel count, and static IRQ resources. Init allocates platform data, determines CPU capabilities, and registers two DMA-facing devices.

Dependencies and integration points: Important routines are `dma_write`, `dma_read`, `omap1_clear_lch_regs`, `omap1_clear_dma`, `omap1_show_dma_caps`, `configure_dma_errata`, and `omap1_system_dma_init`. Integration is through the source path's Kbuild/Kconfig selection, machine descriptor, initcall, platform-device, DT/ATAGS, register, or low-level assembly contract as described for this file.

Risks: Dependencies include `linux/omap-dma.h`, DMA engine, OMAP IRQs, CPU detection, and register-map semantics. Risks are resource count mismatch in `omap_dma_dev_info` versus full resources on the system device, ioremap lifetime, and 2x16-bit register access ordering. Test DMA clients for MMC, MCBSP, UDC, LCD DMA, OMAP15xx/16xx channel counts, and errata behavior.

Test signals: Build the owning ARM machine configuration, boot the matching board or SoC under DT/ATAGS as applicable, and exercise the specific runtime paths named above. Source read size: 394 lines, 9964 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/dma.c -->
