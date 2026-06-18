# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c

## Purpose

This is the central AMDGPU GPUVM implementation. It manages per-process GPU virtual address spaces, VMID/PASID integration, BO-to-VA mappings, page-table update orchestration, TLB flush sequencing, VM memory accounting, page-fault handling, and VM lifecycle. It is the coordination layer between user mappings, TTM BO movement, SDMA/CPU page table writers, hardware VM flush packets, KFD/SVM, and debugfs/sysfs-visible state.

## Important APIs, types, and functions

The file defines interval-tree operations for `struct amdgpu_bo_va_mapping` and internal helpers for PRT callbacks and TLB sequence callbacks. Important exported APIs include `amdgpu_vm_init()`, `amdgpu_vm_make_compute()`, `amdgpu_vm_fini()`, `amdgpu_vm_manager_init()`, `amdgpu_vm_manager_fini()`, `amdgpu_vm_validate()`, `amdgpu_vm_ready()`, `amdgpu_vm_update_pdes()`, `amdgpu_vm_update_range()`, `amdgpu_vm_bo_update()`, `amdgpu_vm_clear_freed()`, `amdgpu_vm_handle_moved()`, `amdgpu_vm_flush_compute_tlb()`, `amdgpu_vm_bo_add()`, `amdgpu_vm_bo_map()`, `amdgpu_vm_bo_replace_map()`, `amdgpu_vm_bo_unmap()`, `amdgpu_vm_bo_clear_mappings()`, `amdgpu_vm_bo_del()`, `amdgpu_vm_bo_invalidate()`, `amdgpu_vm_bo_move()`, `amdgpu_vm_adjust_size()`, `amdgpu_vm_ioctl()`, `amdgpu_vm_handle_fault()`, `amdgpu_vm_update_fault_cache()`, and `amdgpu_sdma_set_vm_pte_scheds()`.

## Control flow, state, and persistence behavior

VM state is organized around explicit lists protected by `vm->status_lock`. Kernel/PT and per-VM BOs flow through `evicted -> relocated/moved -> idle`; user BOs with independent reservation objects flow through `evicted_user` or `invalidated -> done`; freed mappings wait in `vm->freed` until page tables are cleared. `amdgpu_vm_validate()` validates evicted objects, maps page tables for update, and moves them into relocated or moved states. `amdgpu_vm_update_pdes()` consumes relocated page-directory/page-table objects and updates their parent PDEs. `amdgpu_vm_clear_freed()` clears removed ranges, while `amdgpu_vm_handle_moved()` refreshes moved or invalidated mappings and may clear mappings when a BO cannot be reserved.

`amdgpu_vm_update_range()` is the core update orchestration path. It enters the DRM device, allocates a TLB callback object, chooses whether a flush is required, locks VM eviction, waits/fences unlocked updates as needed, prepares the selected update backend, walks resource or DMA-address ranges with `amdgpu_res_cursor`, calls `amdgpu_vm_ptes_update()`, commits, updates TLB sequence state, optionally creates a TLB fence for KFD/user queues, frees child page tables queued for post-flush release, and unlocks eviction. CPU and SDMA behavior is abstracted through `vm->update_funcs`.

Mapping APIs validate page alignment, overflow, BO bounds, and max PFN, then insert mappings into the VM interval tree and invalid list. Replacement first clears overlapping mappings and creates split before/after mappings as needed. Unmap removes a mapping from valid or invalid lists; valid mappings are put on `vm->freed` so page tables can be cleared later. PRT mappings increment a global PRT user counter and decrement through fence callbacks after unmap completion.

VM init creates scheduler entities, selects CPU or SDMA update mode, allocates and clears the root page directory, creates task info, and stores nonzero PASIDs in an XArray. Compute conversion can switch update backends, map all page tables for CPU access, reset `last_update`, and force TLB fences. Fini unregisters KFD VM state, removes PASID mapping, waits for unlocked and TLB flush fences, clears freed mappings, frees page tables, destroys entities, releases VMIDs, checks memory stats, and drops task info. Persistent effects are runtime kernel objects and hardware page-table/TLB state only.

## Dependencies and integration points

This file integrates with DRM exec and GEM, TTM resources and reservation locks, DMA fences, GPU scheduler entities, AMDGPU BO/TTM/GMC/ring/VMID/KFD/SVM/XGMI/dma-buf layers, KFD compute page fault restore, and debugfs. It emits hardware VM flush, PASID mapping, GDS switch, SPM update, cleaner shader, pipeline sync, and fence packets through ring callbacks. VM manager state includes VMID managers, PRT counters, PASID XArray, PTE scheduler list, and global fault cache.

## Risks and test signals

Risks are high because this code coordinates locking, eviction, asynchronous fences, page table freeing, and fault handling. Specific hazards include reservation-lock ordering, freeing page tables before required TLB flushes, stale PASID-to-VM lookups, interval-tree split errors, memory accounting drift, incorrect CPU/SDMA update mode switching, page fault recursion with SVM restore, missing TLB sequence increments, and incorrect behavior during GPU reset or device unplug. Test signals include GPUVM mmap/map/unmap tests, KFD/SVM page-fault recovery, compute and graphics submissions after BO eviction/migration, suspend/resume and GPU reset, imported dma-buf/XGMI mappings, debugfs VM BO list sanity, zero VM stats at fini, and tracepoints showing expected PTE/PDE and TLB activity.
