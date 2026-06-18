# subset-b-003519 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c

### Purpose
`smu7_hwmgr.c` is the SMU7-family PowerPlay hardware-manager backend for AMDGPU. It binds the generic `pp_hwmgr` interface to Southern Islands/Volcanic Islands through Polaris/VegaM-era SMU firmware behavior: backend allocation, ASIC setup, DPM enable/disable, power-state transition programming, voltage/leakage patching, PCIe performance requests, display-aware MCLK/SCLK decisions, thermal/fan integration, OverDriveN editing, power profile updates, sensor reads, and registration of the `pp_hwmgr_func` vtable.

The file is not Ceph-specific despite living under the repository's `distributed-fs/ceph-client` source mirror. It is a Linux kernel DRM GPU power-management component. Its critical job is to translate VBIOS PowerPlay tables, driver feature masks, display state, platform caps, and user controls into SMU mailbox commands and MMIO/indirect register writes that keep clocks, voltage, thermal protection, and power containment coherent.

### Important APIs, Types, And Functions
The external entry points are small but high impact:

- `smu7_init_function_pointers()` installs `smu7_hwmgr_funcs` into `hwmgr->hwmgr_func` and selects the PPTable parser callbacks for `PP_TABLE_V0` or `PP_TABLE_V1`.
- `smu7_get_sleep_divider_id_from_clock()` is exported to sibling code and computes the largest deep-sleep divider that still satisfies the required stutter/display clock floor.
- The static `smu7_hwmgr_funcs` vtable is the main integration surface. It wires backend init/fini, ASIC setup, DPM start/stop, state adjustment/set, forced DPM levels, PPTable entry extraction, fan/thermal controls, clock-level sysfs helpers, power-gating hooks, sensor reads, watermark uploads, OverDriveN edits, profile mode controls, BACO operations, and ASIC power-off into the generic PowerPlay layer.

Important initialization and teardown functions include:

- `smu7_hwmgr_backend_init()` allocates `struct smu7_hwmgr`, applies quirks/defaults, resolves leakage voltages, builds display-clock voltage dependencies, patches V0/V1 dependency tables, records platform descriptors, reads thermal settings, and loads EDC leakage data.
- `smu7_hwmgr_backend_fini()` frees the display-clock dependency table and backend state.
- `smu7_setup_asic_task()` reads MC/clock/memory information, enables static ACPI power management, initializes power-gate state, and sets threshold defaults.

Voltage and dependency-table functions form a large subsystem:

- `smu7_init_dpm_defaults()` seeds backend defaults, feature-disable flags, voltage-control modes, profile parameters, thermal defaults, PCIe ranges, power-gating caps, spread-spectrum caps, EDC enablement, and ASIC-specific workarounds.
- `smu7_get_evv_voltages()`, `smu7_get_elb_voltages()`, `smu7_calculate_ro_range()`, and `smu7_update_edc_leakage_table()` query VBIOS/efuse leakage sources and populate backend leakage tables.
- `smu7_complete_dependency_tables()` patches V1 voltage lookup and dependency tables, calculates VDDC/VDDGFX derived rows, and sorts lookup tables.
- `smu7_patch_dependency_tables_with_leakage()` patches V0 dynamic-state voltage tables, multimedia tables, phase-shedding limits, AC/DC limits, and CAC leakage tables.
- `smu7_construct_voltage_tables()` converts GPIO or SVI2 voltage definitions into firmware-facing voltage tables and trims them to SMU table limits.

DPM setup/start/stop is organized around:

