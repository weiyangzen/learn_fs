# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm.c

## Purpose
`amdgpu_dpm.c` is the public AMDGPU dynamic power-management dispatch layer. It exposes driver-facing helpers for clocks, power gating, BACO and reset flows, power profiles, sensors, fan and power limits, display clock requests, metrics, overdrive, multimedia block enablement, and SMU-specific maintenance operations. Most functions validate support, lock `adev->pm.mutex`, call an operation from `adev->powerplay.pp_funcs` or a SW SMU helper, and translate unsupported paths into standard negative errno values.

## Important APIs and Functions
Clock and DPM state helpers include `amdgpu_dpm_get_sclk`, `amdgpu_dpm_get_mclk`, `amdgpu_dpm_compute_clocks`, `amdgpu_dpm_get_dpm_freq_range`, `amdgpu_dpm_set_soft_freq_range`, clock-level emit/force helpers, overdrive SCLK/MCLK getters/setters, and display clock functions such as `amdgpu_dpm_get_display_mode_validation_clks`, `amdgpu_dpm_set_watermarks_for_clocks_ranges`, `amdgpu_dpm_display_clock_voltage_request`, `amdgpu_dpm_set_min_deep_sleep_dcefclk`, hard-min DCEFCLK/FCLK setters, UCLK DPM state retrieval, and DPM clock table retrieval.

Power and reset APIs include `amdgpu_dpm_set_powergating_by_smu`, `amdgpu_dpm_set_gfx_power_up_by_imu`, BACO enter/exit/reset/capability functions, mode1/mode2/link reset support and execution, `amdgpu_dpm_set_mp1_state`, SDMA/VCN reset support and execution, XGMI/DF C-state setters, GFX state change notification, and multimedia enable wrappers for UVD, VCN, VCE, JPEG, and VPE. User and policy APIs include performance-level get/force, UMD state entry/exit, PM policy get/set, power profile switch/pause/get/set, ppfeature status, pp table get/set, and PowerPlay task dispatch.

Telemetry and controls include sensor read, APU thermal limit get/set, thermal throttling counter, ECC and RAS SMU driver access, GPU/PM/temp/XCP metrics, fan mode and speed controls, power limit get/set, overdrive support/enabled probes, CPU core count, SMU private buffer details, STB debugfs init, and debugfs performance-level printing.

## Control Flow and State
The dominant control flow is guarded dispatch. Functions first check feature support through `pp_funcs`, `is_support_sw_smu(adev)`, SR-IOV state, APU flags, `adev->scpm_enabled`, or device family. Supported paths take `adev->pm.mutex`, call the backend, release the mutex, and return the backend result. Unsupported legacy paths usually return `0`, `-EOPNOTSUPP`, `-ENOENT`, `-EINVAL`, or `-ENOSYS` depending on the interface contract.

Local state updates are narrow but important. `amdgpu_dpm_set_powergating_by_smu` tracks per-IP power state in `adev->pm.pwr_state`. `amdgpu_dpm_set_mp1_state` disables DPM for SR-IOV VFs on FLR. ACPI events update `adev->pm.ac_power` and notify BAPM/SW SMU AC-DC state. SI-family UVD/VCE enable paths update `adev->pm.dpm.uvd_active`, `vce_active`, `vce_level`, and power state before recomputing clocks. Forced performance-level changes update `adev->pm.dpm.forced_level` and may gate or ungate GFX around UMD profile modes. `amdgpu_dpm_set_power_state` stores the user-selected PM state for non-SW-SMU legacy dispatch.

## Dependencies and Integration Points
The file includes core AMDGPU headers, AtomBIOS, I2C, display, PowerPlay `hwmgr.h`, Linux power supply APIs, and SW SMU helpers. It integrates with `struct amd_pm_funcs` backends, `struct smu_context`, DRM display mode state, AMDGPU rings and fences, SR-IOV handling, reset paths, debugfs, sysfs-facing PM controls, multimedia IP power management, and RAS. `amdgpu_dpm_compute_clocks` also waits for ready rings to drain before invoking backend clock recomputation.

## Risks
The biggest risk is backend contract mismatch: many wrappers assume `adev->powerplay.pp_funcs` and `pp_handle` are valid, and some call members without checking the top-level `pp_funcs` pointer. Locking must remain consistent because these operations touch firmware, MMIO, and shared PM state. Some helpers return success when unsupported while others return an error, so callers must preserve existing semantics. Power-gating cache logic is special for multi-instance VCN and could incorrectly skip operations if generalized. UMD profile transitions must undo GFX gate changes if backend forcing fails. SR-IOV, S3/BACO, APU, and legacy SI paths all have explicit exceptions that are easy to regress.

## Test Signals
Build with AMDGPU PM enabled and exercise sysfs/debugfs PM controls. Runtime tests should cover SW SMU and legacy PowerPlay ASICs, SR-IOV VF behavior, BACO and mode1/mode2/link resets, UVD/VCN/VCE/JPEG/VPE power gating, AC/DC power supply events, display reconfiguration and watermark updates, overdrive table read/write where supported, fan and power-limit controls, sensor/metrics reads, and suspend/resume. Lockdep and fault-injection around backend failures are valuable because most code paths are lock-wrapped firmware dispatches.
