# Research: subset-b-003713

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.c -->
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

Key internal functions:

- `ci_initialize_powertune_defaults()` selects hard-coded Powertune/BAPM defaults by PCI device ID and enables CAC/TDC/package power tracking features.
- `ci_populate_pm_base()` builds and uploads `SMU7_Discrete_PmFuses`, including BAPM VID tables, SVI load line, TDC limit, fuzzy-fan delta, VID min/max, and base leakage.
- `ci_process_firmware_header()` reads SMC SRAM firmware-header pointers into `pi->dpm_table_start`, `soft_regs_start`, `mc_reg_table_start`, `fan_table_start`, and `arb_table_start`.
- `ci_init_smc_table()` constructs and uploads the main SMC DPM table, including voltage, graphics, memory, link, ACPI, UVD, VCE, ACP, SAMU, BAPM, boot, thermal, and interval fields.
- `ci_populate_all_graphic_levels()` and `ci_populate_all_memory_levels()` build the SMC graphics and memory level arrays and upload them directly to the firmware table.
- `ci_generate_dpm_level_enable_mask()` trims the SCLK/MCLK/PCIe DPM tables to the requested power-state range and records enable masks.
- `ci_upload_dpm_level_enable_mask()` applies display minimum voltage and sends SCLK/MCLK masks to the SMC.
- `ci_find_dpm_states_clocks_in_dpm_table()`, `ci_freeze_sclk_mclk_dpm()`, `ci_populate_and_upload_sclk_mclk_dpm_levels()`, and `ci_unfreeze_sclk_mclk_dpm()` coordinate runtime table edits around SMC freeze/unfreeze messages.
- `ci_initialize_mc_reg_table()`, `ci_populate_initial_mc_reg_table()`, and `ci_update_and_upload_mc_reg_table()` translate ATOM memory-controller timing tables into SMC MC register tables.
- `ci_program_memory_timing_parameters()` and related helpers compute and upload MC arbiter timing tables for SCLK/MCLK combinations.
- `ci_enable_uvd_dpm()`/`ci_update_uvd_dpm()` and `ci_enable_vce_dpm()`/`ci_update_vce_dpm()` manage media-block DPM masks and boot levels.
- `ci_thermal_start_thermal_controller()`, `ci_thermal_set_temperature_range()`, `ci_thermal_enable_alert()`, `ci_thermal_setup_fan_table()`, and fan-control helpers program thermal interrupts and SMC/hardware fan control.
- `ci_send_msg_to_smc()`, `ci_send_msg_to_smc_with_parameter()`, and `ci_send_msg_to_smc_return_parameter()` are the local PPSMC messaging primitives.

Important local data:

- Hard-coded `ci_pt_defaults` instances for Hawaii XT/Pro, Bonaire XT, and Saturn XT seed Powertune/BAPM behavior.
- `didt_config_ci[]` describes DIDT register programming for SQ/DB/TD/TCP ramping.
- `union power_info`, `union pplib_clock_info`, and `union pplib_power_state` are local ATOM table views used during PowerPlay parsing.

## Control Flow

Initialization starts in `ci_dpm_init()`. It allocates `ci_power_info`, derives system PCIe capabilities, reads VBIOS boot clocks/voltages/link state, parses platform caps and extended PowerPlay data, parses the PowerPlay state table, sets default thresholds and capabilities, maps EVV/leakage IDs to real voltages, patches voltage dependency tables, creates a small display-clock-to-VDDC table, initializes thermal limits, resolves VR hot and AC/DC GPIOs, detects voltage-control methods, and records whether ACPI PCIe performance requests are available.

ASIC setup through `ci_dpm_setup_asic()` prepares hardware before SMC DPM is enabled. It loads MC microcode, snapshots current PLL/MPLL/register values used later for SMC table construction, detects GDDR5 vs DDR3 from `MC_SEQ_MISC0`, enables static ACPI power management, and clears SCLK throttle notification thresholds.

`ci_dpm_enable()` is the main bring-up sequence:

