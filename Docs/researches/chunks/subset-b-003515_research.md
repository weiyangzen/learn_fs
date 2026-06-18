# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c lines 7998-8155

## Purpose

This chunk is the public binding tail for Southern Islands legacy DPM. It finishes wiring the SI DPM implementation into AMDGPU by registering the PowerPlay callback table, the SMC/IP block callback table, thermal interrupt callbacks, state comparison logic, and sysfs/debugfs sensor reads. Most heavy clock, voltage, SMC-table, fan, and transition logic lives earlier in `si_dpm.c`; these lines expose that implementation through the common AMDGPU PM and IP block interfaces.

## Important APIs, Types, and Functions

- `si_dpm_early_init(struct amdgpu_ip_block *ip_block)` installs `si_dpm_funcs` into `adev->powerplay.pp_funcs`, sets `adev->powerplay.pp_handle = adev`, and calls `si_dpm_set_irq_funcs()`. This is the early bridge from the IP block framework to the legacy PM callback table.
- `si_are_power_levels_equal(const struct rv7xx_pl *, const struct rv7xx_pl *)` compares one software performance level by `mclk`, `sclk`, `pcie_gen`, `vddc`, and `vddci`.
- `si_check_state_equal(void *handle, void *current_ps, void *request_ps, bool *equal)` is the `amd_pm_funcs.check_state_equal` implementation. It validates arguments, unwraps `struct amdgpu_ps.ps_priv` into `struct si_ps`, compares performance-level counts and all `struct rv7xx_pl` entries, then uses UVD/VCE clocks as tie breakers.
- `si_dpm_read_sensor(void *handle, int idx, void *value, int *size)` is the legacy sensor callback. It supports `AMDGPU_PP_SENSOR_GFX_SCLK`, `AMDGPU_PP_SENSOR_GFX_MCLK`, and `AMDGPU_PP_SENSOR_GPU_TEMP`; other sensor IDs return `-EOPNOTSUPP`.
- `si_dpm_ip_funcs` exposes the SI DPM IP-block lifecycle (`early_init`, `late_init`, `sw_init`, `hw_init`, suspend/resume, idle, clockgating, powergating).
- `si_smu_ip_block` publishes the block as `AMD_IP_BLOCK_TYPE_SMC` with version `6.0.0`, using `si_dpm_ip_funcs`.
- `si_dpm_funcs` is the central `struct amd_pm_funcs` dispatch table for legacy PM operations: power-state transition, display change handling, clock reads, debug output, forced performance levels, fan control, VCE state lookup, sensor reads, and legacy DPM clock recomputation.
- `si_dpm_irq_funcs` and `si_dpm_set_irq_funcs()` attach SI thermal IRQ `.set`/`.process` handlers to `adev->pm.dpm.thermal.irq`.

Key data types come from this file and `si_dpm.h`: `struct amdgpu_device`, `struct amdgpu_ip_block`, `struct amdgpu_ps`, `struct evergreen_power_info`, `struct ni_power_info`, `struct si_ps`, and `struct rv7xx_pl`.

## Control Flow

During IP discovery/initialization, the SMC block represented by `si_smu_ip_block` is driven through `si_dpm_ip_funcs`. The earliest SI-specific handoff is `si_dpm_early_init()`, which stores the SI legacy PM callback table in `adev->powerplay` and registers thermal interrupt operations. Later generic AMDGPU PM entry points call through `adev->powerplay.pp_funcs` into the functions listed in `si_dpm_funcs`.

Power-state equality is evaluated by `si_check_state_equal()`. The caller passes generic `struct amdgpu_ps` pointers; the function converts them to SI-private `struct si_ps` objects through `si_get_ps()`. It fails fast on null public inputs, reports inequality when the current SI state is absent, checks that both states have the same number of performance levels, then walks each performance level. Only if all levels match does it compare multimedia clocks (`vclk`/`dclk` for UVD and `evclk`/`ecclk` for VCE). The result is returned through the caller-supplied `bool *equal`; the function returns `0` for a successful comparison path even when the states are unequal.

Sensor reads use the current active legacy Radeon power state from `evergreen_get_pi(adev)->current_rps`. For SCLK and MCLK, the hardware register `mmTARGET_AND_CURRENT_PROFILE_INDEX` is read with `RREG32()`, masked by `TARGET_AND_CURRENT_PROFILE_INDEX__CURRENT_STATE_INDEX_MASK`, shifted, and used as an index into `ps->performance_levels`. If the index is in range, the selected level's `sclk` or `mclk` is copied to the caller's `uint32_t` buffer and `*size` is set to 4. Temperature delegates to `si_dpm_get_temp()`, which reads the thermal status register in the preceding chunk and returns millidegrees Celsius.

