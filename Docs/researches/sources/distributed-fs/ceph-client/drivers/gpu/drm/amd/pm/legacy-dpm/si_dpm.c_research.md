# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003514`: lines 1-7997, `Docs/researches/chunks/subset-b-003514_research.md`
- `subset-b-003515`: lines 7998-8155, `Docs/researches/chunks/subset-b-003515_research.md`

## Chunk Research

### subset-b-003514: lines 1-7997

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c lines 1-7997

## Scope And Purpose

This chunk is the first and dominant portion of the Southern Islands legacy DPM implementation for AMDGPU. It covers module firmware declarations, large ASIC-specific PowerTune/CAC/DTE data tables, power-state parsing from ATOM BIOS PowerPlay tables, SMC firmware upload and state-table construction, runtime DPM enable/disable, power-state transitions, fan and thermal control, suspend/resume hooks, and most of the `amd_pm_funcs` callback implementation. The source path lives in a `ceph-client` mirror, but this file is GPU power-management driver code, not Ceph filesystem logic.

The code targets SI-family ASICs such as Tahiti, Pitcairn, Verde, Oland, and Hainan. Its central job is to translate BIOS/platform power policy into SMC-owned hardware state: SCLK/MCLK PLL values, voltage table indexes, memory-controller timing tables, PCIe link settings, thermal/fan tables, PowerTune/CAC/DTE parameters, and runtime driver power states. It then coordinates hardware transitions by halting/resuming the SMC, copying packed big-endian tables into SMC SRAM, sending PPSMC messages, and updating AMDGPU's current/requested power-state pointers.

This chunk ends at line 7997 inside `si_dpm_early_init()` immediately after assigning `adev->powerplay.pp_funcs = &si_dpm_funcs;`. The trailing function body, the concrete `amd_pm_funcs` table, IP block function table, and IRQ setup tail are outside the requested range and should be reconciled with the next chunk before making whole-file claims.

## Important APIs, Types, And Functions

Primary state types and table contracts:

- `struct si_power_info`, accessed through `si_get_pi()`, is the SI-private DPM state under `adev->pm.dpm.priv`. It embeds earlier-generation `ni`/`eg`/`rv7xx` state, plus SI SMC table addresses, copied SMC state tables, leakage voltage entries, fan mode tracking, PowerTune/DTE dynamic data, PCIe forcing state, ULV parameters, voltage-control mode flags, and SMC SRAM limit.
- `struct si_ps`, reached with `si_get_ps()`, is the per-power-state private payload hanging off `struct amdgpu_ps::ps_priv`. It stores `performance_level_count`, an array of `struct rv7xx_pl` levels, and DC compatibility.
- SMC table structures such as `SISLANDS_SMC_STATETABLE`, `SISLANDS_SMC_SWSTATE`, `SISLANDS_SMC_HW_PERFORMANCE_LEVEL`, `SMC_SIslands_MCRegisters`, `PP_SIslands_CacConfig`, `Smc_SIslands_DTE_Configuration`, and `PP_SIslands_FanTable` are populated in CPU memory and copied to SMC SRAM with `amdgpu_si_copy_bytes_to_smc()`.
- `union power_info`, `union fan_info`, `union pplib_clock_info`, and `union pplib_power_state` are local overlays for BIOS/ATOM PowerPlay table revisions.
- Large static tables (`cac_weights_*`, `lcac_*`, `cac_override_*`, `powertune_data_*`, and `dte_data_*`) encode ASIC/device-specific CAC weights, leakage configuration, PowerTune constants, and DTE thermal model parameters.

Initialization and parsing functions:

- `si_dpm_sw_init()` registers thermal IRQ IDs 230/231, initializes default DPM bookkeeping, requests the SMC firmware image, initializes thermal work, and calls `si_dpm_init()`.
- `si_dpm_init_microcode()` chooses the `amdgpu/<chip>_smc.bin` filename based on `adev->asic_type`, PCI device ID, and revision, then requests it through `amdgpu_ucode_request()`.
- `si_dpm_init()` allocates `si_power_info`, discovers platform caps and extended power tables, parses the BIOS PowerPlay table, initializes dependency and voltage-policy state, sets thresholds/defaults, patches leakage-index voltage dependencies, configures PowerTune defaults, and selects boot/current/requested state baselines.
- `si_parse_power_table()`, `si_parse_pplib_non_clock_info()`, and `si_parse_pplib_clock_info()` translate ATOM PPLIB state arrays into `amdgpu_ps` plus `si_ps` levels, including boot/UVD/ACPI/ULV classification, SCLK/MCLK/VDDC/VDDCI, PCIe generation, and VCE state clocks.

