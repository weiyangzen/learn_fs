# sources/distributed-fs/ceph-client/drivers/xen/swiotlb-xen.c

## Purpose
`swiotlb-xen.c` provides Xen-specific DMA mapping operations. It translates Linux physical addresses to Xen bus-frame based DMA addresses and uses SWIOTLB bounce buffers when devices cannot DMA to the translated or contiguous address range safely.

## Important APIs, types, and functions
The exported object is `xen_swiotlb_dma_ops`. Key helpers are `xen_phys_to_bus`, `xen_phys_to_dma`, `xen_dma_to_phys`, `range_straddles_page_boundary`, `range_requires_alignment`, `xen_swiotlb_find_pool`, `xen_swiotlb_map_phys`, `xen_swiotlb_unmap_phys`, sync helpers for single and scatter-gather mappings, and `xen_swiotlb_dma_supported`. On x86 it also implements `xen_swiotlb_fixup`, `xen_swiotlb_alloc_coherent`, and `xen_swiotlb_free_coherent`.

## Control flow
Streaming DMA map converts the physical address to a Xen DMA address, returns it directly when the device can address it and no bounce is required, or allocates a SWIOTLB slot and maps that instead. Unmap and sync convert the DMA address back to the guest physical page, perform architecture or Xen cache synchronization, then unmap/sync the SWIOTLB pool if the address belongs to one. Scatter-gather helpers apply the same operation to each entry and unwind partial failures. Coherent allocation tries normal pages first and, when needed, asks Xen for a contiguous region within the coherent mask.

## State and persistence
The file owns no durable state. It relies on global SWIOTLB pools, Xen PFN/BFN mappings, page flags such as `PageXenRemapped`, device DMA masks, and architecture cache-coherency state.

## Dependencies and integration points
It integrates with Linux `dma_map_ops`, `dma-direct`, SWIOTLB internals, Xen page translation, Xen contiguous-region hypercalls, architecture cache synchronization, and tracing via `trace_swiotlb_bounced`.

## Risks and test signals
Risks include incorrect PFN/BFN translation, page-boundary contiguity checks, DMA mask overflows, bounce pool lookup for foreign bus addresses, cache sync order on noncoherent devices, coherent allocation/free mismatch, and scatter-gather unwind. Test signals include PCI passthrough DMA under PV guests, 32-bit DMA masks, noncontiguous guest memory, forced SWIOTLB bouncing, coherent allocations crossing Xen page boundaries, noncoherent device sync tests, and DMA API debug.
