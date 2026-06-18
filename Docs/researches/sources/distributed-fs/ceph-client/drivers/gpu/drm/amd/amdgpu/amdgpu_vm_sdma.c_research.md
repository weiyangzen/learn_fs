# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c

## Purpose

This file implements the SDMA-backed VM page-table update backend. It builds scheduler jobs and indirect buffers that write or copy PTE/PDE entries through hardware packet functions rather than CPU stores.

## Important APIs, types, and functions

The exported object is `amdgpu_vm_sdma_funcs`. Its methods are `amdgpu_vm_sdma_map_table()`, `amdgpu_vm_sdma_prepare()`, `amdgpu_vm_sdma_update()`, and `amdgpu_vm_sdma_commit()`. Internal helpers include `amdgpu_vm_sdma_alloc_job()`, `amdgpu_vm_sdma_copy_ptes()`, and `amdgpu_vm_sdma_set_ptes()`. It uses `AMDGPU_VM_SDMA_MIN_NUM_DW` and `AMDGPU_VM_SDMA_MAX_NUM_DW` to size command buffers.

## Control flow, state, and persistence behavior

`map_table()` ensures PD/PT BOs have GART mappings. `prepare()` allocates an AMDGPU VM update job on the immediate or delayed VM scheduler entity and pushes sync dependencies into the job. `update()` adds dependencies on kernel fences from the target table, then emits set commands for contiguous physical mappings or stages generated PTE values at the end of the IB and copies them into the page table for discontiguous `pages_addr` mappings. If the IB runs low on space it commits the current job and allocates a new one. `commit()` pads the IB, increments TLB sequence if needed, submits the job, records `last_unlocked` for unlocked updates or adds a bookkeeping fence to the root reservation object, and optionally returns the delayed fence with `DRM_SCHED_FENCE_DONT_PIPELINE` set.

## Dependencies and integration points

The backend depends on AMDGPU job allocation/submission, VM scheduler entities, SDMA/GMC-specific `vm_pte_funcs`, ring padding, BO GPU offsets, DMA reservation iterators, DRM scheduler dependencies, and VM tracepoints. It is the default update backend for many graphics VMs and for compute VMs when CPU updates are disabled.

## Risks and test signals

Risks include underestimated IB space, dependency leaks or missing fence refs, staging PTEs over command space, incorrect delayed/immediate entity selection, and failing to serialize TLB flushes when the page-table queue shares hardware with userspace. Test signals are VM update jobs visible on SDMA/page queues, clean fence completion, correct behavior with discontiguous system memory, no IB length warnings, successful fallback across multiple committed jobs for large mappings, and no page faults after SDMA-updated mappings.
