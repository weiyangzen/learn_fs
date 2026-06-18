# Research: subset-b-003513

Grouped research for AMDGPU legacy DPM Kaveri/Kabini support and shared legacy DPM interfaces. Each section preserves the exact source path in its title and is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c

## Purpose

`kv_dpm.c` implements the AMDGPU legacy Dynamic Power Management block for Kaveri/Kabini/Mullins era APU SMU hardware. It registers the `kv_smu_ip_block` SMC IP block, exposes `amd_pm_funcs` callbacks to the legacy PowerPlay layer, parses ATOM BIOS power tables, builds SMU7 fusion DPM tables, uploads those tables into SMC SRAM, controls SCLK/NB/UVD/VCE/SAMU/ACP DPM, handles thermal interrupts, and reports basic clocks/temperature through the PM sensor callbacks.

## Important APIs, Types, and Functions

The externally visible object is `const struct amdgpu_ip_block_version kv_smu_ip_block`, whose `amd_ip_funcs` point at `kv_dpm_early_init`, `kv_dpm_sw_init`, `kv_dpm_hw_init`, suspend/resume, and fini paths. `kv_dpm_early_init()` installs `kv_dpm_funcs` in `adev->powerplay.pp_funcs`, sets `pp_handle` to `adev`, and assigns thermal IRQ functions.

Core initialization is in `kv_dpm_init()`: it allocates `struct kv_power_info`, parses platform caps and extended PowerPlay tables through `legacy_dpm.c`, seeds defaults and capability flags, parses integrated system info, patches voltage units, constructs the boot power level, parses PPLIB states, and enables DPM. `kv_dpm_enable()` reads SMU firmware header offsets, initializes graphics/multimedia levels, uploads `SMU7_Fusion_DpmTable` fields, enables activity monitor/DPM/ULV/DIDT/CAC/BAPM state, and arms thermal interrupts when the internal Kaveri thermal controller is present.

Runtime callbacks include `kv_dpm_pre_set_power_state()`, `kv_dpm_set_power_state()`, `kv_dpm_post_set_power_state()`, `kv_dpm_force_performance_level()`, `kv_set_powergating_by_smu()`, `kv_check_state_equal()`, `kv_dpm_read_sensor()`, and debug print helpers. Local helpers cover VID conversion, ATOM clock divider lookup, deep-sleep divider calculation, DFS bypass, NB P-state settings, SCLK enable masks, VCE/UVD/SAMU/ACP boot levels, and SMU messages.

## Control Flow

Driver bring-up starts with `kv_dpm_sw_init()`, which registers legacy thermal IRQ IDs 230 and 231, initializes default DPM state to balanced/auto, and if `amdgpu_dpm` is enabled calls `kv_dpm_init()`. Hardware bring-up then enters `kv_dpm_hw_init()`: under `adev->pm.mutex` it calls `kv_dpm_setup_asic()`, `kv_dpm_enable()`, sets `adev->pm.dpm_enabled`, and invokes `amdgpu_legacy_dpm_compute_clocks()` to select and apply the initial state.

Power-state changes are driven by `legacy_dpm.c`. That layer chooses `adev->pm.dpm.requested_ps`, then calls this file's pre/set/post callbacks. The pre callback copies the requested `amdgpu_ps` and its `kv_ps` private state into persistent `kv_power_info` storage, then applies display, VCE, battery, stable-P-state, high-voltage, and NB policy adjustments. The set callback updates BAPM, computes valid SCLK ranges, recalculates deep-sleep and NB settings, freezes or forces SCLK as needed depending on ASIC type, uploads the edited SMU DPM table, programs NB indices, updates VCE/ACP/SCLK thresholds, enables NB DPM, and restores automatic levels. The post callback makes the requested state current.

Multimedia power gating flows through `kv_set_powergating_by_smu()` for UVD/VCE and through late init/disable for SAMU/ACP. UVD and VCE paths coordinate IP block gating with SMU power on/off messages and corresponding DPM enable/disable messages. ACP gating is skipped on Kabini/Mullins.

