# sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h -->
## sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h

### Purpose
`regs.h` is the shared private register, descriptor, and state definition header for the Synopsys DesignWare AHB DMA driver family. It describes the classic DW DMA register map, iDMA32 extensions, linked-list item layout, channel state, and engine-level callbacks used by the implementation files under `drivers/dma/dw/`.

### Important APIs, Types, And Functions
The main hardware-facing types are `struct dw_dma_chan_regs`, `struct dw_dma_irq_regs`, `struct dw_dma_regs`, and `struct dw_lli`. Driver state is represented by `struct dw_dma_chan`, `struct dw_dma`, and `struct dw_desc`. Important enums and flags include `enum dw_dma_fc`, `enum dw_dma_msize`, `enum idma32_msize`, and `enum dw_dmac_flags`. The header also provides access helpers such as `channel_readl()`, `channel_writel()`, `dma_readl()`, `dma_writel()`, `idma32_readq()`, `idma32_writeq()`, `channel_set_bit()`, `channel_clear_bit()`, `to_dw_dma_chan()`, `to_dw_dma()`, and `txd_to_dw_desc()`.

### Control Flow, State, And Persistence
The header itself has no runtime control flow, but it defines how runtime code persists DMA state in memory. A `dw_dma` owns the DMAengine device, MMIO base, descriptor pool, tasklet, channel array, platform data, and variant callbacks for channel initialization, suspend/resume, CTL encoding, block-size conversion, device naming, and global enable/disable. Each `dw_dma_chan` tracks active and queued descriptors under a spinlock, soft-LLP state, slave configuration, burst and block limits, and bit flags for cyclic, paused, initialized, or software-linked-list operation. `struct dw_desc` places the hardware LLI first so descriptors can be DMA-visible while still carrying Linux DMAengine bookkeeping.

### Dependencies, Integration Points, Risks, And Test Signals
This header depends on Linux DMAengine types, interrupt/tasklet infrastructure, MMIO accessors, endian conversion, nonatomic 64-bit IO helpers, and local DW platform definitions in `internal.h`. It integrates with platform-specific DesignWare DMA implementations and iDMA32 variants through callback fields and register-layout macros. Risks are mostly ABI-like: bitfield shifts must match silicon manuals, `DW_REG()` padding assumes the controller's register spacing, and descriptor layout/endian conversions must stay compatible with hardware linked-list fetches. Test signals include successful probing across classic DW and iDMA32 controllers, memcpy/slave/cyclic transfers, linked-list chaining, pause/resume, residue reporting, and interrupt mask/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/dw/regs.h -->
