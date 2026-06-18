# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-pvr2.c



Source read size: 102 lines, 2272 bytes.



Purpose: Dreamcast NEC PowerVR2 DMA provider layered on the on-chip DMAC cascade channel.

Important APIs/types/functions: `pvr2_dma_interrupt()`, `pvr2_request_dma()`, `pvr2_xfer_dma()`, `pvr2_get_dma_residue()`, `pvr2_dma_info`, and cascade channel `PVR2_CASCADE_CHAN`.

Control flow: init requests the PVR2 DMA event, reserves the cascade channel, and registers one TEI-capable channel. Request rejects busy PVR2 mode. Transfer requires no source and a valid destination, resets completion state, and writes PVR2 address/count/mode. Interrupt waits for the SH DMAC cascade residue to drain, marks completion, and wakes waiters via residue semantics.

State and persistence: global `xfer_complete`, debug interrupt counter, PVR2 DMA MMIO registers, and reserved cascade DMA channel.

Dependencies and integration points: depends on Dreamcast hardware event definitions, PVR2 register macros, SH on-chip DMAC, and the legacy DMA API.

Risks and test signals: completion is a global flag for a single channel; cascade failures can stall in interrupt context waiting for completion. Test framebuffer DMA paths, busy-mode rejection, cascade residue behavior, and module unload cleanup.