Thermal flow is interrupt-driven. `kv_set_thermal_temperature_range()` programs low/high thresholds in `ixCG_THERMAL_INT_CTRL`. `kv_dpm_process_interrupt()` maps source IDs 230/231 to direction flags and schedules `amdgpu_dpm_thermal_work_handler()`, which lives in `legacy_dpm.c` and may force an internal thermal power state.

## State and Persistence Behavior

Software state is stored primarily in `adev->pm.dpm` and `struct kv_power_info` at `adev->pm.dpm.priv`. `kv_power_info` caches BIOS-derived system info, dynamic capabilities, boot/current/requested power states, SCLK/NB/DPM level counts, generated SMU table entries, power-gating booleans, and thermal/DPM thresholds. Many fields are copied into SMU SRAM with `amdgpu_kv_copy_bytes_to_smc()` and then become firmware-owned runtime state until reset, suspend, disable, or another upload.

Persistent hardware state includes SMC SRAM DPM tables, SMC soft registers, SMC/DIDT/MMIO registers, thermal interrupt masks, and SMU-managed block power state. Suspend cancels thermal work, disables DPM, resets current/requested pointers to the boot state, and clears `dpm_enabled`; resume rebuilds ASIC state and reapplies clocks. Fini frees PPLIB private states, the power-info object, and extended PowerPlay allocations.

## Dependencies and Integration Points

This file depends on AMDGPU device, IRQ, PM, ATOM BIOS, and display infrastructure; CIK/KV register headers; SMU7 fusion table definitions from `smu7_fusion.h`; SMC message IDs from `ppsmc.h`; and helper declarations from `kv_dpm.h` and `legacy_dpm.h`. It uses `RREG32`, `WREG32`, `RREG32_SMC`, `WREG32_SMC`, `RREG32_DIDT`, `WREG32_DIDT`, ATOM `GetIndexIntoMasterTable`, `amdgpu_atombios_get_clock_dividers()`, `amdgpu_device_ip_set_powergating_state()`, `amdgpu_irq_add_id/get/put()`, and `amdgpu_gfx_rlc_enter_safe_mode()`.

Integration with the rest of AMDGPU is through the IP block list, `adev->powerplay.pp_funcs`, PM mutex, DPM state machine in `legacy_dpm.c`, UVD/VCE power-gating callbacks, debugfs PM printing, and sensor reads for `AMDGPU_PP_SENSOR_GFX_SCLK` and `AMDGPU_PP_SENSOR_GPU_TEMP`.

## Risks and Edge Cases

The code trusts many BIOS table offsets and counts. Bad ATOM data can lead to missing boot states, empty dependency tables, or out-of-range level assumptions. Several loops index arrays sized for SMU7 maximum levels, while inputs come from BIOS table counts, so count validation is critical. SMU SRAM writes require correct endianness and bounds; a wrong `dpm_table_start` or `sram_end` can corrupt firmware memory. Runtime paths ignore some SMU message return values, especially in power-gating helpers, so partial failures may leave software booleans out of sync with hardware. Thermal register programming uses fixed `KV_TEMP_RANGE_MIN/MAX` and direct SMC register fields. DIDT support is compiled in but disabled by `pi->enable_didt = false`, so enabling it later would need hardware validation.

Kabini/Mullins take a different SCLK forcing path than other Kaveri parts; regressions in this branch can show up only on those ASICs. ACP gating deliberately returns on Kabini/Mullins. `kv_get_acp_boot_level()` always returns zero, which may be too simple for future ACP tables.

## Test Signals

Useful signals are a kernel build with legacy DPM enabled, boot logs showing `dpm initialized`, successful SMU messages during `kv_dpm_hw_init()`, populated `/sys/kernel/debug/dri/*/amdgpu_pm_info` or equivalent debugfs output, and sensor reads returning current SCLK and millidegree temperature. Runtime testing should cover AC/DC state changes, forced low/high/auto performance levels, suspend/resume, thermal IRQ handling, UVD/VCE playback power-gating, SAMU/ACP late powerdown, multi-display transitions, and Kabini/Mullins-specific NB DPM behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.h

