# subset-b-003522 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c

## Purpose

This file implements Vega10 PowerTune and DiDt/EDC programming for the AMD PowerPlay hardware manager. It translates platform capability bits and runtime registry settings into SMC feature toggles, SMC messages, and direct or indirect register programming for power containment, current limits, package power limits, and graphics-domain droop/current throttling behavior.

## Important APIs, Types, and Functions

The public entry points are `vega10_initialize_power_tune_defaults`, `vega10_set_power_limit`, `vega10_enable_power_containment`, `vega10_disable_power_containment`, `vega10_power_control_set_level`, `vega10_enable_didt_config`, and `vega10_disable_didt_config`. Internal helpers include `vega10_program_didt_config_registers` for indirect DIDT/GC_CAC/SE_CAC register writes, `vega10_program_gc_didt_config_registers` for direct GC register writes, and `vega10_didt_set_mask` for feature-gated enable bits and the `PPSMC_MSG_ConfigureGfxDidt` message. The file is driven by many sentinel-terminated `struct vega10_didt_config_reg` arrays that encode register offset, mask, shift, and value tuples for SE DiDt, SE EDC, PSM GC DiDt/EDC, AVFS PSM reset/init, stall patterns, thresholds, and droop controls.

## Control Flow, State, and Persistence

Power containment setup pulls `phm_tdp_table` data from `hwmgr->pptable`, stores `default_power_limit` and `power_limit`, enables `GNLD_PPT` and `GNLD_TDC` SMC features when supported, and sends `PPSMC_MSG_SetPptLimit` when package tracking is enabled. PowerTune defaults are copied into `data->smc_state_table.pp_table`, including socket/TDC/EDC limits, temperature limits, load-line resistance, and I2C monitor lines.

DiDt enable/disable dispatches on `data->registry_data.didt_mode`. Modes select CAC-driven SE DiDt, PSM GC DiDt, SE EDC, PSM GC EDC, or SE EDC force-stall setup. Most enable paths enter RLC safe mode, lock `adev->grbm_idx_mutex`, iterate shader engines via `GRBM_GFX_INDEX`, program the selected register tables, restore broadcast indexing, update DIDT/EDC masks, and exit safe mode. Successful public enable/disable calls also toggle `data->smu_features[GNLD_DIDT].enabled`.

## Dependencies and Integration Points

This code depends on `vega10_hwmgr` backend state, SMC feature metadata, `vega10_smumgr`/SMC message helpers, CGS register access, SOC15 register macros, GRBM indexing, and AMDGPU RLC safe-mode helpers. It is called from the Vega10 hwmgr initialization/start/stop paths and consumes table data prepared by `vega10_processpptables.c`.

## Risks and Test Signals

The register tables are hardware-specific constants with little runtime validation beyond the sentinel offset and null-table checks. A malformed mask/shift/value tuple can silently program the wrong field. Several internal enable helpers accumulate errors but return `0` after the loop, so partial failures can be hidden. DiDt mode selection depends on registry data and platform caps, so tests should cover each mode, unsupported feature paths, VF short-circuit behavior, SMC message failures, GRBM index restoration, safe-mode enter/exit pairing, and endian conversion of PowerTune defaults into the SMC PPTable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.h

## Purpose

This header defines the Vega10 PowerTune register-description types, PowerContainment feature masks, and public hwmgr entry points implemented by `vega10_powertune.c`.

## Important APIs, Types, and Functions

`enum vega10_pt_config_reg_type` classifies generic PowerTune register locations as MMR, SMC indirect, DIDT indirect, cache, or max. `enum vega10_didt_config_reg_type` selects the indirect register aperture used by DIDT programming: DIDT, GC CAC, or SE CAC. `struct vega10_pt_config_reg` and `struct vega10_didt_config_reg` describe offset/mask/shift/value writes; the latter is the active structure for the table-driven DiDt implementation. `struct vega10_pt_defaults` preserves legacy default knobs for SVI load line, TDC, and DTE-related behavior. The exported functions cover PowerTune defaults, BAPM/fuse/CAC declarations, power containment, power limit/overdrive control, and DiDt enable/disable.

