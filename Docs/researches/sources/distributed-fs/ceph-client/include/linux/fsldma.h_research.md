# sources/distributed-fs/ceph-client/include/linux/fsldma.h

Purpose: declares a small Freescale DMA helper for externally starting or stopping a DMA channel.

Important APIs and functions: `fsl_dma_external_start(struct dma_chan *dchan, int enable)` toggles external-start behavior for a DMA engine channel.

Control flow and state: DMA clients call the helper with a `dma_chan` and enable flag when hardware handshaking or external trigger control is needed. The header owns no state; provider code updates DMA controller state.

Dependencies and integration points: depends on DMA engine `struct dma_chan` being visible to consumers and integrates with Freescale DMA controller drivers and device drivers requiring external starts.

Risks and test signals: risks include calling it on unsupported DMA channels, ambiguous enable values, and missing provider symbols in configs. Tests should cover enable/disable on supported channels, unsupported channel errors, triggered transfers, and compile/link coverage.