- `smu7_reset_dpm_tables()`, `smu7_setup_dpm_tables_v0()`, `smu7_setup_dpm_tables_v1()`, `smu7_setup_default_pcie_table()`, and `smu7_setup_default_dpm_tables()` build SCLK, MCLK, voltage, and PCIe DPM tables from PPTable data, platform caps, boot state, and override masks.
- `smu7_enable_dpm_tasks()` sequences the full start path: voltage control, MC table initialization, spread-spectrum and thermal bits, static-screen/display-gap/voting-client programming, firmware-header processing, memory arb switch, DPM table setup/upload, display notification, EDC/DIDT/CAC/power-containment/thermal-throttle enablement, PCIe request, and pstate clock bookkeeping.
- `smu7_disable_dpm_tasks()` reverses the major features and stops the SMC, resets defaults, clears voting clients, disables AVFS/power containment/CAC/DIDT/ULV/deep sleep, and forces the memory arbiter back to F0.
- `smu7_start_dpm()` and `smu7_stop_dpm()` handle the direct SMC/register DPM enable/disable sequence for general power management, SCLK/MCLK DPM, PCIe DPM, voltage DPM, and quick-transition GPIO interrupts.

Power-state and display transition functions include:

- `smu7_apply_state_adjust_rules()` clamps requested states against AC/DC limits, display minimum clocks, stable-pstate requirements, multi-display/frame-lock MCLK constraints, vblank timing, and Polaris/VegaM latency allowances.
- `smu7_set_power_state_tasks()` is the transition pipeline: discover whether DPM tables need update, request higher PCIe speed before the transition, freeze DPM, repopulate/upload SCLK/MCLK levels, update AVFS, generate enable masks, update thresholds, unfreeze DPM, upload masks, notify display state to SMC, and issue any lower PCIe speed request after the transition.
- `smu7_check_smc_update_required_for_display_configuration()`, `smu7_program_display_gap()`, `smu7_notify_has_display()`, `smu7_notify_no_display()`, and `smu7_notify_smc_display()` keep firmware display-gap and VBlank timeout state aligned with DAL/display configuration.
- `smu7_request_link_speed_change_before_state_change()` and `smu7_notify_link_speed_change_after_state_change()` coordinate ACPI PSPP requests for PCIe Gen changes around power transitions.

User-facing and query helpers include:

- `smu7_force_dpm_level()`, `smu7_force_clock_level()`, `smu7_emit_clock_levels()`, `smu7_get_sclk_od()`, `smu7_set_sclk_od()`, `smu7_get_mclk_od()`, and `smu7_set_mclk_od()` back manual DPM forcing and sysfs-style DPM/OD views.
- `smu7_odn_edit_dpm_table()` edits OverDriveN SCLK/MCLK voltage tables, validates ranges, restores defaults, or marks tables for commit.
- `smu7_get_power_profile_mode()` and `smu7_set_power_profile_mode()` expose and update workload profile hysteresis/activity settings through `smum_update_dpm_settings()`, with special compute-profile SCLK forcing.
- `smu7_read_sensor()` reports SCLK, MCLK, GPU/memory load, temperature, UVD/VCE power-gate state, input/average power, and VDDGFX.
- `smu7_get_clock_by_type()`, `smu7_get_clock_by_type_with_latency()`, `smu7_get_max_high_clocks()`, and `smu7_get_thermal_temperature_range()` provide clock and thermal metadata to the rest of AMDGPU/DC.

### Control Flow
Boot/setup flow starts when generic PowerPlay calls `smu7_init_function_pointers()`, then `backend_init`, then `asic_setup`, then DPM enable. Backend initialization allocates private state, applies defaults and quirks, detects voltage-control modes, patches PPTable voltage data from leakage information, creates display-clock voltage dependencies, configures platform descriptor fields, and loads thermal/EDC data. ASIC setup then snapshots clock registers, memory type, MC firmware state, ACPI/static power management, and power-gate defaults.

DPM enable is a strict ordered pipeline. Voltage control and voltage tables must be ready before SMU tables are initialized. MC register tables and firmware headers must be processed before the firmware DPM tables are initialized. Display-gap, static-screen, voting-client, thermal, VR hot, EDC, ULV, deep sleep, DIDT, CAC, power containment, AVFS, and PCIe request steps all depend on backend feature flags and platform caps. Many steps continue after recording `result`, but some PP_ASSERT paths return immediately because the following SMU programming would be unsafe without mandatory tables.

