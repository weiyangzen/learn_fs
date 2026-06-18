# Research: subset-b-003516

This grouped report covers AMDGPU legacy DPM, Southern Islands SMC, and PowerPlay hardware manager files. Each section is bounded for deterministic splitting into the source-tree-aligned per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.h

## Purpose
`si_dpm.h` is the Southern Islands legacy DPM state header. It defines register addresses, default timing and power-tune constants, SMC SRAM table offsets, PCIe generation enums, and the host-side state structures used by SI power management code to build SMC state tables, memory-controller timing tables, voltage tables, ULV state, fan state, CAC/powertune data, and DTE thermal estimation data.

## Important APIs, Types, And State
The exported symbol is `si_smu_ip_block`, while the header mainly contributes data contracts: `rv7xx_power_info`, `evergreen_power_info`, `ni_power_info`, and `si_power_info` are intentionally nested with "must be first" layout comments so older-generation helpers can cast through common prefixes. `rv7xx_pl` and `si_ps` model software performance levels. `si_clock_registers`, `si_mc_reg_table`, `si_ulv_param`, `si_powertune_data`, `si_dyn_powertune_data`, and `si_dte_data` hold derived BIOS, firmware, and runtime tuning values.

## Control Flow And Integration
The file has no executable flow, but it drives flow in SI DPM implementation code: boot and ACPI state slots, driver-state slots, SMC table offsets, and scratch copies of `SISLANDS_SMC_STATETABLE`, `SMC_SIslands_MCRegisters`, and `PP_SIslands_PAPMParameters` are filled on the host and written to SMC SRAM through the `sislands_smc.h` interface. It depends on `amdgpu_atombios.h` for voltage table types and on packed SMC ABI definitions from `sislands_smc.h`.

## Risks And Test Signals
The main risks are ABI drift and unit mistakes: table sizes, array counts, register offsets, and temperature/clock units must match firmware expectations. The nested struct-prefix pattern is fragile if fields are reordered. Test signals are successful SI DPM initialization, correct SMC table uploads, suspend/resume without DPM hangs, PCIe generation transitions, fan and thermal sysfs readings, and absence of SMC message failures or memory timing instability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_smc.c

## Purpose
`si_smc.c` implements low-level Southern Islands SMC access helpers for the legacy DPM path. It controls SMC reset/clock state, loads SMC firmware from `adev->pm.fw`, copies arbitrary byte ranges into SMC SRAM, sends firmware messages, and reads/writes SMC SRAM dwords through indirect MMIO registers.

## Important APIs And Control Flow
`si_set_smc_sram_address()` validates 4-byte alignment and address limit, programs `mmSMC_IND_INDEX_0`, and disables auto-increment. `amdgpu_si_copy_bytes_to_smc()` serializes access with `adev->reg.smc.lock`, writes big-endian SMC words, and handles trailing bytes by read-modify-write. `amdgpu_si_load_smc_ucode()` parses `smc_firmware_header_v1_0`, records firmware version, enables auto-increment, and streams aligned firmware words. `amdgpu_si_send_msg_to_smc()` verifies the SMC is running, writes `mmSMC_MESSAGE_0`, polls `mmSMC_RESP_0`, and uses longer timeouts for slow power-state messages.

## State, Persistence, And Dependencies
Persistent effects are entirely hardware and device state: SMC SRAM contents, reset and clock bits, firmware version in `adev->pm.fw_version`, and message/response registers. The code depends on `amdgpu.h`, `sid.h`, `ppsmc.h`, `amdgpu_ucode.h`, `sislands_smc.h`, and generated SMU/GFX register definitions. All SRAM access is protected by the SMC spinlock; reset and clock helpers perform direct register writes without additional policy checks.

## Risks And Test Signals
Risks include wrong SMC SRAM limits, endian conversion mistakes, trailing-byte corruption, timeouts hidden by unconditional `PPSMC_Result_OK` in `amdgpu_si_wait_for_smc_inactive()`, and firmware header size/address mismatch. Test signals are clean firmware load logs, no timeout warnings from `amdgpu_si_send_msg_to_smc()`, successful DPM enable, and stable suspend/resume and power-state switching on SI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/sislands_smc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/sislands_smc.h

## Purpose
`sislands_smc.h` defines the packed host/firmware ABI for Southern Islands SMC power management. It describes SMC performance levels, software states, voltage masks, fan control tables, CAC/powertune configuration, memory-controller register tables, SPLL divider tables, DTE thermal-estimation configuration, firmware-header offsets, and the SI SMC helper function prototypes implemented in `si_smc.c`.