1. Rejects enable if the SMC is already running.
2. Enables voltage control and constructs voltage tables if the board exposes GPIO or SVID2 voltage control.
3. Builds the dynamic MC register table if dynamic AC timing is enabled; on failure it disables only that capability and continues.
4. Enables spread spectrum, thermal protection, display gap handling, and virtual counters.
5. Uploads SMC firmware, reads the firmware header table offsets, switches memory arbiter set F0 to F1, builds and uploads SMC DPM tables, initializes the arbiter table index, uploads MC register tables if enabled, and uploads Powertune fuse data.
6. Starts the SMC and then enables VR-hot interrupt, display-change notification, SCLK control, ULV, deep sleep, voltage/SCLK/MCLK/PCIe DPM, DIDT, CAC, power containment, power-limit adjustment, auto thermal throttle, optional thermal SCLK DPM, and thermal/fan controller state.
7. Copies the boot power state into `current_rps/current_ps`.

Power-state changes flow through three hooks. `ci_dpm_pre_set_power_state()` copies the generic requested state into private storage and applies local adjustment rules, including VCE minimum clocks, DC clock limits, battery classification, and disabling MCLK switching when multiple CRTCs or too-short vblank make it unsafe. `ci_dpm_set_power_state()` then decides whether the SMC table needs overdrive-like SCLK/MCLK edits, optionally requests a faster PCIe link before the state change, freezes affected DPM domains, uploads changed graphics/memory levels, recomputes enable masks, updates VCE DPM, refreshes SCLK thresholds, uploads changed MC timing data, unfreezes DPM, uploads masks, and finally posts PCIe downshift requests. `ci_dpm_post_set_power_state()` updates current-state persistence after the generic layer considers the transition complete.

Disable unwinds most of enable in reverse. It ungates UVD, exits early if the SMC is no longer running, restores default fan mode, disables thermal protection, power containment, CAC, DIDT, spread spectrum, and thermal auto-throttle, stops DPM, disables deep sleep and ULV, clears virtual counters, resets SMC defaults, stops the SMC, returns the memory arbiter to F0, disables thermal SCLK DPM, and restores the boot power state.

## State and Persistence Behavior

All private runtime state is rooted at `rdev->pm.dpm.priv` as `struct ci_power_info`. This object persists from `ci_dpm_init()` until `ci_dpm_fini()` and caches:

- Host-side DPM tables and SMC table images.
- SMC SRAM offsets discovered from firmware.
- Voltage, leakage, boot, ACPI, thermal, fan, PCIe, and feature-capability state.
- Current and requested `radeon_ps` plus private `ci_ps` copies.
- Runtime masks such as `dpm_level_enable_mask`, `last_mclk_dpm_enable_mask`, and update flags in `need_update_smu7_dpm_table`.

SMC state is persistent outside normal CPU memory after upload. The driver writes SMC SRAM via `ci_copy_bytes_to_smc()`/`ci_write_smc_sram_dword()` and drives firmware behavior through PPSMC messages. Several hardware registers are also left programmed while DPM is active: display gap registers, thermal interrupt registers, PLL/spread-spectrum registers, virtual-counter registers, MC arbiter/timing registers, DIDT registers, and fan registers.

The code snapshots some original hardware state before switching control modes. Fan control saves `fan_ctrl_default_mode` and `t_min` before forcing static mode, then restores them in `ci_fan_ctrl_set_default_mode()`. Clock-register snapshots are captured in `ci_read_clock_registers()` and later reused when constructing ACPI, graphics, and memory SMC levels.

Allocated memory is released in `ci_dpm_fini()`: per-power-state `ci_ps` objects, `rdev->pm.dpm.ps`, `rdev->pm.dpm.priv`, the display VDDC dependency table, and extended power-table allocations via `r600_free_extended_power_table()`.

## Dependencies and Integration Points

This file depends on:

