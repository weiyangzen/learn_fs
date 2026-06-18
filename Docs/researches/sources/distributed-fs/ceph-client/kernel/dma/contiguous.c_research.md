# sources/distributed-fs/ceph-client/kernel/dma/contiguous.c

## Purpose
This file integrates the Contiguous Memory Allocator with DMA allocation. It reserves global, per-device, and optional NUMA CMA regions during early boot and provides allocation/free helpers used by the direct DMA allocator.

## Important APIs, Types, And Functions
Important state includes `dma_contiguous_areas[]`, `dma_contiguous_default_area`, command-line CMA size/base/limit values, and optional NUMA CMA arrays. Public APIs include `dma_contiguous_get_area_by_idx()`, `dev_get_cma_area()`, `dma_contiguous_reserve()`, `dma_contiguous_reserve_area()`, `dma_alloc_from_contiguous()`, `dma_release_from_contiguous()`, `dma_alloc_contiguous()`, and `dma_free_contiguous()`. Device-tree hooks include `rmem_cma_validate()`, `rmem_cma_fixup()`, `rmem_cma_setup()`, and device init/release callbacks.

## Control Flow
Early parameters parse `cma=`, `numa_cma=`, and `cma_pernuma=`. `dma_contiguous_reserve()` reserves NUMA CMA areas first, then chooses the default size from command line or Kconfig and declares a default CMA region if needed. Device-tree `shared-dma-pool` regions that are reusable and not `no-map` become CMA areas; `linux,cma-default` selects the default unless overridden by `cma=`. Allocation tries a device-specific CMA area, skips CMA for single-page generic allocations, tries per-NUMA areas when configured, then falls back to the default CMA area. Free releases to the matching device, NUMA, or default CMA area, then falls back to buddy freeing.

## State, Persistence, And Dependencies
CMA regions are persistent for the boot lifetime. Early command-line data is `__initdata`. Dependencies include memblock/CMA core, OF reserved memory, NUMA node state, device `cma_area`, and architecture `dma_contiguous_early_fixup()`.

## Integration Points
`dma_direct_alloc()` and related direct DMA paths call `dma_alloc_contiguous()` and `dma_free_contiguous()`. Reserved-memory device attachment populates `dev->cma_area`. CMA areas can be enumerated by index for heap creation or other subsystem integration.

## Risks
Early reservation failures reduce or remove CMA availability. Alignment is constrained by `CONFIG_CMA_ALIGNMENT` and `CMA_MIN_ALIGNMENT_BYTES`. Command-line `cma=` intentionally overrides device-tree default CMA. Single-page allocations bypass generic CMA, which is intentional but can surprise tests expecting all DMA pages from CMA.

## Test Signals
Test `cma=0`, fixed and ranged `cma=size@base-limit`, default Kconfig sizing modes, per-NUMA and node-specific CMA parameters, DT reusable shared pools, invalid alignment rejection, device-specific allocation, fallback order, and free fallback to buddy pages.