## Purpose

`kv_dpm.h` is the private interface and state definition header for the Kaveri/Kabini legacy DPM implementation. It defines the per-ASIC DPM table dimensions, BIOS mapping tables, Kaveri power-level structures, SMU table caches, capability flags, and prototypes exported by `kv_smc.c` for SMC messaging and SRAM access.

## Important APIs, Types, and Macros

Key limits include `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, `SUMO_MAX_HARDWARE_POWERLEVELS`, `SUMO_MAX_NUMBER_VOLTAGES`, and `KV_NUM_NBPSTATES`. `KV_TEMP_RANGE_MIN` and `KV_TEMP_RANGE_MAX` provide the thermal interrupt range used by `kv_dpm.c`.

Important structs are `sumo_vid_mapping_table`, `sumo_sclk_voltage_mapping_table`, `kv_pt_config_reg`, `kv_lcac_config_values`, `kv_lcac_config_reg`, `kv_pl`, `kv_ps`, `kv_sys_info`, and `kv_power_info`. `kv_pl` represents one graphics power level. `kv_ps` is the Kaveri private payload attached to each generic `struct amdgpu_ps`. `kv_power_info` is the main runtime state object allocated as `adev->pm.dpm.priv`; it contains BIOS-derived system info, generated `SMU7_Fusion_*` tables, boot/current/requested power states, feature flags, power-gating state, and SMU SRAM offsets.

The declared SMC helpers are `amdgpu_kv_notify_message_to_smu()`, `amdgpu_kv_dpm_get_enable_mask()`, `amdgpu_kv_send_msg_to_smc_with_parameter()`, `amdgpu_kv_read_smc_sram_dword()`, `amdgpu_kv_smc_dpm_enable()`, `amdgpu_kv_smc_bapm_enable()`, and `amdgpu_kv_copy_bytes_to_smc()`.

## Control Flow

The header does not implement control flow, but it defines the data contracts used by the flow in `kv_dpm.c`. Init allocates `kv_power_info`, parses BIOS data into `kv_sys_info` and dynamic dependency tables, constructs `kv_ps` instances for each PPLIB state, fills `SMU7_Fusion_GraphicsLevel` and multimedia level arrays, and passes the generated bytes to `kv_smc.c` for SRAM upload. Runtime power-state callbacks edit the `requested_ps` and generated level arrays, then send SMC messages listed in `ppsmc.h`.

## State and Persistence Behavior

All structs are in-memory kernel state except for the `SMU7_Fusion_*` arrays and scalar table fields that are copied into SMU SRAM. `current_rps/current_ps` and `requested_rps/requested_ps` are value copies used so callbacks can mutate private Kaveri state without changing the original BIOS-parsed `adev->pm.dpm.ps` entries. Power-gating booleans mirror SMU/IP block state and must be kept synchronized with message success.

## Dependencies and Integration Points

The header includes `smu7_fusion.h` for firmware table layout and `ppsmc.h` for SMC message types. It assumes AMDGPU core types such as `struct amdgpu_device`, `struct amdgpu_ps`, and integer aliases are visible from including C files. It is included by `kv_dpm.c` and `kv_smc.c`.

## Risks and Edge Cases

Array sizes are hardware contracts. Changing limits or struct fields can break SMU table layout, ABI with firmware, or loops in `kv_dpm.c`. `SMU__NUM_PCIE_DPM_LEVELS` is explicitly `0 /* ??? */`, signaling that PCIe DPM is not modeled here. Several booleans distinguish caps from current enable state; confusing them can send unsupported SMU messages. Temperature range comments and constants are marked uncertain.

## Test Signals

Compile coverage of `kv_dpm.c` and `kv_smc.c` catches type/layout/prototype breakage. Runtime signals include successful allocation/free of `kv_power_info`, correct PPLIB state printing, valid SMU table uploads, sensor reads, and no crashes in suspend/resume or power-gating paths that dereference `adev->pm.dpm.priv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_smc.c

## Purpose