Power-state transitions are display-aware. The request state is first adjusted for DC/AC limits, minimum display clocks, stable-pstate, vblank length, frame lock, and multi-monitor sync. During `power_state_set`, the driver detects if the requested high SCLK/MCLK is absent from the current DPM tables, freezes relevant DPM domains, repopulates firmware graphics/memory levels, optionally disables or toggles AVFS for OD/custom tables, regenerates enable masks, unfreezes domains, applies masks, and updates SMC display state. PCIe speed increases are requested before a clock transition; decreases are delayed until after the transition.

Disable/power-off flow is also ordered. Thermal protection and containment features are disabled before DPM is stopped. SMC CAC, DIDT, AVFS, ULV, and deep sleep are turned off, voting clients are cleared, firmware defaults are restored, the SMC is stopped, and the memory arbiter is forced back to F0.

### State And Persistence Behavior
Persistent runtime state lives primarily in `hwmgr->backend` as `struct smu7_hwmgr`, defined in the companion header. The file mutates DPM tables, golden/default DPM tables, OverDriveN tables, leakage-voltage caches, voltage tables, boot-state data, display timing, profile settings, power-gating flags, thermal thresholds, memory latency tables, PCIe ranges, EDC tables, and update flags.

Other state is stored in shared `pp_hwmgr` fields: `dyn_state` dependency tables and AC/DC limits, `platform_descriptor` caps and limits, `display_config`, `request_ps`, `pstate_*` clocks, workload/profile mode, fan/thermal controller fields, and selected function-pointer tables. The code also persists values into hardware/firmware through SMC soft registers, SMU DPM tables in SMC RAM, direct MMIO registers, indirect SMC/PCIE/DIDT registers, and SMC mailbox messages.

Nothing is persisted to disk. Persistence across runtime phases comes from the backend object, modified PPTable/dynamic-state structures, and hardware/SMC state. Suspend, reset, reload, or backend teardown requires the initialization path to rebuild this state from VBIOS, efuses, platform caps, and current display configuration.

### Dependencies
The file depends heavily on AMDGPU PowerPlay infrastructure:

- Generic manager types and contracts from `hwmgr.h`, `hardwaremanager.h`, `processpptables.h`, and `process_pptables_v1_0.h`.
- AtomBIOS/VBIOS helpers from `ppatomctrl.h`, `atombios.h`, and PPTable structures from `pptable_v1_0.h`.
- SMU7 helpers and firmware-table definitions from `smu7_common.h`, `smu7_smumgr.h`, `polaris10_smumgr.h`, `smu_ucode_xfer_vi.h`, and SMC message/offset helpers.
- Feature-specific siblings: `smu7_powertune.h`, `smu7_dyn_defaults.h`, `smu7_thermal.h`, `smu7_clockpowergating.h`, and `smu7_baco.h`.
- Low-level register access through CGS helpers (`cgs_read_register`, `cgs_write_register`, `cgs_read_ind_register`, `cgs_write_ind_register`) and register-field macros such as `PHM_READ_FIELD`, `PHM_WRITE_FIELD`, and `PHM_WRITE_INDIRECT_FIELD`.
- Kernel services for allocation, sleeping/delays, PCI identifiers, ACPI PCIe performance requests, sysfs formatting, IRQ registration, and bit helpers.

### Integration Points
The central integration point is `smu7_hwmgr_funcs`, consumed by the AMDGPU PowerPlay core. Sibling SMU manager code owns actual SMC table layouts, SMC RAM copy operations, firmware-header processing, and mailbox transport. Thermal/fan operations are delegated to `smu7_thermal` and fan-control helpers. Clock/power-gating and BACO are delegated to sibling modules through the function table. Display integration occurs through `hwmgr->display_config` and DC watermark calls, especially `smu7_set_watermarks_for_clocks_ranges()`, which writes `DisplayWatermark` into the Polaris/VegaM SMC DPM table. ACPI integration is used for PCIe performance state requests when the platform supports PSPP.