- Radeon core structures and ASIC dispatch in `radeon.h`, `radeon_asic.h`, and `radeon_asic.c`.
- CIK register definitions and helpers in `cik.h`/`cikd.h`, including SMC, thermal, MC, PLL, and PCIe register fields.
- SMC firmware protocol definitions in `ppsmc.h` and SMU7 table definitions in `smu7_discrete.h` through `ci_dpm.h`.
- SMC SRAM/firmware primitives implemented in `ci_smc.c`.
- ATOM BIOS parsing helpers from `atom.h`, `radeon_atombios.c`, `r600_dpm.c`, and `si_dpm.c`.
- MC firmware loading via `ci_mc_load_microcode()` and memory timing helpers such as `radeon_atom_set_engine_dram_timings()`, `radeon_atom_get_memory_pll_dividers()`, and `rv770_get_memory_module_index()`.
- ACPI PCIe performance request helpers when `CONFIG_ACPI` is enabled.
- Generic Radeon PM callers in `radeon_pm.c`, media clients in `radeon_uvd.c`/`radeon_vce.c`, display-change paths, debugfs, and sysfs force-performance/fan controls.

The ASIC function table wires these hooks for Bonaire/Hawaii-class ASICs. Media code calls the generic `radeon_dpm_enable_uvd()`/`radeon_dpm_enable_vce()` wrappers, which reach `ci_dpm_powergate_uvd()` and state-update paths. Sysfs force-performance-level writes reach `ci_dpm_force_performance_level()`. Thermal interrupts and display reconfiguration feed back into the DPM policy through generic PM/display code.

## Risks and Edge Cases

- SMC sequencing is fragile. Most operations require the SMC firmware to be uploaded, table offsets to be valid, and `ci_is_smc_running()` to match expectations. A failed PPSMC message often becomes `-EINVAL`, but many state changes before the failure are not rolled back.
- Endianness must be correct. SMC tables use big-endian fields, and each table-population helper selectively converts fields before upload. A missing or duplicate conversion can produce firmware-visible corruption.
- Table counts from VBIOS/PowerPlay are trusted in many loops. Some helpers validate bounds, but others index related tables assuming matching counts.
- `ci_set_private_data_variables_based_on_pptable()` indexes `allowed_mclk_vddc_table` with `allowed_sclk_vddc_table->count - 1` when setting `max_clock_voltage_on_ac.mclk`; if SCLK and MCLK dependency table counts differ, this can select the wrong MCLK entry or risk out-of-bounds access.
- `ci_populate_mvdd_value()` sets a voltage when it finds a matching dependency entry but still returns `-EINVAL` unconditionally. In current use this makes ACPI memory `MinMvdd` fall back to zero, which may be intentional legacy behavior or a latent bug.
- UVD/VCE enable-mask loops start from `count - 1` and use signed loop variables. Zero-count tables can be risky depending on integer conversion; UVD has some count checks elsewhere, but the pattern deserves scrutiny.
- `ci_get_lowest_enabled_level()` assumes a nonzero mask; callers check that today, but the helper itself has no bound.
- Dynamic memory timing and MC register patching have board-specific exceptions for early Hawaii device IDs/revision 0 and depend on VBIOS MC tables. Regression risk is high on marginal memory configurations.
- `ci_dpm_force_performance_level()` appears to pass `level` rather than the computed highest PCIe index to `ci_dpm_force_state_pcie()` in the high-level branch. Because enum values and DPM indices are separate concepts, this path should be verified against hardware behavior.
- Fan-control transitions reject manual PWM writes while SMC fan control is active. Callers must switch mode first or get `-EINVAL`.
- Thermal/fan setup computes slopes from fan table temperature differences; malformed or equal temperature points from firmware/platform data can divide by zero.

## Test Signals

Useful validation signals include:

- Kernel build coverage for `drivers/gpu/drm/radeon/ci_dpm.c`, `ci_dpm.h`, and `ci_smc.c` with Radeon enabled.
- Boot on Bonaire and Hawaii hardware with DPM enabled and firmware present; check for absence of `DRM_ERROR("ci_* failed")` messages during `ci_dpm_enable()`.
- Runtime suspend/resume and module unload/reload to exercise `ci_dpm_disable()`/`ci_dpm_enable()` and `ci_dpm_fini()`.
- Sysfs `power_dpm_force_performance_level` transitions among `low`, `high`, and `auto`, while watching debugfs current SCLK/MCLK output.
- Display mode changes, multiple active CRTCs, and high-refresh modes to verify vblank-based MCLK switching restrictions and display-gap programming.
- UVD decode and VCE encode start/stop tests to verify media DPM masks, boot levels, and MCLK mask interaction.
- Fan sysfs/manual PWM tests, including switching between automatic SMC fan control and manual modes.
- Thermal interrupt and throttling tests under load, including VR-hot GPIO behavior if available.
- PCIe link-speed transition checks on ACPI-capable systems and systems without ACPI performance-request support.
- Power-limit and Powertune behavior under sustained GPU load, with special attention to Hawaii where BAPM is disabled by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.h

## Purpose

`ci_dpm.h` is the private interface and state definition header for the CIK Radeon DPM implementation. It defines the Bonaire/Hawaii DPM constants, private power-state structures, SMC table caches, Powertune defaults, feature flags, and prototypes shared between `ci_dpm.c` and `ci_smc.c`. It also includes `smu7_discrete.h`, which supplies the firmware-facing SMC table layouts that the DPM code populates.

## Important APIs, Types, and Functions

Key constants:

- `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, and `SMU__NUM_PCIE_DPM_LEVELS` establish SMU7 DPM sizing before including `smu7_discrete.h`.
- `CISLANDS_MAX_HARDWARE_POWERLEVELS` limits parsed Radeon power states to two hardware performance levels.
- `CISLANDS_UNUSED_GPIO_PIN` is used for absent VR-hot/AC-DC GPIO pins.
- `CISLAND_MAX_DEEPSLEEP_DIVIDER_ID`, `MAX_REGULAR_DPM_NUMBER`, and `CISLAND_MINIMUM_ENGINE_CLOCK` constrain local DPM table construction.
- `POWERCONTAINMENT_FEATURE_*` bits track which SMC power-containment features were successfully enabled.
- `DPMTABLE_*` bits track why the SMU7 DPM table must be updated.
- Voltage-control constants distinguish no control, GPIO LUT control, and SVID2 control.
- `PCIE_PERF_REQ_*` constants encode ACPI PCIe performance requests.

Core private types:

- `struct ci_pl` is one performance level: memory clock, engine clock, PCIe generation, and lane count.
- `struct ci_ps` is the CIK-private representation of a Radeon power state. It stores a performance-level count, DC compatibility, an SCLK threshold, and up to two `ci_pl` levels.
- `struct ci_dpm_level`, `struct ci_single_dpm_table`, and `struct ci_dpm_table` are host-side DPM table abstractions for SCLK, MCLK, PCIe speed, VDDC, VDDCI, and MVDD.
- `struct ci_mc_reg_entry` and `struct ci_mc_reg_table` cache memory-controller register addresses and per-MCLK register data before converting them to `SMU7_Discrete_MCRegisters`.
- `struct ci_ulv_parm` stores ULV support, SMC parameter state, voltage-change delay, and the ULV performance level.
- `struct ci_leakage_voltage` maps virtual voltage/leakage IDs to actual voltages.
- `struct ci_dpm_level_enable_mask` carries enable masks for UVD, VCE, ACP, SAMU, SCLK, MCLK, and PCIe DPM.
- `struct ci_vbios_boot_state` records boot voltages, SCLK/MCLK, and PCIe link values read from VBIOS/current hardware.
- `struct ci_clock_registers` snapshots SPLL/MPLL/DLL registers used to synthesize SMC levels.
- `struct ci_thermal_temperature_setting` stores low, high, and shutdown thresholds in millidegrees C.
- `struct ci_pcie_perf_range` stores min/max PCIe generation or lane ranges for performance and power-saving policies.
- `enum ci_pt_config_reg_type` and `struct ci_pt_config_reg` describe generic Powertune/DIDT register programming entries.
- `struct ci_pt_defaults` stores ASIC-specific Powertune defaults, including SVI load-line, TDC, DTE ambient, display CAC, BAPM gradient, and BAPM thermal iteration constants.
- `struct ci_power_info` is the master private state object used as `rdev->pm.dpm.priv`.

Shared function prototypes:

- SMC SRAM and firmware helpers implemented in `ci_smc.c`: `ci_copy_bytes_to_smc()`, `ci_start_smc()`, `ci_reset_smc()`, `ci_program_jump_on_start()`, `ci_stop_smc_clock()`, `ci_start_smc_clock()`, `ci_is_smc_running()`, `ci_load_smc_ucode()`, `ci_read_smc_sram_dword()`, and `ci_write_smc_sram_dword()`.
- `ci_wait_for_smc_inactive()` is declared but the implementation in `ci_smc.c` is compiled out with `#if 0`; users should not rely on it unless that implementation is restored.

