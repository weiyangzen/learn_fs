# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.h

## Purpose

`xe_vm.h` declares the Xe VM and VMA public interface used across the driver. It provides lifetime helpers, locking helpers, VMA accessors, VM mode predicates, bind ioctl entry points, rebind and invalidation APIs, kernel BO binding, snapshot APIs, and VM fault recording hooks.

## Important APIs, Types, and Functions

The header forwards `struct xe_vm`, `struct xe_vma`, `struct xe_userptr_vma`, exec queues, sync entries, SVM ranges, and DRM objects through included type headers. Core declarations include `xe_vm_create()`, `xe_vm_lookup()`, `xe_vm_lock()`, `xe_vm_unlock()`, `xe_vm_close_and_put()`, all VM ioctls, compute queue add/remove helpers, rebind helpers, invalidation helpers, protected-BO validation, snapshot capture/print/free, and `xe_vm_add_fault_entry_pf()`.

Inline helpers are important integration glue: `xe_vm_get()` and `xe_vm_put()` wrap `drm_gpuvm_get/put`; `gpuvm_to_vm()`, `gpuva_to_vm()`, `gpuva_to_vma()`, and `gpuva_op_to_vma_op()` define the embedding conversions; `xe_vma_start()`, `xe_vma_size()`, `xe_vma_end()`, `xe_vma_bo_offset()`, `xe_vma_bo()`, `xe_vma_vm()`, `xe_vma_read_only()`, `xe_vma_userptr()`, `xe_vma_is_null()`, `xe_vma_is_cpu_addr_mirror()`, `xe_vma_has_no_bo()`, and `xe_vma_is_userptr()` centralize layout access. Mode helpers identify scratch, fault, LR, preempt-fence, closed, banned, and eviction-allowed states.

The validation helpers `xe_vm_set_validating()`, `xe_vm_clear_validating()`, `xe_vm_is_validating()`, `xe_vm_set_validation_exec()`, and `xe_vm_validation_exec()` expose task-local validation state stored on the VM reservation object. `xe_vm_has_valid_gpu_mapping()` is an advisory READ_ONCE-based tile-present/tile-invalidated predicate.

## Control Flow and State

This header does not implement control flow, but it documents the call contracts: most VM/VMA helpers expect `vm->lock`, VM dma-resv, or BO dma-resv to be held depending on the path. `xe_vm_queue_rebind_worker()` queues compute-mode rebind work on the ordered workqueue, while `xe_vm_reactivate_rebind()` restarts a deactivated rebind worker after compute submission.

## Dependencies and Integration Points

The header depends on DRM GPUVM, Xe BO, map, VM types, assertions, and TLB invalidation batch types. It is included by VM bind, SVM, exec, page fault, madvise, BO eviction, and debug snapshot code. The accessors deliberately hide the embedded DRM GPUVA layout so implementation details can change without touching callers.

## Risks and Edge Cases

The inline mode predicates can be safely relied on only under their documented locks. `xe_vm_is_closed()` notes that `vm->size` is stable only while `vm->lock` is held. `xe_vm_has_valid_gpu_mapping()` is explicitly advisory and unsafe as a hard synchronization primitive; it is intended only where stale reads are harmless. Validation state relies on pairing WRITE_ONCE and READ_ONCE and assumes the VM dma-resv is held when a caller observes current-task validation.

## Test Signals

Compile coverage is important because this header provides many inline conversions. Runtime assertions should cover userptr/null/CPU-address-mirror classification, closed/banned checks under the VM lock, validation exec pairing, rebind worker reactivation, and opportunistic valid-mapping decisions in eviction, userptr invalidation, and fault paths.
