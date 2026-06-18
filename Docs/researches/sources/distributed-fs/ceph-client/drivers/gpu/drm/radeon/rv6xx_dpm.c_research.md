# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.c

## Purpose
`rv6xx_dpm.c` implements dynamic power management for RV610/RV630/RV670-era Radeon ASICs. It programs register-based, non-SMC DPM state tables for engine clock, memory clock, voltage GPIO, backbias, PCIe Gen2, spread spectrum, thermal throttling, display-gap handling, UVD clock ordering, and debug/status reporting.

## Important APIs, Types, and Functions
The public entry points are `rv6xx_dpm_init`, `rv6xx_dpm_enable`, `rv6xx_dpm_disable`, `rv6xx_dpm_set_power_state`, `rv6xx_setup_asic`, `rv6xx_dpm_display_configuration_changed`, `rv6xx_dpm_print_power_state`, `rv6xx_dpm_debugfs_print_current_performance_level`, `rv6xx_dpm_get_current_sclk`, `rv6xx_dpm_get_current_mclk`, `rv6xx_dpm_get_sclk`, `rv6xx_dpm_get_mclk`, `rv6xx_dpm_force_performance_level`, and `rv6xx_dpm_fini`. Internally it uses `struct rv6xx_power_info`, `struct rv6xx_pm_hw_state`, `struct rv6xx_ps`, and `struct rv6xx_pl` from `rv6xx_dpm.h`.

Key helpers generate SCLK stepping tables (`rv6xx_convert_clock_to_stepping`, `rv6xx_generate_steps`, `rv6xx_output_stepping`), program MCLK and voltage entries, compute activity thresholds, and parse ATOM PowerPlay tables. Register helpers from `r600_dpm.h` write common R600 DPM blocks such as power-level entries, voltage pins, activity thresholds, thermal protection, and DPM start/stop controls.

## Control Flow
Initialization allocates `rdev->pm.dpm.priv`, reads platform caps, parses BIOS PowerPlay states, fills voltage response defaults, probes PLL dividers, spread-spectrum support, voltage GPIO support, and feature toggles. ASIC setup enables ACPI PM and optional ASPM L0s/L1/PLL sleep.

Enable refuses to run if DPM is already active, then enables backbias/spread spectrum, programs timing constants, BSP/GIT/TP/TPP/SSTP/FCP/voltage timing, display gap, power-level entry state, and voltage GPIO masks. It calculates the boot power state's stepping data, generates SCLK/MCLK/voltage tables, programs low/medium/high hardware levels, enables levels, enables thermal auto throttle, starts DPM, then enables dynamic PCIe Gen2 and gfx clock gating.

Power-state switching is staged through a safe low/transition state: UVD clocks may be lowered first, high/medium levels are disabled, transition SCLK and a context-switch MCLK entry are programmed, safe voltage/backbias/PCIe settings are applied, dynamic voltage/backbias is temporarily disabled, voltage is stepped up if needed, the engine moves through medium and low, new low entries are installed, voltage may be stepped down, dynamic controls are re-enabled, final low/medium/high tables are generated, and UVD clocks may be raised after the engine clock change.

## State and Persistence
Persistent state lives in `rdev->pm.dpm`: parsed power states, current/requested/boot pointers, platform caps, forced level, display CRT mask, and response times. Private RV6xx state in `struct rv6xx_power_info` tracks feature booleans, reference divider scale, active throttle sources, restricted forced levels, and the computed hardware state arrays. Hardware state persists in GPU registers until disabled or reprogrammed.

## Dependencies and Integration Points
This file depends heavily on ATOMBIOS (`radeon_atom_get_clock_dividers`, voltage GPIO, spread-spectrum and default-voltage queries), `r600_dpm` register helpers, PCIe indirect accessors, IRQ thermal handling, UVD clock callbacks, debugfs `seq_file`, and common Radeon PM policy. It integrates with the radeon ASIC callbacks for DPM lifecycle, display configuration changes, forced performance levels, and current-clock reporting.

## Risks
There are several hardware-sequencing risks: incorrect voltage stepping can undervolt during clock transitions; PCIe Gen2 toggling must fall back to Gen1 safely; spread-spectrum programming relies on valid ATOM data; display-gap changes depend on active CRTC masks; and DPM disable must unwind thermal IRQs and clock gating. The code also has a suspicious assignment in `rv6xx_calculate_voltage_stepping_parameters`: when low voltage differs from medium, it assigns `medium_vddc_index = R600_POWER_LEVEL_LOW` instead of `low_vddc_index`, which can affect voltage table selection.

## Test Signals
Useful signals include successful `rv6xx_dpm_enable`/disable without `-EINVAL`, debugfs current performance level matching `TARGET_AND_CURRENT_PROFILE_INDEX`, stable current SCLK/MCLK reads, clean thermal IRQ enable/disable, absence of hangs during PowerPlay state transitions and UVD state changes, correct forced high/low behavior, and suspend/resume coverage with DPM active.
