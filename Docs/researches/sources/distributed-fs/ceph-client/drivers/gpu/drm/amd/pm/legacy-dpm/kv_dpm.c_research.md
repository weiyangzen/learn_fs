# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c

## Purpose

`kv_dpm.c` implements the AMDGPU legacy Dynamic Power Management block for Kaveri/Kabini/Mullins era APU SMU hardware. It registers the `kv_smu_ip_block` SMC IP block, exposes `amd_pm_funcs` callbacks to the legacy PowerPlay layer, parses ATOM BIOS power tables, builds SMU7 fusion DPM tables, uploads those tables into SMC SRAM, controls SCLK/NB/UVD/VCE/SAMU/ACP DPM, handles thermal interrupts, and reports basic clocks/temperature through the PM sensor callbacks.

## Important APIs, Types, and Functions

The externally visible object is `const struct amdgpu_ip_block_version kv_smu_ip_block`, whose `amd_ip_funcs` point at `kv_dpm_early_init`, `kv_dpm_sw_init`, `kv_dpm_hw_init`, suspend/resume, and fini paths. `kv_dpm_early_init()` installs `kv_dpm_funcs` in `adev->powerplay.pp_funcs`, sets `pp_handle` to `adev`, and assigns thermal IRQ functions.

Core initialization is in `kv_dpm_init()`: it allocates `struct kv_power_info`, parses platform caps and extended PowerPlay tables through `legacy_dpm.c`, seeds defaults and capability flags, parses integrated system info, patches voltage units, constructs the boot power level, parses PPLIB states, and enables DPM. `kv_dpm_enable()` reads SMU firmware header offsets, initializes graphics/multimedia levels, uploads `SMU7_Fusion_DpmTable` fields, enables activity monitor/DPM/ULV/DIDT/CAC/BAPM state, and arms thermal interrupts when the internal Kaveri thermal controller is present.

Runtime callbacks include `kv_dpm_pre_set_power_state()`, `kv_dpm_set_power_state()`, `kv_dpm_post_set_power_state()`, `kv_dpm_force_performance_level()`, `kv_set_powergating_by_smu()`, `kv_check_state_equal()`, `kv_dpm_read_sensor()`, and debug print helpers. Local helpers cover VID conversion, ATOM clock divider lookup, deep-sleep divider calculation, DFS bypass, NB P-state settings, SCLK enable masks, VCE/UVD/SAMU/ACP boot levels, and SMU messages.

## Control Flow

Driver bring-up starts with `kv_dpm_sw_init()`, which registers legacy thermal IRQ IDs 230 and 231, initializes default DPM state to balanced/auto, and if `amdgpu_dpm` is enabled calls `kv_dpm_init()`. Hardware bring-up then enters `kv_dpm_hw_init()`: under `adev->pm.mutex` it calls `kv_dpm_setup_asic()`, `kv_dpm_enable()`, sets `adev->pm.dpm_enabled`, and invokes `amdgpu_legacy_dpm_compute_clocks()` to select and apply the initial state.

Power-state changes are driven by `legacy_dpm.c`. That layer chooses `adev->pm.dpm.requested_ps`, then calls this file's pre/set/post callbacks. The pre callback copies the requested `amdgpu_ps` and its `kv_ps` private state into persistent `kv_power_info` storage, then applies display, VCE, battery, stable-P-state, high-voltage, and NB policy adjustments. The set callback updates BAPM, computes valid SCLK ranges, recalculates deep-sleep and NB settings, freezes or forces SCLK as needed depending on ASIC type, uploads the edited SMU DPM table, programs NB indices, updates VCE/ACP/SCLK thresholds, enables NB DPM, and restores automatic levels. The post callback makes the requested state current.

Multimedia power gating flows through `kv_set_powergating_by_smu()` for UVD/VCE and through late init/disable for SAMU/ACP. UVD and VCE paths coordinate IP block gating with SMU power on/off messages and corresponding DPM enable/disable messages. ACP gating is skipped on Kabini/Mullins.