## Important APIs, Types, And State
The `#pragma pack(push, 1)` block is essential: structures such as `SISLANDS_SMC_HW_PERFORMANCE_LEVEL`, `SISLANDS_SMC_STATETABLE`, `PP_SIslands_CacConfig`, `SMC_SIslands_MCRegisters`, `SMC_SISLANDS_SPLL_DIV_TABLE`, and `Smc_SIslands_DTE_Configuration` must be byte-exact for firmware SRAM consumption. Constants such as `SI_SMC_SOFT_REGISTER_*` and `SISLANDS_SMC_FIRMWARE_HEADER_*` are offsets into SMC soft-register and firmware metadata areas. The function declarations expose byte copy, SRAM dword access, firmware loading, SMC start/reset/clock, and SMC message operations.

## Control Flow And Integration
This header is consumed by SI DPM state construction and SMC upload code. Host code fills the packed tables, converts values as needed for the SMC address space, discovers firmware table addresses through the firmware-header offsets, and writes data through `amdgpu_si_copy_bytes_to_smc()` or dword helpers. It depends on `ppsmc.h` for message and result enums.

## Risks And Test Signals
ABI mismatch is the dominant risk: packing, array dimensions, field order, and offset constants are firmware contracts. Flexible-array state definitions require allocation discipline. Test signals include correct SMC firmware boot, valid fan and CAC behavior, successful DPM level transitions, no SRAM-bound errors from SI SMC helpers, and no thermal or memory-clock instability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/sislands_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/Makefile

## Purpose
This Makefile integrates the legacy PowerPlay implementation into the AMD PM build. It defines the local path, includes subcomponent makefiles for `smumgr` and `hwmgr`, and adds `amd_powerplay.o` to the aggregate `AMD_POWERPLAY_FILES` object list.

## Important Build Flow
`AMD_PP_PATH = ../pm/powerplay` establishes object paths relative to the AMD driver build. `PP_LIBS = smumgr hwmgr` is expanded into per-subdirectory Makefile paths under `$(FULL_AMD_PATH)/pm/powerplay/`, then included. `POWER_MGR-y = amd_powerplay.o` identifies the top-level PowerPlay adapter object, and `AMD_PP_POWER` prefixes it with `$(AMD_PP_PATH)` before appending to `AMD_POWERPLAY_FILES`.

## State, Dependencies, And Integration
The file has no runtime state; its persistence is build-system state in make variables. It depends on parent makefiles defining `FULL_AMD_PATH` and collecting `AMD_POWERPLAY_FILES`. It is the bridge that ensures PowerPlay core, SMU manager, and hardware manager objects are linked into the amdgpu PM component.

## Risks And Test Signals
Risks are path or aggregate-variable drift, missing subdirectory inclusion, and accidental omission of `amd_powerplay.o`. Test signals are successful kernel object builds with PowerPlay enabled, visible compilation of `amd_powerplay.c`, and link resolution for hwmgr/smumgr symbols referenced by the PowerPlay adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/amd_powerplay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/amd_powerplay.c

## Purpose
`amd_powerplay.c` is the top-level legacy PowerPlay adapter. It creates and destroys `pp_hwmgr`, registers the `powerplay` SMC IP block, implements the `amd_pm_funcs` callback surface used by the amdgpu core and display code, and delegates most behavior to ASIC-specific `hwmgr_func`, `pptable_func`, and `smumgr_funcs` tables.

## Important APIs And Control Flow
Lifecycle flow is `pp_early_init()` -> `amd_powerplay_create()` -> `hwmgr_early_init()`, then `pp_sw_init()` -> `hwmgr_sw_init()`, `pp_hw_init()` -> `hwmgr_hw_init()`, `pp_late_init()` task completion and optional SMU private buffer reservation. Fini/suspend/resume route through corresponding hwmgr calls and cancel the software critical-temperature delayed work. `pp_dpm_funcs` exposes firmware loading, forced performance levels, fan controls, pp_table get/set, manual clock forcing, OD controls, sensor reads, display clock/voltage requests, power gating, BACO, feature masks, reset, SMU I2C, metrics, and compute-clock recomputation.

