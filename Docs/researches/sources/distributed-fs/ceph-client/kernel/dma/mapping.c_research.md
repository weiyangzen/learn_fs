# sources/distributed-fs/ceph-client/kernel/dma/mapping.c

## Purpose

`mapping.c` is the architecture-independent front door for the Linux DMA mapping API. It normalizes driver-facing calls such as streaming map/unmap, coherent allocation, scatter-gather mapping, sync, mmap, mask setup, and noncontiguous allocation, then dispatches to the right backend: direct DMA, IOMMU DMA, or architecture/device-specific `struct dma_map_ops`. It also wraps those operations with DMA API debug tracking, tracepoints, KMSAN handling, and devres-managed allocation helpers.

## Important APIs, Types, And Functions

- `struct dma_devres`, `dmam_alloc_attrs()`, and `dmam_free_coherent()` provide devres-managed coherent DMA allocations. The release path calls `dma_free_attrs()`, and the matcher validates that the caller frees the same virtual address, size, and DMA handle.
- `dma_go_direct()`, `dma_alloc_direct()`, and `dma_map_direct()` decide whether an operation can bypass `dma_map_ops`. They reject the direct path when `use_dma_iommu(dev)` is active and optionally honor `CONFIG_DMA_OPS_BYPASS` via `dev->dma_ops_bypass`.
- `dma_map_phys()`, `dma_map_page_attrs()`, `dma_unmap_phys()`, and `dma_unmap_page_attrs()` implement single-buffer streaming mapping. They validate directions, masks, `DMA_ATTR_REQUIRE_COHERENT`, MMIO, confidential-computing shared attributes, and zone-device pages.
- `__dma_map_sg_attrs()`, `dma_map_sg_attrs()`, `dma_map_sgtable()`, and `dma_unmap_sg_attrs()` handle scatterlists and sg_tables. The internal helper preserves negative errno details for `dma_map_sgtable()`, while the legacy scatterlist API collapses errors to zero.
- `dma_map_resource()` and `dma_unmap_resource()` map MMIO/resource ranges by forcing `DMA_ATTR_MMIO` and rejecting normal RAM PFNs under DMA API debug.
- Under `CONFIG_DMA_NEED_SYNC`, `__dma_sync_single_for_cpu()`, `__dma_sync_single_for_device()`, `__dma_sync_sg_for_cpu()`, `__dma_sync_sg_for_device()`, `__dma_need_sync()`, `dma_need_unmap()`, and `dma_setup_need_sync()` centralize cache/ownership synchronization policy.
- `dma_get_sgtable_attrs()`, `dma_can_mmap()`, `dma_mmap_attrs()`, and `dma_pgprot()` expose coherent allocation export/mmap support and choose page protections for coherent or write-combined memory.
- `dma_alloc_attrs()`, `dma_free_attrs()`, `dma_alloc_pages()`, `dma_free_pages()`, `dma_mmap_pages()`, `dma_alloc_noncontiguous()`, `dma_free_noncontiguous()`, `dma_vmap_noncontiguous()`, `dma_vunmap_noncontiguous()`, and `dma_mmap_noncontiguous()` provide allocation variants.
- `dma_set_mask()`, `dma_set_coherent_mask()`, `dma_get_required_mask()`, `dma_addressing_limited()`, `dma_max_mapping_size()`, `dma_opt_mapping_size()`, `dma_get_merge_boundary()`, and `dma_pci_p2pdma_supported()` expose device capability and sizing queries.

## Control Flow

The common control pattern is: validate API inputs, choose direct/IOMMU/ops backend, call the backend, then emit trace/debug/KMSAN side effects. For streaming physical mappings, `dma_map_phys()` first rejects invalid directions or missing masks, rejects required-coherent mappings on noncoherent devices, then uses direct mapping if `dma_map_direct()` or `arch_dma_map_phys_direct()` says it is allowed. Otherwise it rejects `DMA_ATTR_CC_SHARED`, then tries `iommu_dma_map_phys()` or `ops->map_phys()`. Unmap mirrors that path.

