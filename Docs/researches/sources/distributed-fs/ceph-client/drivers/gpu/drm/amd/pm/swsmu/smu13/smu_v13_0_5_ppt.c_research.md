# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_5_ppt.c

## Purpose
`smu_v13_0_5_ppt.c` is the SMU13.0.5 power-play table backend for AMDGPU SWSMU. It wires the generic `smu_context` callbacks to the SMU13.0.5 firmware message ABI, allocates the firmware-facing tables needed by this ASIC, exposes sensors and GPU metrics, and implements the supported DPM, clock forcing, overdrive, watermarks, media power gating, gfx-off, and mode2 reset operations. The file marks the device as an APU-oriented backend in `smu_v13_0_5_set_ppt_funcs()` and uses a custom MP1 C2PMSG register layout for message control.

## Important APIs, Types, And Data
- `smu_v13_0_5_ppt_funcs` is the exported behavior table. It registers callbacks for SMC table init/fini, firmware status/version, VBIOS boot values, feature control, VCN/JPEG power gating, DPM table fetch, sensor reads, watermarks, GPU metrics, feature masks, driver table location, gfx-off, mode2 reset, DPM frequency limits, overdrive edits, sysfs clock-level emission, forced clock levels, performance level selection, and fine-grained GFX frequency defaults.
- `smu_v13_0_5_message_map` translates common `SMU_MSG_*` ids to `PPSMC_MSG_*` ids including VCN/JPEG power, GFX reset, table transfers, GFX clock queries, enabled-feature queries, GFX/VN soft min/max controls, driver interface version, and unload notification.
- `smu_v13_0_5_feature_mask_map` maps generic feature bits to SMU13.0.5 firmware feature ids. Some entries use reverse or half-reverse mappings for firmware bit layout differences.
- `smu_v13_0_5_table_map` declares WATERMARKS, SMU_METRICS, CUSTOM_DPM, and DPMCLOCKS as valid firmware tables.
- `smu_v13_0_5_dpm_features` is the DPM-running mask: CCLK, FCLK, LCLK, GFX, VCN, DCFCLK, SOCCLK, MP0CLK, and SHUBCLK DPM must be enabled for the file to report DPM running.
- `SMU_13_0_5_UMD_PSTATE_GFXCLK` comes from the companion header and supplies the synthetic middle GFX clock shown in clock-level output.

## Control Flow And Behavior
- Initialization enters through `smu_v13_0_5_set_ppt_funcs()`, which installs the callback table, feature/table maps, APU flag, SMU driver interface version, and MP1 message control registers. `smu_v13_0_5_init_msg_ctl()` assigns message, response, and argument registers and uses `smu_msg_v1_ops` with a timeout derived from `adev->usec_timeout`.
- `smu_v13_0_5_init_smc_tables()` initializes VRAM-backed SMU tables for watermarks, DPM clocks, and metrics, then allocates kernel shadow copies for DPM clocks, metrics, and watermarks. It also creates a cached driver table for `gpu_metrics_v2_1`. `smu_v13_0_5_fini_smc_tables()` frees those allocations and tears down the GPU metrics driver table.
- Runtime metrics are pulled through `smu_cmn_get_metrics_table()` into `SmuMetrics_t`. `smu_v13_0_5_get_smu_metrics_data()` translates individual `MetricsMember_t` values into AMDGPU units for clocks, activity, socket power, temperatures, throttling status, and voltages. `smu_v13_0_5_read_sensor()` maps public `amd_pp_sensors` requests onto that helper and reports 4-byte sensor values.
- `smu_v13_0_5_get_gpu_metrics()` fills a `gpu_metrics_v2_1` table from `SmuMetrics_t`, including temperatures, activity, socket/GFX/SOC power, clocks, throttle status, and a boot-time system clock counter. It updates the SMU driver-table cache timestamp before returning the structure size.
- DPM clock data is fetched by `smu_v13_0_5_set_default_dpm_tables()` from `SMU_TABLE_DPMCLOCKS`. Helpers then report current clocks, level counts, indexed DPM frequencies, DPM enablement, and min/max ultimate frequencies. If a clock's DPM feature is disabled, `smu_v13_0_5_get_dpm_ultimate_freq()` falls back to boot frequencies via `smu_v13_0_get_boot_freq_by_index()`.
- Frequency limits are applied by `smu_v13_0_5_set_soft_freq_limited_range()`. GFX/SCLK uses `SetHardMinGfxClk` and `SetSoftMaxGfxClk`; VCLK/DCLK uses packed VCN min/max messages and shifts VCLK values by `SMU_13_VCLK_SHIFT`.
- Sysfs clock-level output is produced by `smu_v13_0_5_emit_clk_levels()`. It prints OD SCLK/range, enumerates SOCCLK/VCLK/DCLK/MCLK DPM levels, and presents GFX/SCLK as min/current-or-UMD/max with an active marker.
- Clock forcing is intentionally narrow: `smu_v13_0_5_force_clk_levels()` supports VCLK and DCLK masks by translating selected indices to frequencies and setting a min/max range; other clock types return `-EINVAL`.
- Overdrive is only accepted when `smu_dpm.dpm_level` is `AMD_DPM_FORCED_LEVEL_MANUAL`. `smu_v13_0_5_od_edit_dpm_table()` validates min/max GFX SCLK edits against default limits, stages them in `smu->gfx_actual_*`, restores defaults, and commits by sending hard-min and soft-max GFX messages.
- Performance levels are translated in `smu_v13_0_5_set_performance_level()` into SCLK, VCLK, and DCLK min/max ranges. HIGH/LOW lock to ultimate max/min, AUTO restores full ranges, profile modes select standard/min/peak-style single frequencies, MANUAL and PROFILE_EXIT leave existing limits untouched, and PROFILE_MIN_MCLK is unsupported.
- `smu_v13_0_5_set_watermarks_table()` copies display read/write watermark ranges into the firmware `Watermarks_t` shadow and writes the table once through `smu_cmn_write_watermarks_table()`, tracked by `smu->watermarks_bitmap`.
- Media power transitions are simple firmware messages: VCN uses `PowerUpVcn`/`PowerDownVcn`, JPEG uses `PowerUpJpeg`/`PowerDownJpeg`. System feature shutdown sends `PrepareMp1ForUnload` unless entering S0ix.
- Reset support is mode2 only in this file: `smu_v13_0_5_mode2_reset()` sends `GfxDeviceDriverReset` with `SMU_RESET_MODE_2`.

