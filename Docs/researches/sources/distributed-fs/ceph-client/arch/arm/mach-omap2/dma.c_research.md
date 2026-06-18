<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c

## Purpose
`dma.c` supplies OMAP2+ system DMA platform data to the shared OMAP DMA engine driver. It describes register offsets, channel stride, capabilities, OMAP24xx slave mappings, and SoC-specific DMA errata flags.

## Important APIs, Types, and Functions
The main exported data object is `struct omap_system_dma_plat_info dma_plat_info`. Internals include `reg_map[]`, `configure_dma_errata()`, `omap24xx_sdma_dt_map[]`, `dma_attr`, and `omap2_system_dma_init()`.

## Control Flow
At `omap_arch_initcall`, `omap2_system_dma_init()` computes errata from SoC family, revision, and GP/secure type. It adds legacy OMAP24xx MUSB/TUSB DMA slave maps, enables `IS_RW_PRIORITY` on non-OMAP242x, and reserves high-security channels on secure OMAP34xx devices. The DMA engine driver later consumes `dma_plat_info`.

## State and Persistence Behavior
Mutable state is limited to boot-time initialization of `dma_plat_info.errata` and `dma_attr.dev_caps`. No persistent data is written. Runtime DMA channel state is managed by the DMA driver, not this file.

## Dependencies and Integration Points
It depends on `linux/omap-dma.h`, DMA engine types, SoC and revision helpers, and initcall ordering before DMA controller probe. It integrates with platform data for the OMAP SDMA driver and legacy consumers requiring slave maps.

## Risks
Errata bits are safety-critical. Missing one can cause FIFO stalls, hung channels, uncleared IRQs after ROM secure save/restore, or invalid priority programming. Over-broad errata can reduce performance or reserve channels unnecessarily. Slave map drift can break legacy MUSB DMA requests.

## Test Signals
Compile OMAP2/3/4/AM/DRA DMA-enabled builds. Runtime tests include DMA memcpy, cyclic audio, MMC, MUSB, parallel channel stress, channel abort/error paths, and suspend/resume on secure OMAP34xx. Confirm the DMA driver sees expected `dev_caps`, `lch_count`, register stride, and errata flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/dma.c -->
