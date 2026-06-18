# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mmu.h

## Purpose
Defines the MSM MMU abstraction used by GPU and display VM code. It provides a common function table for attaching, mapping, unmapping, destroying, fault handling, and VM_BIND page-table preallocation across GPUMMU, base IOMMU, and IOMMU page-table backends.

## Important APIs, Types, and Functions
- `struct msm_mmu_funcs` declares `detach`, `prealloc_count`, `prealloc_allocate`, `prealloc_cleanup`, `map`, `unmap`, `destroy`, and `set_stall`.
- `enum msm_mmu_type` distinguishes `MSM_MMU_GPUMMU`, `MSM_MMU_IOMMU`, and `MSM_MMU_IOMMU_PAGETABLE`.
- `struct msm_mmu_prealloc` tracks page-table pages reserved for async VM updates.
- `struct msm_mmu` stores funcs, device, optional fault handler callback and arg, type, and currently active prealloc pointer.
- `msm_mmu_init()` initializes the base fields.
- Factory/diagnostic declarations include `msm_iommu_new()`, `msm_iommu_gpu_new()`, `msm_iommu_disp_new()`, `msm_iommu_pagetable_create()`, `msm_iommu_pagetable_params()`, `msm_iommu_pagetable_walk()`, and `msm_iommu_get_geometry()`.

## Control Flow
This header defines dispatch contracts. Callers create an `msm_mmu`, then call `mmu->funcs->map()` and `unmap()` from VMA/VM_BIND paths. VM_BIND jobs set `mmu->prealloc` while running so the IOMMU page-table allocator can consume preallocated pages. Fault producers call the configured handler through backend code.

## State and Persistence
State is in-memory and backend-owned. The `prealloc` pointer is transient, protected by `msm_gem_vm::mmu_lock` according to comments. Fault handler pointers persist for the MMU lifetime.

## Dependencies and Integration Points
Consumed by `msm_iommu.c`, `msm_gem_vma.c`, `msm_gpu.c`, and `msm_kms.c`. Depends on Linux IOMMU and SG table types. It links KMS/GPU VM creation to the common VMA map/unmap code.

## Risks
Any backend must implement map/unmap semantics compatible with GEM VMA callers, especially partial failure behavior and preallocation cleanup. The transient `prealloc` pointer requires strict locking. Optional funcs need callers to guard feature availability.

## Test Signals
Compile all MMU backends, exercise GPU and display mapping, fault callbacks, VM_BIND preallocation paths, page-table diagnostic calls, and cleanup/detach flows.
