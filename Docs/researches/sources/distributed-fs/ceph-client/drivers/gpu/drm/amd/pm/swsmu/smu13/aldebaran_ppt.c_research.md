# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c

## Purpose

`aldebaran_ppt.c` implements the Aldebaran SMU13 policy layer for AMD Instinct-class GPUs. It maps common SMU concepts to Aldebaran firmware messages, features, clocks, tables, thermal limits, DPM policy, metrics, power limits, reset flows, I2C EEPROM access, ECC reporting, XGMI PLPD policy, determinism, and bad HBM page/channel notification.

## Important APIs, Types, and Functions

The exported entry point is `aldebaran_set_ppt_funcs`, which installs `aldebaran_ppt_funcs`, clock/feature/table maps, the Aldebaran SMU13 driver interface version, and SMU13 message control.

Important functions include `aldebaran_tables_init`, `aldebaran_select_plpd_policy`, `aldebaran_allocate_dpm_context`, `aldebaran_init_smc_tables`, `aldebaran_init_allowed_features`, `aldebaran_get_dpm_ultimate_freq`, `aldebaran_set_default_dpm_table`, `aldebaran_setup_pptable`, `aldebaran_run_btc`, `aldebaran_populate_umd_state_clk`, `aldebaran_get_smu_metrics_data`, `aldebaran_get_current_clk_freq_by_table`, `aldebaran_emit_clk_levels`, `aldebaran_force_clk_levels`, `aldebaran_get_thermal_temperature_range`, `aldebaran_read_sensor`, `aldebaran_get_power_limit`, `aldebaran_set_power_limit`, `aldebaran_system_features_control`, `aldebaran_set_performance_level`, `aldebaran_set_soft_freq_limited_range`, `aldebaran_usr_edit_dpm_table`, `aldebaran_is_dpm_running`, `aldebaran_i2c_xfer`, `aldebaran_i2c_control_init`, `aldebaran_get_unique_id`, `aldebaran_set_df_cstate`, `aldebaran_log_thermal_throttling_event`, `aldebaran_get_gpu_metrics`, `aldebaran_get_ecc_info`, `aldebaran_mode1_reset`, `aldebaran_mode2_reset`, and bad HBM page/channel helpers.

Key firmware data types include `PPTable_t`, `SmuMetrics_t`, `SwI2cRequest_t`, `SwI2cCmd_t`, `EccInfoTable_t`, `struct gpu_metrics_v1_3`, `struct smu_13_0_dpm_context`, and `struct smu_dpm_policy_ctxt`.

## Control Flow

Initialization registers PPTABLE, PM status log, SMU metrics, I2C commands, and ECC info tables; allocates metrics and ECC buffers; initializes the GPU metrics cache; allocates DPM context; and creates an XGMI PLPD policy whose setter only sends `GmiPwrDnControl` on master die.

PPTABLE setup forces VBIOS table selection, calls common SMU13 PPTABLE setup, copies the embedded SMC PPTABLE into the driver buffer, appends trailing fields from ATOM `smc_dpm_info` revision 4.10, and records thermal controller type.

DPM setup fills SOC, GFX, UCLK, and FCLK DPM tables. GFXCLK is represented as a two-entry fine-grained table using `GfxclkFmin`/`GfxclkFmax` from the PPTABLE. SR-IOV VF ultimate-frequency queries use cached DPM tables; non-VF delegates to common SMU13.

Metrics paths refresh the SMU metrics table and expose clock, activity, power, temperature, throttler, unique ID, energy accumulator, PCIe, and HBM temperature data. Power and energy are valid only on the primary die; secondary dies report zero or `-EOPNOTSUPP` for those values.

Manual and determinism clock control only accepts GFX/SCLK. Manual mode enforces `min < max` and sends common SMU13 soft min/max messages. Determinism mode restores default min/max, waits briefly, then sends `EnableDeterminism` with the target max clock. Changing away from determinism sends `DisableDeterminism`.

I2C transfer builds a `SwI2cRequest_t` command list from Linux I2C messages, handles direction-change restarts and STOP placement, uploads it through `SMU_TABLE_I2C_COMMANDS`, then copies read bytes from the returned driver table. The adapter is registered as "AMDGPU SMU 0" and assigned to RAS/FRU EEPROM bus pointers.

Reset paths are firmware-version dependent. Mode1 uses legacy `Mode1Reset` before PMFW 68.07 and `GfxDeviceDriverReset` afterward, with optional fatal-error flag for RAS FED status on newer firmware. Mode2 sends an async reset, waits, restores PCI config space, then waits for an ACK with retries.

ECC and bad-channel flows gate on minimum PMFW versions, transfer `SMU_TABLE_ECCINFO`, translate v1/v2 ECC table layouts into `umc_ecc_info`, and send bad HBM page/channel counts to firmware.

## State and Persistence Behavior

Persistent driver state includes allocated SMU tables, ECC table, GPU metrics cache, DPM tables, PLPD policy context, copied driver PPTABLE, current/custom GFX pstate min/max values, `adev->unique_id`, RAS/FRU I2C adapter pointers, power limits, and feature/table/clock maps.

Firmware and hardware state changed by this file includes allowed/enabled SMU features, DPM soft limits, determinism, GMI power-down policy, DF C-state control, board/DC BTC calibration, I2C command execution, reset mode, bad HBM page/channel notifications, PPT limits, and thermal throttling notifications to KFD SMI.

## Dependencies

The file depends on SMU13 common helpers, Aldebaran driver interface and PPSMC headers, SMU13 PPTABLE definitions, ATOMBIOS tables, SOC15/NBIO/THM/MP generated registers, AMDGPU XGMI/RAS/KFD/PCI helpers, Linux I2C APIs, and common SMU message/table helpers.

## Integration Points

`aldebaran_ppt_funcs` integrates with AMDGPU powerplay, hwmon/sysfs, GPU metrics, reset/recovery, RAS, XGMI policy, KFD SMI throttling events, EEPROM access, and DC/clock consumers. It delegates common firmware/table/microcode/power/IRQ/display-clock operations to `smu_v13_0_*` helpers while overriding Aldebaran-specific power, reset, metrics, ECC, and I2C behavior.

## Risks and Edge Cases

Many operations must run only on the primary die; sending power calibration or PPT messages on secondary dies can fail or return invalid data. Firmware-version gates are critical for ECC table versions, bad-channel messages, mode resets, fatal reset flags, and board BTC. `aldebaran_allocate_dpm_context` leaks the DPM context if policy allocation fails unless common cleanup handles partial init later. I2C command count is bounded by adapter quirks, but command construction itself relies on the I2C core honoring those quirks. RAS interrupt state suppresses some sensor/clock output. Mode2 reset must restore PCI config space before waiting for firmware ACK.

## Test Signals

Validation should include Aldebaran boot, PPTABLE copy/append, BTC on primary die, DPM table population, sysfs clock levels, manual OD and determinism modes, primary/secondary die power reporting, GPU metrics v1.3 including HBM temperatures and energy, thermal throttling logs and KFD SMI events, I2C EEPROM reads/writes through the SMU adapter, ECC table v1/v2 reads, mode1/mode2 reset across supported firmware versions, SR-IOV VF DPM limits, XGMI PLPD policy changes, DF C-state messages, and bad HBM page/channel notifications.
