# subset-b-003520 Research

Work item: subset-b-003520

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.c

Purpose: implements SMU7 PowerTune support for Southern Islands/VIslands-era discrete AMD GPUs, especially Polaris10/11/12 and VegaM. The file programs DIDT and GC CAC hardware tables, enables/disables SMC CAC, enables/disables power containment features, and applies user TDP adjustment through SMC messages.

Important APIs and functions: `smu7_enable_didt_config()` is the main bring-up routine for dynamic indirect current/temperature throttling. It iterates shader engines using `mmGRBM_GFX_INDEX`, enters RLC safe mode, programs ASIC-specific `gpu_pt_config_reg` tables, enables DIDT blocks, and sends Polaris11-specific DPM DIDT and MC blackout messages. `smu7_disable_didt_config()` reverses the runtime enable. `smu7_enable_smc_cac()` and `smu7_disable_smc_cac()` toggle SMC CAC tracking and persist `smu7_hwmgr::cac_enabled`. `smu7_enable_power_containment()` enables TDC and package power limit features and initializes `hwmgr->default_power_limit` / `hwmgr->power_limit` from the CAC/TDP table. `smu7_set_power_limit()` sends package power limits in 8-bit fractional units. `smu7_power_control_set_level()` computes OverDrive target TDP from platform descriptor adjustment fields and the PP table's TDP/configurable TDP.

Control flow: DIDT setup is table-driven. `smu7_program_pt_config_registers()` walks sentinel-terminated register rows, selects direct, SMC indirect, DIDT indirect, or GC CAC indirect access by row type, merges cached field fragments, and writes the modified register value. The selected tables differ by `hwmgr->chip_id`; Polaris11 also uses kicker tables for P21/P31 ASIC IDs and an efuse gate for the MC blackout workaround. Error paths unlock `grbm_idx_mutex` and exit RLC safe mode.

State and persistence: most state is hardware/SMC-resident. Driver-side state is limited to `smu7_hwmgr::cac_enabled`, `power_containment_features`, and power-limit fields in `pp_hwmgr`. DIDT register programming persists until GPU reset or explicit disable. Package power containment state is tracked by feature bits so disable sends only messages for features that were enabled.

Dependencies and integration: depends on `smum_send_msg_to_smc*`, CGS register accessors, ASIC ID helpers, AtomBIOS efuse reads, `smu7_hwmgr` backend flags, PP table CAC/TDP structures, RLC safe mode, and platform capability bits such as CAC, PowerContainment, SQRamping, TDRamping, TCPRamping, DBRamping.

Risks: register tables are highly ASIC-specific; an incorrect chip/revision branch can program unsafe power/timing values. `smu7_program_pt_config_registers()` assumes masks/shifts/types are valid and sentinel-terminated. Failure handling in PowerTune enable may leave some SMC features enabled if a later feature fails. Power limit units must remain consistent with SMC expectations (`n << 8`, TDP multiplied by 256). DIDT setup touches GRBM global indexing and must always restore it.

Test signals: verify boot/resume on Polaris10/11/12/VegaM, DIDT enable/disable SMC message success, no GRBM index leakage after failed setup, power limit sysfs/OverDrive changes reaching SMC, and dmesg assertions for table programming or CAC/TDC/package power failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.h

Purpose: public interface and local register-field definitions for SMU7 PowerTune. It exposes the PowerTune, CAC, power containment, power limit, and DIDT entry points implemented by `smu7_powertune.c`.

Important APIs/types: defines extra DIDT `UNUSED_0` masks/shifts for SQ, TD, and TCP control/tuning registers when generated headers do not provide them. Defines `POWERCONTAINMENT_FEATURE_DTE`, `POWERCONTAINMENT_FEATURE_TDCLimit`, and `POWERCONTAINMENT_FEATURE_PkgPwrLimit` bit flags used by `smu7_hwmgr::power_containment_features`. Defines indirect register offsets for GC CAC and selected DIDT control registers (`ixGC_CAC_CNTL`, `ixDIDT_*_STALL_CTRL`, `ixDIDT_*_TUNING_CTRL`). Declares `smu7_enable_smc_cac()`, `smu7_disable_smc_cac()`, `smu7_enable_power_containment()`, `smu7_disable_power_containment()`, `smu7_set_power_limit()`, `smu7_power_control_set_level()`, `smu7_enable_didt_config()`, and `smu7_disable_didt_config()`.

