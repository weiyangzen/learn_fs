# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.c

## Purpose
`amdgpu_gfx.c` provides common AMDGPU graphics/compute IP block helpers shared by generation-specific GC implementations. It owns queue selection and bitmap policy, KIQ setup, MQD backing allocation, compute and graphics queue map/unmap, KIQ register access, GFXOFF gating, RAS glue, compute partition sysfs, cleaner-shader/process-isolation control, workload power-profile tracking, command stream preamble construction, and debugfs scheduler masks.

## Important APIs, types, and functions
Key exported helpers include `amdgpu_gfx_compute_queue_acquire()`, `amdgpu_gfx_graphics_queue_acquire()`, `amdgpu_gfx_kiq_init()`, `amdgpu_gfx_kiq_init_ring()`, `amdgpu_gfx_mqd_sw_init()`, `amdgpu_gfx_enable_kcq()`, `amdgpu_gfx_disable_kcq()`, `amdgpu_gfx_enable_kgq()`, `amdgpu_gfx_disable_kgq()`, `amdgpu_kiq_rreg()`, `amdgpu_kiq_wreg()`, `amdgpu_kiq_hdp_flush()`, and `amdgpu_gfx_cp_init_microcode()`. User/admin interfaces are created through `amdgpu_gfx_sysfs_init()` and the debugfs mask initializers. RAS entry points are `amdgpu_gfx_ras_sw_init()`, `amdgpu_gfx_ras_late_init()`, `amdgpu_gfx_cp_ecc_error_irq()`, `amdgpu_gfx_process_ras_data_cb()`, and `amdgpu_gfx_ras_error_func()`.

## Control flow
Queue ownership starts by translating MEC/ME pipe queue coordinates into bit indexes, then populating `adev->gfx.mec_bitmap[xcc].queue_bitmap` and `adev->gfx.me.queue_bitmap` according to multipipe policy, ASIC generation, module parameters, and XCC count. KIQ initialization allocates an EOP/HPD BO, picks an otherwise unowned MEC queue that can issue required queue-management packets, initializes an unscheduled ring, and later allocates MQD BOs/backups for KIQ, KGQ, and KCQ rings.

Queue enable and disable flow either uses MES legacy map/unmap helpers or emits KIQ PM4 packets under `kiq->ring_lock`. KCQ enable builds a set-resource queue mask, flushes HDP, maps each compute ring, commits the KIQ ring, and waits with a ring test. KGQ enable maps graphics rings only from the master XCC. Disable paths unmap or preempt the same ring sets and then run a ring test to confirm command processing.

GFXOFF control is reference-counted by `gfx_off_req_count` under `gfx_off_mutex`: disable cancels delayed enable work and asks SMU to ungate GFX; enable decrements the count and either schedules delayed gating or gates immediately for suspend paths. KIQ register read/write and HDP flush emit tiny command sequences plus polling fences, with early bailout during GPU reset or interrupt context to avoid deadlocking recovery.

Sysfs handlers expose current/available compute partition modes, partition memory allocation mode, cleaner shader execution, isolation enforcement, and supported reset masks. Partition switching validates SPX/DPX/TPX/QPX/CPX against XCC topology and takes the reset-domain semaphore. Cleaner shader execution creates a temporary scheduler entity, submits a tiny kernel IB marked for isolation/cleaner shader handling, and waits for completion. Isolation begin/end hooks coordinate kernel submissions with KFD user queues through delayed work and scheduler stop/start calls. Power profile hooks toggle fullscreen3D or compute profiles while rings have emitted fences or submissions.

## State and persistence behavior
State is runtime-only in `struct amdgpu_device` and hardware queues. Persistent-looking values such as firmware versions, MQD backups, queue bitmaps, GFXOFF reference count, XCP partition state, isolation mode arrays, cleaner shader BOs, and workload profile flags are recreated on driver initialization. Firmware image metadata is copied into `adev->firmware.ucode[]` when PSP loading is used. Sysfs writes change in-memory driver state or request hardware partition changes; no on-disk persistence is used.

## Dependencies and integration points
The file depends on `amdgpu_ring`, `amdgpu_rlc`, MES, SMU/DPM, PSP firmware loading, RAS, KFD, XCP partition management, XGMI, TTM BO allocation, DRM scheduler entities, debugfs, sysfs, runtime PM, reset-domain semaphores, and generation-specific KIQ/GFX function tables. It is a central integration layer between common scheduling/memory management and ASIC-specific GC implementations.

## Risks and edge cases
High-risk areas include queue bitmap mismatches with hardware topology, KIQ queue selection constraints, partial MQD allocation cleanup, MES-vs-KIQ path divergence, queue map/unmap commands issued during reset, KIQ polling timeouts, GFXOFF reference-count imbalance, sysfs partition switching while reset/suspend is active, cleaner shader submission when kernel queues are disabled, and isolation scheduling races with KFD. The queue mask uses a 64-bit set-resource mask even though software constants allow up to 128 queues, so future hardware with more enabled queues needs review.

## Test signals
Useful signals are ring bring-up and ring tests across single/multiple XCC devices, MES enabled and disabled queue map paths, KIQ register read/write timeout injection, GFXOFF toggling and residency counters, sysfs partition mode validation, cleaner shader sysfs execution per XCP, KFD/process-isolation stress, RAS ECC interrupt dispatch, debugfs scheduler mask toggling, suspend/resume with GFXOFF immediate mode, SR-IOV VF unload/reload, and firmware loading size accounting.
