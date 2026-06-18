
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_preempt_mgr.c

## Purpose
Implements the AMDGPU TTM resource manager for preemptible memory. This manager does not allocate real address ranges; it accounts preemptible BO usage and exposes current usage through sysfs.

## Important APIs, Types, and Functions
`mem_info_preempt_used_show` backs the read-only `mem_info_preempt_used` device attribute. `amdgpu_preempt_mgr_new` allocates a generic `ttm_resource`, initializes it, and sets `start` to `AMDGPU_BO_INVALID_OFFSET`. `amdgpu_preempt_mgr_del` finalizes and frees the resource. Public lifecycle functions are `amdgpu_preempt_mgr_init` and `amdgpu_preempt_mgr_fini`.

## Control Flow
Init sets `man->use_tt`, installs the resource manager function table, initializes the manager with a nominal 1 GiB size, creates the sysfs file, registers it as `AMDGPU_PL_PREEMPT`, and marks it used. Allocation simply accounts a resource; no DRM MM range is assigned. Finalization marks the manager unused, evicts all resources, removes sysfs if available, cleans up, and unregisters the manager.

## State and Persistence Behavior
Runtime usage is tracked by the TTM resource manager and reported via `ttm_resource_manager_usage`. Each resource has an invalid GPU start because preemptible memory is not represented by a stable GPU physical address in this manager.

## Dependencies and Integration Points
Depends on AMDGPU memory manager state, TTM resource manager APIs, sysfs device attributes, and the `AMDGPU_PL_PREEMPT` placement selected by BO placement code for preemptible GTT-like allocations.

## Risks and Test Signals
Risks include treating preemptible resources as addressable memory, failing finalization while resources are still live, or exposing stale sysfs after device removal. Test with preemptible BO creation/destruction, sysfs `mem_info_preempt_used`, eviction paths, driver unload, and BO placement that sets `AMDGPU_GEM_CREATE_PREEMPTIBLE`.