SMC firmware/table setup:

- `si_upload_firmware()` resets/clocks the SMC and loads the requested SMC ucode.
- `si_process_firmware_header()` reads the SMC firmware header to discover SRAM offsets for the main state table, soft registers, MC register table, fan table, ARB table, CAC table, DTE table, SPLL table, and PAPM parameters.
- `si_init_smc_table()` builds the initial, ACPI, driver, and ULV SMC states; sets thermal and platform flags; writes VR-hot and PCIe lane soft registers; and copies the finished `SISLANDS_SMC_STATETABLE`.
- `si_init_smc_spll_table()` precomputes 256 SPLL divisor/spread-spectrum entries in 512-kHz steps for SMC use.
- `si_initialize_mc_reg_table()`, `si_populate_mc_reg_table()`, and `si_upload_mc_reg_table()` derive dynamic memory-controller timing registers from BIOS MC tables and copy only varying registers to SMC slots.

Power-state conversion and transition functions:

- `si_apply_state_adjust_rules()` modifies requested power states before upload based on AC/DC limits, display count, vblank duration, high-pixel-clock displays, UVD/VCE activity, voltage dependency tables, leakage limits, SCLK/MCLK ratio/delta policy, and Oland/Hainan device workarounds.
- `si_convert_power_level_to_smc()` converts one `rv7xx_pl` into an SMC hardware level: SCLK/MCLK register images, voltage values and standard voltages, phase-shedding settings, PCIe generation, memory strobe/EDC flags, MVDD, and maximum powered CU count.
- `si_convert_power_state_to_smc()` converts a full requested state, sets DC/UVD/deep-sleep/watermark flags, writes watermark threshold, adds pulse-skip and SQ ramping data, and computes activity thresholds.
- `si_upload_sw_state()`, `si_upload_ulv_state()`, `si_upload_smc_data()`, and `si_program_memory_timing_parameters()` update the SMC's driver-state, ULV-state, display soft-register, and ARB timing data for a transition.
- `si_dpm_pre_set_power_state()`, `si_dpm_set_power_state()`, and `si_dpm_post_set_power_state()` implement the main transition sequence for the PM core.
- `si_dpm_force_performance_level()` maps forced low/high/auto policy to SMC `SetEnabledLevels` and `SetForcedLevels` messages.

PowerTune, CAC, DTE, and voltage support:

- `si_initialize_powertune_defaults()` selects CAC/LCAC/PowerTune/DTE defaults by ASIC type and PCI device ID, enables power containment/CAC/DTE/SQ ramping as applicable, and initializes dynamic PowerTune parameters.
- `si_calculate_adjusted_tdp_limits()`, `si_populate_smc_tdp_limits()`, and `si_populate_smc_tdp_limits_2()` compute adjusted TDP/near-TDP/safe-power limits, write them into the SMC table, and optionally populate PAPM parameters.
- `si_initialize_smc_cac_tables()` builds the CAC leakage LUT and configuration table, programs CAC window state, and writes `ticks_per_us`.
- `si_initialize_hardware_cac_manager()` writes LCAC, CAC override, and CAC weight registers.
- `si_initialize_smc_dte_tables()` copies the DTE temperature-dependent model to SMC SRAM when enabled.
- `si_enable_smc_cac()` and `si_enable_power_containment()` send SMC messages to enable/disable CAC, DTE, long-term averaging, and TDP clamping.
- `si_construct_voltage_tables()`, `si_populate_smc_voltage_tables()`, `si_populate_voltage_value()`, `si_get_std_voltage_value()`, and leakage patch helpers bridge BIOS GPIO/SVI2/phase-shed voltage tables to SMC voltage indexes and standard CAC voltages.

Thermal/fan and platform callbacks:

