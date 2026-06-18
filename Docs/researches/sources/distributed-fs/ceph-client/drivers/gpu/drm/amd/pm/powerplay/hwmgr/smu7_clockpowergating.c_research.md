# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.c

## Purpose

This file implements SMU7 clock and power gating controls for UVD, VCE, GFX, and selected graphics/system clock-gating blocks. It translates hwmgr power-gating requests and clock-gating bitfields into SMU messages and AMDGPU IP block state changes.

## Important APIs, Types, and Functions

Public functions include `smu7_disable_clock_power_gating()`, `smu7_powergate_uvd()`, `smu7_powergate_vce()`, `smu7_update_clock_gatings()`, and `smu7_powergate_gfx()`. Internal helpers enable/disable UVD/VCE DPM, update SMC UVD/VCE tables before ungating, and send UVD/VCE power-on/off messages. `smu7_update_clock_gatings()` decodes `PP_GROUP_*`, `PP_BLOCK_*`, `PP_STATE_*`, and support bits to send `PPSMC_MSG_EnableClockGatingFeature` or `PPSMC_MSG_DisableClockGatingFeature` with `CG_*` masks.

## Control Flow and State

UVD/VCE powergate paths update `struct smu7_hwmgr` booleans, gate or ungate AMDGPU IP block power and clock states, toggle DPM, and send SMU power messages in different orders for gate versus ungate. GFX per-CU power gating sends enable with the CU count or disable with no parameter. No memory is allocated.

## Dependencies and Integration

The file depends on `smu7_hwmgr.h`, `smu7_common.h`, SMU message sending, SMC table updates, platform cap checks, `phm_cf_want_*_power_gating()`, and AMDGPU IP power/clock gating APIs. It is used by SMU7 hwmgr function tables for media and graphics power management.

## Risks and Test Signals

Ordering matters: ungating updates SMC tables after power and clock ungate, while gating disables DPM before powerdown. `smu7_update_clock_gatings()` returns `-EINVAL` for unsupported group/block combinations and for failed SMU messages. Test signals include media playback resume after UVD/VCE gating, SMU message traces, clock-gating feature toggles, power-state sysfs behavior, and GPU stability on Polaris11 GFX CU power gating.
