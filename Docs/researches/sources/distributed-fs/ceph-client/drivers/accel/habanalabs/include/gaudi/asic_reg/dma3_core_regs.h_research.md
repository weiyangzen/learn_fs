# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma3_core_regs.h

## Purpose

`dma3_core_regs.h` defines the generated register offsets for Gaudi `DMA3_CORE`. It exports 67 `mmDMA3_CORE_*` macros from `0x560000` through `0x560238`, with `mmDMA3_CORE_BASE` in `gaudi_blocks.h` at `0x7FFC560000ull`. DMA3 is part of the HBM DMA set.

## Important APIs, Types, And Register Groups

There are no functions or data types. Macro groups cover core configuration/halt/enable, source and destination base registers, transfer sizes and strides for dimensions 0..4, commit and write-completion registers, protection/security property registers, read/write outstanding and cache controls, ARUSER/AWUSER settings, rate limit registers, error cause/config/message registers, status, read debug memory access, and AXI/descriptor debug counters.

## Control Flow And State

The header has no runtime logic. DMA3 control is driven by common Gaudi DMA routines that add `3 * DMA_CORE_OFFSET` to DMA0 core register offsets, plus direct writes in HBM stall paths to `mmDMA3_CORE_CFG_1`. `gaudi_init_dma_core()` enables and configures the core, `gaudi_dma_core_transfer()` programs source/destination/size/commit and polls status, and reset restoration rewrites completion and AWUSER state for HBM DMA channels including DMA3.

The state represented is persistent device register state: active transfer addresses, multidimensional geometry, inflight counters, error status, completion writeback target, MMU/security properties, and debug state. `gaudi_mmu_prepare()` refreshes `mmDMA3_CORE_NON_SECURE_PROPS` when switching ASID context.

## Dependencies And Integration Points

The file enters the build through `gaudi_regs.h`. Its layout must remain isomorphic with DMA0/DMA1 core maps because `DMA_CORE_OFFSET`-based loops address it indirectly. Integration points include HBM DMA initialization and stall, debugfs DMA transfer helper paths, engine idle reporting through `DMA_CORE_STS0`, reset restore, and MMU preparation. Field-level interpretation depends on sibling Gaudi shift/mask headers.

## Risks And Test Signals

Risks are wrong MMIO offsets for transfer-control registers, broken HBM DMA reset restoration, and security regressions if `NON_SECURE_PROPS` or AWUSER registers move. Transfer size/stride register errors can corrupt multidimensional copies. Test evidence should include successful HBM DMA operation on DMA3, idle detection after stop/stall, zero `ERR_CAUSE`, successful reset restore of completion writebacks, and no ASID mismatch in MMU-enabled workloads.