- `si_thermal_start_thermal_controller()`, `si_thermal_set_temperature_range()`, `si_thermal_enable_alert()`, and `si_set_temperature_range()` configure thermal interrupt thresholds and SMC thermal messages.
- `si_thermal_setup_fan_table()`, `si_fan_ctrl_start_smc_fan_control()`, `si_fan_ctrl_stop_smc_fan_control()`, `si_dpm_get_fan_speed_pwm()`, `si_dpm_set_fan_speed_pwm()`, `si_dpm_set_fan_control_mode()`, and `si_dpm_get_fan_control_mode()` implement fan table upload, SMC/manual fan control, and PWM read/write behavior.
- `si_dpm_hw_init()`, `si_dpm_hw_fini()`, `si_dpm_suspend()`, `si_dpm_resume()`, `si_dpm_late_init()`, `si_dpm_get_temp()`, `si_dpm_get_sclk()`, `si_dpm_get_mclk()`, and debugfs/IRQ helpers integrate this implementation with AMDGPU's IP block and PM callback layers.

## Control Flow And Runtime Behavior

Software initialization starts in `si_dpm_sw_init()`. If global `amdgpu_dpm` is disabled, the function leaves DPM mostly inert after basic defaults. Otherwise it requests SMC firmware, initializes thermal work, and calls `si_dpm_init()`. `si_dpm_init()` allocates driver-private state, reads platform and extended PowerPlay data, parses BIOS power states, creates a display-clock voltage dependency table, discovers voltage-control mechanisms, reads spread-spectrum and leakage data, sets thresholds and capability flags, and chooses PowerTune defaults.

Hardware initialization runs through `si_dpm_hw_init()` under `adev->pm.mutex`. It calls `si_dpm_setup_asic()` to snapshot clock registers and enable ACPI power management, then `si_dpm_enable()`. The enable sequence is long and order-sensitive: it refuses to proceed if the SMC is already running, enables voltage control, constructs voltage and MC tables, enables spread spectrum and thermal protection, programs trend/BSP/display-gap/VRC registers, uploads SMC firmware, reads firmware table offsets, initializes ARB slots, builds SMC state/SPLL/MC/CAC/DTE/TDP tables, writes response/deep-sleep soft registers, starts the SMC, enables SCLK control and global DPM, enables thermal auto-throttle, starts thermal/fan control, and records the boot state as current.

Runtime power-state changes are three-stage. `si_dpm_pre_set_power_state()` copies the requested state and calls `si_apply_state_adjust_rules()` to enforce display/media/platform constraints before hardware programming. `si_dpm_set_power_state()` then disables ULV, restricts active SMC levels, optionally requests a higher PCIe speed through ACPI before the transition, changes UVD clocks early if the new state is lower, disables PowerTune/CAC, halts the SMC, uploads the new state plus display/ULV/MC/ARB data, updates PCIe lane-width soft state, resumes the SMC, switches to the software state, adjusts UVD/VCE and PCIe after the transition, conditionally re-enables ULV, re-enables CAC and power containment, and finally refreshes power-control TDP limits. `si_dpm_post_set_power_state()` updates the current-state shadow after success.

Disable, suspend, and resume are similarly sequenced. `si_dpm_disable()` stops thermal/fan control, disables ULV, clears voltage control, disables thermal protection, power containment, CAC, spread spectrum, and thermal auto-throttle, stops DPM, resets the SMC to defaults, stops the SMC clock, switches ARB timing back to F0, and restores the boot state shadow. `si_dpm_suspend()` cancels thermal work and disables DPM under the PM mutex. `si_dpm_resume()` reruns ASIC setup and DPM enable if DPM was disabled.

The SMC is the main execution engine once enabled. This driver constructs tables, writes soft registers, and sends PPSMC messages; the SMC firmware performs autonomous DPM transitions, fan control, CAC/DTE accounting, TDP clamping, and thermal responses according to those uploaded tables and register policies.

## State And Persistence Behavior

Persistent driver state lives in `adev->pm.dpm.priv` as `struct si_power_info`, in `adev->pm.dpm.ps` as parsed BIOS power states, and in AMDGPU PM fields such as `current_ps`, `requested_ps`, `boot_ps`, `uvd_ps`, `dpm_enabled`, fan settings, thermal work/IRQ state, AC/DC status, and dynamic dependency tables. `si_dpm_fini()` releases per-state `ps_priv`, the power-state array, private state, the synthetic display-clock dependency table, and extended power-table memory.