`kv_smc.c` provides the low-level SMC communication helpers used by Kaveri/Kabini legacy DPM. It sends messages to the SMU, passes one message argument, reads SMC SRAM dwords, enables/disables DPM and BAPM, and copies arbitrary byte ranges into SMC SRAM while preserving unaligned leading/trailing bytes.

## Important APIs and Functions

`amdgpu_kv_notify_message_to_smu()` writes a message ID to `mmSMC_MESSAGE_0`, polls `mmSMC_RESP_0` up to `adev->usec_timeout`, and treats response values `0xff` and `0xfe` as invalid. `amdgpu_kv_send_msg_to_smc_with_parameter()` writes `mmSMC_MSG_ARG_0` before calling the notify helper. `amdgpu_kv_dpm_get_enable_mask()` sends `PPSMC_MSG_SCLKDPM_GetEnabledMask` and reads `ixSMC_SYSCON_MSG_ARG_0`.

`kv_set_smc_sram_address()` validates 4-byte alignment and upper bound, writes `mmSMC_IND_INDEX_0`, and disables auto-increment through `mmSMC_IND_ACCESS_CNTL`. `amdgpu_kv_read_smc_sram_dword()` uses that address setup and reads `mmSMC_IND_DATA_0`. `amdgpu_kv_copy_bytes_to_smc()` handles bounded byte copies into the big-endian SMC address space, using read-modify-write for unaligned first and final dwords. `amdgpu_kv_smc_dpm_enable()` and `amdgpu_kv_smc_bapm_enable()` wrap DPM and BAPM enable/disable messages.

## Control Flow

Higher-level DPM code first calls `amdgpu_kv_read_smc_sram_dword()` to discover firmware DPM table offsets, then repeatedly calls `amdgpu_kv_copy_bytes_to_smc()` to upload generated table fields. Runtime changes use `amdgpu_kv_send_msg_to_smc_with_parameter()` for enabled masks and forced levels, while feature toggles use the direct message wrappers.

## State and Persistence Behavior

This file maintains no software state of its own. Its effects persist in hardware mailboxes, SMC SRAM, and SMU firmware state. SRAM writes remain active until overwritten or the SMU/device resets. Message responses are transient and must be interpreted immediately by callers.

## Dependencies and Integration Points

The file includes `amdgpu.h`, `cikd.h`, `kv_dpm.h`, and SMU 7.0 register headers. It depends on AMDGPU MMIO macros `RREG32`, `WREG32`, `RREG32_SMC`, and `WREG32_P`, plus SMC message IDs from `ppsmc.h`. Its functions are declared in `kv_dpm.h` and used throughout `kv_dpm.c`.

## Risks and Edge Cases

The notify helper returns success for any nonzero response other than `0xff` or `0xfe`; if firmware uses additional failure codes, callers may miss them. Timeout leaves `tmp == 0` but still returns success, which is a notable risk. SRAM address setup rejects unaligned reads but byte-copy supports unaligned writes through RMW. The big-endian packing must match firmware layout; mistakes silently corrupt DPM tables. `smc_start_address + byte_count` can overflow if ever called with hostile values, though current callers use small trusted table offsets.

## Test Signals

Validation should include SMU message success during DPM enable/disable, correct SCLK enable-mask reads, firmware table upload without `-EINVAL`, suspend/resume re-upload, and hardware behavior after unaligned writes such as single-byte boot-level fields. Instrumenting SMC response codes is useful when diagnosing failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.c

## Purpose

`legacy_dpm.c` implements shared infrastructure for AMDGPU legacy PowerPlay/DPM ASICs. It parses ATOM PowerPlay tables into `adev->pm.dpm` dynamic state, registers thermal controller information, prints/debugs power states, chooses requested power states from user/internal conditions, coordinates pre/set/post DPM callbacks, computes clocks, and handles thermal workqueue transitions.

## Important APIs and Functions

