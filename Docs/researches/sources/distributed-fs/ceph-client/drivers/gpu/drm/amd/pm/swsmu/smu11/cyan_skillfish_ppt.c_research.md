<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c

## Purpose

`cyan_skillfish_ppt.c` is the Cyan Skillfish SMU11.8/APU-specific PPT implementation. It provides a small SMU message/table map, metrics table allocation, sensor and GPU metrics export, clock-level reporting, simple OverDrive SCLK/VDDC editing, DPM-running detection, and a function-table installer that marks the SMU as APU.

## Important APIs, Types, and Functions

Key constants are `CYAN_SKILLFISH_SCLK_MIN/MAX`, `CYAN_SKILLFISH_VDDC_MIN/MAX`, and `CYAN_SKILLFISH_VDDC_MAGIC`. Static state includes `cyan_skillfish_user_settings` and `cyan_skillfish_sclk_default`. Important functions are `cyan_skillfish_tables_init`, `cyan_skillfish_init_smc_tables`, `cyan_skillfish_get_smu_metrics_data`, `cyan_skillfish_read_sensor`, `cyan_skillfish_get_current_clk_freq`, `cyan_skillfish_emit_clk_levels`, `cyan_skillfish_is_dpm_running`, `cyan_skillfish_get_gpu_metrics`, `cyan_skillfish_od_edit_dpm_table`, `cyan_skillfish_get_dpm_ultimate_freq`, `cyan_skillfish_get_enabled_mask`, and `cyan_skillfish_set_ppt_funcs`.

## Control Flow

`cyan_skillfish_set_ppt_funcs` assigns the Cyan Skillfish function table, table map, APU flag, driver-interface version, and message control map. `init_smc_tables` allocates the SMU metrics table and driver GPU metrics cache, then delegates to common SMU11 table init. Sensor and metrics calls fetch `SmuMetrics_t` through `smu_cmn_get_metrics_table` and convert fields into AMDGPU sensor units or GPU metrics v2.2. OD editing stages values in static user settings, validates ranges, and commits by sending `RequestGfxclk` and either `ForceGfxVid` or `UnforceGfxVid`.

## State and Persistence Behavior

Driver state includes cached metrics, GPU metrics driver table, static user OD settings, default SCLK discovered from metrics, and `smu->is_apu = true`. Firmware state changes when requested GFX clock or forced VID messages are sent. The `get_enabled_mask` hook reports all feature bits as enabled rather than querying per-feature support.

## Dependencies

The file depends on AMDGPU core, `amdgpu_smu.h`, SMU11 common helpers, Cyan Skillfish PMFW/driver interface headers, `smu_v11_8_ppsmc.h`, `smu_v11_8_pmfw.h`, `smu_cmn`, and SOC15 common definitions. It assumes the SMU11.8 metrics layout with `Current` and `Average` nested members.

## Integration Points

Compiled through `smu11/Makefile`, it integrates with AMDGPU APU power management, hwmon sensors, GPU metrics, OverDrive sysfs for SCLK/VDDC, common SMU11 IRQ/memory-table handling, and DPM feature checks.

## Risks and Edge Cases

OD settings are file-static, so multi-device Cyan Skillfish systems would share staged settings. The default SCLK is lazily captured and reset during suspend by returning DPM-not-running. Voltage conversion to SVI2 VID must preserve PMFW units. `get_enabled_mask` filling all bits can hide unsupported-feature distinctions from generic callers. Sensor unit conversions differ from Arcturus and must match the SMU11.8 metrics layout.

## Test Signals

Build and boot on Cyan Skillfish, metrics table reads, hwmon sensors for clocks/power/temperature/voltage, GPU metrics v2.2 fields, OD range output, SCLK/VDDC commit/restore behavior, suspend/resume DPM reinit, and firmware response to `RequestGfxclk`/VID messages validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/cyan_skillfish_ppt.c -->
