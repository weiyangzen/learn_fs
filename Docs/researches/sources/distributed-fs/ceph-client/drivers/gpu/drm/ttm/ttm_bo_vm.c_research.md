# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_vm.c

Purpose: VM fault, mmap, and CPU access helpers for memory mapped TTM BOs. It maps either IO memory PFNs or TT backing pages into user VMAs while avoiding reservation/mmap lock inversions.

Important APIs and functions: exports `ttm_bo_vm_reserve()`, `ttm_bo_vm_fault_reserved()`, `ttm_bo_vm_dummy_page()`, `ttm_bo_vm_fault()`, `ttm_bo_vm_open()`, `ttm_bo_vm_close()`, `ttm_bo_access()`, `ttm_bo_vm_access()`, and `ttm_bo_mmap_obj()`. Internal helpers handle idle waits and PFN calculation.

Control flow: `ttm_bo_vm_fault()` reserves the BO with retry-aware logic, enters the DRM device, faults real pages through `ttm_bo_vm_fault_reserved()`, or maps a dummy zero page if the DRM device is unplugged. The reserved fault path waits for pipelined moves, reserves IO memory, computes VMA-relative BO page offset, applies caching protection, populates TT pages for non-IO resources, decrypts IO mappings, and prefaults up to `TTM_BO_VM_NUM_PREFAULT` pages with `vmf_insert_pfn_prot()`. `ttm_bo_vm_reserve()` drops `mmap_lock` when fault retry allows it and rejects non-mappable external TT pages. Access helpers reserve the BO and either kmap system/TT memory or call a driver `access_memory` hook.

State and dependencies: uses VMA `vm_private_data`, GEM references, `bo->resource->bus`, `bo->ttm`, reservation fences, VMA node offsets, and device unplug state. It depends on DRM managed actions, GEM object refcounting, VM flags, and TTM mapping helpers.

Risks and test signals: lock ordering around mmap fault retry is critical. Dummy-page lifetime is tied to `drmm_add_action_or_reset()`. Imported non-mappable pages return SIGBUS. This subset has no direct VM KUnit file, so regressions are mostly integration-tested by drivers.
