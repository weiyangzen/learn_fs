
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dmem.c

## Purpose
Implements Nouveau's HMM device-private memory support for SVM-enabled GPUs. The file allocates GPU VRAM-backed `MEMORY_DEVICE_PRIVATE` pages, migrates CPU pages into VRAM, migrates them back on CPU faults or device teardown, and uses the GPU copy engine to move or clear page contents. It is enabled only for Pascal and newer devices with a supported DMA copy class.

## Important APIs, Types, and Functions
Key internal types are `struct nouveau_dmem`, `struct nouveau_dmem_chunk`, `struct nouveau_dmem_migrate`, and `struct nouveau_dmem_dma_info`. `nouveau_dmem_init()`, `nouveau_dmem_fini()`, `nouveau_dmem_suspend()`, and `nouveau_dmem_resume()` are the lifecycle hooks called from the DRM device lifecycle. `nouveau_dmem_migrate_vma()` is the SVM-facing entry for migrating a VMA range from system memory to GPU private memory. `nouveau_dmem_migrate_to_ram()` is registered through `dev_pagemap_ops` and is invoked by the mm subsystem when the CPU faults on a device-private page. `nouveau_dmem_page_addr()` converts a device-private `struct page` back to the VRAM offset inside its pinned BO.

The Pascal+ copy-engine implementation is in `nvc0b5_migrate_copy()` and `nvc0b5_migrate_clear()`, selected by `nouveau_dmem_migrate_init()` based on `drm->ttm.copy.oclass`.

## Control Flow
Initialization allocates `drm->dmem`, initializes locks and chunk lists, and binds migration callbacks to the existing TTM copy channel. GPU-private allocation is chunk based: `nouveau_dmem_page_alloc_locked()` first consumes a free page or THP-sized folio, otherwise calls `nouveau_dmem_chunk_alloc()`, which reserves a fake physical address range, allocates a pinned VRAM BO, registers device-private pages with `memremap_pages()`, and pushes all pages onto free lists.

System-to-device migration uses `migrate_vma_setup()`, allocates destination device pages, DMA-maps source pages when present, emits copy or clear commands into the copy channel, calls `migrate_vma_pages()`, waits on a Nouveau fence, maps resulting PFNs into the SVM page tables, unmaps DMA addresses, and finalizes migration. Device-to-system migration on fault allocates a CPU page or folio, invalidates the SVM range under `svmm->mutex`, copies VRAM to host memory, calls `migrate_vma_pages()`, waits for the copy fence, unmaps DMA, and finalizes.

## State and Persistence
State is in-memory only: chunk list, free page/folio lists, per-chunk allocation counts, pinned BOs, dev_pagemap ranges, and migration channel callbacks. Device-private pages store either free-list links or `svmm` pointers in `zone_device_data`. Suspend unpins chunks; resume re-pins them. Finalization evicts all device-private pages back to system memory before unmapping pages and freeing BOs.

## Dependencies and Integration Points
This file depends on Linux HMM/migration APIs, `memremap_pages()`, TTM BO allocation, DMA mapping, Nouveau fences, copy-channel push macros, and SVM PFN mapping helpers. It integrates with `nouveau_drm.c` lifecycle hooks and with SVM code through `nouveau_dmem_migrate_vma()` and `nouveau_pfns_map()`.

## Risks and Test Signals
Risk is high around lifetime and migration error handling. The source contains FIXME notes for TTM-based VRAM page allocation, missing chunk reclaim, and no explicit channel-idle wait when no fence exists. Fault paths have early returns after `migrate_vma_setup()` that bypass shared cleanup in some branches. Large folio handling, DMA map/unmap sizes, suspend pin failures, and teardown eviction need stress coverage. Test signals include SVM migration tests, CPU fault-back after GPU migration, transparent huge page migration, suspend/resume with active device-private mappings, module unload with migrated pages, copy-engine failure injection, and lockdep around `svmm->mutex`, dmem spinlock, and migration callbacks.
