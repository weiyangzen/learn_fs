# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_4_ppt.c

## Purpose
`smu_v13_0_4_ppt.c` is the SMU v13.0.4/v13.0.11 APU-oriented PPT implementation. It maps v13.0.4 PMFW messages/features/tables, manages DPM clocks and watermarks, reports GPU metrics v2.1, exposes APU/dGPU share sensors, and implements APU-specific performance-level and mode2 reset behavior.

## Important APIs And Functions
The exported API is `smu_v13_0_4_set_ppt_funcs`. Key maps are `smu_v13_0_4_message_map`, `smu_v13_0_4_feature_mask_map`, and `smu_v13_0_4_table_map`; DPM coverage is described by `smu_v13_0_4_dpm_features`.

Lifecycle functions are `smu_v13_0_4_init_smc_tables`, `smu_v13_0_4_fini_smc_tables`, `smu_v13_0_4_is_dpm_running`, and `smu_v13_0_4_system_features_control`. Metrics and sensors are handled by `smu_v13_0_4_get_gpu_metrics`, `smu_v13_0_4_get_smu_metrics_data`, `smu_v13_0_4_get_current_clk_freq`, and `smu_v13_0_4_read_sensor`. Clock controls include DPM level readers, `smu_v13_0_4_emit_clk_levels`, `smu_v13_0_4_get_dpm_ultimate_freq`, `smu_v13_0_4_set_soft_freq_limited_range`, `smu_v13_0_4_force_clk_levels`, and `smu_v13_0_4_set_performance_level`.

## Control Flow
Initialization allocates watermarks, DPM clocks, metrics tables, kernel-side caches, and a GPU metrics driver table. It relies on the shared `smu_v13_0_set_default_dpm_tables` path to fetch `SMU_TABLE_DPMCLOCKS`.

Feature disable outside S0ix sends an S4 GFX reset workaround before `PrepareMp1ForUnload`. Clock queries mix direct PMFW messages for GFXCLK/FCLK with metrics-table values for SOC/VCLK/DCLK/UCLK. Performance-level changes compute min/max pairs for SCLK, FCLK, SOCCLK, VCLK, and DCLK, then send hard-min and soft-max PMFW messages; VCLK values are shifted into the VCN argument format.

Watermark programming copies DC reader/writer ranges into `Watermarks_t`, marks `WATERMARKS_EXIST`, and writes the table once when not already loaded.

## State And Persistence
Runtime state includes `clocks_table`, `metrics_table`, `watermarks_table`, GPU metrics driver table, `watermarks_bitmap`, and GFX default/actual hard-min and soft-max fields. These are runtime-only allocations freed by `smu_v13_0_4_fini_smc_tables`.

## Dependencies And Integration Points
The implementation uses shared SMU v13 helpers for firmware status, boot values, VCN/JPEG power, driver table location, GFXOFF, generic OD editing, GFX IMU power-up, and default DPM table fetch. It depends on v13.0.4 PMFW headers, DC watermarks, AMDGPU metrics/hwmon consumers, and `smu_cmn` helpers.

## Risks
Clock-domain mapping is the main risk. Feature gates differ from discrete GPUs, and VCLK/DCLK min/max messages share VCN packed arguments. Unsupported DPM count queries must not be used for unsupported clock types. Metrics unit scaling depends on PMFW schema. Watermarks are written only once after `WATERMARKS_LOADED`, so repeated updates require careful bitmap handling.

## Test Signals
Signals include APU probe with `smu->is_apu`, DPM table load, GPU metrics v2.1 with core/L3 fields, hwmon sensors for load/power/temp/voltage/share, DC watermark programming, GFXOFF, VCN/JPEG toggles, performance-level transitions, mode2 reset, and mailbox register setup on IP 13.0.4 and related users.
