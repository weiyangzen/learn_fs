<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c

## Purpose

This file is the SMU v14.0.2 power-play table implementation for AMDGPU SWSMU. It binds the generic `smu_context` to ASIC-specific firmware messages, clock IDs, feature IDs, table IDs, workload IDs, overdrive limits, fan controls, metrics formats, I2C transport, BACO, reset, and power-limit behavior. The external entry point is `smu_v14_0_2_set_ppt_funcs()`, which installs `smu_v14_0_2_ppt_funcs`, maps common SMU enums to v14.0.2 firmware constants, records `SMU14_DRIVER_IF_VERSION_SMU_V14_0_2`, and initializes the MP1 message mailbox.

## Important APIs, Types, And Tables

Important static maps are `smu_v14_0_2_message_map`, `smu_v14_0_2_clk_map`, `smu_v14_0_2_feature_mask_map`, `smu_v14_0_2_table_map`, `smu_v14_0_2_pwr_src_map`, `smu_v14_0_2_workload_map`, and `smu_v14_0_2_throttler_map`. They define the ABI between common power-management code and PMFW. `PPTable_t`, `SkuTable_t`, `CustomSkuTable_t`, `SmuMetricsExternal_t`, `SmuMetrics_t`, `OverDriveTableExternal_t`, `Watermarks_t`, `SwI2cRequest_t`, `EccInfoTable_t`, and `DpmActivityMonitorCoeffIntExternal_t` are the main firmware-facing table formats.

The key functions are `smu_v14_0_2_setup_pptable()`, `smu_v14_0_2_tables_init()`, `smu_v14_0_2_init_smc_tables()`, `smu_v14_0_2_set_default_dpm_table()`, `smu_v14_0_2_get_smu_metrics_data()`, `smu_v14_0_2_read_sensor()`, `smu_v14_0_2_emit_clk_levels()`, `smu_v14_0_2_force_clk_levels()`, `smu_v14_0_2_update_pcie_parameters()`, `smu_v14_0_2_get_gpu_metrics()`, the OD helpers, the power-profile helpers, the I2C adapter callbacks, and reset/BACO helpers.

## Control Flow

Initialization sets every feature as allowed, fetches the combined PPTABLE from PMFW unless running as an SR-IOV VF, copies the embedded SMC PPT into `driver_pptable`, and derives driver policy from platform caps. Table initialization declares the VRAM/GTT-backed SMU tables, allocates CPU-side metrics, watermarks, ECC, overdrive, and GPU-metrics caches, allocates a `struct smu_14_0_dpm_context`, and then delegates common SMC table allocation to `smu_v14_0_init_smc_tables()`.

At DPM setup, each clock domain chooses either firmware DPM levels via `smu_v14_0_set_single_dpm_table()` or a one-entry boot-value fallback. GFX maximum reporting is clamped to `DriverReportedClocks.GameClockAc` when present. Sensor and sysfs clock reads flow through `smu_cmn_get_metrics_table()` and `smu_v14_0_2_get_smu_metrics_data()`, which translates SMU metrics fields into AMDGPU sensor units. Clock forcing converts a level mask into min/max table entries and sends soft frequency limits. PCIe parameter updates build levels from `SkuTable` and issue `SMU_MSG_OverridePcieParameters` when driver policy or platform caps require clamping.

Overdrive control loads boot/user/runtime tables, validates requested fields against `OverDriveLimitsBasicMin/Max`, marks the relevant `FeatureCtrlMask` bits for one upload, and then clears/caches user-visible settings after a successful `SMU_TABLE_OVERDRIVE` transfer. Power profile custom mode reads and rewrites `SMU_TABLE_ACTIVITY_MONITOR_COEFF`; compute workloads disable deep sleep before setting the workload mask. The I2C path registers `MAX_SMU_I2C_BUSES` Linux adapters and turns `i2c_msg` byte streams into `SwI2cRequest_t` commands transferred through `SMU_TABLE_I2C_COMMANDS`.

## State And Persistence

Persistent runtime state lives in `smu->smu_table` allocations, `smu->smu_dpm.dpm_context`, `smu->pstate_table`, `smu->user_dpm_profile`, `smu->custom_profile_params`, `adev->pm.od_feature_mask`, `adev->unique_id`, BACO state, and the registered I2C adapters. Metrics are cached in `metrics_table` through common SMU cache timing; GPU metrics are cached with `SMU_GPU_METRICS_CACHE_INTERVAL`. User overdrive settings are preserved across S3/S4/runpm resume by copying boot defaults and then restoring saved user fields when `adev->in_suspend` and `user_od` are true. Power-limit state is tracked in `smu->current_power_limit`.

## Dependencies And Integration Points

The file depends on common v14 helpers from `smu_v14_0.*`, the common SMU layer in `smu_cmn`, AMDGPU ATOM/VBIOS data, MP1 register definitions, RAS interrupt state, Linux I2C, firmware table formats from `smu14_driver_if_v14_0.h` and `smu_v14_0_2_pptable.h`, and PMFW message IDs from `smu_v14_0_2_ppsmc.h`. It integrates with sysfs power and clock reporting, pp_od_clk_voltage editing, power profiles, thermal policy, BACO/runpm, reset recovery, FRU/RAS EEPROM access over SMU I2C, and MP1 unload/DF C-state messaging.

## Risks And Edge Cases

`smu_v14_0_2_is_mode1_reset_supported()` unconditionally returns true with a TODO, and `smu_v14_0_2_mode2_reset()` is still a TODO returning success; callers may believe unsupported reset paths worked. `smu_v14_0_2_init_smc_tables()` does not unwind `tables_init()` if DPM context allocation or common initialization later fails. I2C request construction increments `NumCmds` for every byte and relies on adapter quirks to keep transfers within `MAX_SW_I2C_COMMANDS`; bypasses could overflow firmware command capacity. Some OD format strings print signed minima with unsigned formatting. Power-limit OD writes depend on `msg_limit` and `od_enabled`; bad PPTABLE data could expose invalid limits. Sensor paths return `UINT_MAX` for unknown metrics members, so callers must distinguish unsupported sensors from firmware-returned maximum values.

## Test Signals

Useful validation includes booting an IP 14.0.2 board with PMFW table retrieval, checking `pp_dpm_*` and `gpu_metrics` sysfs output, changing performance levels and workload profiles, editing and restoring OD fan/GFX/UCLK/PPT fields, testing suspend/resume OD persistence, forcing PCIe caps with and without `PP_PCIE_DPM_MASK`, exercising FRU/RAS EEPROM reads through SMU I2C, triggering RAS interrupt paths, and verifying BACO/runpm audio-function transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu14/smu_v14_0_2_ppt.c -->
