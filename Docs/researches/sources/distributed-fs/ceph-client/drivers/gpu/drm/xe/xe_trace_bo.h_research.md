# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_bo.h

Purpose: Defines tracepoints for buffer object creation/validation/fault/migration, VMA bind/rebind/invalidation/eviction activity, and VM lifecycle/rebind/failure events.

Important APIs/types/functions: Event class `xe_bo` backs `xe_bo_cpu_fault`, `xe_bo_validate`, and `xe_bo_create`. `xe_bo_move` records old/new TTM placement names and `move_lacks_source`. Event class `xe_vma` backs pagefault, access-counter, bind, pagefault-bind, unbind, userptr/non-userptr rebind, invalidation, eviction, and invalidate-complete events. Event class `xe_vm` backs VM create/free/kill/cpu-bind/restart/rebind-worker events and operation failures.

Control flow: Call sites pass `struct xe_bo`, `struct xe_vma`, or `struct xe_vm`; the trace macros snapshot size, flags, VM pointer, ASID, virtual address bounds, userptr address, and placement strings. The trace include section generates declarations/definitions depending on whether a C unit defines `CREATE_TRACE_POINTS`.

State and persistence behavior: No driver state is mutated. Tracepoint state consists of per-event snapshots of memory-management state at the time of the trace.

Dependencies and integration points: Includes `xe_bo.h`, `xe_bo_types.h`, and `xe_vm.h`. It integrates with BO allocation/migration, page fault handling, VM bind/unbind, rebind workers, and userptr invalidation code. Placement names come from `xe_mem_type_to_name`, so placement indexes must be valid.

Risks: The VMA trace class dereferences `xe_vma_vm(vma)` and computes `xe_vma_end(vma) - 1`; malformed or half-initialized VMAs could produce invalid data. `xe_bo_move` indexes placement names by `new_placement` and `old_placement`; invalid memory type values would risk out-of-bounds access. Trace formats are diagnostic ABI for tooling.

Test signals: Exercise GEM object creation, CPU faults, BO migration between system/VRAM/stolen placements, VM creation/destruction, page-fault binds, and userptr invalidation while observing `events/xe/xe_bo_*`, `xe_vma_*`, and `xe_vm_*`.
