# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu12/renoir_ppt.c

## Purpose

`renoir_ppt.c` implements the Renoir APU-specific SMU12 PowerPlay policy layer. It maps common SMU messages, clocks, tables, workloads, and sensors to Renoir firmware interfaces and provides callbacks for DPM clock reporting/control, power profiles, watermarks, multimedia power gating, GPU metrics, overdrive, GFXOFF, and VBIOS boot values.

## Important APIs, Types, and Functions

The exported entry point is `renoir_set_ppt_funcs`, which installs `renoir_ppt_funcs`, clock/table/workload maps, the SMU12 driver interface version, APU flag, and SMU12 message control.

Important functions include `renoir_init_smc_tables`, `renoir_get_dpm_clk_limited`, `renoir_get_dpm_ultimate_freq`, `renoir_od_edit_dpm_table`, `renoir_set_fine_grain_gfx_freq_parameters`, `renoir_emit_clk_levels`, `renoir_dpm_set_vcn_enable`, `renoir_dpm_set_jpeg_enable`, `renoir_force_dpm_limit_value`, `renoir_unforce_dpm_levels`, `renoir_get_dpm_clock_table`, `renoir_force_clk_levels`, `renoir_set_power_profile_mode`, `renoir_set_performance_level`, `renoir_set_watermarks_table`, `renoir_get_smu_metrics_data`, `renoir_read_sensor`, `renoir_is_dpm_running`, `renoir_get_gpu_metrics`, and `renoir_get_enabled_mask`.

Key firmware structures are `DpmClocks_t`, `Watermarks_t`, `SmuMetrics_t`, and `struct gpu_metrics_v2_2`.

## Control Flow

Initialization defines SMU watermarks, DPM clocks, and metrics tables, allocates CPU-side copies, and registers a GPU metrics cache. Clock maximum/minimum discovery reads firmware min/max messages for GFXCLK and uses DPM clock table indexes for FCLK/UCLK/SOCCLK/VCN clocks. When DPM for a clock is disabled, boot VBIOS values are returned instead.

DPM sysfs emission starts by refreshing `SmuMetrics_t`, then prints OD ranges, synthetic GFX min/current/max levels, or table-based levels for SOCCLK, MCLK/FCLK, DCFCLK, VCLK, and DCLK. MCLK/FCLK levels are printed in reverse order.

Performance level changes set hard-min and soft-max clock constraints through `smu_v12_0_set_soft_freq_limited_range` or direct SMU messages. Standard profile programs fixed UMD P-state constants for GFX/FCLK/SOCCLK/VCN; min and peak profiles derive per-clock targets. Manual overdrive is only accepted when DPM level is manual, stages min/max GFX frequencies, and commits by sending hard-min and soft-max GFX messages.

Watermark handling validates reader/writer counts, copies DC ranges and watermark types into the Renoir watermark table, then uploads once using the watermark bitmap state.

Metrics and sensor paths refresh the SMU metrics table, map clocks/activity/temperature/voltage/power values into common sensor units, compute smart-shift APU/dGPU share percentages, and populate `gpu_metrics_v2_2`.

## State and Persistence Behavior

Allocated state includes `clocks_table`, `metrics_table`, `watermarks_table`, and the GPU metrics cache. Runtime policy state includes staged/current GFX OD min/max, watermark bitmap flags, and `smu->is_apu`. Firmware state is modified for VCN/JPEG power gates, soft/hard clock limits, workload mask, watermarks, GFXOFF, SDMA power gating, CGPG, and mode2 reset.

## Dependencies

The file depends on SMU12 firmware message and driver-interface headers, common SMU helpers, `smu_v12_0.c` common functions, AMDGPU PM objects, sysfs formatting, and Renoir firmware table definitions.

## Integration Points

`renoir_ppt_funcs` plugs into AMDGPU powerplay for Renoir APUs. It delegates common operations to `smu_v12_0_*`, including firmware status, SDMA power gating, GFX CGPG/OFF, table finalization/default load, DPM range programming, driver table address, mode2 reset, and VBIOS boot parsing. DC consumes watermark and DPM clock table callbacks; hwmon/sysfs consumers use sensors, GPU metrics, OD, and DPM controls.

## Risks and Edge Cases

Renoir reports all feature bits enabled through `renoir_get_enabled_mask`, because PMFW lacks early APU feature-mask export; this can hide unsupported feature combinations. Power unit conversion for current socket power depends on MP1 IP version and firmware version. `renior_set_dpm_profile_freq` is misspelled but internal. Some profile helper calls ignore return values in min-profile branches. Watermarks are uploaded only once after `WATERMARKS_LOADED`. GFXCLK exposes synthetic three-level DPM even though firmware provides min/max plus current, so user masks above level 2 are rejected.

## Test Signals

Validation should include Renoir boot and SMU12 firmware status, DPM sysfs level output for all supported clocks, force-clock masks, OD edit/commit/restore, standard/min/peak performance profiles, VCN/JPEG/SDMA power-gating, DC watermark programming, GFXOFF status transitions, GPU metrics v2.2 content, smart-shift sensors, suspend/resume DPM-running behavior, and mode2 reset.
