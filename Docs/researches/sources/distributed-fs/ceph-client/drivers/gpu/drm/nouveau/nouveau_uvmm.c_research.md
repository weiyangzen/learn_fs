# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_uvmm.c

## Purpose
This file implements Nouveau's user-mode GPU virtual memory manager built on DRM GPUVM. It creates raw NVIF VMMs, tracks sparse regions, translates VM_BIND ioctls into scheduled map/unmap jobs, coordinates BO reservation fences, and remaps all GPUVAs during BO moves.

## Important APIs, Types, and Functions
External entry points are `nouveau_uvmm_ioctl_vm_init`, `nouveau_uvmm_ioctl_vm_bind`, `nouveau_uvmm_fini`, `nouveau_uvmm_bo_map_all`, and `nouveau_uvmm_bo_unmap_all`. Important internal types are `struct bind_job_op`, `enum vm_bind_op`, `struct nouveau_uvma`, `struct nouveau_uvma_region`, and `struct nouveau_uvmm_bind_job`. Core helpers manage raw VMM get/put/map/unmap/sparse refs, region maple-tree entries, GPUVA split/merge preparation, bind job submit/run/cleanup, and BO validation.

## Control Flow
VM init validates the kernel-managed range, allocates a `nouveau_uvmm`, creates a GPUVM reservation object, initializes a maple tree protected by the UVMM mutex, initializes DRM GPUVM, creates a raw NVIF VMM excluding the kernel-managed range, and stores it on the client. VM bind copies user operations and sync arrays, creates a `nouveau_job`, and submits it through `nouveau_sched`. Bind submit looks up GEM objects, obtains GPUVM BO wrappers, validates ranges and sparse region overlap, then under the UVMM lock creates DRM GPUVA ops, preallocates UVMA objects, reserves VMM page tables, validates BOs through `drm_exec`, links/unlinks GPUVAs under dma_resv locks, and arms fences. Scheduler run performs the actual NVIF VMM map/unmap calls. Cleanup frees GPUVA ops, drops BO/GEM references, releases sparse regions, signals completions, and marks the job done.

## State and Persistence Behavior
Persistent state includes `cli->uvmm.ptr`, DRM GPUVM VA interval state, NVIF raw VMM state, sparse regions in `region_mt`, per-UVMA page shift/kind/region links, GPUVM BO links under GEM reservations, and scheduled bind jobs with completion/kref lifetime. BO move callbacks invalidate GPUVAs and later remap them with the new `nouveau_mem`.

## Dependencies and Integration Points
It depends on DRM GPUVM, DRM exec, GEM reservation objects, Nouveau BO validation, `nouveau_sched`, `nouveau_job`, NVIF VMM raw methods, NVIF memory objects, and userspace `DRM_NOUVEAU_VM_BIND`/`VM_INIT` ioctls.

## Risks
Atomicity depends on holding the UVMM mutex until all failure paths are gone. Sparse region dirty/completion tracking prevents page-table operations from racing, but mistakes can deadlock or return wrong `-ENOENT`/`-ENOSPC`. Page-shift downgrade logic must match BO placement and VMM page capabilities. Cleanup must handle partially initialized `op->ops`, `op->reg`, `op->vm_bo`, and GEM references.

## Test Signals
Signals include VM init bounds tests, map/unmap/remap operations, sparse map/unmap conflict cases, async syncobj fences, BO eviction and remap callbacks, invalid user handles/ranges, concurrent binds, scheduler failure injection, and client teardown with live mappings.