## Control Flow, State, and Persistence

The header itself holds no state, but it defines the contracts used to mutate `hwmgr->pptable`, `hwmgr->platform_descriptor`, `hwmgr->power_limit`, and `vega10_hwmgr` SMC feature state. Its register tuple structs are consumed as static const arrays in the C file, usually ending with an `offset` sentinel of `0xFFFFFFFF`.

## Dependencies and Integration Points

It assumes `struct pp_hwmgr` and fixed-width integer types are available through earlier hwmgr includes. The prototypes are consumed by `vega10_hwmgr.c` and related Vega10 backend code. Several declared functions, such as BAPM/fuse/CAC population, are not implemented in the paired file in this source subset, so their definitions must be resolved elsewhere or may be vestigial for this tree revision.

## Risks and Test Signals

The generic `vega10_pt_config_reg_type` is broader than the implementation visible here, which can mislead maintainers about supported paths. Tests should compile all users of this header, verify declarations match definitions, and exercise any code that constructs register tables against the expected sentinel convention and enum aperture values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_pptable.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_pptable.h

## Purpose

This header is the packed Vega10 ATOMBIOS PowerPlay table schema. It defines platform capability flags, state classifications, voltage modes, and all subtable layouts consumed by the Vega10 PowerPlay parser.

## Important APIs, Types, and Functions

The root `ATOM_Vega10_POWERPLAYTABLE` contains fixed header fields and offsets to subtables: state, fan, thermal controller, SOC/MEM/GFX/DCEF/PIX/DISP/PHY clock dependencies, voltage lookups, multimedia dependencies, VCE states, PowerTune, hard limits, and PCIe levels. Dynamic-array structs model BIOS records with `ucNumEntries` plus trailing `entries[]`, including `ATOM_Vega10_State_Array`, clock dependency tables, voltage lookup tables, MM dependency tables, PCIe tables, and hard-limit tables. Fan and PowerTune tables have multiple revisions: fan table V1/V2/V3 and PowerTune V1/V2/V3. Macros define thermal-controller IDs, fan-parameter bits, platform caps such as BACO and hardware DC, UI classification values, DC/VariBright flags, table revision, and voltage modes.

## Control Flow, State, and Persistence

The file is declarative, but because it is wrapped in `#pragma pack(push, 1)`, every field layout is persistent ABI with VBIOS data. Parser code computes subtable addresses by adding little-endian offsets from the root table to the base pointer, then converts individual little-endian fields into host-side hwmgr structures.

## Dependencies and Integration Points

It depends on ATOM firmware scalar typedefs such as `UCHAR`, `USHORT`, `ULONG`, and `struct atom_common_table_header`. `vega10_processpptables.c` uses nearly every table here. `vega10_thermal.c` and `vega10_powertune.c` receive values that originated in these records through `phm_ppt_v2_information`, `phm_tdp_table`, and `hwmgr->thermal_controller`.

## Risks and Test Signals

Packing, flexible arrays, and revision-dependent record formats make bounds and offset validation critical. Parser tests should cover all supported fan and PowerTune revisions, zero offsets, zero-entry dependency tables, high/low endian conversions, excessive PCIe entries, hard-limit absence, and table-size validation against offsets before dereference. ABI drift in this header can break VBIOS parsing without compiler errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_pptable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.c

## Purpose

This file loads the Vega10 PowerPlay table from ATOMBIOS or a cached soft table, validates it, converts packed BIOS subtables into runtime `phm_ppt_v2_information`, initializes platform capabilities and thermal metadata, exposes BIOS power-state entries, and provides a BACO-capability refresh helper.

## Important APIs, Types, and Functions