The PPTable integration has two lanes. V0 uses `hwmgr->dyn_state` and legacy `pp_tables_*` callbacks. V1 uses parsed `phm_ppt_v1_information`, Tonga/Polaris state tables, lookup tables, and `pptable_v1_0_funcs`. Both lanes converge into `struct smu7_power_state` entries and common DPM-table construction.

### Risks
The largest risk is hardware sequencing. Many operations program voltage, DPM, memory-controller, thermal, and PCIe state through firmware mailboxes and indirect registers; reordering can cause hangs, flicker, unsafe voltage/clock combinations, or failed transitions. `smu7_enable_dpm_tasks()` and `smu7_set_power_state_tasks()` should be treated as dependency-sensitive sequences.

Table bounds and count assumptions are also risky. DPM arrays are capped by `MAX_REGULAR_DPM_NUMBER` and SMU macro definitions, but several loops index dependency tables from firmware/VBIOS data and assume matching SCLK/MCLK/VDD table counts. The V0 path in `smu7_setup_dpm_tables_v0()` uses `allowed_vdd_sclk_table->count` while reading VDD values from `allowed_vdd_mclk_table`, so malformed or mismatched firmware tables would be dangerous if earlier parser validation is weak.

Display-related MCLK switching has visible failure modes: flicker, underflow, or latency misses. The code depends on accurate `min_vblank_time`, multi-monitor sync, latency tables, and `mclk_ignore_signal` handling. The watermark upload path appears to nest `i` over MCLK count and `j` over SCLK count but compares `dep_sclk_table->entries[i]`, which is suspicious when MCLK and SCLK counts differ; tests should cover asymmetric table sizes.

Voltage/leakage handling is safety-critical. EVV/ELB values are patched into PPTable data and bounded by checks such as nonzero and less than 2000 mV, but derived VDDC/VDDGFX offset math and lookup-table additions still rely on correct firmware data and table capacities. OverDriveN validates requested clocks and voltages, but commit/update behavior depends on later state transitions and flags in `need_update_smu7_dpm_table`.

There are chip-specific quirks and hard-coded register values for CI, Polaris, VegaM, subsystem IDs, and device revisions. These are difficult to validate without hardware coverage and can regress older ASICs when shared code changes are made. IRQ registration allocates one source and registers multiple IDs; ownership/lifetime assumptions must match AMDGPU IRQ core expectations.

### Test Signals
Build coverage should compile this file with relevant kernel configs, including `CONFIG_ACPI` and x86/non-x86 combinations. Static analysis should focus on table bounds, count mismatches, null PPTable pointers, unchecked SMC message failures, and indirect-register address spaces.

Runtime signals on supported hardware include: backend init succeeds; DPM starts and stops without SMC timeouts; SCLK/MCLK/PCIe DPM levels in sysfs match expected PPTable values; forced low/high/auto/profile modes change clocks as expected; display hotplug and refresh changes update display gap/VBlank timeout without flicker; multi-monitor and frame-lock scenarios avoid unsafe MCLK switching; UVD/VCE power-gating state reports correctly; thermal/fan controls respond; input/average power sensors return plausible values on supported ASICs; suspend/resume and ASIC power-off do not leave DPM or SMC state stuck.

For risky paths, useful targeted tests are malformed or minimal PPTable dependency tables, asymmetric SCLK/MCLK table counts, OverDriveN range rejection and commit/restore, AC/DC limit clamping, stable-pstate behavior, PCIe Gen up/down transitions with and without ACPI PSPP success, EVV leakage patching for virtual voltage IDs, EDC enable/disable on Polaris/VegaM variants, and DC watermark programming with multiple watermark ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.h

