<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c

## Purpose

This file is the SMU v15.0.0 ASIC-specific PPT implementation, marked as an APU path in `smu_v15_0_0_set_ppt_funcs()`. It defines the PMFW message map, feature map, table map, mailbox registers, SMU table transfers, metrics decoding, DPM clock handling, watermarks, performance levels, mode2 reset, and block power controls for IP 15.0.0.

## Important APIs, Types, And Tables

The installed `pptable_funcs` include `init_smc_tables`, `fini_smc_tables`, `get_vbios_bootup_values`, `system_features_control`, VCN/JPEG enable, `set_default_dpm_table`, `read_sensor`, `is_dpm_running`, `set_watermarks_table`, `get_gpu_metrics`, `get_enabled_mask`, `gfx_off_control`, `mode2_reset`, `get_dpm_ultimate_freq`, `od_edit_dpm_table`, `emit_clk_levels`, `force_clk_levels`, `set_performance_level`, fine-grain GFX initialization, IMU power-up, VPE/UMSCH power control, and DPM clock table export. Key firmware formats are `SmuMetrics_t`, `DpmClocks_t`, `Watermarks_t`, and `struct gpu_metrics_v3_0`.

## Control Flow

Initialization declares watermarks, DPM clocks, and metrics SMU tables, allocates CPU copies, and initializes a driver GPU metrics cache. Default DPM setup fetches `SMU_TABLE_DPMCLOCKS` from PMFW via `smu_v15_0_0_update_table()`, which copies through the shared driver table, flushes or invalidates HDP around transfers, and sends three-argument table-transfer mailbox messages. Metrics reads are cached for roughly one millisecond and decoded into sensor values, including firmware-version-specific scaling for `GfxActivity`.

DPM query paths read from the `DpmClocks_t` cache. GFX uses min/max fields; SOC, VCN, memory, and FCLK use enabled level counts and arrays. `emit_clk_levels()` prints OD range, OD SCLK, GFX pseudo-levels, or per-level tables. Clock forcing resolves mask endpoints to frequencies and sends soft min/max messages for SOC, FCLK, VCLK, and DCLK. Performance-level control computes high, low, auto, and profile clocks, then sends soft limits for SCLK, FCLK, SOCCLK, VCLK/VCLK1, and DCLK/DCLK1. Watermark updates translate display-provided reader/writer ranges into PMFW watermarks and upload them once.

## State And Persistence

State lives in `smu_table->metrics_table`, `clocks_table`, `watermarks_table`, the GPU metrics driver table, `smu->watermarks_bitmap`, `smu->gfx_default_hard_min_freq`, `smu->gfx_default_soft_max_freq`, and current actual GFX min/max fields. The mailbox setup stores MP1 C2PMSG 30-34 registers and allows up to three argument registers. `smu->is_apu` is set true and changes common v15 behavior such as firmware status register handling and media power messages.

## Dependencies And Integration Points

This file depends on `smu_v15_0.*` common helpers, `smu15_driver_if_v15_0_0.h`, `smu_v15_0_0_ppsmc.h`, `smu_v15_0_0_pmfw.h`, HDP cache helpers, display watermark structures, common GPU metrics initialization, VPE/UMSCH power management, and AMDGPU sysfs sensor/clock/OD entry points. It integrates as the IP 15.0.0 function table selected by the SMU initialization path.

## Risks And Edge Cases

`smu_v15_0_common_get_dpm_freq_by_index()`, `smu_v15_0_common_get_dpm_ultimate_freq()`, `smu_v15_0_common_get_dpm_level_count()`, `smu_v15_0_common_set_fine_grain_gfx_freq_parameters()`, and `smu_v15_0_common_get_dpm_table()` ignore return values from their underlying helpers and return success, which can hide invalid clock types or failed table reads. `smu_v15_0_0_set_soft_freq_limited_range()` does not support UCLK even though some higher-level code reasons about memory clocks. VCLK1/DCLK1 are explicitly skipped by common ultimate-frequency wrappers, so profile code may silently leave them zero. Metrics unit scaling changes by firmware version, which is fragile without broad PMFW coverage. `system_features_control(false)` only prepares MP1 for unload outside S0ix and does not disable all features.

## Test Signals

Test with IP 15.0.0 boot, `gpu_metrics` v3.0 reads, all supported sensors, display watermark programming, `pp_dpm_*` clock listings, forced levels high/low/auto/profile, OD manual SCLK min/max editing, mode2 reset, VCN/JPEG/VPE/UMSCH power toggles, GFXOFF allow/disallow, and suspend/S0ix unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_0_ppt.c -->