The exported `vega10_pptable_funcs` supplies `.pptable_init` and `.pptable_fini` hooks. `vega10_get_number_of_powerplay_table_entries` returns BIOS state count, `vega10_get_powerplay_table_entry` maps one ATOM state through a caller callback, and `vega10_baco_set_cap` refreshes `PHM_PlatformCaps_BACO`.

Key static functions are `get_powerplay_table`, `check_powerplay_tables`, `set_platform_caps`, `init_thermal_controller`, `init_over_drive_limits`, `init_powerplay_extended_tables`, `init_dpm_2_parameters`, and conversion helpers for MM, SOC/GFX/MEM/DCEF/PIX/PHY/DISP clocks, PCIe, hard limits, voltage lookups, valid clock arrays, TDP/PowerTune, and I2C line IDs.

## Control Flow, State, and Persistence

Initialization allocates `hwmgr->pptable`, fetches or caches the BIOS table in `hwmgr->soft_pp_table`, validates revision and state presence, sets platform caps from `ulPlatformCaps`, imports thermal/fan settings, clamps the overdrive engine clock to `VEGA10_ENGINECLOCK_HARDMAX` unless ACG is enabled, builds dependency and lookup tables with `kzalloc_flex`, copies hard limits into `hwmgr->dyn_state`, and initializes DPM2 voltage-mode and TDP overdrive fields. Uninitialization frees most allocated tables and nulls their pointers.

Power-state entry lookup reuses the cached table, validates the state array, computes classification flags from `usClassification` and `usClassification2`, calls the supplied callback with the ATOM state and root table, then patches boot state through `hwmgr->hwmgr_func` when applicable.

## Dependencies and Integration Points

The parser depends on `ppatomfwctrl`, ATOM firmware table access, `vega10_pptable.h`, Linux allocation helpers, `phm_cap_set/unset`, `pp_hwmgr` table hooks, and AMDGPU PCI IDs for a DCEFCLK workaround. Its outputs feed Vega10 DPM setup, fan control, PowerTune default copying, power containment, display clock decisions, overdrive limits, and BACO support.

## Risks and Test Signals

Most subtable pointers are formed by offset arithmetic with limited table-size checks, so malformed BIOS data can lead to out-of-bounds reads. The state entry check uses `entry_index <= ucNumEntries`, which permits an out-of-range zero-based index. `get_vddc_lookup_table` allocates for `max_levels` but sets count from BIOS entries without clamping. Fini does not visibly free every optional table initialized in `init_powerplay_extended_tables` in this source version, such as SOC/DCEF/PIX/PHY/DISP/PCIe/valid SOC/DCEF arrays, which should be checked against the wider tree. Tests should inject synthetic tables for each revision, zero-entry failures, absent optional offsets, pioneer DCEFCLK workaround, ACG overdrive behavior, PCIe truncation, and cleanup after partial initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.h

## Purpose

This header declares the Vega10 PowerPlay table parser interface and the BIOS I2C-line identifier mappings needed to translate PowerTune monitor lines into DAL/SMC line values.

## Important APIs, Types, and Functions

`enum Vega10_I2CLineID` defines BIOS line IDs for DDC1 through DDC6, shared SCL/SDA, and VGA DDC. The `Vega10_I2C_*` macros map those IDs to hardware line constants used by `get_scl_sda_value` in the C file. Exports include `vega10_pptable_funcs`, `vega10_get_number_of_powerplay_table_entries`, `vega10_get_powerplay_table_entry`, and `vega10_baco_set_cap`.

## Control Flow, State, and Persistence

The header does not own memory or state. Its function table export drives hwmgr initialization/fini, while the state-entry callback interface lets the broader PowerPlay stack interpret BIOS state records without exposing parser internals as public structs.

## Dependencies and Integration Points

It includes `hwmgr.h` for `struct pp_hwmgr`, `struct pp_power_state`, and `struct pp_table_func`. `vega10_hwmgr.c` assigns `hwmgr->pptable_func` to `vega10_pptable_funcs` and uses the entry accessors while building state tables. The I2C macros integrate with PowerTune table revisions that encode only a line ID rather than separate SCL/SDA values.

