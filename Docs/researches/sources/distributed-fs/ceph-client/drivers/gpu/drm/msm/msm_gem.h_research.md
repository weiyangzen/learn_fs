# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem.h

## Purpose
Defines MSM GEM, GPU VM, VMA, and submit data structures plus helper APIs used by GEM memory management, VM_BIND, KMS scanout, PRIME, and submit paths.

## Important APIs, types, and functions
- Internal BO flags `MSM_BO_STOLEN` and `MSM_BO_MAP_PRIV`.
- `struct msm_gem_vm` wraps `drm_gpuvm` with scheduler, preallocation throttle, kernel-managed `drm_mm`, MMU, PID, last fence, VM update log, fault count, managed/unusable flags.
- `struct msm_gem_vma` wraps `drm_gpuva` with optional `drm_mm_node` and mapped flag.
- `struct msm_gem_object` extends `drm_gem_object` with flags, madv, vmap count, backing pages/sgt/vaddr, name, metadata, pin count, and VMA refcount.
- `struct msm_gem_submit` tracks scheduler job, refs, VM, exec lock context, fences, submit queue, command buffers, BOs, ring, and flags.
- Inline locks and helpers wrap dma-resv, `drm_exec`, and purgeability checks.

## Control flow
Most content is declarative. `msm_gem_lock_vm_and_obj()` uses `drm_exec` to lock a VM reservation object and a BO reservation object with contention retry. `msm_gem_assert_locked()` allows the free path to look locked when refcount is zero to avoid lockdep false positives. Purgeability helpers classify objects based on import status, pin count, vmap count, and madv.

## State and persistence
This header defines the state carried by GEM objects, VMs, VMAs, and submits throughout object, VM, and job lifetimes. The VM log persists recent VM updates for devcore dumps.

## Dependencies and integration points
Depends on DRM GPUVM, DRM scheduler, DRM exec, dma-resv, MSM MMU, and `msm_drv.h`. Used by GEM, submit, VM_BIND, GPU, KMS, debugfs, and PRIME files.

## Risks
Struct layout and locking helpers are central to driver correctness. VM_BIND permits multiple VMAs per BO per VM, unlike older lookup paths that assume one VMA; callers must use the right API. `vma_ref` intentionally holds lazy KMS VMAs and must be balanced by exports/handles.

## Test signals
Compile coverage plus VM_BIND mapping/unmapping, legacy GEM_INFO IOVA behavior, submit teardown, shrinker classification, and lockdep validation of `msm_gem_lock_vm_and_obj()`.
