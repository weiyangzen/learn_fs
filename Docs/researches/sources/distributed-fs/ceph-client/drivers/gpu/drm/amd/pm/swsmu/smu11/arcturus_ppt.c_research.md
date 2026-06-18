<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c

## Purpose

`arcturus_ppt.c` is the Arcturus-specific SMU11 powerplay table implementation. It installs the Arcturus `pptable_funcs`, maps generic SMU messages/features/tables/clocks/workloads to Arcturus PMFW IDs, initializes SMU driver tables, parses and stores the PowerPlay table, builds DPM state, exposes sensors/clock levels/fan controls/power profiles/GPU metrics, handles SMU-backed I2C, and delegates common lifecycle work to `smu_v11_0` helpers.

## Important APIs, Types, and Functions

Important static maps include `arcturus_message_map`, `arcturus_clk_map`, `arcturus_feature_mask_map`, `arcturus_table_map`, `arcturus_pwr_src_map`, `arcturus_workload_map`, and `arcturus_throttler_map`. Initialization paths are `arcturus_tables_init`, `arcturus_allocate_dpm_context`, `arcturus_init_smc_tables`, and `arcturus_init_allowed_features`. PPTable paths are `arcturus_setup_pptable`, `arcturus_store_powerplay_table`, `arcturus_append_powerplay_table`, `arcturus_check_powerplay_table`, `arcturus_check_bxco_support`, and `arcturus_check_fan_support`. Runtime hooks include DPM table setup, metrics access, clock-level emission/forcing, thermal range, sensors, fan PWM/RPM get/set, power limit/profile handling, VCN DPM, I2C adapter operations, unique ID query, DF C-state control, thermal throttling logging, PCIe speed query, GPU metrics export, and `arcturus_set_ppt_funcs`.

## Control Flow

Probe/setup calls `arcturus_set_ppt_funcs`, which assigns function/mapping tables and initializes message control with SMU11 common code. `init_smc_tables` allocates VRAM driver tables for PPTable, PMSTATUSLOG, metrics, I2C commands, and activity monitor coefficients, then allocates DPM/policy contexts and calls `smu_v11_0_init_smc_tables`. `setup_pptable` runs common SMU11 parsing, copies the embedded `smc_pptable`, appends atom BIOS DPM data, checks BACO/MACO and fan support, then later common code uploads tables and enables features. User-facing calls flow through `pptable_funcs` to metrics reads, DPM table lookups, SMC messages, or THM/MMIO register operations.

## State and Persistence Behavior

Persistent driver state includes allocated metrics and GPU metrics tables, driver PPTable, DPM context, PLPD policy mask/current level, `adev->pm.no_fan`, BACO platform support, fan maximum RPM, custom profile parameters, SMU I2C adapter registrations, RAS/FRU I2C bus pointers, and `adev->unique_id`. Firmware/device state is changed by feature masks, soft frequency limits, power limits, workload masks, fan mode/register writes, DF C-state messages, XGMI PLPD policy, VCN DPM toggles, I2C command table transfers, and BTC/reset-related common helpers.

## Dependencies

The file depends on AMDGPU core, atom firmware/BIOS helpers, common SMU code, SMU11 common functions, Arcturus driver-interface and PPSMC headers, SMU11 PPTable layout, NBIO/THM SOC15 register definitions, XGMI, RAS, Linux I2C, PCI, and mutex/ktime helpers. Firmware-version guards are embedded for PLPD, DF C-state, ReadSerial, and clock forcing.

## Integration Points

It is compiled through `smu11/Makefile` and selected by AMDGPU platform dispatch. It integrates with sysfs clock/OD/power profile paths, hwmon sensor reads, GPU metrics ioctl/sysfs paths, RAS EEPROM and FRU EEPROM I2C, KFD SMI throttling events, BACO/MACO platform support, XGMI PLPD policy, and common SMU11 lifecycle hooks.

## Risks and Edge Cases

Several operations are firmware-version gated; ignoring those checks can send unsupported commands. Clock forcing is intentionally disabled for PMFW 54.18 through 54.26. DPM table indexes derived from masks must be bounds-checked. Metrics use different current vs average fields depending on DPM enablement. Fan RPM/PWM code directly manipulates THM registers and has 0-RPM workarounds based on user flags. The I2C command builder must respect `MAX_SW_I2C_COMMANDS`, restart/stop semantics, DPM-enabled state, and PM mutex serialization. PPTable copying assumes the SMU11 layout and `PPTable_t` size match firmware.

## Test Signals

Build and boot on Arcturus, firmware-version compatibility logs, PPTable parsing/upload, DPM table/sysfs output, clock forcing rejection on affected firmware, fan PWM/RPM get/set, GPU metrics v1.3 sanity, RAS/FRU I2C access, XGMI PLPD policy toggles, DF C-state messages, thermal throttling logs/KFD SMI events, suspend/resume, reset, and BACO paths are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c -->
