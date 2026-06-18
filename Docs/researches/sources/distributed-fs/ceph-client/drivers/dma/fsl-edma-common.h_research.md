# sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h

### Purpose
`fsl-edma-common.h` is the shared private interface for the Freescale/NXP eDMA driver. It defines register bits, TCD layouts, channel and engine state, variant capability flags, endian-aware MMIO helpers, TCD access macros, and prototypes implemented by `fsl-edma-common.c`.

### Important APIs, Types, And Functions
Important hardware types are `struct fsl_edma_hw_tcd`, `struct fsl_edma_hw_tcd64`, `struct fsl_edma3_ch_reg`, and `struct edma_regs`. Runtime state is in `struct fsl_edma_chan`, `struct fsl_edma_desc`, `struct fsl_edma_drvdata`, and `struct fsl_edma_engine`. Variant flags include `FSL_EDMA_DRV_SPLIT_REG`, `FSL_EDMA_DRV_EDMA64`, `FSL_EDMA_DRV_HAS_PD`, `FSL_EDMA_DRV_HAS_CHCLK`, `FSL_EDMA_DRV_HAS_CHMUX`, `FSL_EDMA_DRV_TCD64`, and grouped `FSL_EDMA_DRV_EDMA3`/`FSL_EDMA_DRV_EDMA4`. Inline helpers include `edma_readl()`, `edma_writel()`, `edma_readw()`, `edma_writew()`, `edma_readq()`, `edma_writeq()`, `to_fsl_edma_chan()`, `to_fsl_edma_desc()`, and TCD field read/write/copy macros.

### Control Flow, State, And Persistence
The header has no standalone runtime flow, but its macros determine how common code reads and writes both memory TCDs and MMIO TCD registers. It preserves per-channel state such as active descriptor, DMA slave config, mapped peripheral resource, source ID, IRQ names, power-domain devices, channel clocks, priority, hardware channel ID, direction flags, and multi-FIFO/remote flags. The engine persists global MMIO bases, DMAMUX bases and clocks, a variant data pointer, channel masks, endianness, and the flexible channel array.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on DMAengine, platform-device, virt-dma, tracepoint infrastructure, endian conversion, and MMIO accessors. It integrates the main platform driver, common transfer code, and trace definitions. Risks include complex `_Generic` TCD macros that must compile for both 32- and 64-bit TCD structures, big-endian 8/16-bit register offset swizzling, variant flag combinations that imply different register layouts, and duplicate bus-width bits. Test signals include builds for all compatible variants, sparse/endian warnings, tracepoint compilation through `CREATE_TRACE_POINTS`, 64-bit TCD access, big-endian IO, and masked-channel probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-common.h -->
