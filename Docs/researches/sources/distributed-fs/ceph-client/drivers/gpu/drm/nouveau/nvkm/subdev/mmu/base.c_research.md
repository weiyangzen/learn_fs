# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/base.c

## Purpose
Implements common MMU subdevice construction, memory-type enumeration, global VMM creation, and page-table allocation caching/suballocation.

## Important APIs, Types, and Functions
Important symbols are `nvkm_mmu_ctor`, `nvkm_mmu_new_`, `nvkm_mmu_ptc_get`, `nvkm_mmu_ptc_put`, `nvkm_mmu_ptc_dump`, `nvkm_mmu_oneinit`, `nvkm_mmu_init`, and helpers for host/VRAM heap/type enumeration. Internal `nvkm_mmu_ptc` caches whole page tables; `nvkm_mmu_ptp` suballocates small page tables from a parent allocation.

## Control Flow, State, and Persistence
PT allocation first handles sub-page-table requests when alignment is below 4 KiB, otherwise reuses cached tables by size or allocates `NVKM_MEM_TARGET_INST` memory. Put either returns tables to a small cache or frees them, and recursively destroys empty PTP parents. Oneinit builds `mmu->heap[]` and `mmu->type[]` from FB VRAM heaps, BAR mapping properties, coherency, and kind support, then optionally creates a global GART VMM.

## Dependencies and Integration Points
Depends on instmem memory allocation, BAR, FB RAM heaps, `nvkm_vmm_new`, public NVIF MMU classes, and user MMU object construction.

## Risks and Test Signals
Risks include PT cache leaks, suballocation mask overflow, stale non-zero PTE reuse, incorrect memory type ordering, and BAR/coherency misclassification. Test VMM creation/destruction stress, raw/managed VMMs, VRAM absent systems, BAR1 uncached systems, suspend teardown, and page-table cache debug dumps.
