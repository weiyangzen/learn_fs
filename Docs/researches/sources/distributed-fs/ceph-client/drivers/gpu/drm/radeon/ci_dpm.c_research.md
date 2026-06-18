# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.c

## Purpose

`ci_dpm.c` implements dynamic power management for the Radeon CIK discrete ASICs covered here, primarily Bonaire and Hawaii. It is the ASIC-specific DPM backend registered through `radeon_asic.c` for the generic Radeon power-management layer: it parses VBIOS PowerPlay data, builds host-side DPM state, uploads SMU7/SMC tables, starts and stops SMC-managed power control, handles runtime power-state transitions, controls fan/thermal behavior, manages UVD/VCE DPM, and exposes debug/current clock helpers.

The file is tightly coupled to SMC firmware layout (`SMU7_Firmware_Header`, `SMU7_Discrete_DpmTable`, `SMU7_Discrete_PmFuses`, `SMU7_Discrete_MCRegisters`) and to ATOM BIOS tables. The core job is translating Radeon driver policy (`struct radeon_ps`, display state, AC/DC limits, UVD/VCE activity, forced DPM level) into SMC-readable tables and PPSMC messages.

## Important APIs, Types, and Functions

Public ASIC hooks and helpers:

- `ci_dpm_init()` allocates and initializes `struct ci_power_info`, reads boot values and PowerPlay tables, parses extended power tables, resolves platform/GPIO/voltage capabilities, patches leakage-dependent tables, and sets default feature flags.
- `ci_dpm_setup_asic()` loads MC firmware, snapshots clock registers, detects memory type, enables static ACPI power management, and initializes SCLK notification state.
- `ci_dpm_enable()` performs the full SMC/DPM bring-up sequence.
- `ci_dpm_late_enable()` refreshes thermal range and initially powergates UVD.
- `ci_dpm_disable()` unwinds fan, thermal, power containment, DIDT, CAC, DPM, deep sleep, ULV, virtual counters, SMC, and memory arbiter state.
- `ci_dpm_pre_set_power_state()`, `ci_dpm_set_power_state()`, and `ci_dpm_post_set_power_state()` implement the generic Radeon DPM state-switch contract.
- `ci_dpm_force_performance_level()` forces high, low, or auto DPM levels using SMC masks/force messages.
- `ci_dpm_display_configuration_changed()` reprograms display gap and display-presence hints.
- `ci_dpm_powergate_uvd()` toggles UVD DPM/power-gating state.
- `ci_dpm_vblank_too_short()` determines whether MCLK switching is unsafe for the current display timing.
- `ci_dpm_get_current_sclk()`, `ci_dpm_get_current_mclk()`, `ci_dpm_get_sclk()`, and `ci_dpm_get_mclk()` provide clock query helpers.
- `ci_dpm_debugfs_print_current_performance_level()` and `ci_dpm_print_power_state()` provide debugfs/printk observability.
- `ci_fan_ctrl_get_fan_speed_percent()`, `ci_fan_ctrl_set_fan_speed_percent()`, `ci_fan_ctrl_get_mode()`, and `ci_fan_ctrl_set_mode()` are exported through Radeon ASIC fan-control hooks.

Key internal functions include `ci_initialize_powertune_defaults()`, `ci_populate_pm_base()`, `ci_process_firmware_header()`, `ci_init_smc_table()`, `ci_populate_all_graphic_levels()`, `ci_populate_all_memory_levels()`, `ci_generate_dpm_level_enable_mask()`, `ci_upload_dpm_level_enable_mask()`, the freeze/update/unfreeze helpers around SMC table edits, MC timing/register-table builders, UVD/VCE DPM helpers, thermal/fan helpers, and local PPSMC messaging primitives.

Important local data includes hard-coded `ci_pt_defaults` for Hawaii XT/Pro, Bonaire XT, and Saturn XT; `didt_config_ci[]` for DIDT programming; and local ATOM table unions used during PowerPlay parsing.

## Control Flow

Initialization starts in `ci_dpm_init()`. It allocates `ci_power_info`, derives system PCIe capabilities, reads VBIOS boot clocks/voltages/link state, parses platform caps and extended PowerPlay data, parses the PowerPlay state table, sets default thresholds and capabilities, maps EVV/leakage IDs to real voltages, patches voltage dependency tables, creates a small display-clock-to-VDDC table, initializes thermal limits, resolves VR hot and AC/DC GPIOs, detects voltage-control methods, and records whether ACPI PCIe performance requests are available.

