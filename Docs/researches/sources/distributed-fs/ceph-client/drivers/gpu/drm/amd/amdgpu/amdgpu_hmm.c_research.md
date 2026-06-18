# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.c

## Purpose
`amdgpu_hmm.c` implements AMDGPU HMM/MMU interval notifier support for userptr BOs and KFD/HSA user memory. It blocks or evicts GPU users during CPU page-table invalidations and provides helpers to fault and validate CPU page ranges for GPU mappings.

## Important APIs, types, and functions
Key functions are `amdgpu_hmm_register()`, `amdgpu_hmm_unregister()`, `amdgpu_hmm_range_get_pages()`, `amdgpu_hmm_range_valid()`, `amdgpu_hmm_range_alloc()`, and `amdgpu_hmm_range_free()`. Internal invalidation callbacks are `amdgpu_hmm_invalidate_gfx()` and `amdgpu_hmm_invalidate_hsa()`, installed through `amdgpu_hmm_gfx_ops` or `amdgpu_hmm_hsa_ops`.

## Control flow
Registration chooses the HSA/KFD notifier path when `bo->kfd_bo` is present, otherwise the graphics path. Graphics invalidation refuses non-blockable ranges, locks `adev->notifier_lock`, records the notifier sequence, waits indefinitely for the BO reservation fences at bookkeeping usage, and unlocks. HSA invalidation delegates eviction to `amdgpu_amdkfd_evict_userptr()`. Range faulting allocates an HMM PFN array, fills `struct hmm_range`, faults the CPU pages in chunks no larger than `MAX_WALK_BYTE`, retries transient `-EBUSY` until a timeout, and restores the original PFN pointer before returning. Validation checks the saved notifier sequence with `mmu_interval_read_retry()`.

## State and persistence behavior
The notifier lives in `bo->notifier` and is tied to the current process `mm`. `amdgpu_hmm_range` holds a BO reference plus a transient PFN array and HMM range. All state is runtime and is removed on unregister/free.

## Dependencies and integration points
The file depends on Linux HMM and MMU interval notifier APIs, DMA reservation fences, AMDGPU BOs, KFD eviction hooks, DRM logging, and the device notifier lock. It integrates with userptr validation, VM update, KFD user queues, and command submission paths that need stable CPU page mappings.

## Risks and edge cases
Non-blockable invalidations return false and require the MMU notifier core to retry. Waiting with `MAX_SCHEDULE_TIMEOUT` can stall invalidation behind long GPU work. Large ranges are chunked, but PFN allocation still scales with total page count. `-EBUSY` maps to `-EAGAIN` after timeout. Callers must validate ranges after use and free PFN arrays to avoid stale mappings or leaks.

## Test signals
Userptr BO invalidation under GPU load, KFD userptr eviction, HMM range faulting for read-only and writable pages, large >2 GiB walks, notifier sequence invalidation races, `CONFIG_HMM_MIRROR` disabled builds, OOM paths, and page-table churn during command submission are relevant tests.
