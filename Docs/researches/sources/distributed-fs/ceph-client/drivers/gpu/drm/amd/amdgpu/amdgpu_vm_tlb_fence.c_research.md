# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_tlb_fence.c

## Purpose

This file creates a synthetic DMA fence that represents completion of a PASID TLB flush after VM page-table updates. It is used when AMDGPU needs a fenceable TLB invalidation, especially for KFD or user queue paths where page-table memory must not be freed until invalidation completes.

## Important APIs, types, and functions

The private `struct amdgpu_tlb_fence` embeds `struct dma_fence`, device pointer, dependency fence, work item, spinlock, and PASID. The exported API is `amdgpu_vm_tlb_fence_create()`. Internal functions are the DMA fence ops name helpers and `amdgpu_tlb_fence_work()`.

## Control flow, state, and persistence behavior

`amdgpu_vm_tlb_fence_create()` allocates a TLB fence object. On allocation failure it synchronously waits for the input dependency, flushes the PASID TLB, and returns a stub fence because page tables have already been updated and the operation cannot fail cleanly. On success it stores the dependency and PASID, initializes a work item and fence with the VM TLB fence context and current TLB sequence, takes an extra reference for the worker, schedules work, and replaces the caller's fence pointer with the synthetic fence. The worker waits on the dependency, drops it, calls `amdgpu_gmc_flush_gpu_tlb_pasid()`, records an error on the fence if the flush fails, signals the fence, and drops the worker reference.

## Dependencies and integration points

The file depends on Linux DMA fences and workqueues plus AMDGPU GMC PASID TLB flush helpers. It is called from `amdgpu_vm_update_range()` when `vm->need_tlb_fence` is set and updates are not unlocked; the returned fence is also attached to the VM root reservation object.

## Risks and test signals

Risks include workqueue ordering, flush failure propagation, PASID reuse while an old fence is pending, and the OOM fallback blocking in sensitive paths. The TODO about a separate workqueue signals possible latency isolation risk. Test signals are KFD/user queue unmap stress, page-table free-after-flush correctness, fence error visibility on TLB flush failure injection, and no use-after-free when destroying VMs with pending TLB fences.
