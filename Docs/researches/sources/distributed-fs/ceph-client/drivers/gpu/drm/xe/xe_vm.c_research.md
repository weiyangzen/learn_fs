# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.c

## Purpose

`xe_vm.c` is the main implementation of Xe virtual memory objects, GPU virtual address areas, VM bind ioctls, rebind handling, page-table encoding, VM fault reporting, memory-attribute helper VMAs, and VM snapshot capture. It is the central integration point between the DRM `drm_gpuvm` range manager, Xe page-table update machinery, TTM buffer validation, userptr/SVM invalidation, long-running compute execution, and user-visible VM uAPIs.

## Important APIs, Types, and Functions

The public entry points are `xe_vm_create()`, `xe_vm_lookup()`, `xe_vm_close_and_put()`, `xe_vm_create_ioctl()`, `xe_vm_destroy_ioctl()`, `xe_vm_bind_ioctl()`, `xe_vm_query_vmas_attrs_ioctl()`, `xe_vm_get_property_ioctl()`, `xe_vm_bind_kernel_bo()`, `xe_vm_lock()`, `xe_vm_unlock()`, `xe_vm_invalidate_vma_submit()`, `xe_vm_invalidate_vma()`, `xe_vm_validate_protected()`, the rebind helpers `xe_vm_rebind()`, `xe_vma_rebind()`, `xe_vm_range_rebind()`, `xe_vm_range_unbind()`, and the auxiliary allocators `xe_vm_alloc_madvise_vma()` and `xe_vm_alloc_cpu_addr_mirror_vma()`. It also exposes compute-mode queue participation through `xe_vm_add_compute_exec_queue()`, `xe_vm_remove_compute_exec_queue()`, `xe_vm_add_exec_queue()`, and `xe_vm_remove_exec_queue()`.

The internal operation model is `struct xe_vma_ops` plus `struct xe_vma_op` from `xe_vm_types.h`. `vm_bind_ioctl_ops_create()` converts user bind arguments into `drm_gpuva_ops`; `vm_bind_ioctl_ops_parse()` allocates or splits `struct xe_vma` objects, counts page-table updates per tile, and commits GPUVA tree changes; `vm_bind_ioctl_ops_execute()` locks and validates resources with `drm_exec`, runs page-table update jobs, attaches user fences, and handles unwind. `ops_execute()` is the common tile loop that prepares update operations, submits `xe_pt_update_ops_run()`, collects TLB invalidation fences, and returns a composite `dma_fence_array`.

Page table encoding is supplied through `xelp_pt_ops`, with `xelp_pde_encode_bo()`, `xelp_pte_encode_bo()`, `xelp_pte_encode_vma()`, and `xelp_pte_encode_addr()`. These encode PAT bits, page-size bits, DM bits for VRAM/stolen device memory, read-only state, and scratch/null PTE handling.

## Control Flow and State

VM creation initializes `vm->lock`, `snap_mutex`, GPUVA state, SVM state, range-fence trees, bind queues, optional preempt rebind work, root page tables, optional scratch page tables, and an ASID for user VMs on devices that support USM. For non-migration VMs it creates per-tile VM bind exec queues. Destruction is split between `xe_vm_close_and_put()`, which closes the address space, clears page tables and TLBs, kills bind queues, removes VMAs, tears down SVM and ASID state, and drops the final GPUVM reference, and `vm_destroy_work_func()`, which runs asynchronously because the final put may happen from fence signaling context.

The bind ioctl validates flags, alignment, PAT/coherency, object sizes, PXP key validity, sync entries, exec queue ownership, VM bounds, and CPU address mirror requirements. It then builds one `drm_gpuva_ops` list per bind, commits GPUVA tree changes under the VM write lock, allocates page-table update arrays, performs SVM prefetch range work if needed, and submits update jobs. Failures after partial commit call `vm_bind_ioctl_ops_unwind()` in reverse order to restore removed VMAs and free newly created VMAs.

Rebind state lives in `vm->rebind_list` and per-VMA tile masks. Non-compute rebind happens during validation through `xe_vm_validate_rebind()`. Long-running compute VMs use preempt fences in `vm->preempt.exec_queues` and `preempt_rebind_work_func()`: the worker waits for or triggers preemption, validates evicted BOs and userptr repins, executes rebinds, waits for kernel-operation fences, checks for a repin race, installs fresh preempt fences, resumes queues, or bans the VM on unrecoverable errors.

Fault reporting uses a capped `vm->faults.list` protected by `faults.lock`. `xe_vm_add_fault_entry_pf()` records at most `MAX_FAULTS_SAVED_PER_VM` non-reserved-engine faults; `xe_vm_get_property_ioctl()` reports count and copies fault records to userspace. Snapshots are protected by `snap_mutex`; dumpable VMAs are captured first as metadata and later copied from BOs or userptr memory in `xe_vm_snapshot_capture_delayed()`.

## Dependencies and Integration Points

This file depends on DRM GPUVA/GPUVM helpers, TTM and `dma_resv`, Xe BO validation and migration, `xe_pt` page-table update code, `xe_tlb_inval`, `xe_sync`, `xe_exec_queue`, `xe_svm`, `xe_userptr`, PAT metadata, PXP key checks, runtime PM, tracepoints, and generated WA headers. The WA `22014953428` can force scratch-page creation during `xe_vm_create_ioctl()`. CPU-address-mirror and madvise helper paths are shared with `xe_vm_madvise.c`, while SVM range binds are shared with `xe_svm.c`.

## Risks and Edge Cases

The highest-risk areas are lock ordering, partial-commit unwind, userptr/SVM invalidation races, compute preempt fence lifetime, and dma-fence restrictions in fault mode. `vm_bind_ioctl_check_args()` contains many security-sensitive validation rules around PAT coherency, compression, imported dma-bufs, userptrs, and CPU address mirrors. Purgeable BO state is also delicate: new WILLNEED mappings to DONTNEED or PURGED BOs are rejected, while remap leftovers can inherit DONTNEED. Snapshot capture must avoid UAF by pinning BO references or `mm_struct` references before delayed copying.

## Test Signals

Useful tests include VM create/destroy ioctls for scratch, LR, fault, no-overcommit, and illegal flag combinations; bind/unbind/remap arrays with overlapping ranges; injected `TEST_VM_OPS_ERROR` failures at lock/prepare/run positions; userptr invalidation and repin races; compute-mode preempt rebind under eviction; purgeable DONTNEED/PURGED map and prefetch rejection; PAT/coherency validation on imported and CPU-cached BOs; SVM prefetch to system and VRAM; TLB invalidation paths; VM fault property reporting; and devcoredump snapshot capture for BO, userptr, null, and CPU-address-mirror VMAs.
