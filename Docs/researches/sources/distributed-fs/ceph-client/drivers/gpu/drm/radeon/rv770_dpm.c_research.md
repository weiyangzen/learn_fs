# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.c

## Purpose
`rv770_dpm.c` implements SMC-backed dynamic power management for RV770-family ASICs and also provides shared parsing and helper logic reused by newer Evergreen-era code paths. It converts BIOS PowerPlay states into SMC state tables, uploads firmware/state to SMC SRAM, controls voltage/MVDD/backbias/PCIe Gen2/spread spectrum/thermal events/clock gating, and performs runtime power-state switching through SMC messages.

## Important APIs, Types, and Functions
Public helpers include `rv770_get_ps`, `rv770_get_pi`, `evergreen_get_pi`, `rv770_restore_cgcg`, `rv770_stop_dpm`, `rv770_dpm_enabled`, `rv770_enable_thermal_protection`, `rv770_enable_acpi_pm`, `rv770_get_seq_value`, `rv770_write_smc_soft_register`, `rv770_populate_smc_t`, `rv770_populate_smc_sp`, `rv770_map_clkf_to_ibias`, `rv770_populate_vddc_value`, `rv770_populate_mvdd_value`, `rv770_calculate_memory_refresh_rate`, `rv770_enable_backbias`, `rv770_setup_bsp`, `rv770_program_git/tp/tpp/sstp/vc`, `rv770_upload_firmware`, `rv770_populate_initial_mvdd_value`, `rv770_enable_voltage_control`, `rv770_halt_smc`, `rv770_resume_smc`, `rv770_set_sw_state`, `rv770_set_boot_state`, UVD clock ordering helpers, forced-level controls, SMC start/stop wrappers, setup/enable/late-enable/disable/set-state/init/fini/debug/current-clock functions, and `rv770_dpm_vblank_too_short`.

## Control Flow
`rv770_dpm_init` allocates `rv7xx_power_info`, probes max VDDC/platform caps, parses ATOM PowerPlay tables, initializes defaults and feature flags, and defines SMC SRAM layout. `rv770_dpm_setup_asic` snapshots clock and voltage registers, detects memory type and PCIe Gen2 status, configures ODT thresholds, enables ACPI PM, and applies ASPM settings.

`rv770_dpm_enable` enables voltage control, builds VDDC/MVDD tables, retrieves ODT values, enables backbias/spread-spectrum/thermal, programs timing and activity controls, enables dynamic PCIe Gen2, uploads SMC firmware, initializes the SMC state table, writes SMC soft-register response times, starts the SMC, starts global DPM, enables clock gating, and enables thermal auto throttle. `rv770_dpm_late_enable` configures thermal interrupt thresholds and tells the SMC to enable thermal interrupts.

Power-state switching restricts levels, orders UVD clocks, halts the SMC, uploads a converted driver state, programs memory timings, adjusts ODT before and after the transition when needed, resumes the SMC, and sends `SwitchToSwState`. Disable unwinds thermal/spread-spectrum/PCIe/IRQ/clock-gating/DPM/SMC state and resets SMIO status.

## State and Persistence
Private `rv7xx_power_info` stores SMC table image, clock-register templates, voltage and MVDD tables, thresholds, memory type, PCIe status, feature flags, soft-register offsets, ODT values, active throttle sources, and timing constants. Parsed `rv7xx_ps` objects persist in `radeon_ps.ps_priv`. SMC SRAM persists uploaded firmware, soft registers, initial/ACPI/driver state tables, and state transitions until reset or DPM disable.

## Dependencies and Integration Points
The file depends on `rv770d.h`, `rv770_dpm.h`, `r600_dpm.h`, `cypress_dpm.h`, ATOMBIOS PowerPlay/clock/voltage/spread-spectrum/memory-info APIs, SMC communication helpers, RV730/RV740 chip overlays, PCIe indirect registers, IRQ thermal handling, UVD clock callbacks, debugfs, and common Radeon PM policy.

## Risks
SMC sequencing is failure-prone: firmware upload, table copy, halt/resume, and message acknowledgement all need correct ordering. Voltage-table construction can fail if VREG steps exceed `MAX_NO_VREG_STEPS` or if requested voltages do not map to GPIO entries. Family dispatch must choose the correct clock encoder. Memory timing and ODT changes can destabilize memory if thresholds or ATOM timing calls are wrong. Thermal IRQ programming and dynamic PCIe Gen2 must be unwound during disable. `rv770_dpm_vblank_too_short` disables MCLK switching on desktop RV770 by forcing the limit high, which is intentional but affects performance/power behavior.

## Test Signals
Signals include successful SMC firmware upload and state-table copy, DPM enable/disable and late thermal enable without errors, SMC message acknowledgements, stable state transitions under AC/DC/UVD changes, correct forced high/low behavior, valid debugfs current-level output, stable suspend/resume with DPM active, thermal interrupt delivery, and no memory errors across MCLK/ODT changes.
