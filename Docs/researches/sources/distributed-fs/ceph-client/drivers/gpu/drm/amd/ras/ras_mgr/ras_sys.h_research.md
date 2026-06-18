# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/ras_sys.h

## Purpose

`ras_sys.h` provides AMDGPU-facing logging, register access, instance mapping, and wait/radix helper macros for the RAS manager and rascore adapter layer.

## Important APIs, Types, And Functions

Logging macros `RAS_DEV_ERR/WARN/INFO/DBG` route through `dev_*` when a device is available or `printk` otherwise. `RAS_DEV_RREG32_SOC15` and `RAS_DEV_WREG32_SOC15` wrap SOC15 register access with AMDGPU offsets. `RAS_GET_INST` and `RAS_GET_MASK` translate logical instances/masks through `adev->ip_map` when available. Inline helpers wrap radix-tree deletion by iterator and `wait_event_interruptible_timeout`. The header declares `amdgpu_ras_sys_fn`.

## Control Flow, State, And Persistence

Macros branch on whether a device pointer or IP map callback exists. Register macros perform immediate MMIO reads/writes; wait helper blocks on the supplied waitqueue until the condition or timeout. Persistent state is hardware register state and driver logs, not header-owned memory.

## Dependencies And Integration Points

It includes Linux printk/device/mempool headers and `amdgpu.h`. It is included throughout manager and rascore code to avoid direct AMDGPU dependencies inside generic rascore where possible.

## Risks And Test Signals

Risks include unsafe casts of `void *dev` to `amdgpu_device`, wrong SOC15 offset construction, logging format mismatches, and condition callback misuse in wait helper. Test signals include build coverage, register access smoke tests on supported IPs, logical-to-physical instance mapping tests, and RAS log output checks.