Hardware/firmware state persists across runtime transitions until reset or reprogramming: SMC SRAM tables, soft registers, CAC/LCAC registers, MC ARB timing slots, SPLL divisor tables, fan table, thermal threshold registers, GENERAL_PWRMGT/SCLK/MCLK power-management bits, spread-spectrum state, PCIe link requests, and VCE/UVD clock/powergating state. The driver frequently caches boot register values in `si_pi->clock_registers` so SMC state entries can be reconstructed without rereading every source register during transitions.

The code updates current/requested state shadows with full struct copies in `ni_update_current_ps()` and `ni_update_requested_ps()`, then redirects `ps_priv` to embedded `ni_pi` storage. This avoids dangling pointers into temporary `amdgpu_ps` copies but makes those shadow structs authoritative for later callbacks such as clock reporting and debugfs printing.

Endianness is explicit for SMC-facing structures. The driver stores most SMC table fields as big-endian using `cpu_to_be16()`/`cpu_to_be32()` before copying to SMC SRAM, while BIOS tables are read with little-endian helpers. Any new fields in these paths must preserve that convention.

## Dependencies And Integration Points

This file depends on core AMDGPU device/PM state (`amdgpu.h`, `amdgpu_pm.h`, `amdgpu_dpm.h`, `amdgpu_dpm_internal.h`, `legacy_dpm.h`), ATOM BIOS helpers (`amdgpu_atombios.h`, `atom.h`, PPLIB structures from `pptable.h`), SI/NI/R600 DPM types (`r600_dpm.h`, `si_dpm.h`), and ASIC register address/mask headers for GFX, GMC, DCE, BIF, and SMU blocks.

Important external calls include:

- SMC operations: `amdgpu_si_reset_smc()`, `amdgpu_si_smc_clock()`, `amdgpu_si_load_smc_ucode()`, `amdgpu_si_program_jump_on_start()`, `amdgpu_si_start_smc()`, `amdgpu_si_is_smc_running()`, `amdgpu_si_send_msg_to_smc()`, `amdgpu_si_wait_for_smc_inactive()`, `amdgpu_si_read_smc_sram_dword()`, `amdgpu_si_write_smc_sram_dword()`, and `amdgpu_si_copy_bytes_to_smc()`.
- BIOS/platform helpers: `amdgpu_atom_parse_data_header()`, `amdgpu_atombios_get_voltage_table()`, `amdgpu_atombios_is_voltage_gpio()`, `amdgpu_atombios_get_svi2_info()`, `amdgpu_atombios_get_clock_dividers()`, `amdgpu_atombios_get_memory_pll_dividers()`, `amdgpu_atombios_set_engine_dram_timings()`, `amdgpu_atombios_init_mc_reg_table()`, `amdgpu_atombios_get_default_voltages()`, `amdgpu_parse_extended_power_table()`, and `amdgpu_get_platform_caps()`.
- PM/display/media integration: `amdgpu_legacy_dpm_compute_clocks()`, `amdgpu_pm_print_power_states()`, `amdgpu_dpm_thermal_work_handler`, `amdgpu_asic_set_uvd_clocks()`, `amdgpu_asic_set_vce_clocks()`, `amdgpu_device_ip_set_clockgating_state()`, `amdgpu_device_ip_set_powergating_state()`, and PCIe helpers such as `amdgpu_get_pcie_lanes()`, `amdgpu_set_pcie_lanes()`, and ACPI PCIe performance requests.
- IRQ integration: `amdgpu_irq_add_id()` registers legacy thermal source IDs 230 and 231; `si_dpm_set_interrupt_state()` masks/unmasks high/low thermal interrupts; `si_dpm_process_interrupt()` schedules thermal work.

The `MODULE_FIRMWARE()` declarations advertise all supported SI SMC firmware images: Tahiti, Pitcairn, Pitcairn K, Verde, Verde K, Oland, Oland K, Hainan, Hainan K, and Banks K 2.

## Risks And Edge Cases