Control flow and integration: this header is included by SMU7 hardware manager code to wire PowerTune operations into lifecycle and OverDrive paths. The definitions are intentionally low-level: callers do not manipulate DIDT registers directly but use the declared routines, while the C file consumes the masks and feature bits.

State and persistence: no storage is declared here. The feature bit definitions describe persistent runtime state in the SMU7 backend; register definitions describe hardware state programmed through CGS indirect access.

Dependencies: requires `struct pp_hwmgr` and `uint32_t` to be visible from including files. It relies on register naming conventions from AMD generated headers and SMC message contracts used by the implementation.

Risks: exported prototypes form the contract used by multiple hwmgr paths; changing units or semantics for `smu7_set_power_limit()` or `smu7_power_control_set_level()` can break sysfs/OverDrive behavior. The include guard closing comment is stale (`DGPU_POWERTUNE_H`) but harmless.

Test signals: compile coverage of all SMU7 hwmgr users, plus runtime tests of CAC enable/disable, DIDT enable/disable, and power-limit adjustment on supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.c

Purpose: implements SMU7 thermal controller and fan control operations. It reads temperatures, programs thermal alert thresholds, starts/stops SMC fan control, supports manual PWM/RPM fan modes, and restores fan defaults during shutdown.

Important APIs and functions: `smu7_fan_ctrl_get_fan_speed_info()` reports percentage and optionally RPM capabilities based on fan info and platform caps. `smu7_fan_ctrl_get_fan_speed_pwm()` and `smu7_fan_ctrl_get_fan_speed_rpm()` read SMC indirect thermal/tach registers. `smu7_fan_ctrl_set_static_mode()` caches default FDO mode and `TMIN` in `pp_hwmgr` and switches to static PWM/RPM mode. `smu7_fan_ctrl_set_default_mode()` restores those cached defaults. `smu7_fan_ctrl_start_smc_fan_control()` sends `PPSMC_StartFanControl`, configures fuzzy/table mode, sets max fan output and target temperature, and enables Zero RPM on supported Polaris ASICs. `smu7_start_thermal_controller()` performs initialization, threshold setup, alert enable, AVFS thermal enable, fan table setup, and fan control start.

Control flow: manual fan speed writes stop microcode fan control when enabled, compute either static duty from `FMAX_DUTY100` or tach target period from ASIC crystal clock, then set static FDO mode. Controller start validates a caller-provided temperature range, clamps it against legal alert limits, writes high/low/DPM thresholds, unmasks high/low alerts, enables SMC thermal control, enables AVFS, uploads fan tables, and starts SMC fan policy. Stop disables thermal alerts and restores default fan mode when a fan exists.

State and persistence: caches fan default mode, `TMIN`, `fan_ctrl_is_in_default_mode`, and `fan_ctrl_enabled` in `pp_hwmgr`. Hardware state lives in SMC indirect thermal/FDO/tach registers and SMC fan controller state. Temperature results are returned in `PP_TEMPERATURE_UNITS_PER_CENTIGRADES`.

Dependencies and integration: uses `smu7_common.h`, `smu7_hwmgr.h`, `smum_send_msg_to_smc*`, `smum_thermal_avfs_enable()`, `smum_thermal_setup_fan_table()`, PHM register-field macros, platform caps, and `amdgpu_asic_get_xclk()`.

Risks: tach period math can overflow if inputs are not bounded; RPM set rejects zero, out-of-range, and excessively high values. PWM get/set fails if `FMAX_DUTY100` is zero. `smu7_fan_ctrl_start_smc_fan_control()` sets `fan_ctrl_enabled = true` even if a later SMC message failed. Temperature low-range bit handling maps bit 9 to maximum temperature, which should be checked against hardware docs because the comment says lower than usable range.

Test signals: fan sysfs read/write for PWM and RPM, fan reset on module unload/suspend, thermal interrupt delivery, Zero RPM behavior on Polaris without custom thermal management, AVFS enable failure handling, and no fan paths returning `-ENODEV` or no-op as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.h

Purpose: declares the SMU7 thermal and fan-control interface and the constants shared with SMU7 hwmgr code.