## Risks and Test Signals

The numeric I2C constants are hardware contracts and should match DAL/SMC expectations. Tests should cover each enum-to-SCL/SDA mapping, default mapping to zero for unknown IDs, ABI compatibility of the callback signature, and successful linkage of all exported parser functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_processpptables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.c

## Purpose

This file implements Vega10 thermal controller setup, temperature alert programming, fan speed reporting and manual control, SMC fan-control table updates, and multi-GPU fan boost behavior for the AMD PowerPlay hwmgr.

## Important APIs, Types, and Functions

Public functions include `vega10_fan_ctrl_get_fan_speed_info`, PWM and RPM get/set helpers, `vega10_fan_ctrl_set_static_mode`, `vega10_fan_ctrl_set_default_mode`, `vega10_fan_ctrl_reset_fan_speed_to_default`, `vega10_fan_ctrl_start_smc_fan_control`, `vega10_fan_ctrl_stop_smc_fan_control`, `vega10_thermal_get_temperature`, `vega10_thermal_disable_alert`, `vega10_thermal_stop_thermal_controller`, `vega10_start_thermal_controller`, `vega10_thermal_ctrl_uninitialize_thermal_controller`, and `vega10_enable_mgpu_fan_boost`. Internal helpers toggle the `GNLD_FAN_CONTROL` and `GNLD_FW_CTF` SMC features, initialize tach/PWM registers, program interrupt thresholds, and write fan parameters into the SMC PPTable.

## Control Flow, State, and Persistence

Fan capability reporting is based on `hwmgr->thermal_controller.fanInfo`, no-fan flags, tachometer pulses, and `PHM_PlatformCaps_FanSpeedInTableIsRPM`. PWM reads convert `FDO_PWM_DUTY` against `FMAX_DUTY100` to a 0-255 value. RPM reads use `PPSMC_MSG_GetCurrentRpm` when SMC fan control is supported, otherwise compute from `CG_TACH_STATUS` and ASIC xclk.

Manual PWM/RPM writes stop microcode fan control when needed, program static duty or target tach period, and switch `CG_FDO_CTRL2` into static PWM or static RPM mode. The original default PWM mode and `TMIN` are cached in `hwmgr->fan_ctrl_default_mode`, `hwmgr->tmin`, and `hwmgr->fan_ctrl_is_in_default_mode` so default mode can be restored.

Thermal startup initializes tach response, programs alert min/max using the caller range and PowerTune shutdown temperature, enables FW CTF and interrupt clear bits, writes fan table fields into `data->smc_state_table.pp_table`, pushes the PPTABLE to SMC, and starts SMC fan control if microcode fan control remains enabled. Stop paths disable alerts and restore/default fan control.

## Dependencies and Integration Points

The file depends on SOC15 THM registers, AMDGPU xclk, SMC messages and table manager, Vega10 SMC feature bookkeeping, thermal/fan values parsed by `vega10_processpptables.c`, and hwmgr function tables in `vega10_hwmgr.c`. It updates the SMC PPTable consumed by firmware and exposes fan/thermal operations to the PowerPlay public interface.

## Risks and Test Signals

Risk areas include divide-by-zero guards around tach/PWM values, restoring `TMIN` with the expected field encoding, signed/unsigned temperature conversions, no-fan behavior returning mixed `0` and negative errors, stopping microcode control before manual writes, and restart sequencing after mGPU boost. Tests should cover no-fan boards, boards without `GNLD_FAN_CONTROL`, RPM bounds, PWM saturation at 255, invalid temperature ranges, FW CTF enable/disable failures, SMC table-manager failures, and default-mode restoration after manual control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.h

## Purpose

This header declares the Vega10 thermal and fan-control interface used by the hwmgr function table and related PowerPlay code.

## Important APIs, Types, and Functions

