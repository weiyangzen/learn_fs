# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.h

## Purpose
Declares the public MMU/VM interface used by the Panthor driver. It hides VM internals while exposing lifecycle, mapping, scheduling, reservation, heap, fdinfo, debugfs, and page-table-cache operations.

## Important APIs, Types, and Functions
Forward declarations include `panthor_vm`, `panthor_vma`, `panthor_mmu`, `panthor_gem_object`, and `panthor_heap_pool`. Major exported groups are MMU lifecycle (`panthor_mmu_init()`, reset/suspend/resume/unplug), VM map/query/activity (`panthor_vm_map_bo_range()`, `panthor_vm_unmap_range()`, `panthor_vm_get_bo_for_va()`, `panthor_vm_active()`, `panthor_vm_idle()`), VM pool management, VM_BIND job helpers, dma_resv update helpers, and `panthor_mmu_pt_cache_init()/fini()`.

## Control Flow
Callers initialize the MMU subsystem during device bring-up, create per-file VM pools on file open, create VMs from ioctl paths, use VM_BIND helpers to build scheduler jobs or execute synchronous operations, and tear pools down on file close. Scheduler code activates and idles VMs around group execution, while GEM/kernel BO paths use kernel auto-VA helpers.

## State and Persistence
The header itself stores no state but defines ownership boundaries. `panthor_vm_get()`/`put()` indicate refcounted VM lifetime; VM pools own file handles; VM_BIND jobs own a scheduler job reference; dma_resv helper APIs persist synchronization fences on VM/private and external BO reservations.

## Dependencies and Integration Points
Includes `linux/dma-resv.h` and depends on DRM scheduler, drm_exec, drm_file, Panthor file/device/GEM types, and userspace UAPI structs such as `drm_panthor_vm_create` and `drm_panthor_vm_bind_op`.

## Risks and Edge Cases
The API exposes both sync and async VM_BIND paths, so callers must prepare reservations and reference lifetimes correctly. `PANTHOR_VM_KERNEL_AUTO_VA` is a sentinel magic address and must not be confused with a valid user VA. Activity APIs expose hardware AS state, so scheduler usage must be balanced.

## Test Signals
Header/API compatibility is exercised by compiling all Panthor modules, ioctl tests for VM lifecycle and VM_BIND, scheduler group/job tests that call VM activation, and fdinfo/debugfs builds with relevant config options.