## State and Persistence Behavior

This chunk does not allocate or free long-lived state, but it exposes and relies on persistent DPM state owned by `adev->pm.dpm.priv`. `evergreen_get_pi()` returns that private state as `struct evergreen_power_info`; for SI devices it is embedded at the front of `struct ni_power_info`, which also stores `current_ps` and `requested_ps`. Earlier state-copy helpers keep `eg_pi->current_rps.ps_priv` and `eg_pi->requested_rps.ps_priv` pointed at those SI-private snapshots.

The callback tables themselves are static and immutable after compilation. Runtime registration persists through pointers stored in `adev->powerplay.pp_funcs`, `adev->powerplay.pp_handle`, and `adev->pm.dpm.thermal.irq`. Sensor results are transient reads from the current software state plus hardware profile-index/thermal registers; they do not update cached clocks or requested/current power states.

## Dependencies and Integration Points

- AMDGPU IP framework consumes `si_smu_ip_block` and calls `si_dpm_ip_funcs`.
- Generic DPM and sysfs/debugfs code consume `adev->powerplay.pp_funcs`, especially `read_sensor`, `check_state_equal`, fan methods, forced performance levels, and `pm_compute_clocks`.
- Thermal management uses `si_dpm_irq_funcs` through `adev->pm.dpm.thermal.irq` and also calls `read_sensor(AMDGPU_PP_SENSOR_GPU_TEMP)` to decide whether thermal throttling can be cleared.
- Hwmon and debugfs clock reporting call `amdgpu_dpm_read_sensor()` or `amdgpu_pm_get_sensor_generic()`, which eventually dispatch to `si_dpm_read_sensor()` for `AMDGPU_PP_SENSOR_GFX_SCLK`, `AMDGPU_PP_SENSOR_GFX_MCLK`, and `AMDGPU_PP_SENSOR_GPU_TEMP`.
- Hardware register dependencies include `mmTARGET_AND_CURRENT_PROFILE_INDEX` for the active performance index and the thermal status register used by `si_dpm_get_temp()`. Register masks and shifts come from AMD SMU register headers.
- Function pointers in `si_dpm_funcs` integrate many earlier functions in the same file, including power-state transitions, display reconfiguration, clock getters, fan control, VBlank checks, and debug printing.

## Risks and Edge Cases

- `si_check_state_equal()` validates the current SI-private state pointer but does not explicitly validate `si_rps` after `si_get_ps(rps)`. A malformed requested power state with a null `ps_priv` could be dereferenced during count or level comparison.
- `si_dpm_read_sensor()` checks `*size < 4` but assumes `size`, `value`, `eg_pi`, `rps->ps_priv`, and the SI-private `ps` pointer are valid. The generic PM callers normally satisfy this, but the callback itself is not defensive against all invalid inputs.
- The sensor clock path trusts the hardware current-state index. It bounds the index against `performance_level_count`, returning `-EINVAL` if out of range, which prevents a performance-level array overread but can make hwmon/debugfs clock files fail while hardware/SMC state is inconsistent.
- Equality ignores fields outside the compared set, such as `dc_compatible`, `flags`, and broader `amdgpu_ps` class/capability metadata. That is intentional for transition deduplication only if those omitted fields do not require hardware reprogramming.
- The temperature path reports the legacy SI thermal register result in millidegrees. Any sensor calibration or invalid thermal register behavior is inherited from `si_dpm_get_temp()`.
- IP block versioning is fixed at SMC `6.0.0`; wrong ASIC matching outside this file would attach these callbacks to incompatible hardware.

## Test Signals

- Boot or driver probe on SI hardware should show the SMC/IP block initializing successfully, with `adev->powerplay.pp_funcs` populated by `si_dpm_early_init()` and thermal IRQ function pointers installed.
- Hwmon/debugfs reads for SCLK, MCLK, and GPU temperature should succeed when DPM is enabled; unsupported sensor IDs should return `-EOPNOTSUPP` through the generic PM wrappers.
- Power-state changes that only repeat the same SI performance levels and UVD/VCE clocks should be detected as equal by `check_state_equal`; changes in any level's `sclk`, `mclk`, `pcie_gen`, `vddc`, `vddci`, or multimedia clocks should be reported unequal.
- Fault-injection or register-stability tests can validate that an out-of-range `CURRENT_STATE_INDEX` causes clock sensor reads to return `-EINVAL` rather than indexing beyond `performance_levels`.
- Suspend/resume and thermal interrupt tests should still route through the function tables in this chunk, confirming that the callback registration remains intact across PM lifecycle transitions.