Important APIs/types: defines thermal interrupt mask bits (`SMU7_THERMAL_HIGH_ALERT_MASK`, `SMU7_THERMAL_LOW_ALERT_MASK`), legal temperature reading and alert ranges, and static fan-control modes (`FDO_PWM_MODE_STATIC`, `FDO_PWM_MODE_STATIC_RPM`). Declares temperature read, thermal controller start/stop/uninitialize, alert disable, SMC fan-control start/stop, fan capability query, PWM/RPM read/write, static/default mode switching, and reset-to-default helpers.

Control flow and integration: this header lets SMU7 backend code register fan and thermal callbacks in its hardware-manager function table. Callers use `smu7_start_thermal_controller()` with a `PP_TemperatureRange`, then use fan control functions for sysfs/OverDrive operations, and call stop/uninitialize during shutdown.

State and persistence: no direct storage. The constants constrain hardware threshold programming and fan mode writes performed by `smu7_thermal.c`.

Dependencies: includes `hwmgr.h` for `struct pp_hwmgr`, `struct phm_fan_speed_info`, and `struct PP_TemperatureRange` visibility.

Risks: because this header exposes low-level manual fan controls, callers must respect fan presence and RPM capability checks in the implementation. Any unit mismatch in temperature range arguments would write incorrect alert thresholds.

Test signals: compile users of every declared callback, thermal start with valid/invalid ranges, PWM and RPM capability reporting, and fan default restoration after manual control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.c

Purpose: implements the SMU8 powerplay hardware-manager backend for Carrizo/Stoney-class APUs. It initializes BIOS-derived platform data, patches and uploads SMU clock tables, manages SCLK/UVD/VCE/ACP DPM limits, handles power state transitions, exposes clocks/sensors, and wires the backend into `pp_hwmgr_func`.

Important APIs and functions: `smu8_init_function_pointers()` installs `smu8_hwmgr_funcs` and `pptable_funcs`. Backend lifecycle is `smu8_hwmgr_backend_init()` / `smu8_hwmgr_backend_fini()`. `smu8_get_system_info_data()` parses AtomBIOS `IntegratedSystemInfo` revision 9 into `smu8_hwmgr::sys_info`, including UMA/NB/display clocks, HTC limits, NB DPM enablement, DFS bypass, and display power-level table creation. `smu8_upload_pptable_to_smu()` downloads the SMU clock table, patches SCLK/GFX/ACP/UVD/VCE breakdown levels from dynamic dependency tables, computes DFS dividers via AtomBIOS, and uploads the table. `smu8_setup_asic_task()`, `smu8_enable_dpm_tasks()`, `smu8_set_power_state_tasks()`, and `smu8_disable_dpm_tasks()` form the main setup/enable/transition/disable path.

Control flow: initialization allocates `struct smu8_hwmgr`, sets conservative defaults and caps, reads system info, constructs a boot power level, and advertises eight hardware activity levels. ASIC setup uploads tables, initializes DPM limit ranges, sets initial power-gate state, and clears SCLK thresholds. Enabling DPM programs voting clients, enables SCLK DPM, clamps boot SCLK through soft min/max SMC messages, resets ACP boot level, and populates UMD pstate clocks. State transitions update SCLK limits from display requirements and stable-pstate policy, set deep-sleep and watermark thresholds, enable NB DPM, and update low-memory pstate behavior based on requested action.

State and persistence: the backend stores system info, boot/current/requested power states, DPM soft/hard limits, power-gated booleans, DPM flags, CC6 settings, thermal threshold data, max SCLK cache, and several policy flags. Hardware/SMC state is modified through SMC feature masks and messages, CGS indirect registers, IP block powergating/clockgating calls, and uploaded SMU tables.

Dependencies and integration: depends on AtomBIOS parsing, PPT table helpers, SMU8 firmware message IDs, `smu8_fusion` clock-table layouts, AMDGPU IP powergating/clockgating, platform caps, display configuration, thermal policy arrays, and helper macros from `smu_helper.h`. It integrates via `pp_hwmgr_func` callbacks for power states, sensors, clock levels, DAL power level, CAC buffer info, and UVD/VCE/ACP gating.

Risks: many functions assume dependency tables are non-NULL and counts are within `SMU8_MAX_HARDWARE_POWERLEVELS`; upload asserts counts but later sensor/clock paths may index based on firmware-reported levels. `smu8_hwmgr_backend_init()` leaks allocated backend memory if later initialization fails. `smu8_dpm_get_sclk()` returns `-EINVAL` through a `uint32_t` return type. Several SMC send return values are ignored, so state flags can diverge from firmware. Powergating order is critical for UVD/VCE, especially 4K Stoney low-memory pstate handling.