Debug helpers are `amdgpu_dpm_dbg_print_class_info()`, `amdgpu_dpm_dbg_print_cap_info()`, `amdgpu_dpm_dbg_print_ps_status()`, and `amdgpu_pm_print_power_states()`. BIOS parsing APIs are `amdgpu_get_platform_caps()`, `amdgpu_parse_extended_power_table()`, and `amdgpu_free_extended_power_table()`. `amdgpu_add_thermal_controller()` parses the PPLIB thermal controller record, configures internal thermal type or creates an external I2C client. `amdgpu_get_vce_clock_state()` returns a parsed VCE state by index.

The runtime state machine is centered on `amdgpu_dpm_pick_power_state()`, `amdgpu_dpm_change_power_state_locked()`, `amdgpu_legacy_dpm_compute_clocks()`, and `amdgpu_dpm_thermal_work_handler()`.

## Control Flow

ASIC-specific DPM init calls the parsing helpers to fill `adev->pm.dpm.platform_caps`, response times, fan parameters, dependency tables, CAC/leakage data, VCE/UVD/SAMU/ACP dependency tables, PPM and PowerTune data, and VDDGFX-on-SCLK data when present. Each allocation is later released by `amdgpu_free_extended_power_table()`.

When clocks need recomputing, `amdgpu_legacy_dpm_compute_clocks()` updates display configuration if DC is disabled, then calls `amdgpu_dpm_change_power_state_locked()`. That function rejects work if DPM is disabled, reconciles user state with active thermal/UVD overrides, chooses a matching power state, prints transitions when verbose DPM is enabled, sets VCE active flags, calls ASIC-specific display/pre callbacks, optionally skips if current/requested states compare equal, calls ASIC-specific `set_power_state`, then post callback, then reapplies forced performance level or thermal low forcing.

Thermal interrupts schedule `amdgpu_dpm_thermal_work_handler()`. The work item reads GPU temperature through the ASIC `read_sensor` callback when possible, chooses internal thermal state or user state, updates `thermal_active` and `adev->pm.dpm.state`, and recomputes clocks under `adev->pm.mutex`.

## State and Persistence Behavior

This file populates persistent driver state under `adev->pm.dpm`, including platform caps, fan info, dynamic dependency tables, VCE states, thermal type, current/requested/boot power-state pointers, and thermal active flags. It allocates heap arrays for variable-length BIOS tables and owns their cleanup. It does not directly program SMU DPM tables; instead it calls ASIC-specific callbacks through `adev->powerplay.pp_funcs`.

External I2C thermal controller registration creates kernel I2C device state. Power-state changes persist in the ASIC-specific hardware only after the selected PM callbacks run.

## Dependencies and Integration Points

The file depends on `amdgpu.h`, ATOM BIOS definitions, `amdgpu_i2c`, `amd_pcie`, `amdgpu_display`, `amdgpu_dpm_internal`, and the legacy DPM header. Its macro wrappers call `adev->powerplay.pp_funcs` entries installed by ASIC files such as `kv_dpm.c`. It integrates with display configuration, PM mutex locking, I2C thermal drivers, VCE state users, and debug logging.

## Risks and Edge Cases

ATOM parsing uses many raw offsets into the BIOS image. Incorrect table sizes, revisions, or offsets can cause invalid reads or partial dynamic state. Several allocations happen sequentially; callers must use the free helper on failures to avoid leaks. `amdgpu_dpm_pick_power_state()` has layered fallbacks, so missing specialized UVD/thermal/ACPI states may silently degrade to performance or battery. The equality fast path returns before post callbacks and forced-level reapply, so ASIC `check_state_equal` semantics must be conservative. Thermal work relies on `read_sensor`; if unavailable, it falls back to interrupt direction.

## Test Signals

Test signals include successful parsing of fan/dependency/VCE/UVD/SAMU/ACP tables from real VBIOS images, no memory leaks on init failure and fini, correct `/sys` or debugfs power-state listing, user state changes mapping to expected PPLIB classes, UVD/VCE state selection during media workloads, external thermal I2C device creation when present, and thermal interrupt work switching into and out of thermal states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.h

## Purpose

