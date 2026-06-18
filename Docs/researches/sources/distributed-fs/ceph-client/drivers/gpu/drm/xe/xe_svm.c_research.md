<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c

## Purpose

`xe_svm.c` implements Xe shared virtual memory over DRM GPU SVM and DRM pagemap. It handles CPU mmu-notifier invalidation, GPU page faults, VRAM migration, device-private page maps, TLB invalidation, and SVM range garbage collection.

## Important APIs, Types, and Functions

Lifecycle APIs are `xe_svm_init()`, `xe_svm_close()`, `xe_svm_fini()`, and `xe_svm_flush()`. Fault APIs include `xe_svm_handle_pagefault()`, `xe_svm_range_find_or_insert()`, `xe_svm_range_get_pages()`, `xe_svm_range_validate()`, `xe_svm_range_needs_migrate_to_vram()`, `xe_svm_alloc_vram()`, and `xe_svm_range_migrate_to_smem()`. Mapping helpers include `xe_svm_has_mapping()`, `xe_svm_unmap_address_range()`, `xe_svm_ranges_zap_ptes_in_range()`, `xe_vma_resolve_pagemap()`, and `xe_drm_pagemap_from_fd()`. Pagemap support creates `xe_pagemap`, implements device map/unmap, devmem population, migration copy callbacks, and pagemap cache/shrinker creation.

## Control Flow

In fault mode, init creates the garbage collector, acquires a pagemap owner peer, grabs local pagemaps for each VRAM tile, and initializes `drm_gpusvm` with range allocation/free/invalidate callbacks and 2M/64K/4K fault chunk sizes. MMU invalidation finds affected ranges, zaps PTEs per tile, records invalidated tile masks, submits TLB invalidation to all affected GTs, unmaps pages, and queues garbage collection for CPU unmaps. Page fault handling first drains garbage collection, resolves the target pagemap from VMA attributes and tile, finds or inserts a range, optionally migrates to VRAM, gets pages/DMA mappings, rebinds the range into the VM under validation exec, waits for the bind fence, and updates statistics. VRAM migration allocates DRM pagemap devmem pages, migrates CPU memory to device memory, and uses Xe migration queues to copy between SRAM and VRAM.

## State and Persistence Behavior

SVM state is embedded in `struct xe_vm`: a `drm_gpusvm`, notifier lock, garbage-collector list/work, peer owner, and per-tile pagemap references. Each `xe_svm_range` persists until removed and tracks tile-present and tile-invalidated masks. Device-private memory persists through `xe_pagemap` objects cached per VRAM region and reference-counted with DRM pagemap owners. Statistics accumulate in GT stats counters.

## Dependencies and Integration Points

This file integrates Linux MMU notifiers through DRM GPU SVM, DRM pagemap/devmem, PCI P2PDMA distance checks, Xe VM/VMA binding and validation, Xe PT zap/rebind, TLB invalidation batches, runtime PM, BO/TTM VRAM allocation, migration copy engines, page reclaim, and module SVM parameters.

## Risks and Test Signals

Risks include notifier-lock and VM-lock ordering, stale range masks if PTE zap succeeds but TLB invalidation fails, retry loops around VRAM migration and CPU VMA changes, deadlocks in reclaim paths, devmem lifetime/power references, P2P DMA mapping correctness, and unsupported 4K migration on 64K-only VRAM platforms. Tests should cover SVM init/close/fini, CPU unmap invalidation and garbage collection, valid fault fast path, CPU-to-VRAM and VRAM-to-CPU migration, devmem-only atomic faults, VMA autorestore/splitting, pagemap fd lookup, P2P mapping, and build behavior with `CONFIG_DRM_XE_PAGEMAP` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_svm.c -->
