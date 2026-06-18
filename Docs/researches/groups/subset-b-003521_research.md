# Research Report: subset-b-003521

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.h

## Purpose
This header is the Tonga-family BACO interface declaration for the legacy PowerPlay hardware-manager layer. It includes `smu7_baco.h` so callers share the SMU7 BACO state definitions and command helpers, and it exposes one ASIC-specific transition function, `tonga_baco_set_state()`.

## Important APIs, Types, and Functions
- `tonga_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: public entry point for placing a Tonga ASIC into or out of BACO. The implementation lives outside this header and is expected to use `struct pp_hwmgr` as the device power-management context.
- `enum BACO_STATE`: imported from `smu7_baco.h`; callers pass the target BACO state rather than manipulating register scripts directly.

## Control Flow and Integration
The file has no runtime control flow. Its role is compile-time integration: it lets Tonga-specific hardware-manager code register or call the BACO transition implementation while reusing the SMU7 BACO contract. It mirrors the Vega10 header pattern in this subset, but points at SMU7 rather than SMU9.

## State and Persistence
No state is stored here. State is external in the `pp_hwmgr` backend, the BACO state machine, and the hardware registers touched by the implementation.

## Dependencies
- `smu7_baco.h` for `enum BACO_STATE` and likely the lower-level BACO register-programming support.
- PowerPlay hardware-manager definitions through the included SMU7 BACO header.

## Risks
- The header assumes the implementation and `smu7_baco.h` agree on `enum BACO_STATE` semantics. A mismatch would break suspend, runtime power-management, or passthrough BACO transitions.
- Because only an extern is declared, compile/link coverage is the main guard against missing implementation.

## Test Signals
- Kernel build/link tests should verify that users of `tonga_baco_set_state()` resolve correctly.
- Runtime BACO tests should exercise both `BACO_STATE_IN` and `BACO_STATE_OUT` on supported Tonga hardware, checking that the current BACO state matches the requested state and that device resume remains functional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.c

## Purpose
This file implements the Vega10 BACO transition sequence for the PowerPlay hardware manager. BACO is driven through ordered register command tables for pre-entry, entry, exit, and cleanup. The exported function `vega10_baco_set_state()` compares the current BACO state with the requested state and then runs either the hardware register scripts or the SMC entry message needed to cross the boundary.

## Important APIs, Types, and Functions
- `vega10_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: exported transition entry point used by `vega10_hwmgr.c` through `.set_asic_baco_state`.
- `pre_baco_tbl`: NBIF setup before entering BACO. It enables doorbell monitoring, disables framebuffer access, bypasses BACO D-state behavior, and masks reset interrupts.
- `enter_baco_tbl`: ordered THM/NBIF register operations to wait for SOC idleness, assert BACO enable and isolation bits, power off, delay, assert reset, and wait for BACO mode.
- `exit_baco_tbl`: reverse transition that powers on, clears isolation and reset controls, asserts and waits for BACO exit, clears fences and dummy/LCLK/BACO enable bits, then waits until BACO mode clears.
- `clean_baco_tbl`: zeroes BIOS scratch registers after successful exit.
- `soc15_baco_cmd_entry`: command-table type, used with `CMD_READMODIFYWRITE`, `CMD_WRITE`, `CMD_WAITFOR`, and `CMD_DELAY_MS`.

## Control Flow
`vega10_baco_set_state()` first calls `smu9_baco_get_state()` and returns success if the device is already in the requested state. For `BACO_STATE_IN`, it programs `pre_baco_tbl`; on success it sends `PPSMC_MSG_EnterBaco`; if the SMC message succeeds, it programs `enter_baco_tbl` and returns success only if that command table reports success. For `BACO_STATE_OUT`, it waits 20 ms to satisfy the hardware regulator off/on timing requirement, then programs `exit_baco_tbl` followed by `clean_baco_tbl`. All other paths return `-EINVAL`.

The register sequencing is deliberately table-driven so the shared SOC15 BACO executor owns polling, masking, delays, and RMW details. This keeps Vega10-specific logic limited to the ordering and bit definitions.

## State and Persistence
The function does not allocate persistent software state. Durable effects are hardware register state in NBIF/THM, BIOS scratch cleanup on exit, and SMC firmware state after `PPSMC_MSG_EnterBaco`. The current-state read is external through SMU9 BACO helpers.

