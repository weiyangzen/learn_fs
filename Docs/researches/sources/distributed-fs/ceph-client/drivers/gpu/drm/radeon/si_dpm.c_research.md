# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.c

## Purpose
`si_dpm.c` implements Southern Islands Radeon dynamic power management. It translates AtomBIOS PowerPlay tables and board-specific limits into SMC-resident state tables, programs clock/voltage/memory timing registers, manages PowerTune/CAC/DTE behavior, controls thermal/fan policy, and exposes the SI DPM hooks used by the Radeon ASIC dispatch table.

The file is specific to SI-family chips such as Tahiti, Pitcairn, Verde, Oland, and Hainan. Its large static front matter is not generic data: it contains ASIC and device-id-specific CAC weights, leakage coefficients, PowerTune defaults, and DTE thermal-estimator tables that directly affect throttling and power containment.

## Important APIs, types, and functions
- Public DPM lifecycle hooks: `si_dpm_init`, `si_dpm_setup_asic`, `si_dpm_enable`, `si_dpm_late_enable`, `si_dpm_disable`, `si_dpm_pre_set_power_state`, `si_dpm_set_power_state`, `si_dpm_post_set_power_state`, `si_dpm_fini`, and `si_dpm_display_configuration_changed`.
- Public controls and observability: `si_dpm_force_performance_level`, `si_dpm_debugfs_print_current_performance_level`, `si_dpm_get_current_sclk`, `si_dpm_get_current_mclk`, fan percent/mode helpers, and exported memory-clock ratio helpers `si_get_ddr3_mclk_frequency_ratio`, `si_get_mclk_frequency_ratio`, and `si_trim_voltage_table_to_fit_state_table`.
- SMC table builders: `si_init_smc_table`, `si_upload_sw_state`, `si_upload_ulv_state`, `si_populate_smc_tdp_limits`, `si_initialize_smc_cac_tables`, `si_initialize_smc_dte_tables`, `si_init_smc_spll_table`, `si_populate_mc_reg_table`, and `si_upload_mc_reg_table`.
- Clock and voltage conversion helpers: `si_calculate_sclk_params`, `si_populate_sclk_value`, `si_populate_mclk_value`, `si_construct_voltage_tables`, `si_populate_voltage_value`, `si_get_std_voltage_value`, `si_populate_phase_shedding_value`, and `si_convert_power_level_to_smc`.
- State adjustment and transition helpers: `si_apply_state_adjust_rules`, `si_convert_power_state_to_smc`, `si_restrict_performance_levels_before_switch`, `si_set_sw_state`, `si_halt_smc`, `si_resume_smc`, `si_enable_smc_cac`, `si_enable_power_containment`, and ULV/PCIe/VCE helpers.
- Important local data includes the ASIC-specific `si_cac_config_reg` arrays, `si_powertune_data` instances, DTE tables, `union power_info`, `union pplib_clock_info`, and `union pplib_power_state`. Runtime state lives primarily in `struct si_power_info`, defined in `si_dpm.h`, and its embedded `ni_power_info`/`evergreen_power_info`/`rv7xx_power_info` ancestry.

## Control flow
Initialization begins in `si_dpm_init`. It allocates `struct si_power_info`, derives PCIe capabilities, reads leakage values, patches voltage dependency tables, parses platform and extended power tables, parses SI PowerPlay states, initializes display-clock voltage rules, detects voltage control mechanisms, configures feature defaults, and selects PowerTune/CAC/DTE tables according to chip family and PCI device id.

ASIC setup in `si_dpm_setup_asic` loads MC firmware, detects memory type, snapshots boot clock registers, and enables ACPI static power management. Full enablement in `si_dpm_enable` is a strict hardware bring-up sequence: enable voltage control, build voltage and MC timing tables, enable spread spectrum and thermal protection, program SCLK trend/filter defaults, load SMC firmware, read SMC firmware table offsets, initialize SMC state/SPLL/ARB/MC/CAC/DTE/TDP/fan tables, program response times and deep-sleep registers, start the SMC, enable SCLK/DPM, register thermal throttling, start the thermal controller, and set the current power state to the boot state.

Power-state changes are split across pre/set/post hooks. `si_dpm_pre_set_power_state` copies the requested state into the SI/Evergreen requested state and applies display, UVD/VCE, voltage, dependency-table, DC-limit, and forced-clock adjustments. `si_dpm_set_power_state` then disables ULV and active power containment, requests PCIe speed changes when needed, halts the SMC, uploads the new driver state, display timing soft registers, ULV state, MC register data, and memory timing data, resumes the SMC, asks it to switch to the software state, adjusts UVD/VCE clocks, optionally re-enables ULV, CAC, DTE, and power containment, and refreshes TDP limits through `si_power_control_set_level`. `si_dpm_post_set_power_state` commits the requested state as current.

