# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.c

## Purpose

`rockchip_drm_gem.c` implements Rockchip GEM buffer allocation, mmap, dumb-buffer creation, and PRIME import/export. It supports page-backed buffers mapped through the shared IOMMU domain and contiguous DMA allocations when no IOMMU domain is available.

## Important APIs, Types, and Functions

- `rockchip_gem_create_object()` allocates object metadata and backing storage.
- `rockchip_gem_dumb_create()` sizes dumb buffers with 64-byte pitch alignment and creates a GEM handle.
- IOMMU helpers get pages, build sg tables, allocate IOVA from `drm_mm`, map through `iommu_map_sgtable`, and optionally vmap pages.
- DMA helpers use `dma_alloc_attrs`, `dma_mmap_attrs`, and contiguous sg-table import.
- PRIME helpers export/import sg tables and provide vmap/vunmap.

## Control Flow

New local buffers are created by initializing the GEM object, then selecting IOMMU or DMA backing from `drm->dev_private->domain`. The IOMMU path gets pages, converts them to an sg table, syncs for device, reserves IOVA under `mm_lock`, and maps the sg table. The DMA path uses `dma_alloc_attrs`, adding `DMA_ATTR_NO_KERNEL_MAPPING` when no kernel map is needed. Freeing reverses native allocation or imported sg mapping.

## State and Persistence Behavior

Each `rockchip_gem_object` persists DMA address, optional kernel virtual address, DMA attrs, pages, sg table, page count, IOMMU `drm_mm_node`, and mapped size. Imported objects keep `obj->import_attach` and `rk_obj->sgt` until GEM release. VOP/VOP2 read `dma_addr` directly for scanout.

## Dependencies and Integration Points

This file depends on DRM GEM, GEM DMA VM ops, PRIME helpers, dumb-buffer helpers, Linux IOMMU, DMA-buf, scatter-gather, vmalloc, and Rockchip private DMA helpers. It integrates directly with framebuffer scanout paths through `to_rockchip_obj`.

## Risks and Edge Cases

The IOMMU path depends on `iommu_map_sgtable` size semantics. DMA PRIME import rejects non-contiguous sg tables without IOMMU. mmap relies on DRM setup to bound VMA size after resetting `vm_pgoff`. Cache coherency relies on `dma_sync_sgtable_for_device` and write-combine mappings.

## Test Signals

Exercise dumb allocation with and without IOMMU, mmap, fbdev kernel mapping, PRIME export/import of contiguous and non-contiguous buffers, vmap/vunmap, concurrent allocation/free, and VOP/VOP2 scanout from local and imported buffers.
