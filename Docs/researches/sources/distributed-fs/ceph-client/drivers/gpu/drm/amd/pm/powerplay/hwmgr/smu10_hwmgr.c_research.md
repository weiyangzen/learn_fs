# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.c

## Purpose

This file implements the SMU10/Raven PowerPlay hardware manager. It bridges AMDGPU power-management operations to SMU messages, maintains SMU10 backend state, exposes sysfs clock controls, reports sensors, manages VCN/GFX/MMHUB/SDMA power gating, and wires SMU10 into the generic hwmgr and PowerPlay table interfaces.

## Important APIs, Types, and Functions

`smu10_init_function_pointers()` installs `smu10_hwmgr_funcs` and legacy `pptable_funcs`. Backend lifecycle is handled by `smu10_hwmgr_backend_init()` and `smu10_hwmgr_backend_fini()`. Clock and DPM control flows include `smu10_dpm_force_dpm_level()`, `smu10_force_clock_level()`, `smu10_emit_clock_levels()`, `smu10_set_fine_grain_clk_vol()`, and display-clock request helpers. Sensor and query paths include `smu10_read_sensor()`, `smu10_get_clock_by_type_with_latency()`, `smu10_get_clock_by_type_with_voltage()`, and `smu10_get_performance_level()`.

## Control Flow and State

Backend init allocates `struct smu10_hwmgr`, initializes default caps and DPM fields, copies the SMU clock table or falls back to hardcoded clock/voltage arrays, initializes DAL power-level dependencies, constructs basic platform descriptors, and enables overdrive sysfs. Runtime functions update cached hard/soft frequency limits before sending SMU messages. Forced DPM levels translate policy modes into hard-min and soft-max SMU requests for GFX, FCLK, SOCCLK, and VCN. Cleanup frees clock-voltage dependency tables, DAL dependency state, and the backend object.

## Dependencies and Integration

The file depends on SMU message IDs from `rv_ppsmc.h`, SMU table access through `smum_smc_table_manager`, AMDGPU IP powergating calls, SOC15 register reads, display watermarks, hwmgr function tables, and the legacy PowerPlay table parser. It is a major integration point between display requirements, sysfs power controls, firmware clock tables, and runtime SMU firmware capabilities.

## Risks and Test Signals

Many SMU message sends ignore return values, and some state is updated before firmware success is known. Firmware-version gates affect forced DPM and GPU-busy sensors. `smu10_disable_gfx_off()` waits in a loop until GFX reports on, so broken firmware/register state can stall. Test signals include sysfs `power_dpm_force_performance_level`, `pp_dpm_sclk`, `pp_dpm_mclk`, `pp_od_clk_voltage`, sensor reads, suspend/resume restoration, VCN power-state transitions, watermark programming, and SMU firmware version coverage across Raven/Picasso/Raven2.
