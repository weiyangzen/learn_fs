# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c

## Purpose

`vangogh_ppt.c` implements the Vangogh APU-specific SMU11.5 PowerPlay table policy layer. It maps common SMU abstractions to Vangogh firmware messages, features, tables, workloads, metrics, DPM clocks, sensors, overdrive, watermarks, GFXOFF, power limits, and post-init WGP power-saving behavior, then installs those callbacks with `vangogh_set_ppt_funcs`.

## Important APIs, Types, and Functions

The central API is `vangogh_set_ppt_funcs`, which assigns `vangogh_ppt_funcs`, feature/table/workload maps, marks `smu->is_apu = true`, sets `SMU13_DRIVER_IF_VERSION`, and initializes SMU11 message control with `vangogh_message_map`.

Important functions include `vangogh_tables_init`, `vangogh_init_smc_tables`, `vangogh_dpm_set_vcn_enable`, `vangogh_dpm_set_jpeg_enable`, `vangogh_is_dpm_running`, `vangogh_common_get_smu_metrics_data`, `vangogh_common_emit_clk_levels`, `vangogh_get_dpm_ultimate_freq`, `vangogh_set_power_profile_mode`, `vangogh_set_soft_freq_limited_range`, `vangogh_force_clk_levels`, `vangogh_set_performance_level`, `vangogh_read_sensor`, `vangogh_set_watermarks_table`, `vangogh_common_get_gpu_metrics`, `vangogh_od_edit_dpm_table`, `vangogh_set_default_dpm_tables`, `vangogh_set_fine_grain_gfx_freq_parameters`, `vangogh_post_smu_init`, `vangogh_mode2_reset`, GFXOFF residency/entry helpers, and Vangogh-specific power-limit helpers.

Important firmware data types include `SmuMetrics_t`, `SmuMetrics_legacy_t`, `DpmClocks_t`, `Watermarks_t`, `DpmActivityMonitorCoeffExt_t`, `struct gpu_metrics_v2_2`, `v2_3`, `v2_4`, and `struct smu_11_5_power_context`.

## Control Flow

Initialization registers SMU tables for watermarks, DPM clocks, PM status log, activity monitor coefficients, and SMU metrics, then allocates CPU-side metrics, watermarks, clocks, GPU metrics cache, and a SMU11 DPM context. CPU core count comes from x86 topology when available.

Metrics reads branch on `smu->smc_fw_if_version`: legacy firmware uses `SmuMetrics_legacy_t`, newer firmware uses nested current/average `SmuMetrics_t`. GPU metrics selection also branches on SMU program/version to expose v2.2, v2.3, or v2.4 layouts.

DPM clock queries read `DpmClocks_t`, with reverse indexing for FCLK/MCLK DF pstates. GFXCLK is treated as fine-grained min/current/max rather than a full DPM table. Soft range setting sends clock-specific min/max messages; VCN combines VCLK into high 16 bits and DCLK into low 16 bits of VCN parameters.

Performance-level control resets CPU soft limits, sets GFX hard min/soft max according to high/low/auto/profile modes, optionally forces FCLK/SOCCLK/VCN DPM levels, and for firmware `>= 0x43f1b00` sends per-core CCLK soft min/max messages. Manual overdrive edits only stage values until commit sends GFX and optional CPU CCLK constraints.

Post-init enables GFXOFF when GFX DPM and power gating are available; otherwise it clears `PP_GFXOFF_MASK`. It then optionally requests active WGP count based on CU count and `RLC_PG_ALWAYS_ON_WGP_MASK`.

Watermark setup validates reader/writer counts, copies DC ranges into the firmware watermark table, and uploads once by tracking `WATERMARKS_EXIST` and `WATERMARKS_LOADED`.

## State and Persistence Behavior

The file stores allocated tables in `smu->smu_table`, CPU core count and selected CPU core ID in `smu`, actual/default GFX and CPU frequency limits, watermark load bitmap, Vangogh power limits under `struct smu_11_5_power_context`, cached GFXOFF residency/entry count in `adev->gfx`, and cached GPU metrics via `SMU_DRIVER_TABLE_GPU_METRICS`.

Firmware state changes include VCN/JPEG power state, active workload mask, soft/hard clock ranges, CPU CCLK ranges, GFXOFF enable/allow/disallow/residency logging, WGP active requests, watermarks, thermal limit, fast/slow PPT limits, and asynchronous mode2 reset.

## Dependencies

Dependencies include SMU11 common helpers, Vangogh firmware interface headers, SMU11.5 PPSMC/PMFW message IDs, GC 10.3 RLC register headers, CPU topology on x86, `smu_cmn_*` table/message helpers, `sysfs_emit_at`, KIQ register reads, and AMDGPU PM/DPM state.

## Integration Points

The `pptable_funcs` table integrates with the AMDGPU powerplay framework for sensors, GPU metrics, DPM sysfs, watermarks from DC, multimedia power gating, GFXOFF accounting, runtime reset, thermal limit, PPT limit, and VBIOS boot values. It reuses `smu_v11_0.c` for common firmware status, IRQ handling, table finalization, memory/table location, power context, and VBIOS parsing.

## Risks and Edge Cases

Legacy/new metrics layout selection is firmware-version sensitive; using the wrong layout corrupts sensor values. CPU overdrive accepts only firmware that supports CCLK messages, and the input-size diagnostic text for CPU OD says four parameters while code requires three. Some profile paths call `vangogh_force_clk_levels` without checking every return value. VCN parameter packing differs for VCLK and DCLK. Watermarks upload only once after `WATERMARKS_LOADED`, so later range changes require careful bitmap handling elsewhere. `SMU13_DRIVER_IF_VERSION` is assigned despite this being an SMU11.5 policy, so compatibility depends on the corresponding Vangogh firmware contract.

## Test Signals

Useful validation includes Vangogh boot with both old and new PMFW interfaces, `gpu_metrics` ABI version selection, sensor reads for GPU/VCN load, power, temperatures, CPU clocks, voltage, DPM sysfs clock levels, manual OD edits and commit, GFXOFF enable/status/residency/entry count, VCN/JPEG power-gating during multimedia use, DC watermark programming, WGP power-save request after init, and mode2 reset.
