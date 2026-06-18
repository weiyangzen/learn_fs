# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/amd_powerplay.c

## Purpose
`amd_powerplay.c` is the top-level legacy PowerPlay adapter. It creates and destroys `pp_hwmgr`, registers the `powerplay` SMC IP block, implements the `amd_pm_funcs` callback surface used by the amdgpu core and display code, and delegates most behavior to ASIC-specific `hwmgr_func`, `pptable_func`, and `smumgr_funcs` tables.

## Important APIs And Control Flow
Lifecycle flow is `pp_early_init()` -> `amd_powerplay_create()` -> `hwmgr_early_init()`, then `pp_sw_init()` -> `hwmgr_sw_init()`, `pp_hw_init()` -> `hwmgr_hw_init()`, `pp_late_init()` task completion and optional SMU private buffer reservation. Fini/suspend/resume route through corresponding hwmgr calls and cancel the software critical-temperature delayed work. `pp_dpm_funcs` exposes firmware loading, forced performance levels, fan controls, pp_table get/set, manual clock forcing, OD controls, sensor reads, display clock/voltage requests, power gating, BACO, feature masks, reset, SMU I2C, metrics, and compute-clock recomputation.

## State, Persistence, And Dependencies
The file owns `adev->powerplay.pp_handle`, `adev->powerplay.pp_funcs`, `hwmgr->hardcode_pp_table`, UMD pstate bookkeeping, workload masks, power limits, and `adev->pm.smu_prv_buffer`. It depends on `hwmgr.h`, `amdgpu_dpm_internal.h`, Linux firmware/reboot/workqueue APIs, and amdgpu buffer helpers. The SW CTF delayed work may call `orderly_poweroff(true)` after rechecking hotspot or edge temperature.

## Risks And Test Signals
Notable risks are unchecked pp_table copy size in `pp_dpm_set_pp_table()`, missing function-pointer support returning mixed `0`, `-EINVAL`, `-EOPNOTSUPP`, or `-ENOENT`, and lifecycle races around delayed thermal work and private buffer mapping. Test signals include complete IP block init/fini, sysfs DPM controls, fan and sensor operations, pp_table override/reset behavior, display mode changes, BACO state transitions, and SW CTF shutdown behavior under thermal fault injection.
