# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.h

## Purpose
`si_dpm.h` is the Southern Islands legacy DPM state header. It defines register addresses, default timing and power-tune constants, SMC SRAM table offsets, PCIe generation enums, and the host-side state structures used by SI power management code to build SMC state tables, memory-controller timing tables, voltage tables, ULV state, fan state, CAC/powertune data, and DTE thermal estimation data.

## Important APIs, Types, And State
The exported symbol is `si_smu_ip_block`, while the header mainly contributes data contracts: `rv7xx_power_info`, `evergreen_power_info`, `ni_power_info`, and `si_power_info` are intentionally nested with "must be first" layout comments so older-generation helpers can cast through common prefixes. `rv7xx_pl` and `si_ps` model software performance levels. `si_clock_registers`, `si_mc_reg_table`, `si_ulv_param`, `si_powertune_data`, `si_dyn_powertune_data`, and `si_dte_data` hold derived BIOS, firmware, and runtime tuning values.

## Control Flow And Integration
The file has no executable flow, but it drives flow in SI DPM implementation code: boot and ACPI state slots, driver-state slots, SMC table offsets, and scratch copies of `SISLANDS_SMC_STATETABLE`, `SMC_SIslands_MCRegisters`, and `PP_SIslands_PAPMParameters` are filled on the host and written to SMC SRAM through the `sislands_smc.h` interface. It depends on `amdgpu_atombios.h` for voltage table types and on packed SMC ABI definitions from `sislands_smc.h`.

## Risks And Test Signals
The main risks are ABI drift and unit mistakes: table sizes, array counts, register offsets, and temperature/clock units must match firmware expectations. The nested struct-prefix pattern is fragile if fields are reordered. Test signals are successful SI DPM initialization, correct SMC table uploads, suspend/resume without DPM hangs, PCIe generation transitions, fan and thermal sysfs readings, and absence of SMC message failures or memory timing instability.