`legacy_dpm.h` declares the shared helper API implemented by `legacy_dpm.c` for older AMDGPU DPM backends. It lets ASIC-specific files parse common ATOM PowerPlay data, print/debug power states, register thermal controllers, retrieve VCE states, compute clocks, and use the common thermal work handler.

## Important APIs

The declarations are `amdgpu_dpm_dbg_print_class_info()`, `amdgpu_dpm_dbg_print_cap_info()`, `amdgpu_dpm_dbg_print_ps_status()`, `amdgpu_get_platform_caps()`, `amdgpu_parse_extended_power_table()`, `amdgpu_free_extended_power_table()`, `amdgpu_add_thermal_controller()`, `amdgpu_get_vce_clock_state()`, `amdgpu_pm_print_power_states()`, `amdgpu_legacy_dpm_compute_clocks()`, and `amdgpu_dpm_thermal_work_handler()`.

## Control Flow

There is no implementation in this header. ASIC DPM modules include it during initialization and callback registration. A typical flow is: parse platform caps, parse extended power table, parse ASIC-specific state tables, install `amdgpu_legacy_dpm_compute_clocks` as the PM compute callback, and initialize thermal work with `amdgpu_dpm_thermal_work_handler`.

## State and Persistence Behavior

The functions declared here operate on `struct amdgpu_device`, especially `adev->pm.dpm` and `adev->powerplay.pp_funcs`. Memory ownership for extended table allocations is paired: parse allocates, free releases. Thermal work persists as a `work_struct` embedded in `adev->pm.dpm.thermal`.

## Dependencies and Integration Points

The header assumes AMDGPU core types, `u32`, and `struct work_struct` are visible to including translation units. It is used by `kv_dpm.c` and other legacy ASIC DPM files to share common DPM policy and BIOS parsing.

## Risks and Edge Cases

Because this header exposes un-namespaced legacy helpers, prototype changes affect multiple ASIC backends. The parse/free pairing is not enforced by the type system. The returned `struct amd_vce_state *` points into `adev->pm.dpm` storage and is valid only while that DPM state remains allocated.

## Test Signals

Compile coverage across all legacy DPM ASICs is the primary signal. Runtime signals include successful init/fini without leaks, power-state debug output, clock recomputation through the shared callback, and thermal work executing after ASIC IRQ handlers schedule it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/ppsmc.h

## Purpose

`ppsmc.h` defines legacy PowerPlay SMC firmware constants shared by several AMD DPM generations. It contains software-state flags, thermal/system flags, fan-control modes, SMC result codes, and many SMC message IDs used to command firmware features such as DPM, CAC, BAPM, ULV, UVD/VCE/SAMU/ACP power, clock masks, PCIe/NB DPM, thermal DPM, and ucode loading.

## Important APIs, Types, and Macros

The file is macro-heavy. It defines `PPSMC_Result_OK`, `PPSMC_Result_Failed`, `typedef uint8_t PPSMC_Result`, and `typedef uint16_t PPSMC_Msg`. `enum FAN_CONTROL` declares `FAN_CONTROL_FUZZY` and `FAN_CONTROL_TABLE`. Message IDs include early 8-bit commands like `PPSMC_MSG_Halt`, `PPSMC_MSG_SwitchToSwState`, `PPSMC_MSG_EnableCac`, `PPSMC_MSG_EnableULV`, `PPSMC_MSG_SetEnabledLevels`, and CI/KV/KB 16-bit commands like `PPSMC_MSG_DPM_Enable`, `PPSMC_MSG_SCLKDPM_SetEnabledMask`, `PPSMC_MSG_SCLKDPM_GetEnabledMask`, `PPSMC_MSG_UVDDPM_Enable`, `PPSMC_MSG_VCEDPM_Enable`, `PPSMC_MSG_NBDPM_Enable`, `PPSMC_MSG_EnableBAPM`, and block power on/off commands. Later message IDs cover driver/SMU DRAM addresses and ucode loading.

## Control Flow

