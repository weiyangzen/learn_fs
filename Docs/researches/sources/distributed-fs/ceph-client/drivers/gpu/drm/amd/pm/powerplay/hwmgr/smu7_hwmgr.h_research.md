# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.h

## Purpose
`smu7_hwmgr.h` defines the private data model and constants used by the SMU7 hardware-manager backend. It describes SMU7 performance levels, power states, DPM tables, voltage/leakage caches, boot-state snapshots, display timing, PCIe ranges, OverDriveN tables, profile settings, memory-latency tables, and the large `struct smu7_hwmgr` backend object allocated by `smu7_hwmgr.c`.

The header is the contract between the SMU7 manager implementation and sibling SMU7 modules that need shared backend fields. It also exposes `smu7_get_sleep_divider_id_from_clock()` for deep-sleep divider selection.

## Important APIs, Types, And Functions
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

The only function prototype is `uint8_t smu7_get_sleep_divider_id_from_clock(uint32_t clock, uint32_t clock_insr);`.

## Control Flow
The header contains no executable control flow, but its structures directly shape runtime control flow in `smu7_hwmgr.c`. `struct smu7_hwmgr` fields decide which initialization branches run, which DPM domains are enabled or disabled, whether voltage control uses GPIO or SVID2, whether PCIe/DPM tables must be updated, whether display timing requires a firmware update, whether MCLK switching should be ignored, and whether EDC/AVFS/power-containment features are enabled.

Power-state transition code consumes `struct smu7_power_state` and `struct smu7_performance_level` to clamp and upload SCLK/MCLK/PCIe ranges. DPM upload code consumes `struct smu7_dpm_table` and `struct smu7_dpmlevel_enable_mask`. OverDriveN control mutates `struct smu7_odn_dpm_table`. Display-aware logic relies on `struct smu7_display_timing` and `struct smu7_mclk_latency_table`.

## State And Persistence Behavior
All state defined here is in-memory driver state. `struct smu7_hwmgr` is allocated during backend initialization and freed during backend teardown. Some fields are snapshots of hardware or firmware state, such as boot clocks/voltages, saved clock registers, memory type, MC microcode flags, efuse/VBIOS leakage tables, and current display timing. Other fields are mutable policy state, such as DPM enable masks, OverDriveN edits, profile settings, power-gating flags, update flags, and feature disable booleans.

The header itself does not persist anything. Its fields become persistent for the lifetime of the hardware-manager backend and are used to regenerate or update SMU firmware tables and registers as display, power-source, user-profile, and power-state inputs change.

## Dependencies
The header includes `hwmgr.h` and `ppatomctrl.h`, so it depends on generic PowerPlay manager definitions, AtomBIOS voltage table types, PowerPlay clock/voltage dependency records, OverDriveN structures, and Atom control leakage/EDC structures. The field types also implicitly depend on PPTable V1 types such as `phm_ppt_v1_clock_voltage_dependency_record`, `phm_odn_clock_levels`, `pp_atomctrl_voltage_table`, `AtomCtrl_HiLoLeakageOffsetTable`, and `AtomCtrl_EDCLeakgeTable`.

## Integration Points
`smu7_hwmgr.c` is the primary consumer and producer of this state, but sibling modules for SMU7 thermal control, clock power-gating, PowerTune, BACO, and SMU manager operations also interact with `hwmgr->backend` as an `smu7_hwmgr`. The public sleep-divider helper is used by SMU/clock table code that must select firmware deep-sleep dividers based on display/stutter requirements.

The structure layout is an internal driver ABI. It is not exposed to userspace, but it is shared across C translation units in the SMU7 PowerPlay implementation.

## Risks
The main risk is state coupling. `struct smu7_hwmgr` is large and many booleans or masks have sequencing-sensitive meanings. For example, `need_update_smu7_dpm_table`, `mclk_ignore_signal`, DPM key-disabled fields, OverDriveN dependency tables, PCIe range fields, and voltage-control fields are read in multiple phases. Incorrect initialization or stale values can cause wrong DPM masks, missed firmware uploads, flicker, SMC command failures, or unsafe voltage choices.

Array bounds are important. Performance states hold only `SMU7_MAX_HARDWARE_POWERLEVELS` entries, DPM tables are capped at `MAX_REGULAR_DPM_NUMBER`, and leakage tables hold `SMU7_MAX_LEAKAGE_COUNT` entries. Callers must validate firmware/PPTable counts before filling these arrays. The header itself does not enforce those limits.

The header also mixes policy, hardware snapshots, firmware table addresses, thermal state, display timing, and user-overclocking state in one backend object. That makes accidental cross-feature regressions possible when fields are reused or not reset during reinitialization.

## Test Signals
Compile-time signals include successful builds of all SMU7-related translation units and absence of type mismatches with PPTable/AtomBIOS definitions. Runtime validation should show backend allocation initializes all relevant fields before use, DPM table counts never exceed array limits, OverDriveN edits remain within min/max voltage and clock limits, display timing snapshots update when display configuration changes, and teardown frees the display-clock dependency table and backend without leaks.

Hardware tests should exercise V0 and V1 PPTable paths, Polaris/VegaM-specific fields, UVD/VCE power-gating flags, fan/thermal settings, PCIe performance/power-saving ranges, memory-latency table population, EDC leakage table use, and deep-sleep divider calculation around `SMU7_MINIMUM_ENGINE_CLOCK`.