### Purpose
`smu7_hwmgr.h` defines the private data model and constants used by the SMU7 hardware-manager backend. It describes SMU7 performance levels, power states, DPM tables, voltage/leakage caches, boot-state snapshots, display timing, PCIe ranges, OverDriveN tables, profile settings, memory-latency tables, and the large `struct smu7_hwmgr` backend object allocated by `smu7_hwmgr.c`.

The header is the contract between the SMU7 manager implementation and sibling SMU7 modules that need shared backend fields. It also exposes `smu7_get_sleep_divider_id_from_clock()` for deep-sleep divider selection.

### Important APIs, Types, And Functions
Important constants and enums include:

- `SMU7_MAX_HARDWARE_POWERLEVELS`, `MAX_REGULAR_DPM_NUMBER`, `SMU7_MAX_DEEPSLEEP_DIVIDER_ID`, and `SMU7_MINIMUM_ENGINE_CLOCK`, which size and constrain DPM/power-state behavior.
- `SMU7_VOLTAGE_CONTROL_*` constants, which encode none/GPIO/SVID2/merged voltage-control modes.
- `enum gpu_pt_config_reg_type` and `struct gpu_pt_config_reg`, which describe register programming entries across MMIO, SMC indirect, DIDT indirect, GC CAC indirect, and cache domains.
- `enum SMU7_I2CLineID` plus `SMU7_I2C_*` GPIO pin constants and `SMU7_UNUSED_GPIO_PIN`, which map firmware/display I2C line IDs to GPIO pins.
- `SMU7_Q88_FORMAT_CONVERSION_UNIT`, used when converting values to firmware Q8.8 format.

Core state structures include:

- `struct smu7_performance_level`: memory clock, engine clock, PCIe generation, and PCIe lane count for one level.
- `struct smu7_power_state`: PowerPlay hardware-state payload with magic, UVD/VCE/SAMU clocks, DC compatibility, SCLK threshold, performance-level count, and up to two performance levels.
- `struct smu7_dpm_level`, `struct smu7_single_dpm_table`, and `struct smu7_dpm_table`: enabled/value/parameter entries for SCLK, MCLK, PCIe speed, VDDC, VDDCI, and MVDD domains.
- `struct smu7_clock_registers`: saved SPLL, DLL, MCLK, MPLL, and spread-spectrum register values captured during ASIC setup.
- `struct smu7_leakage_voltage`: up to eight virtual leakage IDs and resolved actual voltages.
- `struct smu7_vbios_boot_state`: boot MVDD/VDDC/VDDCI/VDDGFX, SCLK/MCLK, PCIe generation, and lane width read from firmware/current hardware.
- `struct smu7_odn_dpm_table` and `struct smu7_odn_clock_voltage_dependency_table`: OverDriveN editable clock/voltage state and limits.
- `struct profile_mode_setting`: SCLK/MCLK hysteresis and activity-target update settings for workload profiles.
- `struct smu7_mclk_latency_table`: memory clock latency records used by display-aware MCLK switching.

The central type is `struct smu7_hwmgr`. It stores current and golden DPM tables, OverDriveN state, display timing, voltage-control modes, voltage tables, leakage tables, PCIe caps/ranges, feature booleans, power-containment flags, thermal thresholds, power-gating state, profile settings, AVFS/EDC metadata, memory latency thresholds, and update flags.

The only function prototype is:

- `uint8_t smu7_get_sleep_divider_id_from_clock(uint32_t clock, uint32_t clock_insr);`

### Control Flow
The header contains no executable control flow, but its structures directly shape runtime control flow in `smu7_hwmgr.c`. `struct smu7_hwmgr` fields decide which initialization branches run, which DPM domains are enabled or disabled, whether voltage control uses GPIO or SVID2, whether PCIe/DPM tables must be updated, whether display timing requires a firmware update, whether MCLK switching should be ignored, and whether EDC/AVFS/power-containment features are enabled.

