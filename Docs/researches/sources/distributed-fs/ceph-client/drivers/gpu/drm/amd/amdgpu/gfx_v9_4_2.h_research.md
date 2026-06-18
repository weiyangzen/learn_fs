# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.h

## Purpose

This header exposes the GC 9.4.2/Aldebaran helper functions and RAS descriptor implemented in `gfx_v9_4_2.c` for use by the main GFX 9.0 driver.

## Important APIs, types, and functions

- `gfx_v9_4_2_debug_trap_config_init()`: programs per-VMID trap controls for a VMID range.
- `gfx_v9_4_2_init_golden_registers()`: applies common and die-specific GC golden register settings.
- `gfx_v9_4_2_init_sq()`: configures SQ behavior, including XNACK chain handling when MEC firmware supports it.
- `gfx_v9_4_2_set_power_brake_sequence()`: programs GFX throttle and power-brake stall pattern registers.
- `gfx_v9_4_2_do_edc_gpr_workarounds()`: runs GPR/LDS clearing workarounds when RAS is enabled and the device is not in reset.
- `extern struct amdgpu_gfx_ras gfx_v9_4_2_ras`: RAS descriptor with GFX 9.4.2 counter, status, reset, and watchdog callbacks.

## Control flow and integration

The header has no executable control flow. `gfx_v9_0.c` includes it and calls the helpers from GFX initialization, power-management, RAS, and debug-trap paths. The exported RAS descriptor is assigned to `adev->gfx.ras` for supported ASICs.

## State and persistence behavior

The declarations represent functions that program persistent hardware registers, dispatch compute cleanup shaders, and clear RAS counters/status registers. The header itself stores no state.

## Dependencies

Consumers need AMDGPU core type definitions for `struct amdgpu_device` and `struct amdgpu_gfx_ras`, plus standard fixed-width integer types. The header intentionally does not include those dependencies itself.

## Risks

The prototypes expose low-level hardware programming helpers without documenting locking or ordering requirements. Callers must invoke them in the correct phase of the GFX lifecycle, after rings/register windows are ready and before dependent features are enabled.

## Test signals

Build/link coverage confirms the declarations match `gfx_v9_4_2.c`. Runtime signals include correct Aldebaran initialization, RAS callback registration, debug trap programming for VMIDs, and absence of GPU hangs from the EDC workaround entry point.
