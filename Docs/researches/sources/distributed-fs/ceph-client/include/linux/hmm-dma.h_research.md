# sources/distributed-fs/ceph-client/include/linux/hmm-dma.h

## Purpose
`hmm-dma.h` defines a small DMA mapping helper interface for HMM PFN arrays. It lets device drivers allocate parallel PFN and DMA-address arrays, map individual HMM PFNs including P2P DMA cases, and unmap them later.

## Important APIs, Types, And Functions
`struct hmm_dma_map` contains `struct dma_iova_state state`, `unsigned long *pfn_list`, `dma_addr_t *dma_list`, and `dma_entry_size`. Public functions are `hmm_dma_map_alloc()`, `hmm_dma_map_free()`, `hmm_dma_map_pfn()`, and `hmm_dma_unmap_pfn()`.

## Control Flow And State
A driver allocates an HMM DMA map for a range, fills or receives PFNs from HMM faulting, maps PFNs by index to DMA addresses, stores results in `dma_list`, and unmaps indices when no longer needed. Mapping may use `pci_p2pdma_map_state` for peer-to-peer memory. State is the allocated arrays, IOVA state, per-entry DMA addresses, and implicit DMA API mappings.

## Dependencies And Integration Points
It depends on `linux/dma-mapping.h`, forward-declared `dma_iova_state`, and PCI P2PDMA map state. It integrates with `hmm.h` range-fault results and device DMA APIs.

## Risks
Risks include mismatched entry size, double map/unmap, forgetting to unmap on partial failure, stale DMA addresses after MMU invalidation, and treating P2P/bus-mapped PFNs as ordinary system memory. The caller must coordinate HMM validity and DMA lifetime.

## Test Signals
Test allocation/free, mapping normal system PFNs, P2P PFNs and bus mappings, partial failure unwind, DMA API debug, repeated map/unmap of the same index, and MMU invalidation while device access is active.
