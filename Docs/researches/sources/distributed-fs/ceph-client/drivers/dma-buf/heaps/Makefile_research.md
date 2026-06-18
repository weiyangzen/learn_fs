# sources/distributed-fs/ceph-client/drivers/dma-buf/heaps/Makefile

Purpose: builds optional dma-buf heap backend implementations.

Important APIs/types/functions: maps `CONFIG_DMABUF_HEAPS_SYSTEM` to `system_heap.o` and `CONFIG_DMABUF_HEAPS_CMA` to `cma_heap.o`.

Control flow: no runtime flow. Module/built-in init functions in the selected objects register heap providers with the common dma-heap framework.

State and persistence behavior: none beyond build artifacts.

Dependencies and integration points: driven by `heaps/Kconfig` and consumed by parent `drivers/dma-buf/Makefile`.

Risks and test signals: missing backend object selection results in no heap device despite the generic heap framework being enabled. Test signal is successful Kbuild inclusion for each selected heap symbol.
