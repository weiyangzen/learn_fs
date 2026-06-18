# sources/distributed-fs/ceph-client/drivers/dma/ti/Kconfig

## Purpose
This Kconfig file declares the Texas Instruments DMA driver options for CPPI 4.1, EDMA, OMAP sDMA, K3 UDMA, the K3 UDMA glue layer, the internal K3 PSI-L endpoint library, and the internal TI DMA crossbar router.

## Important APIs, Types, and Functions
There are no runtime functions; the important interface is the Kconfig symbols. `TI_CPPI41` builds the CPPI USB DMA engine on OMAP/DA8xx. `TI_EDMA` selects `DMA_ENGINE`, `DMA_VIRTUAL_CHANNELS`, and conditionally `TI_DMA_CROSSBAR`. `DMA_OMAP` does the same for OMAP sDMA. `TI_K3_UDMA` depends on K3 architecture or compile testing, TI SCI protocol, and TI SCI INTA irqchip support, and selects `SOC_TI`, ring accelerator support, and `TI_K3_PSIL`. `TI_K3_PSIL` is a hidden tristate defaulting to `TI_K3_UDMA`; `TI_DMA_CROSSBAR` is an internal bool.

## Control Flow
Build-time dependency resolution controls which source files in the TI DMA directory are compiled. Enabling UDMA automatically brings in the PSI-L library needed by K3 UDMA endpoint lookup. EDMA and OMAP sDMA select the crossbar on relevant OMAP/compile-test configurations.

## State and Persistence
The file has no runtime state. Its persistent effect is the kernel build configuration and selected object graph.

## Dependencies and Integration Points
It integrates with architecture symbols (`ARCH_OMAP`, `ARCH_DAVINCI`, `ARCH_KEYSTONE`, `ARCH_K3`, `SOC_DRA7XX`), compile-test builds, DMAengine core, virtual channels, TI SCI firmware interfaces, TI INTA interrupt controller support, TI ring accelerator support, and the Makefile in the same directory.

## Risks
Incorrect dependencies can silently omit needed support or build drivers on unsupported platforms. `TI_K3_PSIL` is hidden and defaulted from UDMA, so any UDMA split or modularization must preserve that selection. Whitespace inconsistency in the `help` blocks is cosmetic but can obscure Kconfig review.

## Test Signals
Build matrix checks should cover `allmodconfig`, `allyesconfig`, K3-only configs, OMAP/DRA7 configs, DaVinci configs, Keystone configs, and `COMPILE_TEST`. Verify that enabling `TI_K3_UDMA` links `k3-psil-lib.o`, and that EDMA/OMAP builds include crossbar support where expected.