There is no direct control flow. Callers pass these constants to ASIC-specific mailbox helpers. In this subset, `kv_smc.c` writes the IDs to SMC message registers and `kv_dpm.c` selects messages according to DPM enable, BAPM enable, SCLK masks, forced levels, UVD/VCE/SAMU/ACP gating, ULV, CAC, and NB DPM state.

## State and Persistence Behavior

The header has no runtime state. The constants map to firmware commands that mutate SMU state, power state, DPM masks, firmware loading state, and block power status. Effects persist in SMU firmware and hardware until later messages or reset.

## Dependencies and Integration Points

The file uses `#pragma pack(push, 1)`/`pop`, fixed-width integer types, and no other includes. It is included by legacy SMC/DPM headers such as `kv_dpm.h` and `sislands_smc.h`. It is part of the firmware ABI between the kernel driver and legacy SMU firmware.

## Risks and Edge Cases

Message IDs are hardware/firmware contracts; changing values breaks runtime control. Some macros are duplicated, such as `PPSMC_MSG_PCIeDPM_Disable`, and message widths vary between `uint8_t`, `uint16_t`, and `uint32_t` casts while `PPSMC_Msg` is `uint16_t`. Callers must use the right generation-specific command. Unsupported messages may return firmware failure codes or no response, depending on ASIC firmware.

## Test Signals

Build coverage catches missing names. Runtime validation includes successful SMC responses for DPM enable/disable, CAC/BAPM toggles, SCLK enabled masks, UVD/VCE/SAMU/ACP power messages, and suspend/resume. Firmware tracing or mailbox debug logs are useful when a specific message returns `0xfe`, `0xff`, or times out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/r600_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/r600_dpm.h

## Purpose

`r600_dpm.h` defines legacy R600-family DPM constants and small enums used by older AMD power-management code. It captures default timing, ramping, voltage-response, PLL, thermal, fan, and table-size parameters that are shared by R600-style DPM implementations.

## Important APIs, Types, and Macros

The header provides default constants such as `R600_ASI_DFLT`, `R600_BSP_DFLT`, `R600_VOLTAGERESPONSETIME_DFLT`, `R600_SPLLSTEPTIME_DFLT`, `R600_MPLLLOCKTIME_DFLT`, and many up/down threshold defaults. Table dimensions include `R600_PM_NUMBER_OF_TC`, `R600_PM_NUMBER_OF_SCLKS`, `R600_PM_NUMBER_OF_MCLKS`, `R600_PM_NUMBER_OF_VOLTAGE_LEVELS`, and `R600_PM_NUMBER_OF_ACTIVITY_LEVELS`. Thermal bounds are `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX`. Fan mode macros are `FDO_PWM_MODE_STATIC` and `FDO_PWM_MODE_STATIC_RPM`.

Enums define `r600_power_level` values low/medium/high/context-switch, `r600_td` direction values auto/up/down, `r600_display_watermark` low/high, and `r600_display_gap` behavior for vblank/watermark/ignore.

## Control Flow

The header has no executable logic. R600-era DPM source files use these constants while constructing hardware performance levels, voltage timing tables, thermal thresholds, fan behavior, and display watermark/gap decisions.

## State and Persistence Behavior

There is no state in this header. Values become runtime state only when copied into ASIC-specific power-info structs or programmed into hardware/SMC registers by including source files.

## Dependencies and Integration Points

The file is standalone apart from kernel integer conventions in users. It belongs to the same `legacy-dpm` folder as newer KV support but targets older R600-style code. It provides common vocabulary for display watermark and power-level decisions that later families kept in similar form.

## Risks and Edge Cases

Many constants are magic hardware tuning values; changing them can affect stability, voltage ramp timing, fan behavior, or display underrun margins. The thermal range has the same uncertain comment as KV. Consumers must know whether values are raw register units, microseconds, milliseconds, or millidegrees.

## Test Signals

Compile coverage of R600 legacy DPM users catches enum and macro dependency issues. Runtime tests should watch boot DPM initialization, thermal interrupt thresholds, fan mode programming, display watermark transitions, suspend/resume, and stable clock/voltage switching under low/medium/high forced levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/r600_dpm.h -->
