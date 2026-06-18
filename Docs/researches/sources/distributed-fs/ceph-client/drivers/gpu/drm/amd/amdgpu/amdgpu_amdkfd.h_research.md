<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h

## Purpose
`amdgpu_amdkfd.h` defines the private interface between amdgpu and AMD KFD. It declares bridge lifecycle functions, memory-management types and APIs, KFD device state embedded in `struct amdgpu_device`, GPUVM helpers, reset/suspend/scheduler hooks, KGD-to-KFD callback prototypes, and fallback stubs for builds without HSA/KFD/SVM support.

## Important APIs, types, and functions
- `enum TLB_FLUSH_TYPE`, `enum kfd_mem_attachment_type`, and `enum kgd_engine_type` define bridge-level enums for GPUVM and engine operations.
- `struct kfd_mem_attachment` describes per-device mappings of a KFD allocation with BO VA, VA address, flags, mapping state, and attachment type.
- `struct kgd_mem` is the KFD-facing memory object containing an amdgpu BO or dma-buf/range, attachment list, validation list, domain, VA, allocation flags, invalidation state, process info, sync object, GEM handle, and import/AQL flags.
- `struct amdgpu_amdkfd_fence` extends `dma_fence` for KFD eviction and SVM synchronization.
- `struct amdgpu_kfd_dev` stores per-device KFD state: KFD device pointer, per-XCP VRAM usage counters, init flag, reset work, DRM client, and HMM `dev_pagemap`.
- `struct amdkfd_process_info` tracks all amdgpu VMs and BOs associated with a KFD process, userptr valid/invalid lists, eviction fence, MMU-notifier state, restore work, pid, and notification blocking flag.
- Public bridge APIs cover init/fini, device probe/init/fini, suspend/resume, reset, process teardown, interrupts, memory allocation, GWS, firmware/version queries, local memory and clock info, dmabuf info, PCIe bandwidth, HIQ unmap, scheduler controls, SQ perfmon config, GPUVM allocation/map/sync/import/export, RAS poison, memory limits, and XCP memory sizing.
- `read_user_wptr()` safely reads a user write pointer with page faults disabled and optional temporary kthread mm adoption.
- The `kgd2kfd_*` declarations and stubs define the callback boundary into KFD.

## Control flow
This header defines the call graph used by amdgpu and KFD. amdgpu core calls the `amdgpu_amdkfd_*` lifecycle hooks around probe, init, suspend, reset, and teardown. KFD calls back through memory/GPUVM helpers to allocate BOs, map/unmap GPU memory, synchronize, manage process VMs, reserve memory limits, and drive low-level queues.

Kconfig controls large parts of the flow. With `CONFIG_HSA_AMD`, real KFD callbacks and GPUVM/fence helpers are available. Without it, many functions become no-op or harmless-return stubs so the rest of amdgpu can compile and call bridge hooks unconditionally. With `CONFIG_HSA_AMD_SVM`, zone-device initialization is real; otherwise it is a stub returning success.

## State and persistence behavior
The header describes runtime state owned by amdgpu and KFD. `kgd_mem` objects persist while KFD allocations live. Attachments persist while mapped to one or more GPUs. `amdkfd_process_info` persists for a KFD process and coordinates BO lists, eviction fences, and MMU notifier state. `amdgpu_kfd_dev` persists for the lifetime of an amdgpu device.

No persistent disk state is defined. Memory-limit counters and VRAM usage arrays are runtime accounting only.

## Dependencies and integration points
The header depends on Linux list/mm/kthread/workqueue/mmu-notifier/memremap types, DRM client support, KFD topology and interface headers, amdgpu sync/VM/XCP types, and KFD ioctl flags. It is included by `amdgpu.h`, `amdgpu_amdkfd.c`, GPUVM bridge implementation files, and KFD-facing amdgpu code.

It is a major integration point between DRM render-node/GEM/TTM memory management and ROCm/HSA process management.

## Risks and edge cases
Many structs cross subsystem ownership boundaries. Locking comments are important: `kgd_mem.validate_list` is protected by `amdkfd_process_info.lock`; BO lists, userptr lists, and MMU-notifier state have separate locks. Misusing these types can create deadlocks between DQM, mmap locks, BO reservations, and MMU notifier paths.

The `read_user_wptr()` macro deliberately disables page faults and borrows an mm for kthreads. It must only be used when the memory is pinned and mapped, as the comment states. The stubs for disabled HSA builds must preserve caller expectations; returning success for some stubs and false/error for others is part of the contract.

`struct amdgpu_kfd_dev` contains `dev_pagemap` and is embedded last in `struct amdgpu_device`; layout assumptions from `amdgpu.h` must be preserved.

## Test signals
Compile coverage should include HSA enabled/disabled, HSA SVM enabled/disabled, debugfs enabled/disabled, and P2P enabled/disabled. Runtime signals include ROCm allocation/map/unmap, userptr invalidation/restore, eviction fencing, dmabuf import/export, process teardown, scheduler stop/start, reset pre/post callbacks, and successful no-HSA amdgpu probe with all bridge stubs linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.h -->