Disable reverses the policy stack: it stops thermal/fan management, disables ULV, clears voltage control tuning, disables containment and CAC, disables spread spectrum and thermal throttle sources, stops global DPM, asks the SMC to reset to defaults, resets/stops the SMC, switches MC arbitration back to F0, and restores the boot power state in driver state.

## State and persistence behavior
The file mutates several layers of persistent state. Driver-owned persistent state includes `rdev->pm.dpm.priv`, the parsed power-state array and `ps_priv` allocations, dynamic dependency tables, current/requested/boot power-state pointers, fan mode snapshots, leakage tables, SMC firmware offsets, cached clock registers, and feature flags such as `enable_dte`, `enable_ppm`, `voltage_control_svi2`, `vddc_phase_shed_control`, and `fan_is_controlled_by_smc`.

Hardware state is programmed through MMIO registers for SCLK/MPLL/SPLL control, CAC, thermal interrupts, fan/tach PWM, display gap handling, voltage control, PCIe link/lane settings, MC timing, MC low-power mirror registers, and global DPM enablement. SMC-resident state is persisted by writes into SMC SRAM at firmware-advertised offsets for `SISLANDS_SMC_STATETABLE`, MC register tables, CAC configuration, DTE configuration, SPLL division tables, PAPM parameters, fan tables, and soft registers. These writes use big-endian SMC structures and remain active until overwritten, firmware reset, SMC reset, or device reset.

Memory ownership is explicit but scattered: `si_dpm_init` allocates `si_power_info`, per-state `struct ni_ps`, `rdev->pm.dpm.ps`, and a display-clock voltage dependency table; `si_dpm_fini` frees those and the extended power table. Several table builders allocate temporary SMC-format buffers with `kzalloc_obj` and free them after `si_copy_bytes_to_smc`.

## Dependencies and integration points
`si_dpm.c` sits in the Radeon kernel driver power-management stack. It depends on AtomBIOS helpers for PowerPlay parsing, clock dividers, memory PLL dividers, voltage tables, leakage indices, spread-spectrum data, MC timing programming, and default voltage queries. It uses lower-generation helpers from `r600_dpm.c`, `rv770`, `evergreen`, `btc`, and `ni_dpm` for platform caps, dependency-rule enforcement, UVD clock ordering, memory arbitration switching, and shared power-info structures.

SMC interaction depends on `si_smc.c` and `sislands_smc.h` for SRAM access and PPSMC message definitions. Hardware register names and bitfields come from `sid.h`, `si.h`, and related Radeon headers. VCE integration is through `vce_v1_0_enable_mgcg` and `radeon_set_vce_clocks`. PCIe integration uses PCI capability helpers, Radeon PCIe lane/speed helpers, and optional ACPI performance requests. The public DPM hooks are wired through `radeon_asic.c`/`radeon_asic.h`.

## Risks and edge cases
- The enable and state-switch sequences are order-sensitive. Halting/resuming the SMC, uploading SMC tables, switching MC arbitration sets, and changing voltage/clock/PCIe policy out of order can hang the GPU or leave unsafe clocks active.
- Many fields are endian-converted into SMC structures. Missing `cpu_to_be16`/`cpu_to_be32` conversions or copying host-endian data into SMC SRAM would corrupt firmware interpretation.
- Static CAC/DTE/PowerTune tables are keyed by chip family and PCI device id. Wrong table selection can mis-estimate leakage or thermal behavior and cause under-throttling, over-throttling, fan problems, or instability.
- Voltage table handling has several fallback paths. GPIO LUT, SVI2, MVDD, VDDCI, leakage-index patching, and phase shedding must all agree with the AtomBIOS data and maximum SMC level counts.
- Several functions intentionally disable features on errors and continue, for example CAC or dynamic AC timing. This avoids hard failures but can hide performance or thermal-policy regressions.
- Display, UVD, VCE, and multi-CRTC constraints can force high clocks or disable switching. Regressions here commonly show up as flicker, underruns, video decode/encode failures, or excessive idle power.
- There are legacy `#if 0` blocks and comments marking incomplete validation, especially around ULV and display requirements. These paths should be treated conservatively.

## Test signals
Useful validation includes SI ASIC probe and DPM enable/disable, suspend/resume, runtime power-state switching on AC and DC, forced low/high/auto levels, debugfs current SCLK/MCLK reporting, thermal interrupt delivery, fan auto/static mode changes, UVD playback, VCE encode clock changes, multi-monitor modesets, high pixel-clock displays, PCIe speed/lane transitions, and GPU stability under power/thermal stress. Kernel logs should be checked for the explicit `DRM_ERROR` messages emitted by firmware upload, SMC header parsing, SMC table initialization, CAC/DTE setup, MC timing upload, and state switch failures.
