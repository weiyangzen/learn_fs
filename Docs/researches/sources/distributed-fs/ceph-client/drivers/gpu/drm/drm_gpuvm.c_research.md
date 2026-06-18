# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gpuvm.c

## Purpose

`drm_gpuvm.c` implements the DRM GPU virtual-address manager. It gives render drivers a common in-kernel model for a GPU VM address space, backed by interval-tree/rb-tree GPU VA nodes (`struct drm_gpuva`) and per-VM/per-GEM object association records (`struct drm_gpuvm_bo`). It also provides the split/merge algorithms used by VM_BIND-style APIs, helpers for dma-resv locking through `drm_exec`, evicted-object validation, fence propagation, and operation-list construction.

## Important APIs, Types, And Functions

The central types are `struct drm_gpuvm`, `struct drm_gpuva`, `struct drm_gpuvm_bo`, `struct drm_gpuva_op`, `struct drm_gpuva_ops`, `struct drm_gpuvm_map_req`, and `struct drm_gpuvm_ops`. Exported lifecycle and locking APIs include `drm_gpuvm_resv_object_alloc()`, `drm_gpuvm_init()`, `drm_gpuvm_put()`, `drm_gpuvm_prepare_vm()`, `drm_gpuvm_prepare_objects()`, `drm_gpuvm_prepare_range()`, `drm_gpuvm_exec_lock()`, `drm_gpuvm_exec_lock_array()`, `drm_gpuvm_exec_lock_range()`, `drm_gpuvm_validate()`, and `drm_gpuvm_resv_add_fence()`.

Object association APIs include `drm_gpuvm_bo_create()`, `drm_gpuvm_bo_put()`, `drm_gpuvm_bo_put_deferred()`, `drm_gpuvm_bo_deferred_cleanup()`, `drm_gpuvm_bo_find()`, `drm_gpuvm_bo_obtain_locked()`, `drm_gpuvm_bo_obtain_prealloc()`, `drm_gpuvm_bo_extobj_add()`, and `drm_gpuvm_bo_evict()`. GPUVA tree/list APIs include `drm_gpuva_insert()`, `drm_gpuva_remove()`, `drm_gpuva_link()`, `drm_gpuva_unlink()`, `drm_gpuva_unlink_defer()`, `drm_gpuva_find_first()`, `drm_gpuva_find()`, `drm_gpuva_find_prev()`, `drm_gpuva_find_next()`, `drm_gpuvm_interval_empty()`, `drm_gpuva_map()`, `drm_gpuva_remap()`, and `drm_gpuva_unmap()`. Split/merge APIs are `drm_gpuvm_sm_map()`, `drm_gpuvm_sm_unmap()`, `drm_gpuvm_sm_map_exec_lock()`, `drm_gpuvm_sm_unmap_exec_lock()`, `drm_gpuvm_sm_map_ops_create()`, `drm_gpuvm_madvise_ops_create()`, `drm_gpuvm_sm_unmap_ops_create()`, `drm_gpuvm_prefetch_ops_create()`, `drm_gpuvm_bo_unmap_ops_create()`, and `drm_gpuva_ops_free()`.

## Control Flow

`drm_gpuvm_init()` initializes the GPUVA rb-tree/list, external-object and evicted-object lists, deferred BO cleanup list, reference count, VM bounds, common reservation object, and optional kernel-reserved GPUVA node. `drm_gpuvm_put()` drops the VM kref; final release removes the reserved node, warns if mappings/lists are still populated, puts the reservation object, and calls the driver's `vm_free` callback.

Locking flows are built around `drm_exec`. `drm_gpuvm_exec_lock()` locks or prepares the VM reservation object first, then every external BO, then optional driver-provided extra objects inside a retry-on-contention loop. Range and array variants narrow or extend the object set. `drm_gpuvm_validate()` walks evicted VM BOs and delegates repair to `ops->vm_bo_validate`; if the VM is protected by its common reservation lock, it uses that lock rather than internal spinlocks.

BO flows preserve the unique tuple `(gpuvm, gem_object)`. Drivers either allocate with `drm_gpuvm_bo_create()` and install with `drm_gpuvm_bo_obtain_locked()`, or use `drm_gpuvm_bo_obtain_prealloc()` for immediate-mode paths that cannot allocate while holding the GEM GPUVA mutex. Mapping insertion validates address/range against the VM bounds and reserved kernel node, rejects overlap in `__drm_gpuva_insert()`, links into both interval tree and ordered list, and takes a VM reference. Link/unlink calls attach individual GPUVA mappings to the VM BO and maintain VM BO references.

The split/merge engine scans existing mappings intersecting a requested map or unmap range. `__drm_gpuvm_sm_map()` emits unmap, remap, and at most one final map callback depending on interval overlap, object equality, and GEM offset contiguity; the `keep` flag tells drivers when backing PTEs can be preserved for delta updates. `__drm_gpuvm_sm_unmap()` emits unmaps or split remaps for partially covered mappings. Operation-list creators reuse those callbacks with allocation-backed list nodes, while exec-lock variants reuse the algorithm with callbacks that only lock touched GEM objects.

## State And Persistence

State is in-memory DRM driver state: the GPUVA interval tree, ordered GPUVA list, optional kernel-reserved node, common reservation GEM object, per-GEM GPUVA lists, per-VM external and evicted object lists, BO deferred cleanup lockless list, krefs, and flags such as immediate/resv-protected mode. Nothing persists beyond the `drm_device`/driver VM lifetime; the source of truth is reconstructed by driver VM_BIND or VM initialization code. Fences are written into locked dma-resv objects through `drm_gpuvm_resv_add_fence()`.

## Dependencies And Integration Points

The file depends on DRM GEM, dma-resv, `drm_exec`, interval-tree helpers, Linux rb/list/llist/kref infrastructure, and driver-supplied `drm_gpuvm_ops`. It is consumed by GPU drivers implementing VM_BIND, sparse resources, page-table update batching, BO eviction/validation, and shared VM reservation objects. It integrates with GEM object's `gpuva` list/mutex and with driver alloc/free callbacks for custom VM BO or operation objects.

## Risks And Edge Cases

Range correctness is critical: overflow and reserved-kernel-node checks protect the VM tree, but callers must still update the GPUVM view after processing split/merge operations before requesting another dependent operation. Deferred cleanup is subtle because GEM GPUVA mutex lifetime and GEM object final put must not overlap incorrectly; `drm_gpuvm_bo_deferred_cleanup()` is required after deferred puts. Immediate-mode callers are warned away from allocating under the GEM GPUVA lock and must use preallocation. `drm_gpuva_find_prev(start)` computes `start - 1`, so invalid zero starts rely on range validation to fail. The operation-list path deep-copies remap substructures; allocation failures must unwind through `drm_gpuva_ops_free()`.

## Test Signals

Useful tests include VM init/fini leak warnings, reserved-range rejection, overlapping insert rejection, exact/partial map replacement, left/right/both-side split remaps, sparse/madvise operation generation, unmap of fully and partially covered ranges, prefetch op creation, BO unmap op creation, external-object locking under both resv-protected and spinlock modes, eviction validation, deferred VM BO cleanup, and fence addition to private versus external objects.