## State, Persistence, And Dependencies
The file owns `adev->powerplay.pp_handle`, `adev->powerplay.pp_funcs`, `hwmgr->hardcode_pp_table`, UMD pstate bookkeeping, workload masks, power limits, and `adev->pm.smu_prv_buffer`. It depends on `hwmgr.h`, `amdgpu_dpm_internal.h`, Linux firmware/reboot/workqueue APIs, and amdgpu buffer helpers. The SW CTF delayed work may call `orderly_poweroff(true)` after rechecking hotspot or edge temperature.

## Risks And Test Signals
Notable risks are unchecked pp_table copy size in `pp_dpm_set_pp_table()`, missing function-pointer support returning mixed `0`, `-EINVAL`, `-EOPNOTSUPP`, or `-ENOENT`, and lifecycle races around delayed thermal work and private buffer mapping. Test signals include complete IP block init/fini, sysfs DPM controls, fan and sensor operations, pp_table override/reset behavior, display mode changes, BACO state transitions, and SW CTF shutdown behavior under thermal fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/amd_powerplay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/Makefile

## Purpose
This Makefile enumerates the PowerPlay hardware-manager object set. It collects generic hwmgr/PSM/table-processing helpers, ASIC-specific managers, thermal and powertune implementations, OverDrive support, and BACO implementations for several generations.

## Important Build Flow
`HARDWARE_MGR` lists objects such as `hwmgr.o`, `hardwaremanager.o`, `processpptables.o`, `smu7_hwmgr.o`, `vega10_hwmgr.o`, `vega20_hwmgr.o`, `common_baco.o`, `polaris_baco.o`, `fiji_baco.o`, `ci_baco.o`, and related thermal/powertune files. `AMD_PP_HWMGR` prefixes those entries with `$(AMD_PP_PATH)/hwmgr/`, then appends them to `AMD_POWERPLAY_FILES` for the parent build.

## State, Dependencies, And Integration
The file has build-state effects only. It depends on the parent PowerPlay Makefile defining `AMD_PP_PATH` and on the listed source files matching actual ASIC support compiled into the driver. It is the link-time integration point for hwmgr function tables that `hwmgr.c`, `hardwaremanager.c`, and `amd_powerplay.c` call.

## Risks And Test Signals
Risks are missing an object when a function table or ASIC implementation is referenced, retaining obsolete object names, or build-order assumptions hidden in aggregate variables. Test signals are successful compile/link of the amdgpu PM component and resolved symbols for all selected ASIC families and BACO state handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c

## Purpose
`ci_baco.c` implements BACO enter/exit sequencing for CI-generation SMU7 hardware. It provides `ci_baco_set_state()`, which drives hardware into or out of BACO using static register command tables executed by `baco_program_registers()`.

## Important APIs And Control Flow
The command tables prepare GPIOs, enable frame-buffer request rejection, switch clocks to bypass/reference sources, power down PLLs and memory clocks, assert BACO control bits, wait for BACO mode, and later reverse isolation/power/reset bits. `ci_baco_set_state()` first calls `smu7_baco_get_state()`, returns early if already in the requested state, executes the enter sequence for `BACO_STATE_IN`, and for `BACO_STATE_OUT` waits at least 20 ms before running the exit and cleanup tables.

## State, Dependencies, And Integration
Persistent state is hardware register state: GPIO masks, SMC indirect clock registers, PLL and memory-controller registers, `BACO_CNTL`, BIOS scratch registers, and CP PFP ucode address cleanup. The file depends on `amdgpu.h`, `ci_baco.h`, SMU7 BACO declarations, and CI register definition headers for GMC, BIF, DCE, SMU, and GFX.

## Risks And Test Signals
Risks include wrong magic register values, wait-mask/value mismatches, ignored failures from preparatory tables, and hardware hangs if clock or PLL steps are skipped. Test signals are successful `get_asic_baco_state`/`set_asic_baco_state`, correct BACO mode bits, no timeout in command waits, clean resume from BACO, and no display, memory, or CP firmware corruption after exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.h

## Purpose
`ci_baco.h` declares the CI-specific BACO state transition function used by the SMU7/PowerPlay hardware-manager backend.

## Important API
The single API is `ci_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`. It takes the generic PowerPlay hardware-manager context and a BACO state enum from `smu7_baco.h`, allowing the SMU7 backend to wire CI ASICs into the generic `get_asic_baco_state` and `set_asic_baco_state` callbacks exposed by `amd_powerplay.c`.