ASIC setup through `ci_dpm_setup_asic()` prepares hardware before SMC DPM is enabled. It loads MC microcode, snapshots current PLL/MPLL/register values used later for SMC table construction, detects GDDR5 vs DDR3 from `MC_SEQ_MISC0`, enables static ACPI power management, and clears SCLK throttle notification thresholds.

`ci_dpm_enable()` rejects enable if the SMC is already running; enables voltage control and constructs voltage tables; optionally builds dynamic MC register tables; enables spread spectrum, thermal protection, display gap handling, and virtual counters; uploads SMC firmware and reads firmware table offsets; builds and uploads SMC DPM, MC, arbiter, and Powertune tables; starts the SMC; then enables VR-hot, display notification, SCLK control, ULV, deep sleep, voltage/SCLK/MCLK/PCIe DPM, DIDT, CAC, power containment, power-limit adjustment, auto thermal throttle, optional thermal SCLK DPM, and thermal/fan controller state.

Power-state changes flow through `pre_set`, `set`, and `post` hooks. The pre hook copies and adjusts requested state for display, DC, battery, VCE, and vblank constraints. The set hook computes whether SCLK/MCLK table edits are needed, optionally requests PCIe upshift, freezes domains, uploads changed levels and MC timing data, recomputes masks, updates VCE DPM, unfreezes domains, uploads masks, and optionally posts PCIe downshift. The post hook persists the requested state as current.

Disable unwinds most of enable in reverse, including UVD ungate, fan restore, thermal/power containment/CAC/DIDT/spread-spectrum disable, DPM stop, deep sleep/ULV disable, virtual-counter clear, SMC reset/clock stop, memory arbiter F0 restore, thermal SCLK DPM disable, and boot-state restore.

## State and Persistence Behavior

All private runtime state is rooted at `rdev->pm.dpm.priv` as `struct ci_power_info`. It caches host DPM tables, SMC table images, SMC SRAM offsets, voltage/leakage/boot/ACPI/thermal/fan/PCIe capability state, current/requested power-state copies, DPM masks, media flags, and fan-control ownership. SMC SRAM and hardware registers retain firmware-visible state after upload, so failed operations can leave partially programmed firmware or hardware state until disable/reset paths run.

The code snapshots original fan mode/TMIN before manual mode and snapshots PLL/MPLL/DLL registers before synthesizing ACPI, graphics, and memory levels. `ci_dpm_fini()` frees per-state private data, `rdev->pm.dpm.ps`, `rdev->pm.dpm.priv`, the display VDDC dependency table, and extended power-table allocations.

## Dependencies and Integration Points

This file depends on Radeon core/ASIC dispatch, CIK register definitions, PPSMC message definitions, SMU7 discrete table layouts, SMC SRAM helpers from `ci_smc.c`, ATOM BIOS parsing, R600/SI DPM helper routines, MC firmware/memory timing helpers, ACPI PCIe performance requests, generic Radeon PM, media clients, display-change paths, debugfs, and sysfs fan/force-performance controls.

The ASIC function table wires these hooks for Bonaire/Hawaii-class ASICs. Media code reaches UVD/VCE paths through generic wrappers, sysfs reaches force-performance and fan controls, and display/thermal paths feed policy changes back into DPM.

## Risks and Edge Cases

- SMC sequencing is fragile and many failures return after partial register/SMC changes.
- SMC table endianness is hand-managed per field.
- VBIOS/PowerPlay table counts are trusted in several loops.
- `ci_set_private_data_variables_based_on_pptable()` indexes the MCLK table with the SCLK table count when setting `max_clock_voltage_on_ac.mclk`, which is risky if counts differ.
- `ci_populate_mvdd_value()` appears to return `-EINVAL` even after finding a value, causing ACPI memory `MinMvdd` to fall back to zero.
- UVD/VCE enable-mask loops need scrutiny for zero-count tables.
- `ci_get_lowest_enabled_level()` assumes nonzero masks.
- Dynamic MC timing and early-Hawaii register patches are high-risk hardware paths.
- `ci_dpm_force_performance_level()` high-level PCIe branch passes the enum `level` to `ci_dpm_force_state_pcie()` rather than the computed highest level index.
- Fan-control transitions require callers to leave SMC fan control before manual PWM writes.
- Fan-table slope calculation can divide by zero if firmware/platform temperature points are malformed.

## Test Signals

Useful validation signals include kernel build coverage; boot on Bonaire/Hawaii with DPM enabled; suspend/resume and unload/reload; sysfs force-performance transitions; debugfs SCLK/MCLK observation; display mode and multi-CRTC changes; UVD decode and VCE encode start/stop; fan automatic/manual tests; thermal/VR-hot throttling; PCIe link-speed checks; and sustained-load Powertune/power-limit behavior.