## Dependencies and Integration Points
- Includes `amdgpu.h`, SOC15 register helpers, Vega10 register offsets/masks, `vega10_ppsmc.h`, and `vega10_baco.h`.
- Depends on `soc15_baco_program_registers()` for command-table execution and on `smum_send_msg_to_smc()` for firmware coordination.
- Integrated by `vega10_hwmgr.c` as `.set_asic_baco_state = vega10_baco_set_state`; passthrough initialization can expose BACO support via `vega10_baco_set_cap()`.

## Risks
- Register ordering is safety-critical. Changing the sequence, wait masks, or delays can leave the ASIC isolated, powered off, or not fully reset.
- The nested success checks are easy to misread because the command executor appears to return nonzero on successful table completion in this code path. Any refactor should confirm the helper's return contract before simplifying conditions.
- BACO exit depends on a fixed 20 ms regulator interval plus a 10 ms table delay. Hardware variants with different timing requirements would need validated updates.
- Failure returns are mostly `-EINVAL`, so callers get limited diagnostics without register tracing.

## Test Signals
- BACO state transition tests should cover in, out, no-op when already in target state, and SMC-message failure.
- Hardware validation should watch NBIF/THM BACO mode bits, doorbell/framebuffer behavior, and post-exit display/PCIe recovery.
- Suspend/resume, runtime power-management, GPU reset, and passthrough tests are high-value because they exercise the same BACO boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.h

## Purpose
This header declares the Vega10 BACO transition entry point and imports the SMU9 BACO state contract. It is the narrow public surface between the Vega10 hardware manager and the implementation in `vega10_baco.c`.

## Important APIs, Types, and Functions
- `vega10_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: transitions a Vega10 ASIC to the requested BACO state.
- `enum BACO_STATE`: imported from `smu9_baco.h` and shared with generic SMU9 BACO helpers such as `smu9_baco_get_state()`.

## Control Flow and Integration
This file has no executable logic. It is consumed by `vega10_hwmgr.c`, which wires `vega10_baco_set_state()` into the `pp_hwmgr_func` table, and by `vega10_baco.c`, which provides the implementation.

## State and Persistence
No state is stored in the header. Runtime state lives in hardware, the SMU firmware, and the `pp_hwmgr` backend.

## Dependencies
- `smu9_baco.h` for the common SMU9 BACO state definitions and helper declarations.
- `struct pp_hwmgr` is expected through the included PowerPlay/SMU headers.

## Risks
- The declaration couples callers to the SMU9 BACO ABI. If `enum BACO_STATE` or the helper semantics change, both the implementation and hardware-manager callback contract must remain aligned.
- Missing include guards or wrong SMU generation includes would cause build or behavioral failures; this file correctly uses a unique guard and SMU9 include.

## Test Signals
- Kernel build tests should confirm that `vega10_baco.c` and `vega10_hwmgr.c` share a consistent declaration.
- Runtime coverage comes from the same BACO in/out tests used for `vega10_baco.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.c

## Purpose
This is the Vega10 implementation of the legacy AMD PowerPlay hardware-manager backend. It converts VBIOS PowerPlay tables, Atom firmware data, display requirements, OverDrive edits, thermal/fan policy, and user/sysfs requests into SMU9 firmware tables and SMC messages. It registers a `pp_hwmgr_func` callback table through `vega10_hwmgr_init()` so the common PowerPlay layer can initialize DPM, switch power states, read sensors, control clocks/fans, handle display changes, power-gate media blocks, manage BACO, and shut down MP1.