Thermal flow is interrupt-driven. `kv_set_thermal_temperature_range()` programs low/high thresholds in `ixCG_THERMAL_INT_CTRL`. `kv_dpm_process_interrupt()` maps source IDs 230/231 to direction flags and schedules `amdgpu_dpm_thermal_work_handler()`, which lives in `legacy_dpm.c` and may force an internal thermal power state.

## State and Persistence Behavior

Software state is stored primarily in `adev->pm.dpm` and `struct kv_power_info` at `adev->pm.dpm.priv`. `kv_power_info` caches BIOS-derived system info, dynamic capabilities, boot/current/requested power states, SCLK/NB/DPM level counts, generated SMU table entries, power-gating booleans, and thermal/DPM thresholds. Many fields are copied into SMU SRAM with `amdgpu_kv_copy_bytes_to_smc()` and then become firmware-owned runtime state until reset, suspend, disable, or another upload.

Persistent hardware state includes SMC SRAM DPM tables, SMC soft registers, SMC/DIDT/MMIO registers, thermal interrupt masks, and SMU-managed block power state. Suspend cancels thermal work, disables DPM, resets current/requested pointers to the boot state, and clears `dpm_enabled`; resume rebuilds ASIC state and reapplies clocks. Fini frees PPLIB private states, the power-info object, and extended PowerPlay allocations.

## Dependencies and Integration Points

This file depends on AMDGPU device, IRQ, PM, ATOM BIOS, and display infrastructure; CIK/KV register headers; SMU7 fusion table definitions from `smu7_fusion.h`; SMC message IDs from `ppsmc.h`; and helper declarations from `kv_dpm.h` and `legacy_dpm.h`. It uses `RREG32`, `WREG32`, `RREG32_SMC`, `WREG32_SMC`, `RREG32_DIDT`, `WREG32_DIDT`, ATOM `GetIndexIntoMasterTable`, `amdgpu_atombios_get_clock_dividers()`, `amdgpu_device_ip_set_powergating_state()`, `amdgpu_irq_add_id/get/put()`, and `amdgpu_gfx_rlc_enter_safe_mode()`.

Integration with the rest of AMDGPU is through the IP block list, `adev->powerplay.pp_funcs`, PM mutex, DPM state machine in `legacy_dpm.c`, UVD/VCE power-gating callbacks, debugfs PM printing, and sensor reads for `AMDGPU_PP_SENSOR_GFX_SCLK` and `AMDGPU_PP_SENSOR_GPU_TEMP`.

## Risks and Edge Cases

The code trusts many BIOS table offsets and counts. Bad ATOM data can lead to missing boot states, empty dependency tables, or out-of-range level assumptions. Several loops index arrays sized for SMU7 maximum levels, while inputs come from BIOS table counts, so count validation is critical. SMU SRAM writes require correct endianness and bounds; a wrong `dpm_table_start` or `sram_end` can corrupt firmware memory. Runtime paths ignore some SMU message return values, especially in power-gating helpers, so partial failures may leave software booleans out of sync with hardware. Thermal register programming uses fixed `KV_TEMP_RANGE_MIN/MAX` and direct SMC register fields. DIDT support is compiled in but disabled by `pi->enable_didt = false`, so enabling it later would need hardware validation.

Kabini/Mullins take a different SCLK forcing path than other Kaveri parts; regressions in this branch can show up only on those ASICs. ACP gating deliberately returns on Kabini/Mullins. `kv_get_acp_boot_level()` always returns zero, which may be too simple for future ACP tables.

## Test Signals

Useful signals are a kernel build with legacy DPM enabled, boot logs showing `dpm initialized`, successful SMU messages during `kv_dpm_hw_init()`, populated `/sys/kernel/debug/dri/*/amdgpu_pm_info` or equivalent debugfs output, and sensor reads returning current SCLK and millidegree temperature. Runtime testing should cover AC/DC state changes, forced low/high/auto performance levels, suspend/resume, thermal IRQ handling, UVD/VCE playback power-gating, SAMU/ACP late powerdown, multi-display transitions, and Kabini/Mullins-specific NB DPM behavior.