## Control Flow

The header itself has no executable control flow, but it defines the state carried through the lifecycle:

1. `ci_dpm_init()` allocates `struct ci_power_info` and fills boot, capability, GPIO, voltage, thermal, PCIe, leakage, and parsed power-state fields.
2. `ci_dpm_enable()` uses `ci_power_info` to build `SMU7_Discrete_DpmTable`, `SMU7_Discrete_MCRegisters`, and `SMU7_Discrete_PmFuses`, then uploads them to SMC SRAM through the prototypes declared here.
3. Runtime state transitions mutate `dpm_table`, `dpm_level_enable_mask`, `need_update_smu7_dpm_table`, media flags, and current/requested power-state copies.
4. `ci_dpm_disable()` and `ci_dpm_fini()` consume the same fields to restore hardware state and free allocations.

## State and Persistence Behavior

`struct ci_power_info` is the long-lived state anchor. Important persistence groups:

- SMC location state: `sram_end`, `dpm_table_start`, `soft_regs_start`, `mc_reg_table_start`, `fan_table_start`, and `arb_table_start`.
- SMC image state: `smc_state_table`, `smc_mc_reg_table`, and `smc_powertune_table`.
- Host policy state: DPM tables, voltage tables, leakage tables, boot state, thermal settings, PCIe ranges, activity targets, feature/capability flags, and runtime booleans.
- Runtime requested/current state: `current_rps/current_ps` and `requested_rps/requested_ps`.
- Fan state: default-mode tracking, SMC fan-control ownership, saved TMIN, and saved default PWM mode.

This design lets the implementation rebuild pieces of firmware-visible state without reparsing ATOM BIOS on every transition. The downside is that stale or partially updated fields can affect later transitions if an earlier enable or state change fails midway.

## Dependencies and Integration Points

The header depends directly on `ppsmc.h`, `radeon.h`, and `smu7_discrete.h`. It is included by both `ci_dpm.c` and `ci_smc.c`, and its SMC helper prototypes are used by the DPM implementation to transfer firmware and tables into SMC SRAM.

It is also indirectly coupled to:

- ATOM BIOS/PowerPlay structures stored in generic Radeon PM state.
- `radeon_asic.h`, where public `ci_dpm_*` hooks are declared separately for ASIC dispatch.
- CIK register definitions used by the implementation.
- Firmware constants from `radeon_ucode.h` used by `ci_smc.c` for old-style SMC firmware loading.

## Risks and Edge Cases

- `CISLANDS_MAX_HARDWARE_POWERLEVELS` is only two, so parsing more than two DPM levels per PowerPlay state truncates the state to low/high behavior. That matches the implementation but is a policy constraint.
- `MAX_REGULAR_DPM_NUMBER` is eight. Any firmware or table change with more levels needs coordinated updates across this header, SMU7 table definitions, and implementation bounds.
- `ci_wait_for_smc_inactive()` is declared while its implementation is disabled. A new caller would compile only if another definition exists; otherwise this declaration can mislead maintainers.
- `struct ci_power_info` mixes immutable capabilities, parsed VBIOS data, SMC SRAM offsets, runtime masks, and fan mode state. Changes need care to avoid reinitializing live runtime fields or retaining stale fields across disable/enable cycles.
- Many booleans represent both capabilities (`caps_*`) and current runtime flags (`*_enabled`, `*_power_gated`, `fan_is_controlled_by_smc`). Tests should distinguish whether a field means hardware support, desired policy, or current state.