## Dependencies And Integration
The header includes `smu7_baco.h`, which provides `enum BACO_STATE`, `struct pp_hwmgr` visibility through included headers, and common SMU7 BACO support declarations. It is included by `ci_baco.c` and referenced by ASIC function-pointer setup code outside this file.

## Risks And Test Signals
The risk surface is small but ABI-sensitive: mismatching the prototype or enum source would break function-table wiring. Test signals are successful compilation, correct symbol resolution for `ci_baco_set_state`, and BACO capability/state callbacks dispatching to CI-specific behavior only for supported ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.c

## Purpose
`common_baco.c` is the shared BACO command interpreter. It executes compact command tables used by ASIC-specific BACO files to program MMIO registers, poll fields, and delay between power sequencing steps.

## Important APIs And Control Flow
`baco_wait_register()` polls a register every millisecond up to 5000 iterations until `(data & mask) == value`. `baco_cmd_handler()` implements `CMD_WRITE`, `CMD_READMODIFYWRITE`, `CMD_WAITFOR`, `CMD_DELAY_MS`, and `CMD_DELAY_US`, warning on invalid commands. `baco_program_registers()` walks legacy command entries, tracks the active register across commands, and aborts on the first failed command. `soc15_baco_program_registers()` performs the same logic but computes the register base through `adev->reg_offset[hwip][inst][seg]`.

## State, Dependencies, And Integration
The file mutates hardware registers only; it has no persistent software state. It depends on `common_baco.h`, `hwmgr.h`, `amdgpu_device` MMIO access macros, `msleep()`, and `udelay()`. It is used by CI, Fiji, Polaris, Vega, and other BACO implementation files to keep state-machine tables declarative.

## Risks And Test Signals
Risks include the fixed 5-second poll timeout being too long for failing paths, no locking around MMIO sequences, RMW on registers with side effects, and table encoding mistakes where delay entries reuse the previous register implicitly. Test signals are BACO enter/exit success across supported ASICs, no invalid-command warnings, expected wait completion, and clean recovery when a table wait intentionally fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.h

## Purpose
`common_baco.h` defines the table format and public helpers for BACO register sequencing. It lets ASIC-specific files describe power-off and power-on flows as arrays rather than open-coded MMIO sequences.

## Important APIs And Types
`enum baco_cmd_type` defines write, read-modify-write, wait, millisecond delay, and microsecond delay commands. `struct baco_cmd_entry` stores command, register offset, mask, shift, timeout, and value for pre-SOC15 register spaces. `struct soc15_baco_cmd_entry` adds `hwip`, `inst`, and `seg` fields so SOC15 code can resolve per-block register bases from `adev->reg_offset`. The exported helpers are `baco_program_registers()` and `soc15_baco_program_registers()`.

## State, Dependencies, And Integration
The header includes `hwmgr.h` for `struct pp_hwmgr` and integer types. It is included by common and ASIC BACO implementations. The command arrays it defines become an implicit hardware state machine for BACO transitions.

## Risks And Test Signals
The main risks are command table misencoding, mask/shift mismatches, and the typo-like include guard name `__COMMON_BOCO_H__`, which is harmless locally but worth preserving carefully. Test signals are successful compilation for all BACO users, static command arrays matching the expected struct type, and runtime BACO transitions succeeding through the shared executor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/common_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c

## Purpose
`fiji_baco.c` implements BACO state transitions for Fiji-class VI hardware. It is structurally similar to the CI path but uses Fiji register headers, Fiji-specific clock/PLL command tables, and broader BIOS scratch cleanup.

## Important APIs And Control Flow
`fiji_baco_set_state()` reads current state through `smu7_baco_get_state()`, returns early if no transition is needed, then enters BACO by programming GPIOs, frame-buffer request rejection, BCLK bypass, PLL shutdown, clock request switching, and BACO control bits. Exiting waits 20 ms, runs the exit table, and clears BIOS scratch registers 0 through 15 if exit succeeds.

## State, Dependencies, And Integration
Persistent effects are hardware register changes in GPIO, DCE, BIF, GMC, SMU indirect clock controls, MPLL/SPLL, `BACO_CNTL`, and BIOS scratch registers. It depends on `fiji_baco.h`, `smu7_baco.h`, `common_baco.h`, and generated register headers for GMC 8.1, BIF 5.0, DCE 10.0, and SMU 7.1.3.

## Risks And Test Signals
Risks are sequencing drift relative to hardware requirements, ignoring failures before the final enter/exit table, and scratch register cleanup masking firmware assumptions. Test signals are successful BACO in/out on Fiji boards, correct `BACO_MODE` transitions, absence of wait timeouts, stable display and memory clocks after exit, and successful subsequent DPM or reset operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.h

