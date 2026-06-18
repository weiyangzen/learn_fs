# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/kgd_kfd_interface.h

## Purpose
Defines the private interface between AMDGPU KGD and AMD KFD. It is the bridge by which KFD obtains graphics-driver resources and invokes generation-specific services for queue programming, VM mapping, trap/debug setup, SDMA HQD management, and CU occupancy.

## Important APIs, Types, and Functions
Important types include `enum kfd_preempt_type`, `struct kfd_vm_fault_info`, `struct kfd_local_mem_info`, `enum kgd_memory_pool`, `struct kfd_cu_occupancy`, `enum kfd_sched_policy`, `struct kgd2kfd_shared_resources`, and `struct tile_config`. The central API is `struct kfd2kgd_calls`, a callback table implemented by AMDGPU GFX-generation files and consumed by KFD. It covers shader-memory programming, PASID/VMID mapping, interrupt init, CP and SDMA HQD load/dump/destroy, VM page table programming, TLB invalidation, VM fault register reads, debug trap enable/disable, wave launch controls, address watchpoints, dequeue wait packet construction, CU occupancy, trap handler settings, HQD address/reset, and SDMA doorbell lookup.

## Control Flow
The file declares no executable code. Runtime flow is callback-driven: KFD selects and stores a generation-specific `kfd2kgd_calls` table during device setup, then calls it during queue create/destroy, fault handling, debugging, and reset paths. AMDGPU provides `kgd2kfd_shared_resources` so KFD can allocate VMIDs, queues, and doorbells within hardware constraints.

## State and Persistence
The header defines state shapes but owns no storage. Persistent state lives in KFD and AMDGPU device objects: VMID bitmaps, CP queue bitmaps, SDMA doorbell indices, doorbell aperture data, GPUVM size, render minor, local memory data, and callback table pointers. `tile_config` contains borrowed pointers to AMDGPU-owned tile arrays and must follow device lifetime.

## Dependencies and Integration Points
It includes Linux types, bitmap, DMA fence, `amdgpu_irq.h`, and `amdgpu_gfx.h`; it forward declares AMDGPU/KFD device structs. Integration points include KFD device setup, KFD interrupt processors, topology/CRAT creation, tile-config ioctl, AMDGPU GPUVM, and per-generation `amdgpu_amdkfd_gfx_*` implementations.

## Risks and Test Signals
Risks include mismatched callback signatures, missing callbacks on unsupported ASICs, stale borrowed pointers, wrong VMID/PASID programming, and debug operations targeting the wrong VMID or instance. Test signals include KFD queue lifecycle, SDMA queue load/destroy, GPUVM fault delivery to KFD events, debugger watch/trap operations, topology reporting, tile-config ioctl behavior, and suspend/reset coverage across GFX generations.
