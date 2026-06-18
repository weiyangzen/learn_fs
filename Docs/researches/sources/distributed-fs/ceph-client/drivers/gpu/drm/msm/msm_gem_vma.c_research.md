# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_vma.c

## Purpose
Implements MSM GPU virtual address management on top of DRM GPUVM. It supports both kernel-managed address spaces and userspace-managed VM_BIND address spaces, translates bind/unbind ioctls into GPUVM state-machine operations, schedules asynchronous page-table updates, logs VM operations for crash diagnosis, and marks contexts unusable after unrecoverable mapping failures.

## Important APIs, Types, and Functions
- `struct msm_vm_map_op`, `struct msm_vm_unmap_op`, and `struct msm_vm_op` describe physical MMU updates derived from higher-level GPUVM map/unmap operations.
- `struct msm_vm_bind_job` is a DRM scheduler job carrying parsed userspace bind ops, preallocated MMU page-table pages, queued MMU operations, pinned BO state, and a completion fence.
- `msm_gem_vm_create()` constructs `struct msm_gem_vm`, initializes DRM GPUVM and optional VM_BIND scheduler, sets up `drm_mm`, MMU lock, and optional operation log.
- `msm_gem_vm_close()` drains VM_BIND work and tears down remaining mappings on file close.
- `msm_gem_vma_new()`, `msm_gem_vma_map()`, `msm_gem_vma_unmap()`, and `msm_gem_vma_close()` manage individual GPU virtual areas.
- `msm_ioctl_vm_bind()` is the VM_BIND ioctl entry point.
- `vm_bind_job_lookup_ops()`, `vm_bind_prealloc_count()`, `vm_bind_job_lock_objects()`, `vm_bind_job_pin_objects()`, and `vm_bind_job_prepare()` are the staged validation/preparation pipeline.
- DRM GPUVM callbacks `msm_gem_vm_sm_step_map()`, `msm_gem_vm_sm_step_remap()`, and `msm_gem_vm_sm_step_unmap()` translate GPUVM state-machine results into actual `msm_vm_op` lists.
- `msm_vma_job_run()` executes queued map/unmap operations under `vm->mmu_lock`.

## Control Flow
For kernel-managed VMs, callers allocate VMAs through `msm_gem_vma_new()` and perform synchronous map/unmap through `msm_gem_vma_map()` and `msm_gem_vma_unmap()`. For userspace-managed VM_BIND, `msm_ioctl_vm_bind()` validates context and queue type, handles sync-file and syncobj dependencies, copies one or many bind ops, checks alignment/range/flags/PRR support, bulk-resolves GEM handles, estimates page-table preallocation, locks the VM and affected objects, pins pages and LRU state, preallocates page-table memory, then invokes the DRM GPUVM state machine. The state machine may generate unmaps, maps, remaps, and in-place flag updates. The job is armed, exposed through an optional sync-file and syncobjs, and pushed to the VM_BIND scheduler. `msm_vma_job_run()` applies queued unmaps even after a map failure but stops further maps; any failure makes the VM unusable.

## State and Persistence
`struct msm_gem_vm` stores the backing `msm_mmu`, DRM GPUVM, managed/unmanaged mode, `drm_mm` allocator, VM_BIND scheduler, `last_fence`, fault and unusable counters/state, optional pid, operation log, preallocation throttle state, and MMU lock. VMA state includes `mapped`, DRM GPUVA metadata, optional `drm_mm` node, and flags such as `MSM_VMA_DUMP`. VM_BIND jobs hold GEM object refs and queued op refs until run/free. State is in-memory and tied to DRM file/context lifetime.

## Dependencies and Integration Points
Integrates with DRM GPUVM/GPUVA, DRM scheduler, drm_exec, dma-fence/sync-file/syncobj, MSM GEM page/pin helpers, `msm_mmu` map/unmap/preallocation hooks, Adreno PRR support for MAP_NULL, RD/crash dump VMA flags, and submit path VM validation. The submit path rejects unusable VMs and uses `vm->last_fence` for VM_BIND synchronization.

## Risks
The risky parts are partial VM updates, object/VM reservation lock ordering, preallocation accounting, sparse mapping behavior, and asynchronous unmap lifetime. The code holds GEM references for async unmaps, marks VMs unusable after undefined partial state, throttles preallocated page-table pages, uses single-page granules for VM_BIND page tables, and treats in-place remaps specially to avoid page-table churn while GPU work may be active.

## Test Signals
Test single and batched VM_BIND map/unmap/map-null operations, invalid alignment and ranges, MAP_NULL without PRR support, sparse tiny mappings, remaps splitting a VMA into prev/next regions, in-place flag-only remap, fence fd and syncobj behavior, close-time teardown, preallocation throttle wakeups, and crash/fault paths that set `unusable` and print VM logs.
