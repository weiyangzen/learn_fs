# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dpm.h

## Purpose
`si_dpm.h` defines the Southern Islands DPM private state schema and a small cross-file helper API. It bridges generic Northern Islands/Evergreen/RV7xx DPM structures with SI-specific SMC tables, PowerTune/CAC/DTE data, memory-controller register tables, ULV parameters, PCIe policy, SVI2 metadata, and fan-control bookkeeping.

## Important APIs, types, and data
- Includes `ni_dpm.h` and `sislands_smc.h`, so the header depends on shared DPM state, Atom voltage-table types, and SMC structure definitions.
- `enum si_cac_config_reg_type` distinguishes normal MMIO register configuration from SMC clock-gating indexed register configuration.
- `struct si_cac_config_reg` describes one CAC register field patch: offset, mask, shift, value, and register-space type.
- `struct si_powertune_data`, `struct si_dyn_powertune_data`, and `struct si_dte_data` carry static and runtime PowerTune/CAC/DTE parameters such as leakage coefficients, CAC windows, long-term-average settings, temperature filters, thresholds, and enable defaults.
- `struct si_clock_registers` snapshots boot SPLL/MPLL/DLL registers so SMC power levels can be populated from known hardware state.
- `struct si_mc_reg_entry` and `struct si_mc_reg_table` store AtomBIOS memory-controller timing entries and the SI SMC register-address/value form.
- `struct si_leakage_voltage` maps special leakage-index pseudo-voltages to real board voltages read from AtomBIOS.
- `struct si_ulv_param` stores ultra-low-voltage support, its power level, control registers, delay, and PCIe x1 preference.
- `struct si_power_info` is the central SI private power state. It embeds `struct ni_power_info` as its first field, then adds cached registers, SMC scratch tables, voltage tables, leakage data, ULV info, PCIe state, feature flags, SMC firmware offsets, PowerTune/DTE pointers, SVI2 GPIO IDs, and fan control state.
- Exported helpers are `si_get_ddr3_mclk_frequency_ratio`, `si_get_mclk_frequency_ratio`, and `si_trim_voltage_table_to_fit_state_table`.

## Control flow and integration points
The header has no executable control flow, but its layout shapes the runtime behavior of `si_dpm.c`. `si_dpm_init` allocates `struct si_power_info` and stores it in `rdev->pm.dpm.priv`; helper accessors then cast it back and access embedded NI/Evergreen/RV7xx state. SMC table builders fill the scratch SMC structures stored in `si_power_info`, while firmware header parsing fills the SMC offset fields. Consumers outside `si_dpm.c`, especially CIK DPM code, reuse the exported memory-clock ratio and voltage-table trimming helpers.

## State and persistence behavior
This header defines persistent driver state rather than mutating it. Instances of `struct si_power_info` persist for the DPM lifetime and are freed by `si_dpm_fini`. The SMC offset fields persist after firmware header parsing and are used for later SMC SRAM writes. Cached clock registers represent boot hardware state used repeatedly when constructing initial, ACPI, ULV, and driver power levels. Fan fields persist the pre-manual default mode so manual fan control can be reverted.

## Dependencies and constraints
`struct si_power_info` must keep `struct ni_power_info ni` first because existing helper code treats SI state as NI/Evergreen/RV7xx state through embedded base structures. Array sizes are tied to SMC ABI constants such as `SMC_SISLANDS_MC_REGISTER_ARRAY_SIZE`, `SMC_SISLANDS_DTE_MAX_FILTER_STAGES`, and `SISLANDS_MAX_HARDWARE_POWERLEVELS`. Callers must respect these fixed counts when copying AtomBIOS tables and building SMC payloads.

## Risks and test signals
The main risks are ABI and layout drift. Reordering the first field breaks inherited power-info access; changing table sizes or indexes breaks SMC SRAM payload construction; changing defaults for DPM2, ULV, or leakage constants changes throttling behavior. Compile coverage catches many type/layout errors, but runtime signals are DPM initialization, power-state switching, CAC/DTE enablement, MC timing upload, fan control, and reuse of the exported helpers by later Radeon DPM code.
