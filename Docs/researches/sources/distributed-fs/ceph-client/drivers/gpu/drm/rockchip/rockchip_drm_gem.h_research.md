# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_gem.h

## Purpose

`rockchip_drm_gem.h` defines the Rockchip GEM object layout and exports the allocation, free, dumb-buffer, PRIME, and vmap interfaces implemented by `rockchip_drm_gem.c`.

## Important APIs, Types, and Functions

- `to_rockchip_obj()` converts a `drm_gem_object` to `struct rockchip_gem_object`.
- `struct rockchip_gem_object` embeds the DRM GEM base and stores `kvaddr`, `dma_addr`, DMA attributes, IOMMU `drm_mm_node`, pages, sg table, page count, and mapped size.
- Exported functions create/free objects, create dumb buffers, and handle PRIME sg-table/vmap operations.

## Control Flow

The header is consumed by framebuffer and display-controller paths. Plane update code uses `to_rockchip_obj` on framebuffer GEM objects and reads `dma_addr` directly to program scanout registers.

## State and Persistence Behavior

The object fields persist for the GEM lifetime. In IOMMU mode, `pages`, `sgt`, `num_pages`, `mm`, `size`, and `dma_addr` describe the IOVA mapping. In DMA mode, `kvaddr`, `dma_addr`, and `dma_attrs` describe the allocation.

## Dependencies and Integration Points

The type relies on DRM GEM and Linux DMA/scatterlist types from including contexts. It is tightly integrated with VOP/VOP2 plane programming, PRIME dma-buf import/export, dumb-buffer creation, and the shared IOMMU domain.

## Risks and Edge Cases

Direct field access by scanout code makes `dma_addr` a cross-file invariant. `flags` is present but unused. Include ordering must provide several type declarations because the header does not include all dependencies itself.

## Test Signals

Build all users of `to_rockchip_obj`, then run allocation, mmap, PRIME, and scanout tests that confirm fields are valid in both IOMMU and DMA configurations.
