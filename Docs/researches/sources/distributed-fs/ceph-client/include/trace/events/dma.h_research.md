<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma.h

## Purpose
Defines tracepoints for the generic DMA mapping API. It makes map/unmap/allocation/free/synchronization behavior observable across single buffers, pages, scatter-gather tables, and DMA-coherent allocations.

## APIs, Control Flow, and State
The header declares event classes for `dma_map`, `dma_unmap`, `dma_alloc_class`, `dma_free_class`, `dma_sync_single`, and `dma_sync_sg`, then instantiates events such as `dma_map_phys`, `dma_unmap_phys`, `dma_alloc`, `dma_alloc_pages`, `dma_alloc_sgt`, `dma_alloc_sgt_err`, `dma_free`, `dma_free_pages`, `dma_free_sgt`, `dma_map_sg`, `dma_map_sg_err`, `dma_unmap_sg`, `dma_sync_single_for_cpu/device`, and `dma_sync_sg_for_cpu/device`. `TRACE_DEFINE_ENUM()` exports DMA directions, while helper formatters decode directions, DMA attributes, GFP flags, and scatterlist arrays. `dma_map_sg` caps traced arrays at `DMA_TRACE_MAX_ENTRIES` and records whether output was truncated. The header persists no mapping state; it only snapshots arguments and scatterlist-derived physical/DMA addresses at call time.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/dma-direction.h>`, `<linux/dma-mapping.h>`, scatterlist helpers, device names, and `trace/events/mmflags.h`. Integration points are DMA API instrumentation in architecture or core DMA mapping paths, IOMMU-backed devices, confidential-computing DMA attributes, and driver debugging. Risks include exposing physical/DMA addresses, allocating large dynamic arrays for scatterlists, inconsistent address semantics for unmap events that print physical addresses, and missing entries after the 128-entry cap. Test signals include DMA API debug runs, IOMMU map/unmap traces, SG mapping with more than 128 entries, cache sync paths, allocation/free pairing, and build checks as new `DMA_ATTR_*` bits are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma.h -->