## State And Persistence
- Persistent driver state lives in `smu->smu_table` shadow pointers, the GPU metrics driver table, `smu->watermarks_bitmap`, DPM clocks loaded from firmware, and `smu->gfx_default_*` / `smu->gfx_actual_*` frequency fields.
- The watermarks table is write-once per load in this implementation: after `WATERMARKS_LOADED` is set, future calls do not rewrite unless higher-level code clears the bitmap.
- Metrics caching is mostly delegated to common helpers; `get_gpu_metrics()` explicitly refreshes and updates the driver-table cache timestamp.
- The message controller mutex and register configuration are initialized once with the PPT backend and are used by common SMC messaging paths.

## Dependencies And Integration Points
- Depends on SMU13 common code (`smu_v13_0.*`, `smu_cmn.*`), SMU13.0.5 firmware headers (`smu13_driver_if_v13_0_5.h`, `smu_v13_0_5_ppsmc.h`, `smu_v13_0_5_pmfw.h`), AMDGPU device/runtime structures, and Linux kernel memory/time/sysfs helpers.
- Integrates with the AMDGPU powerplay layer through `pptable_funcs`; with firmware through SMC messages and VRAM tables; with sysfs through clock-level and overdrive callbacks; with display memory timing through watermark programming; and with reset paths through the mode2 reset callback.
- It intentionally uses common helpers for firmware version checks, feature masks, PP feature masks, VBIOS boot values, gfx-off control, and driver table location.

## Risks And Edge Cases
- `smu_v13_0_5_get_smu_metrics_data()` returns `UINT_MAX` for unsupported metrics but still reports success, so callers must understand that sentinel. Several sensors such as `SS_APU_SHARE` and `SS_DGPU_SHARE` request members not handled by the helper and will receive that sentinel with a successful return.
- DPM min/max logic for MCLK/UCLK/FCLK uses reversed DF pstate ordering: max is index 0 and min is the last enabled DF pstate. Regressions here would invert memory or fabric limits.
- `smu_v13_0_5_set_watermarks_table()` only writes the firmware table if it has not already been loaded. Dynamic watermark changes after the first load may be ignored unless external code resets `WATERMARKS_LOADED`.
- Clock forcing only handles VCLK/DCLK. User expectations for SCLK/MCLK forcing must be covered elsewhere or surfaced as unsupported.
- Overdrive staged values are stored in `smu_context`; failed commits can leave staged actual min/max values that differ from firmware if only one SMC message succeeds.
- Temperature and power unit conversions are specific to `SmuMetrics_t` layout and Q/unit conventions; changes in firmware metrics format require corresponding conversion updates.

## Test Signals
- Boot/probe tests should verify `smu_v13_0_5_set_ppt_funcs()` installs the correct function table, message registers, feature/table maps, `is_apu = true`, and `SMU13_0_5_DRIVER_IF_VERSION`.
- SMC table init/fini tests or fault injection should cover allocation failure paths and confirm all shadows and driver tables are freed.
- Sensor tests should compare GPU load, VCN load, power, edge/hotspot temperature, SCLK/MCLK, and voltages against known `SmuMetrics_t` inputs and verify unsupported sensors return `-EOPNOTSUPP` or the documented sentinel behavior.
- Clock sysfs tests should validate DPM level ordering, active markers, GFX min/mid/max output, and behavior when DPM features are disabled.
- Overdrive tests should cover manual-mode gating, min/max validation, restore defaults, commit ordering, and error propagation from each SMC message.
- Watermark tests should check range-count validation, row mapping for reader/writer sets, bitmap transitions, and single upload behavior.
- Reset and media tests should confirm expected SMC messages for mode2 reset and VCN/JPEG enable/disable transitions.