- The file is hardware sequencing code. Reordering SMC halt/resume, table upload, CAC/PowerTune disable/enable, PCIe requests, or UVD/VCE clock changes can cause hangs, bad display transitions, or firmware timeouts.
- Many paths trust BIOS table shape after limited bounds checks. `si_parse_power_table()` allocates per-state private data in a loop; if a later allocation fails it returns immediately and cleanup relies on later failure handling. Clock-info indices beyond the clock array are skipped, so malformed tables can produce states with fewer DPM levels.
- Several functions return errors only after mutating feature flags. CAC, power containment, SQ ramping, dynamic AC timing, phase shedding, MVDD control, and SMC fan control may be disabled dynamically after setup failures. Tests should check both success and graceful-degradation behavior.
- `si_get_vce_clock_voltage()` uses `table && table->count == 0` but then dereferences `table` later; callers depend on a valid dependency table when nonzero clocks are requested.
- `si_patch_single_dependency_table_based_on_leakage()` iterates backward from `table->count - 2` with an `int`; zero-count tables would underflow before conversion if passed in unexpectedly.
- `si_set_valid_flag()` stores varying MC-register bits in `table->valid_flag`, which is shifted by register index. If `table->last` exceeds the bit width of that flag type, later registers cannot be represented safely.
- PowerTune calculations perform integer arithmetic on TDP limits, near-TDP limits, leakage, voltage, and temperature. Invalid BIOS/platform values can lead to `-EINVAL`, disabled containment, or clamped leakage table values.
- Display adjustment rules are intentionally ad hoc. High-pixel-clock displays, short vblank, multiple displays, UVD activity, and some Oland/Hainan IDs force SCLK/MCLK switching off or cap clocks; regressions may show as flicker, underruns, or excessive power use only under specific monitor configurations.
- The fan-control paths reject manual PWM changes while SMC fan control owns the fan. Mode changes must stop SMC fan control before static control and restore the original hardware mode/TMIN when returning to default.
- This chunk ends before the final callback/function table definitions. Whole-file API availability must be verified after merging with the following chunk.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU with legacy SI DPM enabled and firmware loading enabled; missing register macros, SMC structure mismatches, or callback prototype drift should fail compilation.
- Boot each supported ASIC family, especially device/revision-specific firmware names and PowerTune/DTE table selections: Tahiti, Pitcairn/Pitcairn K, Verde/Verde K, Oland/Oland K, Hainan/Hainan K, and Banks K 2.
- Confirm firmware request logs and `si dpm initialized`; failure logs identify the stage (`si_upload_firmware`, `si_process_firmware_header`, `si_init_smc_table`, CAC/DTE/TDP table setup, MC table setup, etc.).
- Exercise AC/DC changes, forced low/high/auto levels, boot-to-balanced transition, suspend/resume, DPM disable/unload, and repeated state changes under PM mutex coverage.
- Run display tests with no displays, one high-pixel-clock display, multiple displays, short-vblank modes, and UVD/VCE active workloads. Watch for flicker, underruns, stuck clocks, VCE/UVD gating failures, or wrong MCLK switching.
- Validate thermal behavior by reading temperature, enabling thermal IRQs, crossing high/low thresholds, and checking that thermal work is scheduled. Verify fan PWM get/set, SMC fan control start/stop, and restoration of default fan mode.
- Inspect debugfs current performance-level output and clock getters for consistency with requested/current SMC state.
- Stress PowerTune/CAC/DTE with high GPU load and media workloads; monitor for SMC message failures, TDP clamping behavior, disabled CAC fallback, and unexpected thermal throttling.
- Check suspend/resume and runtime unload for stale work items, leaked `ps_priv` allocations, stale firmware references, and correct return to boot power state.

## Cross-Chunk Notes

The next chunk is needed for the end of `si_dpm_early_init()`, the final public callback tables, and IRQ setup completion. This chunk already contains nearly all implementation logic, but the final per-file report should merge boundary context before stating the complete external surface of `si_dpm.c`.

### subset-b-003515: lines 7998-8155

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c lines 7998-8155

## Purpose

This chunk is the public binding tail for Southern Islands legacy DPM. It finishes wiring the SI DPM implementation into AMDGPU by registering the PowerPlay callback table, the SMC/IP block callback table, thermal interrupt callbacks, state comparison logic, and sysfs/debugfs sensor reads. Most heavy clock, voltage, SMC-table, fan, and transition logic lives earlier in `si_dpm.c`; these lines expose that implementation through the common AMDGPU PM and IP block interfaces.

## Important APIs, Types, and Functions

