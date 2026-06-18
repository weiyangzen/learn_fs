# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Kconfig

Purpose: defines selectable dma-buf heap backends.

Important APIs/types/functions: `DMABUF_HEAPS_SYSTEM` enables the buddy-allocator-backed system heap and depends on `DMABUF_HEAPS`; `DMABUF_HEAPS_CMA` enables the CMA-backed heap and depends on `DMABUF_HEAPS && DMA_CMA`.

Control flow: no runtime control flow. These symbols select heap object files in `heaps/Makefile`, whose init functions register heap devices with `dma_heap_add()`.

State and persistence behavior: build configuration only.

Dependencies and integration points: integrates heap backend selection with the generic dma-heap framework. System heap uses normal pages; CMA heap uses contiguous memory allocator areas.

Risks and test signals: enabling CMA heap without usable CMA areas may produce no useful allocation node except where CMA regions exist. Test signals are `/dev/dma_heap/system`, optional `/dev/dma_heap/system_cc_shared`, and CMA heap device nodes matching configured CMA areas.
