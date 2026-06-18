# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.h

## Purpose
`amdgpu_ids.h` declares PASID and VMID manager data structures and APIs for AMDGPU VM submission code.

## Important APIs, types, and functions
It defines `AMDGPU_NUM_VMID`, `struct amdgpu_vmid`, and `struct amdgpu_vmid_mgr`. `struct amdgpu_vmid` tracks LRU linkage, active sync, last flush fence, owner context, PD address, flushed update sequence, reset counter, GDS/GWS/OA ranges, PASID, and PASID mapping fence. It declares all PASID and VMID allocation, reset, and lifecycle helpers implemented in `amdgpu_ids.c`.

## Control flow
The header has no executable flow. VM/job submission code calls `amdgpu_vmid_grab()` before scheduling work, may reserve VMIDs for debugging/SPM, and uses reset helpers to force future flushes.

## State and persistence behavior
The structures describe volatile per-device and global runtime state. Sync/fence fields are used to delay reuse until GPU work is complete; no durable persistence exists.

## Dependencies and integration points
It depends on Linux mutex/list/fence types and `amdgpu_sync`. It integrates with VM manager, ring scheduling, KFD VMID partitioning, PASID/IOMMU address-space identity, and reset handling.

## Risks and edge cases
Callers must hold/use manager locks according to implementation expectations. Fence pointers require balanced references. The fixed 16-VMID array must match hardware VMID limits and KFD partitioning.

## Test signals
Compile coverage, VMID lifecycle tests, fence reference leak checks, PASID allocation tests, reserved VMID tests, and VM submission under reset validate the header contract.