## Important APIs, Types, and Functions
- `vega10_hwmgr_init()`: public init hook. It assigns `hwmgr->hwmgr_func = &vega10_hwmgr_funcs`, assigns `vega10_pptable_funcs`, and enables BACO capability for passthrough devices.
- `vega10_hwmgr_backend_init()` / `vega10_hwmgr_backend_fini()`: allocate and free `struct vega10_hwmgr`, derive voltage control modes, set platform capabilities, initialize SMU feature metadata, patch dependency tables, seed OverDrive and fan defaults, and cache memory-channel information.
- `vega10_enable_dpm_tasks()` / `vega10_disable_dpm_tasks()`: main lifecycle gates for DPM, voltage tables, SMC PPTable upload, thermal/VR hot/deep-sleep/ULV/DIDT/power-containment/ACG features, and their shutdown order.
- `vega10_init_smc_table()`: constructs software DPM tables, fills `PPTable_t`, uploads it via `smum_smc_table_manager(..., PPTABLE, false)`, uploads AVFS fuse overrides, and enables AVFS/ACG.
- `vega10_set_power_state_tasks()`: applies a requested power state by updating DPM tables when necessary, generating boot/max DPM limits, uploading the PPTable, and toggling AVFS around OD or custom-table changes.
- `vega10_read_sensor()`: services PowerPlay sensor queries for clocks, load, temperatures, UVD/VCE power state, package power, VDDGFX, and enabled SMU features.
- `vega10_emit_clock_levels()`, `vega10_force_clock_level()`, and `vega10_dpm_force_dpm_level()`: implement sysfs-style clock reporting and forced DPM policies.
- `vega10_odn_edit_dpm_table()`: validates and applies OverDrive Next clock/voltage edits, restore, and commit commands.
- `vega10_set_power_profile_mode()` / `vega10_get_power_profile_mode()`: expose workload/profile tuning and custom GFX DPM parameters.

## Control Flow
Initialization starts in `vega10_hwmgr_init()`, which only installs function tables and optionally sets BACO capability. The common PowerPlay layer later calls `.backend_init`, which allocates backend state, selects SVID2/GPIO voltage control based on Atom firmware, initializes registry defaults, derives platform caps, queries SMU version and serial number, populates SMU feature support flags, completes voltage dependency tables, and caches default limits.

When dynamic state management is enabled, `vega10_enable_dpm_tasks()` configures telemetry, constructs voltage tables, initializes and uploads the SMU PPTable, then enables thermal protection, VR hot, deep sleep, DPM features, DIDT, power containment, power-control levels, and ULV. The PPTable construction path builds DPM tables from VBIOS dependencies, duplicates last valid entries to fill firmware fixed-size arrays, derives PLL dividers through Atom firmware helpers, programs boot voltages and deep-sleep DCEF clocks, fills AVFS/GPIO parameters, and uploads through the SMU table manager.

Power-state changes flow through `vega10_apply_state_adjust_rules()` and `vega10_set_power_state_tasks()`. The adjust phase clamps clocks for DC, stable pstate, display minimums, and multi-display memory-switching restrictions. The set phase finds whether requested clocks require DPM table edits, repopulates SCLK/MCLK/SOCCLK portions when flagged, calculates low/high enabled DPM indexes, uploads soft min/max indexes to SMC, uploads the PPTable, and updates AVFS state.

Display changes call `vega10_notify_smc_display_config_after_ps_adjustment()` and `vega10_display_configuration_changed_task()`. Those paths toggle UCLK fast switching, request DCEF/display clock voltage, set deep-sleep DCEF limits, upload watermark tables once present, and notify the SMC of display count.

Shutdown uses `vega10_power_off_asic()` and `.dynamic_state_management_disable` to disable thermal, power containment, DIDT, AVFS, DPM, deep sleep, ULV, ACG, and PCC limiting, then clears the loaded watermark bit.

## State and Persistence Behavior
Persistent per-device software state is in `hwmgr->backend`, cast to `struct vega10_hwmgr`. It stores live DPM tables, golden default DPM tables, registry feature knobs, voltage tables, leakage data, SMU feature support/enabled flags, boot state, watermarks, OD tables, custom profile data, media power-gating booleans, display timing cache, and flags such as `need_update_dpm_table`.

Hardware/firmware state is persisted through SMU messages and table uploads: soft min/max clock indexes, enabled feature masks, workload mask, PPTable/WMTABLE/AVFS fuse tables, BACO state, telemetry config, power containment, and display clock requests. Some backend fields mirror firmware state, especially `smu_features[].enabled`, DPM soft limits, `water_marks_bitmap`, `uvd_power_gated`, and `vce_power_gated`. Those mirrors are important but can become stale if SMU calls fail after local mutation.

No disk persistence occurs. All settings are runtime driver state rebuilt from VBIOS, Atom firmware, module feature masks, and user requests.