- `si_dpm_early_init(struct amdgpu_ip_block *ip_block)` installs `si_dpm_funcs` into `adev->powerplay.pp_funcs`, sets `adev->powerplay.pp_handle = adev`, and calls `si_dpm_set_irq_funcs()`. This is the early bridge from the IP block framework to the legacy PM callback table.
- `si_are_power_levels_equal(const struct rv7xx_pl *, const struct rv7xx_pl *)` compares one software performance level by `mclk`, `sclk`, `pcie_gen`, `vddc`, and `vddci`.
- `si_check_state_equal(void *handle, void *current_ps, void *request_ps, bool *equal)` is the `amd_pm_funcs.check_state_equal` implementation. It validates arguments, unwraps `struct amdgpu_ps.ps_priv` into `struct si_ps`, compares performance-level counts and all `struct rv7xx_pl` entries, then uses UVD/VCE clocks as tie breakers.
- `si_dpm_read_sensor(void *handle, int idx, void *value, int *size)` is the legacy sensor callback. It supports `AMDGPU_PP_SENSOR_GFX_SCLK`, `AMDGPU_PP_SENSOR_GFX_MCLK`, and `AMDGPU_PP_SENSOR_GPU_TEMP`; other sensor IDs return `-EOPNOTSUPP`.
- `si_dpm_ip_funcs` exposes the SI DPM IP-block lifecycle (`early_init`, `late_init`, `sw_init`, `hw_init`, suspend/resume, idle, clockgating, powergating).
- `si_smu_ip_block` publishes the block as `AMD_IP_BLOCK_TYPE_SMC` with version `6.0.0`, using `si_dpm_ip_funcs`.
- `si_dpm_funcs` is the central `struct amd_pm_funcs` dispatch table for legacy PM operations: power-state transition, display change handling, clock reads, debug output, forced performance levels, fan control, VCE state lookup, sensor reads, and legacy DPM clock recomputation.
- `si_dpm_irq_funcs` and `si_dpm_set_irq_funcs()` attach SI thermal IRQ `.set`/`.process` handlers to `adev->pm.dpm.thermal.irq`.

Key data types come from this file and `si_dpm.h`: `struct amdgpu_device`, `struct amdgpu_ip_block`, `struct amdgpu_ps`, `struct evergreen_power_info`, `struct ni_power_info`, `struct si_ps`, and `struct rv7xx_pl`.

## Control Flow

During IP discovery/initialization, the SMC block represented by `si_smu_ip_block` is driven through `si_dpm_ip_funcs`. The earliest SI-specific handoff is `si_dpm_early_init()`, which stores the SI legacy PM callback table in `adev->powerplay` and registers thermal interrupt operations. Later generic AMDGPU PM entry points call through `adev->powerplay.pp_funcs` into the functions listed in `si_dpm_funcs`.

Power-state equality is evaluated by `si_check_state_equal()`. The caller passes generic `struct amdgpu_ps` pointers; the function converts them to SI-private `struct si_ps` objects through `si_get_ps()`. It fails fast on null public inputs, reports inequality when the current SI state is absent, checks that both states have the same number of performance levels, then walks each performance level. Only if all levels match does it compare multimedia clocks (`vclk`/`dclk` for UVD and `evclk`/`ecclk` for VCE). The result is returned through the caller-supplied `bool *equal`; the function returns `0` for a successful comparison path even when the states are unequal.

Sensor reads use the current active legacy Radeon power state from `evergreen_get_pi(adev)->current_rps`. For SCLK and MCLK, the hardware register `mmTARGET_AND_CURRENT_PROFILE_INDEX` is read with `RREG32()`, masked by `TARGET_AND_CURRENT_PROFILE_INDEX__CURRENT_STATE_INDEX_MASK`, shifted, and used as an index into `ps->performance_levels`. If the index is in range, the selected level's `sclk` or `mclk` is copied to the caller's `uint32_t` buffer and `*size` is set to 4. Temperature delegates to `si_dpm_get_temp()`, which reads the thermal status register in the preceding chunk and returns millidegrees Celsius.

## State and Persistence Behavior

This chunk does not allocate or free long-lived state, but it exposes and relies on persistent DPM state owned by `adev->pm.dpm.priv`. `evergreen_get_pi()` returns that private state as `struct evergreen_power_info`; for SI devices it is embedded at the front of `struct ni_power_info`, which also stores `current_ps` and `requested_ps`. Earlier state-copy helpers keep `eg_pi->current_rps.ps_priv` and `eg_pi->requested_rps.ps_priv` pointed at those SI-private snapshots.

