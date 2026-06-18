<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c

## Purpose
`amdgpu_amdkfd.c` implements the amdgpu side of the private KGD-to-KFD bridge. It initializes and shuts down KFD support, probes and initializes per-GPU KFD devices, reports shared GPU resources, manages KFD suspend/resume/reset handoff, allocates kernel/GWS memory for KFD, exposes firmware/memory/clock/dmabuf/PCIe information, submits low-level IBs, toggles compute idle power policy, drains interrupts, and forwards RAS/poison and scheduler operations.

## Important APIs, types, and functions
- Global lifecycle: `amdgpu_amdkfd_init()`, `amdgpu_amdkfd_fini()`, and `amdgpu_amdkfd_device_probe()`.
- Device lifecycle: `amdgpu_amdkfd_device_init()` builds `kgd2kfd_shared_resources` and calls `kgd2kfd_device_init()`; `amdgpu_amdkfd_device_fini_sw()` calls `kgd2kfd_device_exit()`.
- DRM client support: `amdgpu_amdkfd_drm_client_create()` registers a DRM client named `kfd`.
- Reset/suspend/process flow: `amdgpu_amdkfd_suspend()`, `resume()`, `suspend_process()`, `resume_process()`, `pre_reset()`, `post_reset()`, `gpu_reset()`, and `amdgpu_amdkfd_reset_work()`.
- Memory helpers: `amdgpu_amdkfd_alloc_kernel_mem()`, `free_kernel_mem()`, `alloc_gws()`, and `free_gws()`.
- Information helpers: `amdgpu_amdkfd_get_fw_version()`, `get_local_mem_info()`, `get_gpu_clock_counter()`, `get_max_engine_clock_in_mhz()`, `get_dmabuf_info()`, `get_pcie_bandwidth_mbytes()`, and `amdgpu_amdkfd_xcp_memory_size()`.
- Execution/control helpers: `amdgpu_amdkfd_submit_ib()`, `set_compute_idle()`, `is_kfd_vmid()`, `have_atomics_support()`, `unmap_hiq()`, `stop_sched()`, `start_sched()`, `compute_active()`, and `config_sq_perfmon()`.
- RAS/interrupt helpers forward poison consumption and close-event payloads into KFD/UMC/interrupt code.

## Control flow
Module-level init calculates total system memory from `si_meminfo()`, calls `kgd2kfd_init()`, and records whether KFD initialized. Per-device probe calls `kgd2kfd_probe()` if global KFD init succeeded. Device init initializes GPUVM memory limits, builds shared resources from VMID allocation, MEC queue topology, GPUVM size, render node minor, SDMA doorbell index, MES state, compute queue bitmap, doorbell aperture, and non-CP doorbell range, then calls `kgd2kfd_device_init()`.

Reset flow is delegated both ways. KFD can trigger `amdgpu_amdkfd_gpu_reset()`, which schedules `adev->kfd.reset_work` on the reset domain if recovery is allowed. The work item builds an `amdgpu_reset_context` with source HWS or MES and calls `amdgpu_device_gpu_recover()`. During amdgpu reset, pre/post reset calls are forwarded to KFD.

Memory allocation for KFD creates amdgpu BOs with kernel/device types, pins them, allocates GART backing, maps to CPU when needed, and returns BO pointer, GPU address, and CPU pointer. Failure unwinds in reverse order. GWS allocation creates a user BO in the GWS domain with no CPU access.

Low-level IB submission chooses a compute or SDMA ring by KGD engine type, allocates an amdgpu job, fills one IB with caller-provided command pointer and VMID, schedules it, waits on the returned fence, drops the fence reference, and frees the job.

## State and persistence behavior
Global state includes `amdgpu_amdkfd_total_mem_size` and `kfd_initialized`. Per-device KFD state lives in `adev->kfd`: KFD device pointer, VRAM accounting arrays, init-complete flag, reset work, DRM client, and HMM page map. Device init increments total memory by real VRAM size; fini decrements it.

Memory helpers create BOs whose lifetime is owned by KFD through opaque `mem_obj` pointers. Scheduler and process suspend state are owned by KFD but controlled through forwarded calls. No persistent storage is written by this file.

## Dependencies and integration points
The file depends on the `kgd2kfd_*` callback interface, amdgpu VM/BO/job/IB/ring/doorbell/GFX/SDMA/DPM/XGMI/RAS/UMC/reset code, DRM client registration, dma-buf and TTM helpers, Linux KFD UAPI flags, and PSP performance-monitor configuration.

It integrates with KFD HSA runtime support, HMM/SVM memory migration through declarations in the header, reset domains, interrupt handling, RAS poison handling, and power management. It also relies on `amdgpu_amdkfd.h` stubs so builds without HSA support compile cleanly.

## Risks and edge cases
Doorbell reporting changes when MES is enabled: KFD receives only the base address while amdgpu manages the doorbell space. Non-MES paths must correctly reserve kernel doorbells at the start of the aperture. Incorrect queue bitmap complementing or last-valid-bit clearing can expose invalid compute queues to KFD.

`amdgpu_amdkfd_submit_ib()` uses caller-provided IB memory and explicit VMID, with a comment noting this works for NO_HWS and needs better handling without knowing VMID. It waits synchronously and must free jobs/fences on all paths.

`amdgpu_amdkfd_unmap_hiq()` fabricates a temporary ring/functions pair for KIQ unmap queues and locks the KIQ ring while emitting packets. Allocation failures, reset-in-progress, or unscheduled rings must be handled without leaving ring state inconsistent.

Memory accounting and partition sizing are subtle for APUs, XCP memory partitioning, NPS1 app-APU mode, even memory capping, and `apu_prefer_gtt`. Wrong size reporting can overcommit ROCm allocations or hide usable memory.

## Test signals
Good signals include KFD module init/fini success, per-GPU KFD node creation, correct queue/doorbell resources in KFD topology, ROCm process creation and teardown, suspend/resume with and without S0ix, GPU reset recovery with active KFD queues, BO allocation/free leak tests, GWS allocation, dmabuf import metadata checks, PCIe bandwidth values matching link masks, IB submission completion, HIQ unmap success, scheduler stop/start behavior, and poison consumption notifications reaching KFD/UMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd.c -->
