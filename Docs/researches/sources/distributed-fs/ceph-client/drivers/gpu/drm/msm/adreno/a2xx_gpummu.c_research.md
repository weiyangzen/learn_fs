# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/a2xx_gpummu.c

## Purpose
`a2xx_gpummu.c` implements the legacy A2xx GPU MMU backend used when creating an A2xx `drm_gpuvm`. It allocates a contiguous page table, maps DRM GEM scatterlists into the GPU's 4 KiB page table format, invalidates the A2xx MMU after changes, and reports page table and translation-error addresses to hardware init.

## Important APIs, Types, And Functions
The private type is `struct a2xx_gpummu`, embedding `struct msm_mmu` and storing `gpu`, `pt_base`, and the CPU pointer to the table. Public functions are `a2xx_gpummu_new` and `a2xx_gpummu_params`. The `msm_mmu_funcs` implementation supplies `a2xx_gpummu_map`, `a2xx_gpummu_unmap`, `a2xx_gpummu_detach`, and `a2xx_gpummu_destroy`.

## Control Flow
`a2xx_gpummu_new` allocates the wrapper, then allocates `TABLE_SIZE + 32` bytes of force-contiguous DMA memory for the page table plus translation-error area, initializes `msm_mmu` with type `MSM_MMU_GPUMMU`, and returns the base object. Map computes the table index from `(iova - GPUMMU_VA_START) / 4 KiB`, derives read/write protection bits from IOMMU flags, iterates DMA pages in the scatter-gather table, writes one table entry per 4 KiB page, then invalidates all MMU and texture-cache translations. Unmap clears entries over the supplied length and performs the same invalidation. Destroy frees the contiguous DMA allocation and wrapper.

## State And Persistence
Persistent MMU state is the DMA-coherent page table and its bus address. `GPUMMU_VA_START` is 16 MiB and the range is `0xfff * 64 KiB`, matching `a2xx_create_vm`. The translation-error pointer returned by `a2xx_gpummu_params` is immediately after the table and is expected to be 32-byte aligned.

## Dependencies And Integration Points
This file depends on Linux DMA mapping, MSM MMU abstractions, `msm_drv`, `adreno_gpu`, `a2xx_gpu`, and A2xx MMU invalidation register definitions. `a2xx_gpu.c` calls `a2xx_gpummu_params` during hardware initialization and uses `a2xx_gpummu_new` when creating the GPU VM.

## Risks
Map/unmap assume page-aligned 4 KiB iteration and warn, but do not recover, if `off != 0`. Bounds are trusted from the upper VM layer, so an invalid IOVA could index outside the allocated table. The table uses simple read/write bits with no richer caching attributes. Every map/unmap flushes immediately, which is safe but can be costly under many small mappings.

## Test Signals
Signals include successful DMA allocation on probe, valid `MH_MMU_PT_BASE`/`TRAN_ERROR` programming, command buffers executing from mapped IOVAs, MMU page faults for unmapped addresses, no out-of-range table warnings from VM tests, and clean DMA free on GPU teardown.