Test signals: boot and suspend/resume on Carrizo/Stoney, AtomBIOS table revision rejection, SMU clock table upload, DPM force high/low/auto sysfs behavior, sensor reads for SCLK/VDDNB/VDDGFX/UVD/VCE/load/temp, UVD/VCE playback and encode powergating, stable-pstate/UMD pstate behavior, CC6 display power parameter messages, and failure injection for SMC messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.h

Purpose: defines the SMU8 backend data model, DPM constants, display PHY packing helpers, and the public initialization hook for SMU8 hwmgr.

Important APIs/types: constants define NB pstate counts, memory clock counts, display-clock levels, max hardware power levels, default voting clients, minimum deep-sleep SCLK, and Carrizo PCI device IDs. `struct smu8_dpm_entry` stores soft/hard min/max clocks. `struct smu8_sys_info` mirrors AtomBIOS integrated system info used by runtime policy. `DDI_POWERGATING_ARG()` packs PHY ID, lane mask, and RX/TX/core bits. `struct smu8_power_level` and `struct smu8_power_state` hold per-state engine clock, voltage, divider, display/VCE watermark, NB pstate, BAPM, and action data. `struct smu8_hwmgr` is the large backend state block. The only exported function is `smu8_init_function_pointers()`.

Control flow and integration: structures here are consumed by `smu8_hwmgr.c` and by generic powerplay code through `pp_power_state::hardware`. The `magic` field protects casts between generic `pp_hw_power_state` and SMU8-specific states. DPM flags mirror enabled SMC feature state for SCLK/UVD/VCE/ACP and forced-level/debug state.

State and persistence: `struct smu8_hwmgr` persists across the hardware-manager lifetime and caches BIOS data, current/requested states, DPM limits, power-gate booleans, CC6 settings, PowerTune feature booleans, SRAM/soft-register addresses, boot levels, intervals, display config, CAC buffer addresses, and cached max SCLK level. This driver state must stay coherent with SMC firmware state.

Dependencies: includes `cgs_common.h` and `ppatomctrl.h`; uses many powerplay types defined elsewhere, including dependency tables, `pp_hwmgr`, and power-state structures.

Risks: this header is a shared state contract; field layout changes can break casts and callbacks. Several fields are policy flags with similar names (`bapm_enabled`, `enable_ba_pm_feature`, `enable_tdc_limit_feature`, `power_containment_features`) and need careful initialization. Fixed-size arrays depend on BIOS/SMU counts not exceeding constants.

