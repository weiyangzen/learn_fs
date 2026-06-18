## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-regs.h

Purpose: Packed MMIO and linked-list register definitions for eDMA v0 hardware.

Important APIs/types/functions: defines masks for channel counts, viewport, done/abort interrupts, channel status, doorbell channel, linked-list errors, MSI data packing, and `EDMA_V0_MAX_NR_CH`. Structures include `dw_edma_v0_ch_regs`, `dw_edma_v0_ch`, `dw_edma_v0_unroll`, `dw_edma_v0_legacy`, `dw_edma_v0_regs`, `dw_edma_v0_lli`, and `dw_edma_v0_llp`.

Control flow: no executable flow; these layouts are used by the v0 core and debugfs code to compute MMIO addresses and linked-list element format.

State and persistence: represents hardware-visible state in registers and LL memory. Structures are packed because offsets must match the hardware programming model.

Dependencies and integration: includes DMAengine definitions and is private to the eDMA v0 implementation.

Risks and test signals: any offset, padding, or mask error can break channel count discovery, interrupts, MSI setup, descriptor fetch, or debugfs output. Test by comparing offsets against hardware docs, reading debugfs registers, and running transfers on legacy and unroll variants.
