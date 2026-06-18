# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c

## Purpose
`smu_v13_0_0_ppt.c` is the ASIC-specific SMU v13.0.0/v13.0.10 PPT implementation for discrete GPUs. It maps generic SMU concepts to v13.0.0 PMFW message IDs, table IDs, clock IDs, feature bits, workload bits, and power-source IDs, and implements discrete-GPU-specific table setup, OD editing, metrics, software I2C, power profiles, WBRF gates, ECC access, and reset behavior.

## Important APIs And Functions
The exported registration API is `smu_v13_0_0_set_ppt_funcs`. Core maps are `smu_v13_0_0_message_map`, `smu_v13_0_0_clk_map`, `smu_v13_0_0_feature_mask_map`, `smu_v13_0_0_table_map`, `smu_v13_0_0_pwr_src_map`, `smu_v13_0_0_workload_map`, and `smu_v13_0_0_throttler_map`.

Table setup uses `smu_v13_0_0_tables_init`, `smu_v13_0_0_allocate_dpm_context`, `smu_v13_0_0_init_smc_tables`, `smu_v13_0_0_get_pptable_from_pmfw`, `smu_v13_0_0_setup_pptable`, `smu_v13_0_0_store_powerplay_table`, `smu_v13_0_0_append_powerplay_table`, and `smu_v13_0_0_check_powerplay_table`. Runtime functionality includes `smu_v13_0_0_set_default_dpm_table`, `smu_v13_0_0_get_smu_metrics_data`, `smu_v13_0_0_read_sensor`, `smu_v13_0_0_emit_clk_levels`, `smu_v13_0_0_force_clk_levels`, `smu_v13_0_0_get_gpu_metrics`, `smu_v13_0_0_get_power_limit`, `smu_v13_0_0_set_power_limit`, and power-profile helpers.

## Control Flow
Initialization allocates PMFW tables, metrics, watermarks, ECC, OD, and DPM contexts. PPT setup retrieves the combo PPT from PMFW, copies the SMC table into `driver_pptable`, optionally appends board data from ATOM `smc_dpm_info`, and derives BACO/MACO, hardware DC, OD enablement, thermal controller, OD settings, and no-fan flags.

DPM population queries PMFW for enabled domains or falls back to boot clocks; GFX max is clamped to the driver-reported game clock when present. OD edits validate feature support and bounds, mutate the cached overdrive table, set a transaction `FeatureCtrlMask`, and upload on commit/restore. Software I2C converts Linux `i2c_msg` arrays into `SwI2cRequest_t` commands and submits them through `SMU_TABLE_I2C_COMMANDS`.

## State And Persistence
Runtime state includes `driver_pptable`, combo PPT, metrics cache, watermarks, ECC table, overdrive tables, DPM context, `user_overdrive_table`, `smu->user_dpm_profile.user_od`, and optional `smu->custom_profile_params`. Suspend/resume OD preservation is implemented by restoring selected user fields after refreshing boot OD defaults.

## Dependencies And Integration Points
The file depends on v13.0.0 PMFW interface headers, shared `smu_v13_0.c` helpers, `smu_cmn`, ATOM BIOS board tables, Linux I2C, AMDGPU RAS, VCN/JPEG control, thermal IRQs, BACO/runpm, WBRF, and sysfs/hwmon readers. The `pptable_funcs` table is the main integration contract.

## Risks
OD editing can write invalid PMFW control values if feature gates or bounds are wrong. I2C command construction must respect `MAX_SW_I2C_COMMANDS` and adapter quirks. Firmware-version gates control GFXOFF, compute optimizations, ECC, WBRF, and RAS reset parameters. Metrics field validity varies by firmware version. Mode1 reset disables MMIO access and depends on strict ordering.

## Test Signals
Signals include probe on SMU 13.0.0 and 13.0.10, combo PPT retrieval, DPM sysfs levels, OD read/edit/commit/restore, suspend/resume OD persistence, GPU metrics v1.3, fan controls, custom power profile programming, SMU I2C EEPROM access, ECC info on supported firmware, mode1/mode2 reset, WBRF support gates, and PCIe level clamping.
