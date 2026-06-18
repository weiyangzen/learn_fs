# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_dma_helper.c

## Purpose
`drm_gem_dma_helper.c` implements GEM objects backed by DMA-addressable memory that is contiguous from the device perspective. It targets simple display and accelerator devices that either require physically contiguous CMA memory or see contiguous IOVA through an IOMMU. It supplies default GEM object callbacks, dumb-buffer creation, mmap, vmap, debug printing, and PRIME import/export helpers.

## Important APIs, Types, And Functions
The key type is `struct drm_gem_dma_object`, wrapping `struct drm_gem_object` with `vaddr`, `dma_addr`, `sgt`, and noncoherent mapping state. Public functions include `drm_gem_dma_create()`, `drm_gem_dma_free()`, `drm_gem_dma_dumb_create[_internal]()`, `drm_gem_dma_get_sg_table()`, `drm_gem_dma_prime_import_sg_table()`, `drm_gem_dma_prime_import_sg_table_vmap()`, `drm_gem_dma_vmap()`, `drm_gem_dma_mmap()`, `drm_gem_dma_print_info()`, and no-MMU `drm_gem_dma_get_unmapped_area()`. `drm_gem_dma_default_funcs` wires these into GEM callbacks.

## Control Flow
Creation rounds size to pages, allocates or driver-creates a GEM object, installs default funcs when missing, initializes either shmem-backed public GEM state or private imported state, creates a fake mmap offset, then allocates backing memory with `dma_alloc_wc()` or `dma_alloc_noncoherent()`. Dumb creation computes pitch and size, creates the DMA object, publishes a GEM handle, and drops the allocation reference. Freeing distinguishes imported buffers from native allocations: imported objects unmap any vmap and call `drm_prime_gem_destroy()`, while native objects free DMA memory through the matching coherent/write-combined API. Mmap adjusts the fake offset to object-relative offset, clears PFNMAP from the generic GEM setup, sets DONTDUMP/DONTEXPAND, and maps the whole DMA allocation with `dma_mmap_wc()` or `dma_mmap_pages()`.

## State And Persistence Behavior
Native DMA GEM objects keep a stable kernel virtual address and bus address for their lifetime. Imported objects may only have `dma_addr`, `sgt`, and optional vmap state derived from the dma-buf exporter. GEM handle state and mmap offsets are owned by the core GEM code. The `map_noncoherent` flag selects allocation and mmap/free symmetry.

## Dependencies And Integration Points
This helper depends on the DMA mapping API, CMA or IOMMU behavior behind `drm_dev_dma_dev()`, drm dumb-buffer sizing, GEM VMA management, dma-buf PRIME attachment/import paths, and optional no-MMU file operation integration. Drivers typically use the macros in the corresponding header to populate `drm_driver` and `drm_gem_object_funcs`.

## Risks
The largest risk is assuming physical contiguity for imported buffers: `drm_gem_dma_prime_import_sg_table()` rejects imports whose contiguous size is smaller than the dma-buf size, and relaxing that would break devices without scatter-gather. Allocation/free APIs must match `map_noncoherent`. Mmap must preserve VMA flags so core GEM references are released if mapping fails. Imported vmap paths must unmap with `dma_buf_vunmap_unlocked()` during free. Dumb-buffer size multiplication should remain guarded by `drm_mode_size_dumb()` where possible.

## Test Signals
Useful tests include dumb-buffer creation and mmap on CMA and IOMMU-backed devices, PRIME import of contiguous and non-contiguous sg tables, dma-buf vmap import and free, no-MMU get-unmapped-area lookup and permission checks, debugfs print verification, and failure injection for DMA allocation, mmap, and handle publication.
