# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c

## Purpose
`amdgpu_ids.c` manages global PASID allocation and per-VMHUB VMID assignment. PASIDs identify shared address spaces across GPU/IOMMU/driver, while VMIDs identify active GPU page-table contexts on each VM hub. The code delays PASID reuse behind fences and assigns/reuses VMIDs with LRU fairness, active-fence tracking, reserved IDs, TLB-flush decisions, and GDS/GWS/OA compatibility checks.

## Important APIs, types, and functions
PASID APIs are `amdgpu_pasid_alloc()`, `amdgpu_pasid_free()`, `amdgpu_pasid_free_delayed()`, and `amdgpu_pasid_mgr_cleanup()`. VMID APIs are `amdgpu_vmid_grab()`, `amdgpu_vmid_uses_reserved()`, `amdgpu_vmid_alloc_reserved()`, `amdgpu_vmid_free_reserved()`, `amdgpu_vmid_reset()`, `amdgpu_vmid_reset_all()`, `amdgpu_vmid_mgr_init()`, `amdgpu_vmid_mgr_fini()`, and `amdgpu_vmid_had_gpu_reset()`.

## Control flow
PASID allocation uses a global IRQ-safe xarray cyclic allocator from 1 to `(1 << bits) - 1`. Freeing removes the xarray entry under IRQ lock. Delayed free extracts a singleton reservation fence and either installs a fence callback to free the PASID after completion or blocks as an OOM/fallback path.

VMID grabbing locks the hub manager, first looks for an idle VMID or returns a fence to wait on for fairness. Reserved VMIDs are checked against owner, PD address, GDS/GWS/OA state, update sequence, and last flush fence; they may force a flush or return an active fence. Non-reserved VMIDs try to reuse a compatible active ID, otherwise use the idle ID. The selected ID records the job fence in its active sync, moves in the LRU list, updates flush/update state and resource bases, and writes `job->vmid` and `job->pasid`.

Initialization configures per-hub VMID counts based on GC version, MMHUB, and the KFD VMID boundary, skips VMID0, creates active sync objects, and populates the LRU. Finalization destroys locks, syncs, last flush fences, and PASID mapping fences.

## State and persistence behavior
Global PASID state is the xarray plus cyclic next value. Per-device VMID state lives in `adev->vm_manager.id_mgr[]`: mutex, LRU list, reserved flag, and `struct amdgpu_vmid` entries with owner, PD address, active sync, flush sequence, last flush fence, resource bases, PASID, and mapping fence. All state is in memory and reset on driver/module teardown.

## Dependencies and integration points
This file depends on Linux xarray, DMA fences, DMA reservation objects, AMDGPU VM update sequence helpers, ring fence contexts, sync objects, tracepoints, GPU reset counters, and KFD VMID partitioning. It feeds job submission and VM flush decisions consumed by `amdgpu_ib_schedule()`.

## Risks and edge cases
PASID allocation with `bits >= 32` would make `1U << bits` unsafe; callers must provide supported widths. Delayed PASID free can block under OOM. VMID reuse correctness depends on fence signaling, concurrent flush mode, PD/GDS compatibility, and update sequence tracking. Reserved VMIDs remove one ID from the LRU and can starve if active fences do not drain. Reset handling resets owner/resource state but not all fence fields.

## Test signals
PASID allocation/free wraparound, delayed free with active and already-signaled fences, OOM fallback, VMID reuse with and without concurrent flush, reserved VMID allocation/free, GDS/GWS/OA switching, GPU reset detection, KFD VMID boundary behavior, and multi-ring/multi-hub submission stress are useful tests.
