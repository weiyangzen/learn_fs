# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr.c

## Purpose
`hwmgr.c` owns legacy PowerPlay hardware-manager lifecycle and ASIC selection. It initializes default capabilities, applies feature-mask policy, chooses SMU manager and hardware-manager backends by family/chip, initializes pptables/backends/PSM, enables DPM and thermal control, handles suspend/resume, and dispatches high-level power-management tasks.

## Important APIs And Control Flow
`hwmgr_early_init()` sets defaults, workload priorities, OD/DPM levels, disables unsupported feature bits, handles Bonaire quirks, chooses SMU function tables, and calls ASIC init hooks. `hwmgr_sw_init()` registers IRQs and calls SMU init. `hwmgr_hw_init()` computes SR-IOV/PM enablement, initializes pptables and backend, repairs DC max clocks from AC if needed, initializes PSM, sets up ASIC, enables dynamic state management, starts thermal control, and sets performance states. `hwmgr_hw_fini()`, `hwmgr_suspend()`, and `hwmgr_resume()` unwind or restore this sequence. `hwmgr_handle_task()` handles display changes, user state requests, complete init, and power-state readjustment.

## State, Dependencies, And Integration
It mutates `pp_hwmgr` fields such as `pm_en`, `pp_one_vf`, `feature_mask`, `platformCaps`, `smumgr_funcs`, `dpm_level`, workload priority arrays, OD enablement, and `adev->pm.dpm_enabled`. It depends on PSM helpers, PHM wrappers, ACPI PCIe capability checks, SR-IOV/passthrough helpers, ASIC SMU function tables, and ASIC hwmgr initialization functions.

## Risks And Test Signals
Risks include unsupported chip selection returning `-EINVAL`, partial init cleanup correctness, feature-mask/capability mismatches, special-case quirks affecting DPM coverage, and suspend/resume ordering. Test signals are successful init across CI/CZ/VI/AI/RV devices, correct feature masks, working PSM transitions, display reconfiguration without underclocking, and clean hw_fini/suspend/resume with no DPM hangs.