Test signals: compile all SMU8 users, inspect backend allocation/zero-init assumptions, validate state casts via `PHM_Cz_Magic`, and exercise power-state parsing for entries up to `SMU8_MAX_HARDWARE_POWERLEVELS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.c

Purpose: provides SMU9 BACO/BAMACO support probing and current BACO state reporting for SOC15-era GPUs.

Important APIs and functions: `smu9_get_bamaco_support()` checks the platform BACO capability bit, performs a magic indexed register write/read at `0x12074/0x12075`, then reads `RCC_BIF_STRAP0` through SOC15 NBIF registers to see whether `STRAP_PX_CAPABLE` is set. It returns `BACO_SUPPORT` only when both hardware checks pass. `smu9_baco_get_state()` reads `mmBACO_CNTL` and maps `BACO_MODE` to `BACO_STATE_IN` or `BACO_STATE_OUT`.

Control flow: there is no state transition logic in this file; it is a support/state query layer used by higher-level BACO management. Probing short-circuits if platform caps do not advertise BACO.

State and persistence: no driver-side state is stored. The functions observe hardware strap and BACO control registers. The temporary write to `0x12074` selects/probes internal state and should be treated as hardware-specific.

Dependencies and integration: includes SOC15, Vega10 offset/include headers, `amdgpu.h`, and `smu9_baco.h`. Uses `RREG32`, `WREG32`, and `RREG32_SOC15` register access macros, plus `PHM_PlatformCaps_BACO` and `enum BACO_STATE` from common BACO headers.

Risks: magic registers are not self-documenting and may be ASIC-specific. Incorrect support detection can expose BACO on unsupported systems or hide it on supported systems. `adev` is only used indirectly by register macros, so refactors should avoid removing it if macros depend on local naming. No null checks are present for `hwmgr` or `state`.

Test signals: BACO support detection on SMU9 dGPU platforms with and without PX capability, BACO state reads before/after entry/exit through the higher-level BACO path, and register access safety during early init/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.h

Purpose: declares the SMU9 BACO support query and state query functions.

Important APIs/types: includes `hwmgr.h` and `common_baco.h`, then exports `smu9_get_bamaco_support(struct pp_hwmgr *hwmgr)` and `smu9_baco_get_state(struct pp_hwmgr *hwmgr, enum BACO_STATE *state)`.

Control flow and integration: higher-level power management code includes this header to decide whether BACO is available and to query whether the GPU is currently in or out of BACO. Actual entry/exit sequencing is not declared here.

State and persistence: no state is declared. The API reports hardware capability/state from the C implementation.

Dependencies: depends on `struct pp_hwmgr`, `enum BACO_STATE`, and `BACO_SUPPORT` definitions from included hwmgr/common BACO headers.

Risks: small interface, but callers must provide a valid `state` pointer. The function name `smu9_get_bamaco_support` includes "bamaco" while the rest of the subsystem often says BACO, so searches and API consistency can be easy to miss.

Test signals: compile all SMU9 BACO users and validate capability/state paths on ASICs with SOC15 NBIF BACO registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu9_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.c

Purpose: shared helper implementation for AMD powerplay hardware managers. It provides voltage conversion and table manipulation, register wait helpers, DPM table utilities, EVV voltage lookup, thermal interrupt processing, SMU9 IRQ registration, AtomBIOS data-table lookup, PPT v1 dependency copying, and SOC15 watermark table population.

Important APIs and functions: `convert_to_vid()` / `convert_to_vddc()` convert between millivolt-style VDDC and SVI2 VID using the 6200/25 formula and `VOLTAGE_SCALE`. `phm_copy_clock_limits_array()` and `phm_copy_overdrive_settings_limits_array()` allocate little-endian converted arrays from PPT data. `phm_wait_on_register()` / `phm_wait_on_indirect_register()` and unequal variants poll with `hwmgr->usec_timeout`. Voltage helpers trim duplicate entries, create MVDD/VDDCI/VDD voltage tables, clamp voltage table size, find voltage indexes/IDs, find closest VDDCI, find boot DPM levels, and query EVV voltage on SCLK. DPM helpers reset single tables, set PCIe entries, and compute enable masks. `phm_irq_process()` handles thermal low/high and critical temperature interrupts and schedules SW CTF work or powers off the system on hardware CTF. `smu9_register_irq_handlers()` registers THM and SMUIO GPIO19 interrupt sources. `smu_atom_get_data_table()` wraps AtomBIOS table lookup. `smu_set_watermarks_for_clocks_ranges()` maps DAL watermark ranges into firmware table rows.

Control flow: most helpers are pure transformations or bounded polling. IRQ processing branches by interrupt client/source: legacy thermal high-to-low reports under-temperature, low-to-high schedules delayed SW CTF work, GPIO19/SOC15 SMUIO critical thermal faults call `orderly_poweroff(true)`. Watermark programming validates no more than four DMIF/MCIF sets and writes rows in little-endian MHz units.

State and persistence: allocation helpers transfer ownership of new arrays to caller-provided pointers. Voltage trimming rewrites the caller's table in place. Register wait helpers do not store state. IRQ registration allocates an `amdgpu_irq_src` and registers it with AMDGPU IRQ infrastructure. Critical thermal handling initiates system shutdown.

Dependencies and integration: used across hwmgr implementations. Depends on AtomBIOS helpers, powerplay PPT v1 structs, CGS register access, AMDGPU IRQ/delayed work, Linux reboot API, endian conversion helpers, and SOC15/legacy thermal interrupt source IDs.

Risks: `phm_get_lowest_enabled_level()` loops until it finds a set bit and has no zero-mask guard. Voltage table trimming assumes destination capacity is large enough. Several helpers return `0` on assertion failures for index lookups, which can look like a valid first entry. `phm_wait_on_register()` returns `-1` while unequal variant returns `-ETIME`, so callers must not assume uniform errno. Critical thermal IRQ path intentionally powers off the machine and must only run on true CTF events.

Test signals: unit-style tests for table trimming and voltage conversions, boot/resume coverage for register waits, IRQ registration and thermal interrupt injection, EVV lookup across pre-Tonga/Tonga-Polaris/Polaris+ branches, and DAL watermark range programming with invalid counts and boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.h

Purpose: shared helper declarations and register-field macros for AMD powerplay SMU hardware managers.

Important APIs/types: forward declares core powerplay types, defines generic watermark row/table structures consumed by SOC15 watermark programming, declares voltage conversion, PPT array copy, register wait, power-gating preference, voltage table, DPM table, EVV, IRQ, AtomBIOS, dependency table, and watermark helper functions. Provides `phm_get_sysfs_buf()` to align a sysfs buffer pointer to the current page while returning the original page offset.

Control flow and integration: the macro section centralizes bitfield read/write/wait patterns. `PHM_SET_FIELD()` and `PHM_GET_FIELD()` operate on generated register masks/shifts. `PHM_READ_FIELD`, `PHM_READ_INDIRECT_FIELD`, and `PHM_READ_VFPF_INDIRECT_FIELD` select direct, indirect, or VFPF indirect CGS access. Write macros perform read-modify-write. Wait macros map register/field names to polling helpers, including unequal waits.

State and persistence: no storage is defined except stack-level helper types. The macros mutate hardware registers through CGS accessors and the function declarations expose helpers that may allocate or mutate caller-owned tables.

Dependencies: relies on generated AMD register naming conventions (`mmREG`, `ixREG`, `REG__FIELD_MASK`, `REG__FIELD__SHIFT`), CGS register APIs, Linux page-offset helper, and types from hwmgr/AtomBIOS/PPT/DAL included by users.

Risks: macros evaluate arguments in hardware access expressions, so callers should avoid side-effect arguments. Read-modify-write macros are not synchronized by themselves and require callers to hold appropriate locks. The VFPF indirect macros use `mmPORT_INDEX_11`, which is hardware-specific. The header declares `phm_cf_want_microcode_fan_ctrl()` but no implementation appears in the paired C file in this subset, so linkage depends on another file or dead code elimination.

Test signals: compile coverage across all hwmgr users, register-field macro spot checks against generated masks/shifts, sysfs buffer alignment tests for clock-level emitters, and runtime waits on direct/indirect/VFPF registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c

Purpose: implements BACO state transitions for Tonga/Iceland-family SMU7-era ASICs using command-table-driven hardware register sequences.

Important APIs and functions: the exported function is `tonga_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`. Static command tables describe the entry/exit programming sequence: GPIO isolation, framebuffer request rejection, switching to BCLK, turning off SPLL/MPLL and memory clocks, entering BACO through `BACO_CNTL`, exiting BACO, and cleaning BIOS scratch registers. Iceland/Topaz has reduced GPIO and different exit/clean tables.

Control flow: `tonga_baco_set_state()` first calls `smu7_baco_get_state()` and returns success if the target state is already active. For `BACO_STATE_IN`, it programs chip-specific GPIO setup, enables FB request rejection, switches clocks to BCLK, turns off PLLs, then executes `enter_baco_tbl`; a nonzero table execution result returns success, matching the existing common BACO helper convention. For `BACO_STATE_OUT`, it waits 20 ms to satisfy regulator off/on timing, then executes the chip-specific exit table and, if successful, clean table. Unsupported or failed transitions return `-EINVAL`.

State and persistence: no driver-side state is stored. BACO state is entirely in hardware registers, including `BACO_CNTL`, PLL/memory/display GPIO registers, and BIOS scratch registers. Entry powers down major clock and memory paths; exit restores power/isolation state through the scripted sequence.

Dependencies and integration: depends on `amdgpu.h`, `tonga_baco.h`, generated GMC/BIF/DCE/SMU register definitions and masks, `common_baco` command types, `baco_program_registers()`, and `smu7_baco_get_state()`.

Risks: table ordering and wait masks are hardware-critical; reordering can strand the GPU in BACO or fail resume. The return convention is non-obvious because successful command-table execution appears to be tested as nonzero in this code path. `BACO_CNTL__PWRGOOD_MASK` is defined by adding masks rather than bitwise OR, which works only if masks do not overlap. Hardware timing relies on a fixed 20 ms sleep before exit.

Test signals: BACO enter/exit on Tonga and Topaz/Iceland, repeated idempotent set-state calls, suspend/resume and runtime power-management cycles, framebuffer request handling during entry, PLL/memory restoration after exit, and command-table failure-path logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c -->
