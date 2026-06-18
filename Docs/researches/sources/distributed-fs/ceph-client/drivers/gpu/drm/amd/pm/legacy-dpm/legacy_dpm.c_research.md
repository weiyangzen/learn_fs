# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.c

## Purpose

`legacy_dpm.c` implements shared infrastructure for AMDGPU legacy PowerPlay/DPM ASICs. It parses ATOM PowerPlay tables into `adev->pm.dpm` dynamic state, registers thermal controller information, prints/debugs power states, chooses requested power states from user/internal conditions, coordinates pre/set/post DPM callbacks, computes clocks, and handles thermal workqueue transitions.

## Important APIs and Functions

Debug helpers are `amdgpu_dpm_dbg_print_class_info()`, `amdgpu_dpm_dbg_print_cap_info()`, `amdgpu_dpm_dbg_print_ps_status()`, and `amdgpu_pm_print_power_states()`. BIOS parsing APIs are `amdgpu_get_platform_caps()`, `amdgpu_parse_extended_power_table()`, and `amdgpu_free_extended_power_table()`. `amdgpu_add_thermal_controller()` parses the PPLIB thermal controller record, configures internal thermal type or creates an external I2C client. `amdgpu_get_vce_clock_state()` returns a parsed VCE state by index.

The runtime state machine is centered on `amdgpu_dpm_pick_power_state()`, `amdgpu_dpm_change_power_state_locked()`, `amdgpu_legacy_dpm_compute_clocks()`, and `amdgpu_dpm_thermal_work_handler()`.

## Control Flow

ASIC-specific DPM init calls the parsing helpers to fill `adev->pm.dpm.platform_caps`, response times, fan parameters, dependency tables, CAC/leakage data, VCE/UVD/SAMU/ACP dependency tables, PPM and PowerTune data, and VDDGFX-on-SCLK data when present. Each allocation is later released by `amdgpu_free_extended_power_table()`.

When clocks need recomputing, `amdgpu_legacy_dpm_compute_clocks()` updates display configuration if DC is disabled, then calls `amdgpu_dpm_change_power_state_locked()`. That function rejects work if DPM is disabled, reconciles user state with active thermal/UVD overrides, chooses a matching power state, prints transitions when verbose DPM is enabled, sets VCE active flags, calls ASIC-specific display/pre callbacks, optionally skips if current/requested states compare equal, calls ASIC-specific `set_power_state`, then post callback, then reapplies forced performance level or thermal low forcing.

Thermal interrupts schedule `amdgpu_dpm_thermal_work_handler()`. The work item reads GPU temperature through the ASIC `read_sensor` callback when possible, chooses internal thermal state or user state, updates `thermal_active` and `adev->pm.dpm.state`, and recomputes clocks under `adev->pm.mutex`.

## State and Persistence Behavior

This file populates persistent driver state under `adev->pm.dpm`, including platform caps, fan info, dynamic dependency tables, VCE states, thermal type, current/requested/boot power-state pointers, and thermal active flags. It allocates heap arrays for variable-length BIOS tables and owns their cleanup. It does not directly program SMU DPM tables; instead it calls ASIC-specific callbacks through `adev->powerplay.pp_funcs`.

External I2C thermal controller registration creates kernel I2C device state. Power-state changes persist in the ASIC-specific hardware only after the selected PM callbacks run.

## Dependencies and Integration Points

The file depends on `amdgpu.h`, ATOM BIOS definitions, `amdgpu_i2c`, `amd_pcie`, `amdgpu_display`, `amdgpu_dpm_internal`, and the legacy DPM header. Its macro wrappers call `adev->powerplay.pp_funcs` entries installed by ASIC files such as `kv_dpm.c`. It integrates with display configuration, PM mutex locking, I2C thermal drivers, VCE state users, and debug logging.

## Risks and Edge Cases

ATOM parsing uses many raw offsets into the BIOS image. Incorrect table sizes, revisions, or offsets can cause invalid reads or partial dynamic state. Several allocations happen sequentially; callers must use the free helper on failures to avoid leaks. `amdgpu_dpm_pick_power_state()` has layered fallbacks, so missing specialized UVD/thermal/ACPI states may silently degrade to performance or battery. The equality fast path returns before post callbacks and forced-level reapply, so ASIC `check_state_equal` semantics must be conservative. Thermal work relies on `read_sensor`; if unavailable, it falls back to interrupt direction.

## Test Signals

Test signals include successful parsing of fan/dependency/VCE/UVD/SAMU/ACP tables from real VBIOS images, no memory leaks on init failure and fini, correct `/sys` or debugfs power-state listing, user state changes mapping to expected PPLIB classes, UVD/VCE state selection during media workloads, external thermal I2C device creation when present, and thermal interrupt work switching into and out of thermal states.
