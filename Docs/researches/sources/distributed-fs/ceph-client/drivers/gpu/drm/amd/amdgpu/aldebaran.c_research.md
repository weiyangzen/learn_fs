<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c

## Purpose
`aldebaran.c` implements Aldebaran-specific reset-control plumbing, centered on MODE2 reset. It registers reset handlers for Aldebaran devices, selects the reset method, suspends and restores the right IP blocks, launches resets across XGMI-connected devices, reloads firmware after reset, resumes RAS and topology state, and exposes init/fini entry points for `adev->reset_cntl`.

The file is targeted at ASIC reset recovery rather than normal device initialization. It has special handling for MP1 13.0.2 devices connected to the CPU through XGMI, multi-AID systems, and XGMI hives where multiple physical nodes should reset in parallel.

## Important APIs, types, and functions
- `aldebaran_reset_init()` allocates and attaches `struct amdgpu_reset_control`, sets `async_reset`, `get_reset_handler`, initializes reset work, and installs `aldebaran_rst_handlers`.
- `aldebaran_reset_fini()` frees the reset control.
- `aldebaran_get_reset_handler()` selects the active reset method. If no method is specified, it chooses MODE2 for the CPU-connected MP1 13.0.2 case, otherwise defers to `amdgpu_asic_reset_method()`.
- `aldebaran_mode2_handler` is the `struct amdgpu_reset_handler` for MODE2 and wires prepare, perform, restore, and direct reset callbacks.
- `aldebaran_mode2_suspend_ip()` ungates power/clock state and suspends GFX, SDMA, and sometimes IH IP blocks in reverse IP-block order.
- `aldebaran_mode2_perform_reset()` marks devices as actively MODE2 resetting, runs `amdgpu_dpm_mode2_reset()`, parallelizes multi-node XGMI reset through `system_dfl_wq`, waits for work completion, and clears active reset state.
- `aldebaran_mode2_restore_ip()` reinitializes COMMON/IH/GFXHUB, reloads selected GFX and SDMA microcode through PSP, resumes RLC, waits for SMU reset completion, resumes GFX/SDMA blocks, runs late init, and regates clocks/power.
- `aldebaran_mode2_restore_hwcontext()` applies reset-recovery init level, clears RAS error state, calls restore IP, re-registers the GPU instance, reruns RAS late-init, resumes RAS, updates XGMI topology, resumes IRQ reset helpers, and runs IB ring tests.

## Control flow
Initialization installs a reset control with two handlers: Aldebaran MODE2 and XGMI reset-on-init. During recovery, the reset framework asks `get_reset_handler()` for a handler. The selector fills `reset_context->method` if it was `AMD_RESET_METHOD_NONE`, then scans the registered handlers.

For MODE2, prepare first suspends the affected HW context unless running as an SR-IOV VF. The suspend mask starts with GFX and SDMA, adds IH when `adev->aid_mask` indicates multi-AID, and drops SDMA from the suspend mask for multi-AID SDMA versions because those are handled differently.

The perform stage validates the reset-device list and hive requirements for MP1 13.0.2. It locks each device reset control, sets `active_reset`, and resets all devices in the reset list. Multi-node XGMI devices are reset asynchronously using their reset work, while single-node devices reset inline. The function then flushes queued work, reads each device's `asic_reset_res`, unlocks the reset controls, and clears `active_reset`.

The restore stage loops over every reset device. Each device is moved to `AMDGPU_INIT_LEVEL_RESET_RECOVERY`, restored through `aldebaran_mode2_restore_ip()`, then brought back into default state only after RAS resume, optional XGMI topology update, IRQ reset helper resume, and IB ring tests succeed.

## State and persistence behavior
The file mutates runtime reset state in `adev->reset_cntl`, `reset_context`, `adev->asic_reset_res`, reset work queues, per-device `reset_lock`, `active_reset`, IP block status flags, init level, RAS error state, topology state, and GPU instance registration. It also reloads firmware from `adev->firmware.ucode[]`, but it does not persist data across boots.

The reset path intentionally preserves device-level recovery ordering. It clears RAS errors after reset, reestablishes GART and firmware state, and marks late init completed for relevant blocks. Failed IB tests convert recovery to `-EAGAIN` and store the result in `tmp_adev->asic_reset_res`, signaling higher reset logic that another recovery attempt may be needed.

## Dependencies and integration points
The implementation depends on the amdgpu reset framework, DPM/SMU mode2 reset calls, PSP firmware loading, GFXHUB and RLC callbacks, IP-block suspend/resume/later-init helpers, RAS, IRQ reset helpers, IB ring tests, XGMI hive topology management, PCI bus mastering control, and Linux workqueues.

It integrates directly with `amdgpu_device_gpu_recover()` and reset domains through the `amdgpu_reset_control` object. It also relies on `amdgpu.h` macros for IP versions, clock/power gating, init levels, and GPU instance registration.

## Risks and edge cases
Reset concurrency is the highest risk. The code queues parallel reset work for XGMI devices, then flushes each work item and reads `asic_reset_res`; missed locking or stale `active_reset` could corrupt simultaneous reset decisions. Returning `-EALREADY` from `queue_work()` is treated as a reset failure, so duplicate work submission has visible recovery impact.

The firmware reload list is manually filtered to SDMA, MEC, RLC restore lists, and RLC G firmware. Missing a required ucode id or changing firmware ids without updating this list can produce post-reset hangs. The MP1 13.0.2 path requires a hive context, and returning `-EINVAL` prevents recovery with an incorrect reset context.

Multi-AID handling changes both the IP suspend mask and IH inclusion. Any new Aldebaran-like IP layout needs careful review of `aldebaran_get_ip_block_mask()`, SDMA skip logic, and restore ordering.

## Test signals
Strong signals are successful MODE2 reset recovery on Aldebaran, especially XGMI multi-node systems; successful PSP reload of GFX/SDMA/RLC firmware; `SMU_EVENT_RESET_COMPLETE` received; GFX and SDMA IP late init passing; RAS late init and resume passing; topology update success; and `amdgpu_ib_ring_tests()` passing after reset. Negative-path tests should cover missing reset lists, missing hive context for MP1 13.0.2, missing COMMON/IH blocks, and firmware reload failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/aldebaran.c -->
