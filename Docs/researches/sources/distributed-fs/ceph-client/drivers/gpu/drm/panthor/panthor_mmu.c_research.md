# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_mmu.c

## Purpose
Implements Panthor GPU virtual memory and MMU address-space management. It owns per-file VM pools, `struct panthor_vm`, GPUVA mapping state, io-pgtable page-table operations, AS slot assignment/recycling, MMU fault handling, VM_BIND job scheduling, and debugfs GPUVA inspection.

## Important APIs, Types, and Functions
Key internal types are `panthor_mmu`, `panthor_as_slot`, `panthor_vm_pool`, `panthor_vm`, `panthor_vma`, `panthor_vm_op_ctx`, and `panthor_vm_bind_job`. Exported entry points include `panthor_mmu_init()`, `panthor_mmu_unplug()`, suspend/reset hooks, VM pool helpers, `panthor_vm_create()`, `panthor_vm_map_bo_range()`, `panthor_vm_unmap_range()`, `panthor_vm_bind_job_create()`, reservation helpers, and `panthor_vm_get_bo_for_va()`. Page-table allocation is centralized through `alloc_pt()`/`free_pt()` and the global `pt_cache`.

## Control Flow
Initialization allocates `panthor_mmu`, initializes AS and VM lists, requests the named `mmu` IRQ, creates the VM_BIND workqueue, and clamps VA bits on 32-bit kernels. VM creation validates user/kernel VA split, initializes `drm_mm`, allocates ARM LPAE S1 `io_pgtable_ops`, sets MAIR-derived Mali memory attributes, starts a one-job VM_BIND scheduler, and registers the VM with `drm_gpuvm`. VM activation assigns AS0 to MCU VMs and nonzero AS slots to user VMs, evicting LRU idle VMs when needed, then programs `AS_TRANSTAB`, `AS_MEMATTR`, and `AS_TRANSCFG`. Mapping/unmapping preallocates all VMAs, page-table pages, GEM pins, sg tables, and `drm_gpuvm_bo` objects, locks the affected MMU region, runs drm_gpuvm state-machine callbacks, updates io-pgtable mappings, flushes/unlocks the region, and cleans deferred objects. MMU IRQ handling decodes page faults, disables the affected AS, marks the VM faulted, and tells the scheduler to terminate/fault relevant work.

## State and Persistence
Persistent runtime state lives in `ptdev->mmu`, AS masks, AS slot VM pointers, VM list, VM schedulers, `drm_gpuvm` VA tree, `drm_mm` kernel VA allocator, heap pool pointer, active AS refcount, `destroyed`, `unusable`, `unhandled_fault`, and locked region fields. BO mappings persist as `panthor_vma` objects linked to `drm_gpuvm_bo`. AS bindings persist across idle until recycled, but reset/suspend/unplug clear hardware state and release slots.

## Dependencies and Integration Points
Depends on DRM GPUVM, DRM scheduler, drm_exec/dma_resv, GEM shmem, ARM io-pgtable, platform IRQs, runtime PM, Panthor GEM/heap/GPU/scheduler/device helpers, and register definitions from `panthor_regs.h`. It integrates with scheduler fault paths through `panthor_sched_report_mmu_fault()` and `panthor_sched_prepare_for_vm_destruction()`, with kernel BO/heap code through kernel auto-VA allocation, and with debugfs through `DRM_DEBUGFS_GPUVA_INFO`.

## Risks and Edge Cases
The main risk surface is consistency between drm_gpuvm metadata and io-pgtable state; failures in async VM_BIND intentionally mark VMs unusable. Huge-page partial unmaps require widening locked regions and remapping preserved ranges. AS command timeouts schedule GPU resets. Imported/exclusive BO handling, deferred cleanup outside dma-signaling paths, and LRU AS recycling are concurrency-sensitive. Fault handling is terminal rather than recoverable, so userspace must recreate affected VM/device state.

## Test Signals
Useful signals are VM create/destroy/map/unmap ioctl coverage, overlapping map/remap/unmap cases, huge-page partial unmaps, imported and exclusive BO mapping attempts, AS slot pressure above hardware slots, reset/suspend/resume with active VMs, MMU fault injection, debugfs GPUVA output, dma_resv fence sequencing for VM_BIND, and leak checking of page-table cache/GEM pins.
