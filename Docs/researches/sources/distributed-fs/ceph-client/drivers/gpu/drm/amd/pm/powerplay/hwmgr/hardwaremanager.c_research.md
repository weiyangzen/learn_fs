# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hardwaremanager.c

## Purpose
`hardwaremanager.c` provides generic Power Hardware Manager (`phm_*`) wrappers over ASIC-specific `hwmgr_func` callbacks. It centralizes null/function checks, thermal range propagation into `adev->pm.dpm.thermal`, display configuration storage, clock queries, and generic state-management calls used by `hwmgr.c` and `amd_powerplay.c`.

## Important APIs And Control Flow
Key wrappers include `phm_setup_asic()`, `phm_power_down_asic()`, `phm_set_power_state()`, dynamic state enable/disable, `phm_force_dpm_levels()`, display pre/change notification, thermal start/stop, IRQ registration, clock queries by performance level/type/latency/voltage, display clock voltage requests, watermarks, and SMC CTF disable. `phm_start_thermal_controller()` begins with a default 0 to 80 C range, lets the backend override it, starts thermal control if the capability is set, and copies all critical/emergency limits into amdgpu PM state.

## State, Dependencies, And Integration
The file mutates `hwmgr->platform_descriptor`, `hwmgr->adev->pm.dpm.thermal`, display active-count state, CC6 data, and backend power-management state via callbacks. It depends on `hwmgr.h`, `hardwaremanager.h`, `power_state.h`, `pp_debug.h`, ACPI/pass-through checks, and `smum_is_dpm_running()`.

## Risks And Test Signals
Risks are inconsistent return conventions for optional callbacks, default thermal ranges being unsafe if backend range retrieval fails, VF/pass-through/suspend skip logic, and capability flags not matching backend support. Test signals include DPM enable/disable, thermal sysfs limits, fan control startup, display hotplug/reconfiguration, clock query correctness, and stable suspend/resume paths.
