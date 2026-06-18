# sources/distributed-fs/ceph-client/drivers/dma-buf/dma-buf-mapping.c

Purpose: provides exporter helpers for creating and freeing dma-buf scatter-gather tables from physical MMIO ranges, including PCI P2PDMA and IOVA-backed mappings.

Important APIs/types/functions: exports `dma_buf_phys_vec_to_sgt()` and `dma_buf_free_sgt()` in the `DMA_BUF` namespace. Internal helpers `fill_sg_entry()` and `calc_sg_nents()` split large DMA spans into scatterlist entries compatible with `sg_dma_len`.

Control flow: `dma_buf_phys_vec_to_sgt()` asserts the dma-buf reservation lock, validates attachment and P2P provider, allocates a private `struct dma_buf_dma`, chooses mapping mode via `pci_p2pdma_map_type()`, optionally allocates `dma_iova_state`, allocates an sg table, maps each physical vector either to P2P bus addresses, DMA API physical mappings, or IOVA links, and fills only DMA address/length fields in the returned scatterlist. For IOVA mappings it syncs the whole IOVA range and emits one logical DMA address span. On errors it unmaps any partial work and frees state. `dma_buf_free_sgt()` performs the corresponding IOVA destroy or `dma_unmap_phys()` loop, frees the sg table, and releases wrapper state.

State and persistence behavior: mapping state persists in the private object containing the returned `sg_table`; callers must release it through `dma_buf_free_sgt()`. `orig_nents` is set to zero to signal that there is no CPU page list.

Dependencies and integration points: depends on dma-resv locking, PCI P2PDMA routing, DMA IOVA helpers, DMA mapping APIs, `struct phys_vec`, and dma-buf attachment semantics. Intended for exporters of MMIO/P2P memory, not normal page-backed buffers.

Risks and test signals: callers must hold the reservation lock and must not treat returned scatterlist entries as page-backed. Alignment is documented as page-sized; misuse by importers can break because `sg_page` is deliberately NULL. Error cleanup has separate paths for IOVA and non-IOVA mappings. Test signals include P2P bus-address mapping, host-bridge IOVA mapping, non-IOVA `dma_map_phys()` fallback, correct splitting above `UINT_MAX`, and balanced unmap/free under injected mapping failures.