`struct vega10_temperature` groups edge, hotspot, HBM, VR, liquid, and PLX temperature channels, although the paired C file only exposes a single current temperature read in this subset. Macros define thermal alert masks, min/max raw reading ranges, min/max alert temperatures, and static PWM/RPM mode constants. Exported functions cover temperature readout, thermal controller start/stop/uninitialize, alert disable, fan speed capability query, PWM/RPM fan get/set, static/default mode switching, SMC fan-control start/stop, reset-to-default, and mGPU fan boost.

## Control Flow, State, and Persistence

The header owns no state. Its functions operate on `struct pp_hwmgr`, especially `hwmgr->thermal_controller`, fan default-mode cache fields, platform caps, and Vega10 backend SMC feature flags. Startup requires a `struct PP_TemperatureRange` supplied by the caller.

## Dependencies and Integration Points

It includes `hwmgr.h` and is consumed by `vega10_hwmgr.c` to populate thermal and fan callbacks. The C implementation depends on fan tables and PowerTune limits parsed from BIOS tables before these APIs are invoked.

## Risks and Test Signals

The declared surface mixes low-level register mode control with high-level SMC fan control. Tests should verify callback registration, no-fan board behavior, RPM/PWM support flags, thermal startup with null and valid ranges, and that all declared exports have matching definitions in the linked build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.c

## Purpose

This file implements Vega12 BACO state transitions for the PowerPlay hwmgr using SOC15 BACO command tables and an SMC fallback for entering BACO.

## Important APIs, Types, and Functions

The exported function is `vega12_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`. Static `soc15_baco_cmd_entry` arrays describe the hardware sequences: `pre_baco_tbl` disables doorbell monitoring/framebuffer and masks reset interrupts, `enter_baco_tbl` waits for SOC idle and powers/islands the BACO domain down, `exit_baco_tbl` reverses power/isolation/reset/clock controls and waits for exit, and `clean_baco_tbl` clears BIOS scratch registers.

## Control Flow, State, and Persistence

The function reads current state through `smu9_baco_get_state` and returns immediately if already at the requested target. For `BACO_STATE_IN`, it runs the pre-BACO table, sends `PPSMC_MSG_EnterBaco` only if that table reports success, then runs the hardware enter table and returns success if it reports success. For `BACO_STATE_OUT`, it sleeps 20 ms to satisfy regulator off/on timing, runs the exit table, then clears scratch registers. Failed or unsupported paths return `-EINVAL`.

## Dependencies and Integration Points

The file depends on Vega12 SOC15 register offsets and masks, `soc15_baco_program_registers`, SMU9 BACO state helpers, Vega12 PPSMC message IDs, and the shared hwmgr device context. It is used by the Vega12 power-management path that exposes BACO entry/exit.

## Risks and Test Signals

The command table interpreter's return convention is crucial: this code treats nonzero returns from `soc15_baco_program_registers` as success. Any convention mismatch in the shared helper would invert behavior. Hardware waits use masks and expected values that must match Vega12 register semantics. Tests should cover already-in-state returns, enter fallback failure, enter table wait timeout, exit timing, scratch cleanup, invalid target states, and full suspend/resume or runtime power-cycle sequences on BACO-capable Vega12 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.h

## Purpose

This header declares the Vega12 BACO state transition entry point.

## Important APIs, Types, and Functions

It includes `smu9_baco.h` for `enum BACO_STATE` and declares `vega12_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`.

## Control Flow, State, and Persistence

The header contains no state. The declared function mutates hardware BACO state through register command tables and SMC messages in the C implementation.

## Dependencies and Integration Points

It depends on the shared SMU9 BACO declarations and is intended for Vega12 hwmgr integration code that needs to enter or leave BACO during power transitions.

## Risks and Test Signals

Build tests should ensure `struct pp_hwmgr` and `enum BACO_STATE` are visible through included headers in all translation units that include this file. Runtime tests should exercise both `BACO_STATE_IN` and `BACO_STATE_OUT` through the exported function rather than duplicating command sequences elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.h -->