Scatter-gather mapping follows the same backend selection but has more error normalization. `__dma_map_sg_attrs()` accepts only expected negative errors (`-EINVAL`, `-ENOMEM`, `-EIO`, `-EREMOTEIO`); unexpected negative returns are warned, traced as errors, and converted to `-EIO`. The public `dma_map_sg_attrs()` returns zero on any negative error to preserve the older API contract, while `dma_map_sgtable()` propagates the errno and records `sgt->nents` on success.

Allocation flow first checks device coherent mask and rejects `__GFP_COMP`, then tries per-device coherent memory with `dma_alloc_from_dev_coherent()`. If that does not satisfy the request, it strips caller-provided DMA zone flags and dispatches to direct, IOMMU, or `ops->alloc`. Freeing reverses this order: release device coherent memory first, warn if called with IRQs disabled, trace/debug the free, then dispatch to direct, IOMMU, or `ops->free`.

Noncontiguous allocation uses the IOMMU allocator when available; otherwise it falls back to a single page-backed sg_table from `alloc_single_sgt()`. Vmap, vunmap, and mmap for noncontiguous allocations similarly defer to IOMMU helpers or operate on the single fallback page.

## State And Persistence Behavior

This file does not persist state to disk. It mutates runtime device state: DMA masks (`*dev->dma_mask`, `dev->coherent_dma_mask`), `dev->dma_skip_sync`, and devres allocation records. It also emits tracepoints and DMA debug records, updates KMSAN state for DMA ownership transfers, and relies on per-device coherent pools managed elsewhere. Managed allocations persist until explicit free or device detach through devres.

## Dependencies And Integration Points

The file is tightly integrated with `linux/dma-map-ops.h`, `direct.h`, `iommu-dma.h`, `debug.h`, KMSAN, trace events in `trace/events/dma.h`, scatterlist APIs, vm/mmap APIs, and arch hooks such as `arch_dma_map_phys_direct()`, `arch_dma_alloc_direct()`, `arch_dma_set_mask()`, and cache-sync operations. It is exported heavily (`EXPORT_SYMBOL`, `EXPORT_SYMBOL_GPL`) and is therefore a shared kernel subsystem surface used by drivers, IOMMU backends, architecture DMA implementations, and DMA API debugging.

## Risks And Edge Cases

- Backend selection must stay symmetric between map/unmap and alloc/free; mismatches can leak IOVA space, bounce buffers, or coherent memory.
- `DMA_ATTR_REQUIRE_COHERENT`, `DMA_ATTR_MMIO`, and `DMA_ATTR_CC_SHARED` are policy-sensitive. Incorrect handling can break noncoherent devices, resource mappings, or confidential-computing sharing assumptions.
- The direct path depends on masks, `bus_dma_limit`, and optional bypass state. Incorrect mask updates can silently expose devices to unreachable DMA addresses.
- `dma_free_attrs()` warns in IRQ-disabled context because some noncoherent implementations may sleep through `vunmap()`.
- `dma_get_sgtable_attrs()` is explicitly documented as fundamentally unsafe for some coherent allocations because not all coherent memory has ordinary `struct page` backing and streaming APIs must not be mixed with coherent aliases.
- `dma_need_unmap()` can return false only after mappings have been established, because SWIOTLB use can reset `dev->dma_skip_sync`.

## Test Signals

Useful test signals include DMA API debug warnings, tracepoints (`dma_map_phys`, `dma_map_sg`, allocation/free and sync traces), KMSAN reports around DMA buffers, boot/device tests across direct DMA and IOMMU configurations, noncoherent architecture tests, SWIOTLB/bounce-buffer tests, P2PDMA capability checks, mmap tests for coherent allocations, and sg_table error-path tests verifying errno versus zero-return API behavior.