The callback tables themselves are static and immutable after compilation. Runtime registration persists through pointers stored in `adev->powerplay.pp_funcs`, `adev->powerplay.pp_handle`, and `adev->pm.dpm.thermal.irq`. Sensor results are transient reads from the current software state plus hardware profile-index/thermal registers; they do not update cached clocks or requested/current power states.

## Dependencies and Integration Points

- AMDGPU IP framework consumes `si_smu_ip_block` and calls `si_dpm_ip_funcs`.
- Generic DPM and sysfs/debugfs code consume `adev->powerplay.pp_funcs`, especially `read_sensor`, `check_state_equal`, fan methods, forced performance levels, and `pm_compute_clocks`.
- Thermal management uses `si_dpm_irq_funcs` through `adev->pm.dpm.thermal.irq` and also calls `read_sensor(AMDGPU_PP_SENSOR_GPU_TEMP)` to decide whether thermal throttling can be cleared.
- Hwmon and debugfs clock reporting call `amdgpu_dpm_read_sensor()` or `amdgpu_pm_get_sensor_generic()`, which eventually dispatch to `si_dpm_read_sensor()` for `AMDGPU_PP_SENSOR_GFX_SCLK`, `AMDGPU_PP_SENSOR_GFX_MCLK`, and `AMDGPU_PP_SENSOR_GPU_TEMP`.
- Hardware register dependencies include `mmTARGET_AND_CURRENT_PROFILE_INDEX` for the active performance index and the thermal status register used by `si_dpm_get_temp()`. Register masks and shifts come from AMD SMU register headers.
- Function pointers in `si_dpm_funcs` integrate many earlier functions in the same file, including power-state transitions, display reconfiguration, clock getters, fan control, VBlank checks, and debug printing.

## Risks and Edge Cases

- `si_check_state_equal()` validates the current SI-private state pointer but does not explicitly validate `si_rps` after `si_get_ps(rps)`. A malformed requested power state with a null `ps_priv` could be dereferenced during count or level comparison.
- `si_dpm_read_sensor()` checks `*size < 4` but assumes `size`, `value`, `eg_pi`, `rps->ps_priv`, and the SI-private `ps` pointer are valid. The generic PM callers normally satisfy this, but the callback itself is not defensive against all invalid inputs.
- The sensor clock path trusts the hardware current-state index. It bounds the index against `performance_level_count`, returning `-EINVAL` if out of range, which prevents a performance-level array overread but can make hwmon/debugfs clock files fail while hardware/SMC state is inconsistent.
- Equality ignores fields outside the compared set, such as `dc_compatible`, `flags`, and broader `amdgpu_ps` class/capability metadata. That is intentional for transition deduplication only if those omitted fields do not require hardware reprogramming.
- The temperature path reports the legacy SI thermal register result in millidegrees. Any sensor calibration or invalid thermal register behavior is inherited from `si_dpm_get_temp()`.
- IP block versioning is fixed at SMC `6.0.0`; wrong ASIC matching outside this file would attach these callbacks to incompatible hardware.

## Test Signals

- Boot or driver probe on SI hardware should show the SMC/IP block initializing successfully, with `adev->powerplay.pp_funcs` populated by `si_dpm_early_init()` and thermal IRQ function pointers installed.
- Hwmon/debugfs reads for SCLK, MCLK, and GPU temperature should succeed when DPM is enabled; unsupported sensor IDs should return `-EOPNOTSUPP` through the generic PM wrappers.
- Power-state changes that only repeat the same SI performance levels and UVD/VCE clocks should be detected as equal by `check_state_equal`; changes in any level's `sclk`, `mclk`, `pcie_gen`, `vddc`, `vddci`, or multimedia clocks should be reported unequal.
- Fault-injection or register-stability tests can validate that an out-of-range `CURRENT_STATE_INDEX` causes clock sensor reads to return `-EINVAL` rather than indexing beyond `performance_levels`.
- Suspend/resume and thermal interrupt tests should still route through the function tables in this chunk, confirming that the callback registration remains intact across PM lifecycle transitions.
