# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/goya_blocks.h

Purpose: auto-generated top-level Goya hardware block map. It defines 64-bit base addresses, maximum offsets, and section sizes for router, DMA, MME, SRAM, CPU, MMU, PLL, DDR, PCIe, PSOC, TPC, CoreSight, bus-monitor, and trace blocks.

Important APIs/types/functions: no functions or types. The API is a large macro set such as `mmDMA_NRTR_BASE`, `DMA_NRTR_MAX_OFFSET`, `DMA_NRTR_SECTION`, `mmDMA_QM_0_BASE` through `mmDMA_QM_4_BASE`, `mmDMA_CH_3_BASE`, `mmDMA_CH_4_BASE`, `mmMC_PLL_BASE`, `mmIC_PLL_BASE`, `mmDMA_MACRO_BASE`, `mmMME1_RTR_BASE`, and many CoreSight/debug block bases. The repeated triplet pattern lets driver code reason about block windows and protection/register access limits.

Control flow: none in the header. Runtime code uses base macros to configure protected blocks, locate CoreSight components, validate register offsets, and translate block-relative register maps into full device addresses.

State and persistence: the file itself is static compile-time metadata. It describes persistent device address space layout but stores no runtime state. Hardware block state persists in the MMIO regions named here.

Dependencies and integration: included by `goya_regs.h`, then indirectly by `goya_masks.h`, `goya.c`, `goya_security.c`, and `goya_coresight.c`. `goya_security.c` calls protection helpers on block bases such as `mmMME1_RTR_BASE`, `mmDMA_NRTR_BASE`, `mmDMA_CH_3_BASE`, and `mmDMA_CH_4_BASE`. `goya_coresight.c` uses CoreSight, SPMU, CTI, funnel, and bus-monitor bases from this header.

Risks: this is a root address authority. A bad base, max offset, or section size can redirect MMIO to the wrong hardware, leave registers unprotected, or make debug discovery operate on the wrong component. Section sizes are not uniform; deriving instance layout arithmetically instead of using macros can fail.

Test signals: driver probe succeeds, protected-block setup covers expected windows, CoreSight registration finds the expected components, DMA/MME/TPC/PCIe register access lands in valid ranges, and register access tests do not trigger unexpected bus faults or RAZWI events.