## Test Signals

For this header, meaningful signals are mostly integration/build oriented:

- Compile `ci_dpm.c` and `ci_smc.c` together with Radeon enabled to catch layout/prototype mismatches.
- Exercise DPM init/enable/disable to validate `struct ci_power_info` fields are initialized before use and freed once.
- Check forced performance, UVD/VCE, fan, thermal, and display-change paths because they touch different subsets of the shared private state.
- Static analysis should focus on table bounds, uninitialized fields in `ci_power_info`, endian conversion of firmware table fields, and declarations without definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_smc.c

## Purpose

`ci_smc.c` provides the low-level SMC firmware and SRAM access primitives for the CIK Radeon DPM implementation. It controls SMC reset/clock state, loads SMC microcode, programs the startup jump, checks whether the SMC is running, and reads/writes SMC SRAM through indirect MMIO registers. `ci_dpm.c` builds policy and table contents; this file is the transport and lifecycle layer that moves bytes and dwords into the SMC address space.

## Important APIs, Types, and Functions

Public functions declared in `ci_dpm.h`:

- `ci_copy_bytes_to_smc()` copies arbitrary bytes into SMC SRAM, requiring a 4-byte-aligned start address and checking the caller-supplied limit.
- `ci_start_smc()` clears `RST_REG` in `SMC_SYSCON_RESET_CNTL`.
- `ci_reset_smc()` sets `RST_REG` in `SMC_SYSCON_RESET_CNTL`.
- `ci_program_jump_on_start()` writes a fixed 4-byte jump sequence at SMC address zero.
- `ci_stop_smc_clock()` sets `CK_DISABLE` in `SMC_SYSCON_CLOCK_CNTL_0`.
- `ci_start_smc_clock()` clears `CK_DISABLE`.
- `ci_is_smc_running()` checks that the clock is not disabled and that `SMC_PC_C` is at or beyond `0x20100`.
- `ci_load_smc_ucode()` copies SMC firmware into SRAM, supporting both new firmware headers and legacy family-specific firmware sizes/addresses.
- `ci_read_smc_sram_dword()` reads one dword from SMC SRAM.
- `ci_write_smc_sram_dword()` writes one dword to SMC SRAM.

Internal helper:

- `ci_set_smc_sram_address()` validates 4-byte alignment and bounds, writes `SMC_IND_INDEX_0`, and disables auto-increment for indexed access.

Compiled-out helper:

- `ci_wait_for_smc_inactive()` exists under `#if 0`, polling clock state and returning `PPSMC_Result_OK`. Because it is not compiled, the declaration in `ci_dpm.h` should be treated cautiously.

## Control Flow

All SRAM accesses use the same indirect-register pattern. `ci_set_smc_sram_address()` validates the target dword and writes the indirect index. `ci_read_smc_sram_dword()` and `ci_write_smc_sram_dword()` hold `rdev->smc_idx_lock`, call the helper, then access `SMC_IND_DATA_0`. `ci_copy_bytes_to_smc()` also holds `smc_idx_lock` for the whole transfer.

`ci_copy_bytes_to_smc()` writes full dwords in big-endian SMC byte order: source bytes are packed as `src[0] << 24 | src[1] << 16 | src[2] << 8 | src[3]`. If the byte count is not a multiple of four, it reads the existing final dword, merges only the high-order bytes from the source, preserves the trailing existing bytes, and writes the merged dword back. This is important for table fragments that are not dword-sized.

`ci_load_smc_ucode()` chooses firmware layout based on `rdev->new_fw`:

- New firmware: interprets `rdev->smc_fw->data` as `struct smc_firmware_header_v1_0`, prints the header, reads `ucode_start_addr`, `ucode_size_bytes`, and `ucode_array_offset_bytes`, then copies that firmware payload.
- Legacy firmware: selects fixed start address and size from `BONAIRE_SMC_UCODE_*` or `HAWAII_SMC_UCODE_*` based on `rdev->family`, with unknown families treated as a fatal driver bug.