## Dependencies and Integration Points
- Common PowerPlay: `hwmgr.h`, `hardwaremanager.h`, `amd_powerplay.h`, `pp_overdriver.h`, `pp_thermal.h`, `ppinterrupt.h`.
- Atom firmware and VBIOS parsing: `ppatomfwctrl.h`, `atomfirmware.h`, `vega10_processpptables.h`, `vega10_pptable.h`.
- SMU9: `smu9.h`, `smu9_driver_if.h`, `vega10_smumgr.h`, `vega10_ppsmc.h`, `smum_send_msg_to_smc*()`, `smum_smc_table_manager()`.
- Vega10 companion modules: `vega10_powertune.h`, `vega10_thermal.h`, `vega10_baco.h`.
- SOC/register access: `vega10_inc.h`, `soc15_common.h`, SMUIO offsets/masks, PCIe helpers, and `RREG32_SOC15`/`RREG32_PCIE`.
- Display manager integration occurs through display config data and watermark callbacks; media integration occurs through UVD/VCE DPM and power-gating callbacks.

## Risks
- The file contains many hardware-table array fills with firmware-defined maximums. Off-by-one errors or unvalidated VBIOS counts can corrupt fixed-size PPTable fields; assertions check many but not all assumptions.
- Local SMU feature `enabled` mirrors are sometimes updated before or around firmware calls. A failed SMC transaction can leave software state inconsistent with firmware state.
- `need_update_dpm_table` is a shared bitfield driving OD, SOCCLK, SCLK, MCLK, and AVFS behavior. Missing a bit or failing to clear the right bits can leave stale DPM data or disable AVFS longer than intended.
- Some logic is ASIC- or mode-specific, such as `pp_one_vf` peak limits, passthrough BACO capability, ACG firmware major version checks, and PCC limiting for specific chip/subvendor combinations.
- Display and memory-clock constraints are tightly coupled. Multi-monitor, VR, frame-lock, and latency policy changes can affect UCLK switching and flicker/power behavior.
- Several paths return generic `-EINVAL` or continue after `PP_ASSERT` diagnostics, so failures may be hard to diagnose without SMC/register tracing.

## Test Signals
- Build coverage with Vega10 PowerPlay enabled is required for the callback table and all companion headers.
- Boot/init tests should verify backend allocation, SMU version/serial reads, voltage control detection, PPTable upload, and DPM feature enablement.
- Runtime tests should cover AC/DC switching, stable pstate, forced DPM levels, manual clock masks, OD edit/commit/restore, power profiles, sensor reads, thermal/fan control, and UVD/VCE power gating.
- Display tests should cover no display, single display, unsynchronized multi-display, watermark upload, DCEF/deep-sleep clock requests, and memory-switching latency constraints.
- Suspend/resume, GPU reset, passthrough, and BACO in/out tests should check that DPM disable/enable ordering and watermarks recover correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.h

## Purpose
This header defines the Vega10 PowerPlay backend data model used by `vega10_hwmgr.c`. It names SMU feature indexes, DPM table shapes, PowerPlay hardware power-state records, voltage and leakage caches, registry/configuration knobs, OverDrive state, and the top-level `struct vega10_hwmgr` stored in `hwmgr->backend`.

## Important APIs, Types, and Functions
- `enum GNLD_*`: indexes logical SMU features such as GFX/UCLK/SOCCLK DPM, UVD/VCE DPM, ULV, AVFS, thermal, fan control, ACG, DIDT, and PCC limiting. `GNLD_DPM_MAX` bounds the DPM feature subset, while `GNLD_FEATURES_MAX` bounds the whole feature array.
- `struct smu_features`: per-feature support/enabled state plus SMU feature id and bitmap.
- `struct vega10_power_state`: hardware power-state payload embedded in `pp_power_state`, including UVD/VCE clocks, performance levels, DC compatibility, and SCLK threshold.
- `struct vega10_dpm_table` and related `vega10_single_dpm_table`, `vega10_dpm_level`, `vega10_dpm_state`, `vega10_pcie_table`: software representation of clock/link DPM levels before they are converted to firmware PPTable fields.
- `struct vega10_smc_state_table`: caches firmware-facing `PPTable_t`, watermark table, AVFS table, and boot/max DPM indexes.
- `struct vega10_registry_data`: runtime policy flags derived from feature masks or registry-like defaults, controlling DPM enablement, power containment, AVFS, DIDT, thermal/fan behavior, watermarks, PCIe overrides, OD support, and GPIO features.
- `struct vega10_hwmgr`: top-level backend state with DPM tables, golden defaults, voltage tables, leakage data, BACO flags, OD state, display timing, feature array, SMU tables, and custom profile fields.
- Exported declarations: media DPM update helpers, `vega10_enable_disable_vce_dpm()`, and `vega10_hwmgr_init()`.

