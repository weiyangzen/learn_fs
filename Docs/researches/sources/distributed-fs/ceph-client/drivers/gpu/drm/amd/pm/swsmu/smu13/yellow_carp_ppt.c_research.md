# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/yellow_carp_ppt.c

## Purpose
Implements the SMU13 Yellow Carp APU PPT backend. It maps Yellow Carp firmware messages, features, and tables, initializes APU SMC tables, controls VCN/JPEG/GFXOFF/reset behavior, reads APU metrics and sensors, manages display watermarks, exposes DPM and OD sysfs clock views, and installs a Yellow Carp `pptable_funcs` table.

## Important APIs, Types, And Functions
- Mapping and feature contracts are `yellow_carp_message_map`, `yellow_carp_feature_mask_map`, `yellow_carp_table_map`, and `yellow_carp_dpm_features`.
- Table lifetime is handled by `yellow_carp_init_smc_tables` and `yellow_carp_fini_smc_tables`.
- Power and media controls include `yellow_carp_system_features_control`, `yellow_carp_dpm_set_vcn_enable`, `yellow_carp_dpm_set_jpeg_enable`, `yellow_carp_post_smu_init`, `yellow_carp_mode2_reset`, and common SMU13 GFXOFF helpers.
- Telemetry and watermarks use `yellow_carp_get_smu_metrics_data`, `yellow_carp_read_sensor`, `yellow_carp_set_watermarks_table`, `yellow_carp_get_gpu_metrics`, and `yellow_carp_get_gfxoff_status`.
- DPM and tuning helpers include `yellow_carp_set_default_dpm_tables`, `yellow_carp_get_dpm_ultimate_freq`, `yellow_carp_set_soft_freq_limited_range`, `yellow_carp_emit_clk_levels`, `yellow_carp_force_clk_levels`, `yellow_carp_od_edit_dpm_table`, `yellow_carp_set_performance_level`, and `yellow_carp_set_fine_grain_gfx_freq_parameters`.

## Control Flow
`yellow_carp_set_ppt_funcs` marks the SMU as an APU, installs feature/table/message maps, sets the Yellow Carp driver interface version, and initializes common SMU13 message control. Initialization allocates VRAM-backed watermarks, DPM clocks, and metrics tables plus software buffers and a GPU metrics v2.1 cache. Runtime feature shutdown sends `PrepareMp1ForUnload` only outside S0ix. Post-init explicitly enables GFXOFF before later allow/disallow control. Media power gating sends VCN/JPEG up/down messages, while mode2 reset sends `GfxDeviceDriverReset` with reset mode 2.

DPM data is read from the `DpmClocks_t` table. If a DPM feature is disabled, ultimate frequency queries fall back to VBIOS boot clocks. GFXCLK exposes fine-grain min/max through `gfx_default_hard_min_freq`, `gfx_default_soft_max_freq`, and the actual user-selected values. Performance-level changes compute target ranges for SCLK, FCLK, SOCCLK, VCLK, and DCLK and send the matching hard-min or soft-max SMU messages. Watermark programming copies display-provided reader/writer ranges into the firmware table and uploads it once per watermark load.

## State And Persistence
Driver state includes `clocks_table`, `metrics_table`, `watermarks_table`, the GPU metrics cache, `watermarks_bitmap`, fine-grain GFX min/max fields, the current forced DPM level, and `smu->is_apu`. Firmware-visible state includes watermarks, soft/hard clock limits, VCN/JPEG power state, GFXOFF state, and reset state. No disk state is stored.

## Dependencies And Integration Points
The file depends on AMDGPU core, `smu_v13_0` common helpers, Yellow Carp generated firmware interface headers, SMU common table/message helpers, SOC15 register access for GFXOFF status, display watermark input, VCN/JPEG harvest state through common device structures, and the SWSMU `pptable_funcs` table. Userspace observes the code through sensors, GPU metrics, OD clock sysfs, forced performance levels, and media power-management behavior.

## Risks And Edge Cases
Metrics units differ by field: some values are divided by 100, some converted to fixed-point power, and GPU metrics v2.1 stores several raw firmware fields. SmartShift share calculation divides by STAPM limits and must guard zero limits. DPM-level ordering for memory/FCLK reverses indexes for display, and disabled DPM paths return boot frequencies scaled from 10 kHz to MHz. OD edits are only allowed in manual DPM mode and only cover GFX min/max. Watermarks are uploaded only once after `WATERMARKS_LOADED`, so later range changes require bitmap management elsewhere. The code assumes IP versions 13.0.1/13.0.3/13.0.8 for UMD pstate defaults.

## Test Signals
Signals include successful allocation/freeing of all SMC software tables, GFXOFF enable during post-init, no unload message during S0ix, VCN/JPEG up/down messages, mode2 reset message, DPM tables populated from firmware, fallback boot clocks when features are disabled, GFX fine-grain OD range validation in manual mode, watermark upload and bitmap transitions, GFXOFF status register decoding, and GPU metrics v2.1 fields matching firmware metrics.