Firmware loading requires the microcode size to be dword-aligned. It enables indirect auto-increment once, streams packed big-endian dwords to `SMC_IND_DATA_0`, then disables auto-increment.

Clock/reset control is direct register manipulation. The DPM bring-up path in `ci_dpm.c` uses these helpers to stop and reset the SMC before loading firmware, then program the start jump, enable the SMC clock, release reset, and wait for firmware flags.

## State and Persistence Behavior

This file does not allocate persistent memory. It mutates hardware/SMC state:

- SMC SRAM contents, including firmware image, tables, soft registers, and small startup code.
- `SMC_IND_INDEX_0`, `SMC_IND_DATA_0`, and `SMC_IND_ACCESS_CNTL` indirect access registers.
- `SMC_SYSCON_RESET_CNTL` reset bit.
- `SMC_SYSCON_CLOCK_CNTL_0` clock-disable bit.

The lock `rdev->smc_idx_lock` serializes indirect SRAM access among CPU callers, protecting index/data register pairs from interleaving. The lock does not protect higher-level SMC firmware semantics; callers still need to sequence firmware loading, SMC start/stop, and PPSMC messages correctly.

## Dependencies and Integration Points

`ci_smc.c` depends on:

- `radeon.h` for `struct radeon_device`, register access macros, firmware pointers, timeout fields, and `smc_idx_lock`.
- `cikd.h` for SMC register and bit definitions.
- `ppsmc.h` for SMC result type in the disabled helper.
- `radeon_ucode.h` for firmware header layout and legacy SMC firmware addresses/sizes.
- `ci_dpm.h` for shared prototypes and integration with the DPM implementation.

The primary consumer is `ci_dpm.c`, which uses these helpers to load SMC firmware, read firmware header offsets, upload DPM/MC/Powertune/fan tables, write SMC soft registers, start/stop the SMC, and test whether PPSMC messaging is legal. Firmware files are selected and requested elsewhere in the CIK/Radeon initialization path; this file assumes `rdev->smc_fw` is already available.

## Risks and Edge Cases

- Address validation depends on caller-supplied `limit`. Passing an incorrect limit can either reject valid firmware/table writes or allow writes beyond the intended SMC region.
- `ci_copy_bytes_to_smc()` requires the start address to be aligned even for byte-sized fragments. Callers needing unaligned writes must use another mechanism or realign their data.
- SMC SRAM is treated as big-endian. Any caller that pre-converts data incorrectly can double-swap fields.
- The final partial-dword merge preserves low-order bytes from the existing SMC dword. This assumes the SMC address is readable and already contains meaningful data for the preserved bytes.
- `ci_load_smc_ucode()` checks dword alignment of firmware size but does not explicitly compare the selected firmware payload size against `limit`; it relies on known firmware constants/header correctness and the earlier loaded firmware validation path.
- The legacy unknown-family path logs an error and calls `BUG()`, which is intentionally fatal.
- `ci_is_smc_running()` uses a simple PC threshold. Firmware that is clocked and alive but below that PC, or wedged above it, may be misclassified.
- `ci_program_jump_on_start()` passes `sizeof(data) + 1` as the limit when writing four bytes at address zero. This is enough for the write check but unusual; changing the helper's bounds semantics could affect this path.

## Test Signals

Useful validation signals include:

- Kernel build coverage with both new-firmware and legacy-firmware code paths compiled.
- Boot on Bonaire and Hawaii hardware with SMC firmware present, checking that firmware upload succeeds and no `unknown asic in smc ucode loader` error appears.
- DPM enable/disable cycles to verify reset/clock sequencing and SMC running detection.
- Tests or instrumentation around SMC table upload paths to verify byte ordering and partial-dword writes.
- Concurrency stress from fan/sysfs/debugfs/media/display paths that can trigger SMC SRAM reads/writes while DPM is active, validating `smc_idx_lock` coverage.
- Fault injection for missing `rdev->smc_fw`, malformed firmware size, bad SRAM limits, and SMC nonresponse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_smc.c -->
