# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_types.h

## Purpose

`xe_vm_types.h` defines the core data structures and flags used by the Xe VM implementation: VMAs, userptr VMAs, VM fault records, VM object state, memory attributes, bind-operation state, SVM range operations, and per-operation page-table update arrays.

## Important APIs, Types, and Functions

The key VMA flags are `XE_VMA_READ_ONLY`, `XE_VMA_DESTROYED`, `XE_VMA_ATOMIC_PTE_BIT`, page-size flags `XE_VMA_PTE_4K/2M/1G/64K/COMPACT`, `XE_VMA_DUMPABLE`, `XE_VMA_SYSTEM_ALLOCATOR`, and `XE_VMA_MADV_AUTORESET`. `struct xe_vma_mem_attr` stores preferred location, atomic access, default/current PAT index, and purgeable state. `struct xe_vma` embeds `struct drm_gpuva` and tracks rebind/destroy links, async destruction callbacks, tile state masks, skip-invalidation state, an optional user fence, and memory attributes. `struct xe_userptr_vma` extends `xe_vma` with `struct xe_userptr`.

`struct xe_vm` embeds `struct drm_gpuvm`, SVM state, per-tile bind queues, LRU bulk move state, root and scratch page tables, flags, locks, rebind and destruction work, range-fence trees, userptr state, preempt state, exec queue lists, ASID and last fault VMA, fault list, validation task state, TLB flush state, and file ownership.

Bind operation types include `struct xe_vma_op_map`, `xe_vma_op_remap`, `xe_vma_op_prefetch`, `xe_vma_op_map_range`, `xe_vma_op_unmap_range`, and `xe_vma_op_prefetch_range`. `enum xe_vma_op_flags` tracks commit state for unwind. `struct xe_vma_op` wraps `drm_gpuva_op` with Xe-specific operation payload. `struct xe_vma_ops` is an execution batch with a VMA op list, bind queue, syncs, per-tile `xe_vm_pgtable_update_ops`, and flags such as SVM prefetch, madvise, array-of-binds, skip-TLB-wait, and allow-SVM-unmap.

## Control Flow and State

These structures define how `xe_vm.c` persists state across VM creation, binds, execs, evictions, fault handling, madvise, and destruction. The VM object owns the GPUVA tree and page-table roots. VMAs persist in the GPUVA tree until removed by bind/unbind or VM close. Operation structs are temporary per-ioctl or per-rebind objects and carry enough commit bits to unwind partial updates.

## Dependencies and Integration Points

The file depends on DRM GPUVM/GPUSVM, DRM pagemap utilities, Linux dma-resv/kref/mmu notifier/scatterlist primitives, Xe device types, page-table types, range fences, TLB invalidation types, and userptr state. It is included throughout VM, SVM, BO, exec, page fault, and madvise code.

## Risks and Edge Cases

The lock comments are part of the contract. `tile_invalidated`, `tile_present`, and `tile_staged` have different protection rules for BO, userptr, VM lock, and notifier lock cases; misuse can cause stale GPU mappings or missed invalidations. The unioned `combined_links` and destroy callback/work fields are mutually exclusive lifecycle states and must not be used in the wrong phase. `validation.validating` is task state stored on a shared VM object and must be paired carefully. Purgeable state is protected by BO dma-resv and must remain coherent with BO-level holder counts.

## Test Signals

Important signals include lockdep coverage of documented lock rules, KASAN/UAF coverage for VMA destroy callbacks and delayed work, bind unwind tests that exercise each commit flag, SVM/userptr invalidation races around tile masks, purgeable state transitions under BO locks, and compile coverage for configuration-dependent debug error injection and pagemap fields.
