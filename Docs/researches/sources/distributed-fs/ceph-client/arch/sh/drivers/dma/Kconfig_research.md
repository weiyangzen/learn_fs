# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Kconfig



Source read size: 76 lines, 2290 bytes.



Purpose: legacy SH DMA Kconfig menu covering on-chip DMAC, channel counts, API-vs-DMAengine selection, SH7760 DMABRG, Dreamcast PVR2, and G2 DMA.

Important APIs/types/functions: `SH_DMA`, `SH_DMA_IRQ_MULTI`, `SH_DMA_API`, `NR_ONCHIP_DMA_CHANNELS`, `SH_DMABRG`, `PVR2_DMA`, and `G2_DMA`.

Control flow: CPU subtype selects default channel counts and IRQ layout; `SH_DMA_API` enables legacy API users while warning against simultaneous DMAengine use.

State and persistence: compile-time feature matrix only.

Dependencies and integration points: drives `dma/Makefile`, CPU-specific DMAC register definitions, Dreamcast support, and SH7760 audio/USB DMA.

Risks and test signals: wrong channel count or IRQ-multi setting corrupts DMAC indexing; enabling legacy API with DMAengine can conflict. Test representative CPU subtype builds and DMA transfer smoke tests.