Power-state transition code consumes `struct smu7_power_state` and `struct smu7_performance_level` to clamp and upload SCLK/MCLK/PCIe ranges. DPM upload code consumes `struct smu7_dpm_table` and `struct smu7_dpmlevel_enable_mask`. OverDriveN control mutates `struct smu7_odn_dpm_table`. Display-aware logic relies on `struct smu7_display_timing` and `struct smu7_mclk_latency_table`.

### State And Persistence Behavior
All state defined here is in-memory driver state. `struct smu7_hwmgr` is allocated during backend initialization and freed during backend teardown. Some fields are snapshots of hardware or firmware state, such as boot clocks/voltages, saved clock registers, memory type, MC microcode flags, efuse/VBIOS leakage tables, and current display timing. Other fields are mutable policy state, such as DPM enable masks, OverDriveN edits, profile settings, power-gating flags, update flags, and feature disable booleans.

The header itself does not persist anything. Its fields become persistent for the lifetime of the hardware-manager backend and are used to regenerate or update SMU firmware tables and registers as display, power-source, user-profile, and power-state inputs change.

### Dependencies
The header includes `hwmgr.h` and `ppatomctrl.h`, so it depends on generic PowerPlay manager definitions, AtomBIOS voltage table types, PowerPlay clock/voltage dependency records, OverDriveN structures, and Atom control leakage/EDC structures. The field types also implicitly depend on PPTable V1 types such as `phm_ppt_v1_clock_voltage_dependency_record`, `phm_odn_clock_levels`, `pp_atomctrl_voltage_table`, `AtomCtrl_HiLoLeakageOffsetTable`, and `AtomCtrl_EDCLeakgeTable`.

### Integration Points
`smu7_hwmgr.c` is the primary consumer and producer of this state, but sibling modules for SMU7 thermal control, clock power-gating, PowerTune, BACO, and SMU manager operations also interact with `hwmgr->backend` as an `smu7_hwmgr`. The public sleep-divider helper is used by SMU/clock table code that must select firmware deep-sleep dividers based on display/stutter requirements.

The structure layout is an internal driver ABI. It is not exposed to userspace, but it is shared across C translation units in the SMU7 PowerPlay implementation.

### Risks
The main risk is state coupling. `struct smu7_hwmgr` is large and many booleans or masks have sequencing-sensitive meanings. For example, `need_update_smu7_dpm_table`, `mclk_ignore_signal`, DPM key-disabled fields, OverDriveN dependency tables, PCIe range fields, and voltage-control fields are read in multiple phases. Incorrect initialization or stale values can cause wrong DPM masks, missed firmware uploads, flicker, SMC command failures, or unsafe voltage choices.

Array bounds are important. Performance states hold only `SMU7_MAX_HARDWARE_POWERLEVELS` entries, DPM tables are capped at `MAX_REGULAR_DPM_NUMBER`, and leakage tables hold `SMU7_MAX_LEAKAGE_COUNT` entries. Callers must validate firmware/PPTable counts before filling these arrays. The header itself does not enforce those limits.

The header also mixes policy, hardware snapshots, firmware table addresses, thermal state, display timing, and user-overclocking state in one backend object. That makes accidental cross-feature regressions possible when fields are reused or not reset during reinitialization.

### Test Signals
Compile-time signals include successful builds of all SMU7-related translation units and absence of type mismatches with PPTable/AtomBIOS definitions. Runtime validation should show backend allocation initializes all relevant fields before use, DPM table counts never exceed array limits, OverDriveN edits remain within min/max voltage and clock limits, display timing snapshots update when display configuration changes, and teardown frees the display-clock dependency table and backend without leaks.

Hardware tests should exercise V0 and V1 PPTable paths, Polaris/VegaM-specific fields, UVD/VCE power-gating flags, fan/thermal settings, PCIe performance/power-saving ranges, memory-latency table population, EDC leakage table use, and deep-sleep divider calculation around `SMU7_MINIMUM_ENGINE_CLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.h -->