## Purpose
`fiji_baco.h` declares the Fiji-specific BACO transition entry point for PowerPlay SMU7 hardware-manager integration.

## Important API
`fiji_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)` is the only exported declaration. The generic hwmgr callback table can use it to route `BACO_STATE_IN` and `BACO_STATE_OUT` requests to Fiji register sequences.

## Dependencies And Integration
The header includes `smu7_baco.h` for the BACO enum and shared SMU7 BACO support. It is included by `fiji_baco.c` and participates in function-pointer wiring from the SMU7 backend to `amd_powerplay.c` BACO callbacks.

## Risks And Test Signals
Risks are limited to prototype drift and incorrect inclusion in ASIC-specific wiring. Test signals are compile/link success, symbol availability for Fiji hwmgr setup, and correct dispatch when `get_asic_baco_capability`, `get_asic_baco_state`, and `set_asic_baco_state` are exercised on Fiji hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hardwaremanager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hardwaremanager.c

## Purpose
`hardwaremanager.c` provides generic Power Hardware Manager (`phm_*`) wrappers over ASIC-specific `hwmgr_func` callbacks. It centralizes null/function checks, thermal range propagation into `adev->pm.dpm.thermal`, display configuration storage, clock queries, and generic state-management calls used by `hwmgr.c` and `amd_powerplay.c`.

## Important APIs And Control Flow
Key wrappers include `phm_setup_asic()`, `phm_power_down_asic()`, `phm_set_power_state()`, dynamic state enable/disable, `phm_force_dpm_levels()`, display pre/change notification, thermal start/stop, IRQ registration, clock queries by performance level/type/latency/voltage, display clock voltage requests, watermarks, and SMC CTF disable. `phm_start_thermal_controller()` begins with a default 0 to 80 C range, lets the backend override it, starts thermal control if the capability is set, and copies all critical/emergency limits into amdgpu PM state.

## State, Dependencies, And Integration
The file mutates `hwmgr->platform_descriptor`, `hwmgr->adev->pm.dpm.thermal`, display active-count state, CC6 data, and backend power-management state via callbacks. It depends on `hwmgr.h`, `hardwaremanager.h`, `power_state.h`, `pp_debug.h`, ACPI/pass-through checks, and `smum_is_dpm_running()`.

## Risks And Test Signals
Risks are inconsistent return conventions for optional callbacks, default thermal ranges being unsafe if backend range retrieval fails, VF/pass-through/suspend skip logic, and capability flags not matching backend support. Test signals include DPM enable/disable, thermal sysfs limits, fan control startup, display hotplug/reconfiguration, clock query correctness, and stable suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hardwaremanager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr.c

## Purpose
`hwmgr.c` owns legacy PowerPlay hardware-manager lifecycle and ASIC selection. It initializes default capabilities, applies feature-mask policy, chooses SMU manager and hardware-manager backends by family/chip, initializes pptables/backends/PSM, enables DPM and thermal control, handles suspend/resume, and dispatches high-level power-management tasks.

## Important APIs And Control Flow
`hwmgr_early_init()` sets defaults, workload priorities, OD/DPM levels, disables unsupported feature bits, handles Bonaire quirks, chooses SMU function tables, and calls ASIC init hooks. `hwmgr_sw_init()` registers IRQs and calls SMU init. `hwmgr_hw_init()` computes SR-IOV/PM enablement, initializes pptables and backend, repairs DC max clocks from AC if needed, initializes PSM, sets up ASIC, enables dynamic state management, starts thermal control, and sets performance states. `hwmgr_hw_fini()`, `hwmgr_suspend()`, and `hwmgr_resume()` unwind or restore this sequence. `hwmgr_handle_task()` handles display changes, user state requests, complete init, and power-state readjustment.

## State, Dependencies, And Integration
It mutates `pp_hwmgr` fields such as `pm_en`, `pp_one_vf`, `feature_mask`, `platformCaps`, `smumgr_funcs`, `dpm_level`, workload priority arrays, OD enablement, and `adev->pm.dpm_enabled`. It depends on PSM helpers, PHM wrappers, ACPI PCIe capability checks, SR-IOV/passthrough helpers, ASIC SMU function tables, and ASIC hwmgr initialization functions.