## Control Flow and Integration
The header itself has no executable flow, but its structures define the control data used throughout the Vega10 manager. The common hardware manager stores a `struct vega10_hwmgr` pointer in `hwmgr->backend`; implementation functions mutate this state and then issue SMC messages or table uploads. The `vega10_power_state` shape determines how PowerPlay table entries are parsed and compared during state transitions.

## State and Persistence
The key persistent runtime state is `struct vega10_hwmgr`. It keeps both desired software configuration and mirrors of firmware state: DPM levels, soft min/max indexes, enabled features, watermarks, power-gating flags, voltage tables, OD edits, and custom workload profile data. `golden_dpm_table` is a reset baseline for OD restore and range reporting. None of this is disk-persistent; it is reconstructed on driver load and adjusted at runtime.

## Dependencies
- Core PowerPlay types from `hwmgr.h`, `ppatomctrl.h`, `ppatomfwctrl.h`.
- SMU firmware ABI types from `smu9_driver_if.h` and `vega10_ppsmc.h`.
- PowerTune constants/types from `vega10_powertune.h`.
- Legacy Tonga declarations remain at the bottom, suggesting shared or migrated code paths from earlier ASIC support.

## Risks
- Many arrays use fixed firmware limits such as `MAX_REGULAR_DPM_NUMBER`, `MAX_PCIE_CONF`, and `VEGA10_MAX_HARDWARE_POWERLEVELS`. Implementation code must validate VBIOS counts before filling them.
- `struct vega10_hwmgr` is broad and mutable; feature toggles, OD edits, display changes, and SMC table contents share the same object, increasing stale-state risk.
- The header exposes several Tonga-named externs in a Vega10 header. If unused, they are harmless but confusing; if used, they signal tight legacy coupling.
- Boolean registry fields are compact but numerous. Default initialization must remain comprehensive or new fields can silently default to unsupported behavior.

## Test Signals
- Compile tests catch struct and callback signature drift across `vega10_hwmgr.c` and companion modules.
- Runtime tests should observe that backend state mirrors firmware state after DPM enable/disable, OD restore, feature toggles, watermarks, and media power gating.
- ABI-sensitive changes should be tested against SMU table layout expectations because `PPTable_t`, `Watermarks_t`, and AVFS structures are firmware-facing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_hwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h

## Purpose
This header centralizes Vega10 register include files needed by the hardware manager and BACO implementation. It pulls in default, offset, and shift/mask definitions for THM, MP, GC, and NBIO register blocks so implementation files can use generated register names and bit masks.

## Important APIs, Types, and Functions
This file declares no functions or types. Its important surface is the include bundle:
- THM 9.0 defaults, offsets, and masks.
- MP 9.0 offsets and masks.
- GC 9.0 defaults, offsets, and masks.
- NBIO 6.1 defaults, offsets, and masks.

## Control Flow and Integration
There is no runtime control flow. Files such as `vega10_baco.c` include it to access register constants used in SOC15 command-table entries and bit manipulation.

## State and Persistence
No state is stored here. It only makes generated register metadata visible at compile time.

## Dependencies
The header depends on generated ASIC register headers under `asic_reg/`. Those headers provide the symbolic register offsets and masks used by SOC15 access macros.

## Risks
- Incorrect register-generation version or wrong IP block include would make register programming target the wrong offsets or masks.
- Because this header is a broad include bundle, users may appear to compile without including the exact IP-specific header they directly need, increasing hidden dependency coupling.

## Test Signals
- Build tests should catch missing generated register headers or renamed symbols.
- Hardware smoke tests that exercise BACO, DPM, thermal, and SMU register paths indirectly validate that the included register definitions match Vega10 silicon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h -->