## Risks And Test Signals
Risks include unsupported chip selection returning `-EINVAL`, partial init cleanup correctness, feature-mask/capability mismatches, special-case quirks affecting DPM coverage, and suspend/resume ordering. Test signals are successful init across CI/CZ/VI/AI/RV devices, correct feature masks, working PSM transitions, display reconfiguration without underclocking, and clean hw_fini/suspend/resume with no DPM hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr_ppt.h

## Purpose
`hwmgr_ppt.h` defines PowerPlay table v1 data structures consumed by hwmgr table-processing code. It models clock/voltage dependency records, multimedia clock dependencies, voltage lookup rows, PCIe entries, and GPIO-related PowerPlay table data.

## Important Types
`phm_ppt_v1_clock_voltage_dependency_record` stores a clock with voltage indices and concrete voltage values for VDDC, VDDGFX, VDDCI, MVDD, phase count, CKS flags, voltage offsets, and SCLK offset. The dependency table wrappers use flexible arrays with `count`. Multimedia records capture UVD, VCE, ACP, and SAMU clocks with related voltage data. Voltage lookup records hold calculated/base/CAC-low/mid/high voltages. PCIe records include generation speed, lane width, and associated SCLK. `phm_ppt_v1_gpio_table` exposes the VRHot-triggered SCLK DPM index.

## State, Dependencies, And Integration
This header has no executable state. It depends on `hardwaremanager.h`, `smumgr.h`, and AtomBIOS types. Runtime table parsers allocate and fill these structures from VBIOS/PowerPlay tables; ASIC hwmgr code then uses them to build dynamic states, DPM levels, voltage tables, and PCIe policy.

## Risks And Test Signals
Risks are flexible-array allocation mistakes, count overflow, unit mismatch between BIOS tables and hwmgr consumers, and version confusion between PowerPlay table formats. Test signals include successful pptable parsing, correct DPM level counts and voltages, valid PCIe lane/gen policy, VRHot behavior, and no out-of-bounds access under malformed VBIOS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/hwmgr_ppt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.c

## Purpose
`polaris_baco.c` implements BACO enter/exit sequencing for Polaris and VegaM SMU7-family hardware. It is table-driven like the CI and Fiji paths but contains alternate BCLK and PLL shutdown sequences for `CHIP_VEGAM`.

## Important APIs And Control Flow
`polaris_baco_set_state()` checks current BACO state through `smu7_baco_get_state()`. Entering BACO programs GPIOs, frame-buffer request rejection, either standard Polaris or VegaM-specific clock bypass and PLL tables, common clock-request table, then BACO control bits. Exiting waits 20 ms, runs exit control sequencing, and clears BIOS scratch 6 and 7 on success.

## State, Dependencies, And Integration
The persistent effects are MMIO state in GPIO, DCE 11, BIF 5, GMC 8.1, SMU 7.1.3 indirect clock registers, MPLL/DRAM controls, `BACO_CNTL`, and BIOS scratch registers. The file depends on `polaris_baco.h`, `common_baco.h`, `smu7_baco.h`, `amdgpu.h`, and generated register headers. It integrates with `pp_get_asic_baco_*` and `pp_set_asic_baco_state()` through hwmgr callback wiring.

## Risks And Test Signals
Risks include using the wrong path for VegaM versus Polaris, ignored failures in preparatory tables, hard-coded undocumented registers, and waits with very short timeouts in PLL shutdown. Test signals are correct BACO mode changes on Polaris10/11/12 and VegaM, no wait failures, clean display/memory recovery after exit, and subsequent DPM/fan/sensor operations working.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.h

## Purpose
`polaris_baco.h` declares the Polaris/VegaM BACO transition entry point for the SMU7 PowerPlay backend.

## Important API
`polaris_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)` is the only exported declaration. It allows generic BACO state callbacks to invoke Polaris-specific register sequencing while keeping the public PowerPlay interface ASIC-neutral.

## Dependencies And Integration
The header includes `smu7_baco.h` for `enum BACO_STATE` and shared SMU7 BACO support. It is included by `polaris_baco.c` and used indirectly by SMU7 hwmgr setup code that installs `get_asic_baco_state` and `set_asic_baco_state` callbacks.

## Risks And Test Signals
Risks are prototype drift, incorrect ASIC callback wiring, and accidental use on unsupported chips. Test signals are compile/link success, symbol availability, and correct dispatch for Polaris10/11/12 and VegaM BACO sysfs or reset flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/polaris_baco.h -->
