# subset-b-003740 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.c

## Purpose

`trinity_dpm.c` implements Dynamic Power Management for AMD Trinity/Aruba-class Radeon APUs. It parses AtomBIOS PowerPlay and IntegratedSystemInfo tables, builds Trinity-specific power-state/private structures, programs SCLK DPM levels into SMU registers, coordinates UVD/VCE/media clocks, configures NB P-states, enables/disables clock and power gating, and exposes DPM lifecycle/debug helpers used by the Radeon ASIC callbacks.

## Important APIs, Types, and Functions

- Trinity private data is accessed through `trinity_get_pi()` and `trinity_get_ps()`, mapping `rdev->pm.dpm.priv` to `struct trinity_power_info` and `radeon_ps::ps_priv` to `struct trinity_ps`.
- Clock/power gating helpers include `trinity_enable_clock_power_gating()`, `trinity_disable_clock_power_gating()`, `trinity_mg_clockgating_initialize()`, `trinity_gfx_powergating_initialize()`, `trinity_gfx_dynamic_mgpg_enable()`, and sequence programming helpers for hardcoded register triplets/pairs.
- SCLK DPM programming helpers write SMU state-table fields: `trinity_set_divider_value()`, `trinity_set_vid()`, `trinity_set_ds_dividers()`, `trinity_set_ss_dividers()`, `trinity_set_display_wm()`, `trinity_set_vce_wm()`, `trinity_set_at()`, `trinity_program_power_level()`, and `trinity_power_level_enable_disable()`.
- Runtime lifecycle entry points are `trinity_dpm_init()`, `trinity_dpm_setup_asic()`, `trinity_dpm_enable()`, `trinity_dpm_late_enable()`, `trinity_dpm_disable()`, `trinity_dpm_fini()`, `trinity_dpm_pre_set_power_state()`, `trinity_dpm_set_power_state()`, and `trinity_dpm_post_set_power_state()`.
- Power-state adjustment is centralized in `trinity_apply_state_adjust_rules()`, which patches thermal states, UVD dividers, VCE clock/voltage requirements, display watermarks, BAPM flags, SCLK floors, and NB P-state policy.
- UVD/VCE integration is handled by `trinity_setup_uvd_clocks()`, `trinity_set_uvd_clock_before_set_eng_clock()`, `trinity_set_uvd_clock_after_set_eng_clock()`, and `trinity_set_vce_clock()`.
- Firmware table parsers include `trinity_parse_sys_info_table()` for `IntegratedSystemInfo` revision 7 and `trinity_parse_power_table()` for PowerPlay state/clock/non-clock arrays.
- Debug and query APIs include `trinity_dpm_print_power_state()`, `trinity_dpm_debugfs_print_current_performance_level()`, `trinity_dpm_get_current_sclk()`, `trinity_dpm_get_current_mclk()`, `trinity_dpm_get_sclk()`, and `trinity_dpm_get_mclk()`.

## Control Flow

Initialization allocates `struct trinity_power_info`, selects feature defaults such as BAPM, NBPS, SCLK deep sleep, clock/power gating, UVD DPM, and auto thermal throttling, then parses AtomBIOS integrated-system and PowerPlay data. Parsed boot data seeds `boot_pl` and `current_ps`, extended power/VCE dependency tables are imported by shared R600 helpers, and DPM is marked enabled only after all parsing succeeds.

ASIC setup takes SMU ownership through the Sumo path, records fuse-derived minimum SCLK divider data, and later `trinity_dpm_enable()` acquires the SMC mutex, programs the boot state, sets voltage control, starts activity monitors, programs thermal throttling and SCLK DPM intervals, starts DPM, waits for DPM/current state to settle at level 0, disables BAPM initially, releases the mutex, and records boot as current state. Late enable adds clock/power gating and thermal IRQ setup.

Power-state changes are split into pre/set/post phases. Pre-set clones the requested Radeon power state into `pi->requested_*` and applies Trinity policy. Set-state acquires the SMC mutex, optionally toggles BAPM according to AC power, changes UVD clocks before or after SCLK programming depending on whether the new top SCLK is lower or higher, forces level 0, programs NB P-state simulation and all SCLK levels, unforces DPM, updates VCE clocks, and releases the mutex. Post-set copies requested state into current state.

Shutdown disables BAPM and gating, clears voltage control, waits for level 0, stops SCLK DPM, resets activity monitors, disables thermal IRQs, restores current state to boot, and final teardown releases SMU control plus all allocated DPM power-state/private memory.

## State and Persistence Behavior

Persistent state lives in `rdev->pm.dpm` and `struct trinity_power_info`: parsed system information, boot/current/requested power states, firmware-derived UVD clock table entries, per-level activity thresholds, feature booleans, and thermal limits. Hardware state persists in SMU/MMIO registers, clock-gating tables, DPM state-table slots, CRTC-display CAC values, and interrupt enable state.

The file uses SMU scratch/register state heavily and relies on `trinity_acquire_mutex()`/`trinity_release_mutex()` from `trinity_smc.c` around most SMU programming. Current/requested state snapshots copy the public `radeon_ps` plus private `trinity_ps`, then rewrite `ps_priv` to the internal copy to avoid dangling references to transient stack clones.

## Dependencies and Integration Points

- Depends on Radeon core power-management fields, AtomBIOS parser helpers, R600/Sumo DPM helpers, ASIC clock setters, VCE clock-gating helpers, IRQ programming, PCI subsystem IDs, and register definitions from `trinityd.h`.
- Consumes AtomBIOS `PowerPlayInfo`, `IntegratedSystemInfo`, and extended VCE dependency tables.
- Integrates with media blocks through `radeon_set_uvd_clocks()`, `radeon_set_vce_clocks()`, `r600_is_uvd_state()`, and `vce_v1_0_enable_mgcg()`.
- Integrates with display mode changes through `trinity_dpm_display_configuration_changed()`, active CRTC counts, and DC CAC programming.

## Risks and Edge Cases

- `trinity_set_uvd_clock_before_set_eng_clock()` assigns `current_ps = trinity_get_ps(new_rps)` instead of using `old_rps`; this makes the comparison self-referential and likely prevents the intended pre-SCLK UVD clock transition on downclocks.
- `trinity_parse_power_table()` allocates `struct sumo_ps` for Trinity private state even though the rest of this file treats `ps_priv` as `struct trinity_ps`; this works only if layout compatibility is intentional and should be verified.
- Firmware table offsets and counts are mostly trusted after `atom_parse_data_header()`. Malformed table lengths, state counts, entry sizes, or VCE clock indices could cause out-of-bounds reads.
- `trinity_get_vce_clock_voltage()` returns `-EINVAL` when falling back to the highest voltage, but callers ignore the return value and consume the fallback voltage. This is intentional-looking but fragile for future error handling.
- Several hardware policy values are hardcoded or marked uncertain (`/* ??? */`, disabled pre-display voltage drop flow, hardcoded UVD DPM interval, DPM/BAPM board workaround).
- `trinity_dpm_force_performance_level()` calls `trinity_dpm_n_levels_disabled(rdev, 0)` inside a loop for auto level, repeating the same message unnecessarily.
- Cleanup after partial `trinity_dpm_init()` failure does not free everything allocated before the failing parse/helper call unless the caller runs `trinity_dpm_fini()` on failed init, which is unlikely.

## Test Signals

- Boot/resume on Trinity/Aruba APUs should show successful PowerPlay/sys-info parsing, DPM enable, thermal IRQ setup, and stable transitions between boot, battery, balanced, UVD, VCE, and thermal states.
- Instrumented register tests should confirm DPM state slots, NB P-state config, UVD DPM states, VCE clocks, display watermarks, and clock-gating registers match requested state transitions.
- Regression tests should cover MSI/non-MSI BAPM defaults, malformed or unsupported AtomBIOS table revisions, VCE dependency fallback behavior, CRTC count changes, and suspend/resume disable/enable cycles.
- Debugfs current performance output should match `TARGET_AND_CURRENT_PROFILE_INDEX` and avoid invalid profile reports under normal transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.h

## Purpose

`trinity_dpm.h` defines the Trinity-specific DPM private data model shared by `trinity_dpm.c` and `trinity_smc.c`. It describes per-power-level fields, per-power-state policy flags, parsed system information, persistent DPM driver state, and the SMC message helper prototypes used to control DPM firmware.

## Important APIs, Types, and Functions

- `struct trinity_pl` is one hardware SCLK DPM level: SCLK, voltage index, deep/sleep dividers, NB slow/force settings, display watermark, and VCE watermark.
- `struct trinity_ps` wraps up to `SUMO_MAX_HARDWARE_POWERLEVELS` levels plus NB P-state flags, BAPM flags, NB low/high policy values, and UVD low/high divider selections.
- `struct trinity_uvd_clock_table_entry` maps firmware UVD VCLK/DCLK values to divider IDs.
- `struct trinity_sys_info` stores IntegratedSystemInfo data: boot clocks, minimum SCLK, dentist VCO, NB P-state clocks/voltages, thermal limits, SCLK/VID mapping tables, UMA channels, and UVD clock table entries.
- `struct trinity_power_info` is the device-lifetime private DPM state with per-level activity thresholds, feature flags, parsed sys-info, boot level, minimum divider, and current/requested Radeon/Trinity power-state snapshots.
- Prototypes expose SMC operations: BAPM enable, DPM config, UVD DPM config, forced state, disabled-level count, no-forced-level, DCE voltage adjustment, dynamic MGPG config, and SMC mutex acquire/release.

## Control Flow

The header does not execute behavior directly. `trinity_dpm_init()` allocates and populates `struct trinity_power_info`, and every Trinity DPM transition uses the structures here to transform AtomBIOS states into SMU register programming. `trinity_smc.c` implements the SMC command prototypes declared here.

## State and Persistence Behavior

All structures are in-memory driver state; persistent hardware state is represented indirectly through the values later written into SMU registers. `current_rps/current_ps` and `requested_rps/requested_ps` keep stable internal snapshots, with `ps_priv` redirected to the embedded Trinity private copies.

## Dependencies and Integration Points

- Includes `sumo_dpm.h` for shared Sumo/Trinity constants and mapping table types.
- Depends on `struct radeon_device`, `struct radeon_ps`, and Radeon DPM definitions supplied by including translation units.
- Uses register spacing from `trinityd.h` through `TRINITY_SIZEOF_DPM_STATE_TABLE`, so register layout and DPM state structure are coupled.

## Risks and Edge Cases

- The header exposes mutable private structures broadly, so consumers can bypass invariants around `num_levels`, `ps_priv`, or feature flags.
- `TRINITY_POWERSTATE_FLAGS_NBPS_*` and `TRINITY_POWERSTATE_FLAGS_BAPM_DISABLE` are overlapping bit values in separate fields; mixing fields would be easy in future edits.
- `trinity_power_info` stores many booleans that gate register programming; uninitialized or partially initialized instances would produce unsafe hardware sequences.

## Test Signals

- Build coverage should catch type drift between this header, `trinity_dpm.c`, `trinity_smc.c`, and Sumo helpers.
- Runtime DPM tests should inspect current/requested state snapshots and confirm `ps_priv` points at the embedded private state after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_smc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_smc.c

## Purpose

`trinity_smc.c` is the low-level SMC/SMU message transport used by Trinity DPM. It writes message IDs and scratch arguments to SMC registers, polls for firmware responses, maps common DPM operations to PPSMC messages, and provides a simple SMU mutex request/release mechanism.

## Important APIs, Types, and Functions

- `trinity_notify_message_to_smu()` writes `SMC_MESSAGE_0`, polls `SMC_RESP_0` up to `rdev->usec_timeout`, and translates response codes `0xff` and `0xfe` into `-EINVAL`.
- `trinity_dpm_bapm_enable()` sends `PPSMC_MSG_EnableBAPM` or `PPSMC_MSG_DisableBAPM`.
- `trinity_dpm_config()` writes `SMU_SCRATCH0` to 1 or 0 before `PPSMC_MSG_DPM_Config`.
- `trinity_dpm_force_state()` and `trinity_dpm_n_levels_disabled()` pass an argument through `SMU_SCRATCH0`.
- `trinity_uvd_dpm_config()`, `trinity_dpm_no_forced_level()`, `trinity_dce_enable_voltage_adjustment()`, and `trinity_gfx_dynamic_mgpg_config()` send specific PPSMC messages.
- `trinity_acquire_mutex()` requests SMC ownership through `SMC_INT_REQ`; `trinity_release_mutex()` clears it.

## Control Flow

All exported command helpers funnel through `trinity_notify_message_to_smu()`. Callers that need an argument write scratch first, then send the message. Most higher-level DPM paths in `trinity_dpm.c` wrap these calls with `trinity_acquire_mutex()` and `trinity_release_mutex()`.

## State and Persistence Behavior

The file persists no C-side state. It mutates hardware registers: `SMC_MESSAGE_0`, `SMC_RESP_0`, `SMU_SCRATCH0`, and `SMC_INT_REQ`. Scratch arguments remain in SMC-visible registers until overwritten, and firmware-side DPM state changes persist after successful messages.

## Dependencies and Integration Points

- Depends on `radeon.h` register access macros, Trinity register definitions, DPM private header prototypes, and PPSMC message IDs from `ppsmc.h`.
- Called by Trinity DPM lifecycle, BAPM, UVD DPM, VCE/media, voltage-adjustment, and forced-level flows.

## Risks and Edge Cases

- `trinity_notify_message_to_smu()` treats a timeout with response value 0 as success unless the response is `0xff` or `0xfe`; callers cannot distinguish no response from success.
- `trinity_acquire_mutex()` has no return value and does not report timeout if `SMC_INT_REQ` never acknowledges.
- Message arguments use one shared scratch register, so callers must preserve ordering and locking externally.

## Test Signals

- Hardware tests should inject/observe `SMC_RESP_0` values for success, unknown message, failed handling, and timeout/no-response cases.
- DPM transition tests should confirm every scratch-argument message writes the expected value before message delivery.
- Locking tests should verify callers hold the SMC mutex around multi-register SMC sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinityd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinityd.h

## Purpose

`trinityd.h` is the Trinity DPM register and bitfield definition header. It maps SMU, SMC, clock-gating, thermal, power-management, fuse, scratch, and display-related register offsets plus field masks/shifts used by `trinity_dpm.c` and `trinity_smc.c`.

## Important APIs, Types, and Functions

- DPM state table registers: `SMU_SCLK_DPM_STATE_0_CNTL_0`, `_CNTL_1`, `_CNTL_3`, `_AT`, `_PG_CNTL`, and `SMU_SCLK_DPM_STATE_1_CNTL_0`.
- Field macros define DPM level validity, clock divider, VID/LVRT, deep-sleep dividers, display/VCE watermarks, GNB slow, forced NB P-state, and activity threshold values.
- Global DPM controls include `SMU_SCLK_DPM_CNTL`, `SMU_SCLK_DPM_TT_CNTL`, `SMU_SCLK_DPM_TTT`, `PM_I_CNTL_1`, `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, and `TARGET_AND_CURRENT_PROFILE_INDEX`.
- UVD/NB/media controls include `SMU_UVD_DPM_STATES`, `SMU_UVD_DPM_CNTL`, `NB_PSTATE_CONFIG`, and `DC_CAC_VALUE`.
- Power-gating and clock-gating controls include `GFX_POWER_GATING_CNTL`, `SMU_S_PG_CNTL`, `CG_GIPOTS`, `CG_PG_CTRL`, `CG_CGTT_LOCAL_0/1`, `CGTS_SM_CTRL_REG`, and `CG_MISC_REG`.
- SMC communication registers are `SMC_INT_REQ`, `SMC_MESSAGE_0`, `SMC_RESP_0`, and `SMU_SCRATCH0`.

## Control Flow

The header has no runtime control flow. It enables the DPM implementation to perform read/modify/write sequences with named fields and register offsets.

## State and Persistence Behavior

Every macro names hardware state that persists in MMIO or SMC register space. The C driver caches only selected values elsewhere; the authoritative DPM, thermal, clock-gating, and SMC message state resides in hardware/firmware registers.

## Dependencies and Integration Points

- Used by Trinity DPM and SMC files through Radeon register access macros such as `RREG32`, `WREG32`, `RREG32_SMC`, and `WREG32_SMC`.
- Constants must match the Trinity hardware register map and firmware expectations for DPM state-table spacing.

## Risks and Edge Cases

- Macros are simple shifts and masks with no range checking. Callers can silently truncate or overflow fields if values exceed bit width.
- Register offsets are hardware ABI. A wrong value can corrupt unrelated GPU state.
- `TRINITY_SIZEOF_DPM_STATE_TABLE` in `trinity_dpm.h` depends on the spacing between definitions in this header.

## Test Signals

- Register programming tests should compare known-good traces against generated values for DPM levels, thermal thresholds, NB P-states, and clock-gating sequences.
- Static review should verify mask/shift pairs and DPM state-table spacing whenever register definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinityd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v1_0.c

## Purpose

`uvd_v1_0.c` implements first-generation Radeon UVD ring and block control. It programs UVD firmware memory layout, starts/stops the VCPU and ring buffer controller, emits fences and IB commands, performs ring/IB tests, and provides register pointer callbacks for the Radeon ring infrastructure.

## Important APIs, Types, and Functions

- Ring pointer callbacks: `uvd_v1_0_get_rptr()`, `uvd_v1_0_get_wptr()`, and `uvd_v1_0_set_wptr()` access `UVD_RBC_RB_RPTR/WPTR`.
- `uvd_v1_0_fence_emit()` writes a fence sequence and trap through `UVD_GPCOM_VCPU_*` packet registers.
- `uvd_v1_0_resume()` calls `radeon_uvd_resume()`, splits the firmware/heap/stack/session backing buffer into VCPU cache ranges, writes 40-bit address extension registers, and sets `UVD_FW_START`.
- `uvd_v1_0_init()` raises UVD clocks, starts hardware, marks the ring ready, runs ring test, programs semaphore timeouts/control, applies ASIC workarounds, and lowers clocks.
- `uvd_v1_0_start()` performs reset/stall sequencing, LMI/MPC setup, VCPU boot polling/retry, interrupt enable, ring base/size programming, and ring pointer initialization.
- `uvd_v1_0_stop()` idles RBC, stalls UMC/register bus, resets VCPU, disables VCPU clock, and unstalls buses.
- `uvd_v1_0_ring_test()` verifies ring writes by updating `UVD_CONTEXT_ID`.
- `uvd_v1_0_semaphore_emit()` returns false because V1 hardware does not support UVD semaphores.
- `uvd_v1_0_ib_execute()` emits IB base/size commands, and `uvd_v1_0_ib_test()` submits create/destroy messages and waits on a fence.

## Control Flow

Resume prepares firmware memory ranges first. Init raises clocks, calls start, enables the ring only after the VCPU responds, validates the ring, programs semaphore controls through the ring, then drops clocks. Start sequences multiple resets with delays, boots the VCPU, retries up to ten times if status bit 2 does not appear, and only then exposes the ring buffer to command submission.

IB testing raises clocks, builds a UVD create message, builds a destroy message that returns a fence, waits for completion with `RADEON_USEC_IB_TEST_TIMEOUT`, releases the fence, and drops clocks on all exits.

## State and Persistence Behavior

Persistent state includes UVD firmware BO placement in `rdev->uvd`, ring `wptr/ready`, VCPU cache register ranges, LMI address-extension registers, interrupt enable bits, and block reset/clock state. The file relies on `radeon_uvd_resume()` to populate CPU/GPU firmware buffer state before cache registers are programmed.

## Dependencies and Integration Points

- Uses Radeon ring, fence, UVD message, clock, firmware, and register helper infrastructure.
- Register definitions come from `r600d.h`; ASIC family checks choose clocks and workarounds.
- Integrates with the generic scheduler through ring pointer, fence, semaphore, IB execute, ring test, and IB test callbacks.

## Risks and Edge Cases

- `uvd_v1_0_start()` uses long fixed `mdelay()` polling/retry loops and returns `-1` instead of a specific errno after repeated VCPU failure.
- Firmware memory layout assumes the BO is large and aligned enough for firmware, heap, stack, and all sessions.
- Semaphores are disabled for V1, so synchronization paths must handle a false return and avoid relying on hardware semaphores.
- Several workarounds are ASIC-family-specific and can regress old chips if family classification changes.
- `UVD_RBC_RB_BASE` is written with `ring->gpu_addr` directly; correctness depends on register semantics matching the lower address bits for this generation.

## Test Signals

- Ring tests should observe `UVD_CONTEXT_ID` changing to `0xDEADBEEF` within `usec_timeout`.
- IB tests should complete create/destroy messages and fence wait under raised clocks.
- Resume/start tests should validate programmed cache offsets/sizes, address extensions, ring base/size, and VCPU status.
- Stop/start cycles should leave ring readiness and VCPU reset/clock state consistent across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v2_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v2_2.c

## Purpose

`uvd_v2_2.c` provides UVD 2.2 generation-specific fence, semaphore, and firmware memory-controller programming. It reuses older UVD support where needed and adds chip-ID reporting for firmware across RV7xx, Evergreen, Northern Islands, and early Southern Islands families.

## Important APIs, Types, and Functions

- `uvd_v2_2_fence_emit()` writes context ID, lower/upper fence address bits, fence sequence, and trap command into the UVD ring.
- `uvd_v2_2_semaphore_emit()` emits wait/signal commands through `UVD_SEMA_ADDR_LOW/HIGH` and `UVD_SEMA_CMD`.
- `uvd_v2_2_resume()` handles firmware/heap/stack/session cache range setup, address extension registers, and `UVD_VCPU_CHIP_ID`.

## Control Flow

Resume delegates RV770 to `uvd_v1_0_resume()` because that ASIC uses V1 memory-controller semantics. For other supported families it calls `radeon_uvd_resume()`, programs the three VCPU cache ranges, writes high address bits, maps `rdev->family` to a firmware chip ID, writes it to `UVD_VCPU_CHIP_ID`, and returns `-EINVAL` for unsupported families.

## State and Persistence Behavior

The function persists VCPU cache offsets/sizes and firmware chip ID in hardware registers. Fence and semaphore functions only append commands to the ring; completion state is observed by generic fence/semaphore infrastructure.

## Dependencies and Integration Points

- Uses `radeon_uvd_resume()` and UVD buffer fields from the Radeon device.
- Depends on `uvd_v1_0_resume()` compatibility, family enums, `PACKET0`, ring writing, and `rv770d.h` UVD register definitions.
- Supplies generation-specific callbacks to Radeon ASIC tables.

## Risks and Edge Cases

- Unsupported family values fail resume with `-EINVAL`; ASIC dispatch must only bind this implementation to listed families.
- Semaphore address encoding shifts by 3 and 23 with 20-bit masks; invalid alignment or address range assumptions could break synchronization.
- Cache size calculation includes firmware size plus 4 bytes, which must match the firmware image format expected by this generation.

## Test Signals

- Resume tests should verify correct chip IDs for each supported family and RV770 fallback to V1 resume.
- Fence tests should verify the emitted command sequence writes both low and upper fence address bits.
- Semaphore tests should verify wait and signal command encodings and address shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v2_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v3_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v3_1.c

## Purpose

`uvd_v3_1.c` contains the UVD 3.1-specific semaphore emitter. This generation uses the same address register layout as UVD 2.2 but sets an additional command bit.

## Important APIs, Types, and Functions

- `uvd_v3_1_semaphore_emit()` writes semaphore GPU address fields to `UVD_SEMA_ADDR_LOW/HIGH` and emits `UVD_SEMA_CMD` with `0x80` ORed with wait/signal selection.

## Control Flow

The function is straight-line ring emission: encode address, emit low/high registers, emit command, and return true to signal that hardware semaphore support exists.

## State and Persistence Behavior

No C-side state is persisted. The command stream updates hardware semaphore behavior when executed by the UVD ring.

## Dependencies and Integration Points

- Depends on Radeon ring writing, semaphore objects, `PACKET0`, and `nid.h` register definitions.
- Used as a generation callback by Radeon UVD ring synchronization paths.

## Risks and Edge Cases

- The address encoding requires the semaphore object to be aligned as expected by hardware.
- Because this file only supplies semaphore emission, all start/resume/fence behavior must be correctly paired from adjacent UVD generation code.

## Test Signals

- Ring capture should show `UVD_SEMA_CMD` values `0x81` for wait and `0x80` for signal.
- Cross-ring synchronization tests should confirm semaphore waits/signals complete without deadlock on UVD 3.1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v3_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v4_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v4_2.c

## Purpose

`uvd_v4_2.c` implements UVD 4.2 firmware memory-controller resume programming. It handles the newer firmware-header layout, programs VCPU cache ranges, writes high address extension registers, and passes the maximum handle count to firmware when needed.

## Important APIs, Types, and Functions

- `uvd_v4_2_resume()` is the sole entry point. It computes firmware start address with an optional `0x200` header skip, writes cache offsets/sizes for firmware, heap, and stack/session memory, writes `UVD_LMI_ADDR_EXT` and `UVD_LMI_EXT40_ADDR`, and optionally writes `UVD_GP_SCRATCH4`.

## Control Flow

Resume derives the firmware cache base from `rdev->uvd.gpu_addr`, skipping the header only when `rdev->uvd.fw_header_present` is true. It then lays out heap and stack/session regions contiguously after the firmware region and writes high address bits separately. New-header firmware receives `max_handles` through scratch register 4.

## State and Persistence Behavior

The function persists firmware buffer layout and max handle count in UVD hardware registers. It assumes generic UVD resume/firmware upload has already established `rdev->uvd.gpu_addr`, `rdev->uvd_fw`, and `rdev->uvd.max_handles`.

## Dependencies and Integration Points

- Depends on Radeon UVD state and `cikd.h` register definitions.
- Used by ASIC resume paths for UVD 4.2 generation chips.

## Risks and Edge Cases

- The firmware size calculation still uses `uvd_fw->size + 4` even when the programmed start skips a 0x200-byte header; buffer layout must account for the header convention exactly.
- No call to `radeon_uvd_resume()` appears in this function, so caller sequencing must perform generic firmware resume before invoking it.
- Address extension registers are derived from the BO base, while cache offset0 may be header-skipped; this must match hardware semantics for upper bits.

## Test Signals

- Resume tests should cover both header-present and legacy firmware images and confirm offset0 differs by 0x200 >> 3 only for new firmware.
- Firmware boot tests should confirm `UVD_GP_SCRATCH4` is programmed with `max_handles` when the header is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/uvd_v4_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce.h

## Purpose

`vce.h` is the private Radeon VCE header for generation-specific media clock-gating control. It forward declares `struct radeon_device` and exposes MGC clock-gating toggles for VCE 1.0 and VCE 2.0 implementations.

## Important APIs, Types, and Functions

- `vce_v1_0_enable_mgcg(struct radeon_device *rdev, bool enable)`.
- `vce_v2_0_enable_mgcg(struct radeon_device *rdev, bool enable)`.

## Control Flow

The header has no runtime flow. Callers such as Trinity DPM include it to turn VCE medium-grain clock gating off while encoding clocks are active and on again when VCE clocks are disabled.

## State and Persistence Behavior

No state is stored in the header. Implementations persist changes in VCE hardware clock-gating registers.

## Dependencies and Integration Points

- Consumed by `trinity_dpm.c`, `vce_v1_0.c`, and `vce_v2_0.c`.
- Requires callers to include a definition for `bool` and the Radeon device type through surrounding includes.

## Risks and Edge Cases

- This header exposes only clock-gating toggles, so other VCE generation functions must be declared elsewhere or through ASIC callback tables.
- Calling the wrong generation function for an ASIC can write incompatible registers.

## Test Signals

- Build coverage should ensure VCE MGC clock-gating prototypes match both implementation files and all callers.
- Runtime clock tests should verify VCE gating changes match the selected ASIC generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v1_0.c

## Purpose

`vce_v1_0.c` implements first-generation Radeon Video Coding Engine support: firmware signature preparation, BO sizing, memory-controller/cache setup, firmware authentication polling, clock-gating control, dual VCE ring start, ring pointer accessors, and init-time ring tests.

## Important APIs, Types, and Functions

- `struct vce_v1_0_fw_signature` describes the signed firmware metadata, chip-id entries, nonces, signatures, and key select value.
- Ring callbacks `vce_v1_0_get_rptr()`, `vce_v1_0_get_wptr()`, and `vce_v1_0_set_wptr()` select ring 1 or ring 2 registers based on `ring->idx`.
- `vce_v1_0_enable_mgcg()` and `vce_v1_0_init_cg()` program VCE/UENC clock-gating registers.
- `vce_v1_0_load_fw()` selects a signature by chip ID, writes nonce, firmware payload, signature, and `rdev->vce.keyselect` into the VCE BO image.
- `vce_v1_0_bo_size()` returns firmware plus stack plus per-handle data size.
- `vce_v1_0_resume()` programs LMI/cache registers, scratch max-handle count, firmware keyselect, polls firmware status for done/pass/not-busy, then initializes clock gating.
- `vce_v1_0_start()` sets ring base/size/pointers for both VCE rings, resets and boots ECPU/FME blocks, polls `VCE_STATUS`, and clears the busy flag.
- `vce_v1_0_init()` starts VCE, marks both rings ready, and runs ring tests.

## Control Flow

Firmware load runs before resume and transforms the signed firmware blob into the BO layout expected by the VCE security engine. Resume disables/initializes gating, configures LMI and three cache regions at fixed sizes after a 256-byte header, writes keyselect, waits for firmware authentication to complete/pass, waits for the busy bit to clear, and initializes clock gating.

Start configures both ring buffers, enables VCPU clock, asserts/deasserts soft resets, waits for status bit 2 with retry resets, clears busy, and returns success only when the engine responds. Init then validates both rings independently and leaves their `ready` flags true only after successful tests.

## State and Persistence Behavior

Persistent driver state includes `rdev->vce.keyselect`, VCE BO GPU address, ring `wptr/ready`, and firmware object data. Hardware state includes LMI/cache range registers, firmware authentication state, clock-gating registers, status bits, reset bits, ring base/size/pointer registers, and scratch max-handle count.

## Dependencies and Integration Points

- Uses Radeon firmware, ring, ASIC family, register, and clock-gating infrastructure.
- Register definitions come from `sid.h`; ring indexes use Trinity/Southern Islands VCE ring constants.
- `trinity_dpm.c` calls `vce_v1_0_enable_mgcg()` around VCE clock changes.

## Risks and Edge Cases

- `vce_v1_0_load_fw()` trusts signature header fields enough to copy `rdev->vce_fw->size - sizeof(*sign)` into the target buffer; malformed firmware could exceed fixed BO layout despite `bo_size()` warning only checking total firmware size.
- Signature table iteration uses firmware-provided `num` without bounding it to the fixed `val[8]` array.
- `vce_v1_0_bo_size()` uses `WARN_ON()` but still returns a size even if firmware is larger than the fixed VCE firmware area.
- Start failure returns `-1` rather than a specific errno.
- Long polling delays can make failure paths slow.

## Test Signals

- Firmware-load tests should cover each supported family chip ID and malformed signature counts/lengths.
- Resume tests should validate firmware status done/pass/busy handling and timeout/error returns.
- Ring tests should confirm both VCE rings are programmed and tested independently.
- Clock-gating tests should verify registers change only when `RADEON_CG_SUPPORT_VCE_MGCG` permits enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v2_0.c

## Purpose

`vce_v2_0.c` implements VCE 2.0 resume-time memory-controller/cache setup and generation-specific medium-grain clock-gating behavior. Compared with VCE 1.0, it uses a 40-bit cache BAR register and separates dynamic versus software clock gating paths.

## Important APIs, Types, and Functions

- `vce_v2_0_set_sw_cg()` programs software clock-gating bits in `VCE_CLOCK_GATING_B`, `VCE_UENC_CLOCK_GATING`, `VCE_UENC_REG_CLOCK_GATING`, and `VCE_CGTT_CLK_OVERRIDE`.
- `vce_v2_0_set_dyn_cg()` programs dynamic clock-gating bits and clears stale UENC gating masks.
- `vce_v2_0_disable_cg()` forces the clock override.
- `vce_v2_0_enable_mgcg()` chooses dynamic clock gating by default and gates only when requested and supported by `rdev->cg_flags`.
- `vce_v2_0_init_cg()` programs gating delay timers and wait-awake behavior.
- `vce_v2_0_bo_size()` returns firmware plus stack plus per-handle data size.
- `vce_v2_0_resume()` initializes LMI/cache registers, writes `VCE_LMI_VCPU_CACHE_40BIT_BAR`, programs three cache regions, enables trap interrupts, and initializes clock gating.

## Control Flow

Resume first disables/normalizes clock-gating state, configures LMI/cache/swap/VM registers, writes the upper address BAR from the VCE BO, programs firmware/stack/data cache windows, enables trap interrupt delivery, and initializes generation-specific clock-gating timers. MGC clock gating can later be toggled by DPM or ASIC code through `vce_v2_0_enable_mgcg()`.

## State and Persistence Behavior

Persistent hardware state includes VCE cache BAR and offsets/sizes, interrupt enable, LMI state, clock-gating registers, and clock override state. The file stores no private C state.

## Dependencies and Integration Points

- Depends on Radeon VCE firmware state, `RADEON_MAX_VCE_HANDLES`, `rdev->cg_flags`, register access macros, and `cikd.h`.
- Used by Radeon ASIC generation tables and by callers that toggle VCE MGC clock gating through `vce.h`.

## Risks and Edge Cases

- `vce_v2_0_bo_size()` warns if firmware exceeds 256 KiB but does not fail; callers must enforce allocation/upload safety elsewhere.
- The local `sw_cg` debug variable is hardcoded false, so software clock-gating paths are present but not normally exercised.
- Cache offset programming masks addresses with `0x7fffffff` after reducing `addr` to low bits; mistakes in BAR/offset split would break high-address BO placement.

## Test Signals

- Resume tests should validate cache BAR/offset programming for BOs above 4 GiB.
- Clock-gating tests should exercise enable/disable paths with and without `RADEON_CG_SUPPORT_VCE_MGCG`.
- Interrupt tests should confirm trap interrupt enable is set after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/vce_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Kconfig

## Purpose

This top-level Renesas DRM Kconfig file includes the three Renesas display-driver configuration namespaces: R-Car DU, RZ/G2L DU, and legacy shmobile.

## Important APIs, Types, and Functions

- Sources `drivers/gpu/drm/renesas/rcar-du/Kconfig`.
- Sources `drivers/gpu/drm/renesas/rz-du/Kconfig`.
- Sources `drivers/gpu/drm/renesas/shmobile/Kconfig`.

## Control Flow

Kconfig evaluation enters this file from the parent DRM Kconfig and then evaluates the included subdriver menus/options.

## State and Persistence Behavior

No runtime state. The selected configuration symbols persist into the kernel build configuration and control compiled objects.

## Dependencies and Integration Points

Integrates Renesas DRM subdrivers into the main DRM configuration tree.

## Risks and Edge Cases

Renaming or moving subdirectories requires updating these source paths or the Renesas DRM menu will lose options.

## Test Signals

Configuration tests should confirm `DRM_RCAR_DU`, RZ DU, and shmobile options appear under DRM after Kconfig parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Makefile

## Purpose

This top-level Renesas DRM Makefile descends into Renesas display subdirectories and conditionally builds the shmobile driver directory.

## Important APIs, Types, and Functions

- Always includes `rcar-du/` and `rz-du/` through `obj-y`.
- Includes `shmobile/` only when `CONFIG_DRM_SHMOBILE` is enabled.

## Control Flow

Kbuild traverses the listed subdirectories during DRM driver compilation. Individual subdirectory Makefiles decide which objects are emitted based on their Kconfig symbols.

## State and Persistence Behavior

No runtime state. It affects build graph membership.

## Dependencies and Integration Points

Connected to Kbuild and the Kconfig symbols in this directory tree.

## Risks and Edge Cases

Because `rcar-du/` and `rz-du/` are always traversed, their Makefiles must keep object emission fully gated by config symbols.

## Test Signals

Build tests with Renesas options disabled should traverse these directories without producing unwanted modules or built-in objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Kconfig

## Purpose

`rcar-du/Kconfig` defines build-time options for the Renesas R-Car Display Unit DRM driver and its companion CMM, HDMI, LVDS, MIPI DSI, VSP compositor, and writeback support.

## Important APIs, Types, and Functions

- `DRM_RCAR_DU` is the main tristate driver option and selects KMS, display helper, bridge connector, GEM DMA helper, and videomode helpers.
- `DRM_RCAR_USE_CMM` and `DRM_RCAR_CMM` control Color Management Module support.
- `DRM_RCAR_DW_HDMI` enables the internal DesignWare HDMI encoder glue.
- `DRM_RCAR_USE_LVDS` and `DRM_RCAR_LVDS` control embedded LVDS encoder support.
- `DRM_RCAR_USE_MIPI_DSI` and `DRM_RCAR_MIPI_DSI` control embedded MIPI DSI encoder support.
- `DRM_RCAR_VSP` enables VSP1 compositor-backed KMS planes and has dependency logic to keep VSP1 and DU linkage buildable.
- `DRM_RCAR_WRITEBACK` defaults to yes on ARM64 and depends on the main DU driver.

## Control Flow

Kconfig dependencies restrict visibility and selection by architecture, OF, DRM core, bridge, PM, reset, VSP1, and module/built-in compatibility. The main driver can be built as module or built-in; dependent companions follow tristate or bool defaults.

## State and Persistence Behavior

No runtime state. Selected symbols determine compiled object files and conditional code paths, including stub versus real CMM functions and VSP/writeback objects.

## Dependencies and Integration Points

Connects R-Car DU to DRM core helpers, bridge/panel/MIPI/DesignWare HDMI libraries, reset controller, PM, and media VSP1 driver configuration.

## Risks and Edge Cases

- VSP dependency must prevent an illegal built-in DU from depending on modular VSP1.
- Default-enabling companion support can expose probe deferrals when firmware/DT nodes reference bridges or CMM devices not yet available.
- Disabling `DRM_RCAR_USE_CMM` compiles CMM stubs, so color-management paths must behave correctly without hardware support.

## Test Signals

- Matrix builds should cover DU disabled, DU module, DU built-in, CMM disabled, LVDS/DSI/HDMI enabled, VSP module compatibility, ARM, ARM64, and COMPILE_TEST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Makefile

## Purpose

The R-Car DU Makefile defines the main `rcar-du-drm` composite object and optional companion objects for CMM, HDMI, LVDS, MIPI DSI, VSP, and writeback.

## Important APIs, Types, and Functions

- `rcar-du-drm-y` consists of `rcar_du_crtc.o`, `rcar_du_drv.o`, `rcar_du_encoder.o`, `rcar_du_group.o`, `rcar_du_kms.o`, and `rcar_du_plane.o`.
- `rcar-du-drm-$(CONFIG_DRM_RCAR_VSP)` adds `rcar_du_vsp.o`.
- `rcar-du-drm-$(CONFIG_DRM_RCAR_WRITEBACK)` adds `rcar_du_writeback.o`.
- Separate module/built-in objects are gated for `rcar_cmm.o`, `rcar_dw_hdmi.o`, `rcar_lvds.o`, and `rcar_mipi_dsi.o`.

## Control Flow

Kbuild combines core DU objects into one driver when `CONFIG_DRM_RCAR_DU` is enabled and conditionally extends it with VSP/writeback support. Companion hardware blocks build as separate objects/modules under their own symbols.

## State and Persistence Behavior

No runtime state. It controls link composition and module boundaries.

## Dependencies and Integration Points

Works with Kconfig symbols in the same directory. The object split matches source-level responsibilities: platform driver, KMS setup, CRTCs, groups, planes, encoders, VSP/writeback, and bridge-specific companion drivers.

## Risks and Edge Cases

If a source file uses symbols from optional objects without Kconfig guards or stubs, link failures can occur in partial configurations.

## Test Signals

Build coverage should verify each optional symbol toggles the expected object and that `rcar-du-drm` links with and without VSP/writeback support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.c

## Purpose

`rcar_cmm.c` implements the Renesas R-Car Color Management Module driver used by R-Car DU CRTCs for gamma/LUT programming. It probes standalone CMM platform devices, maps registers, manages runtime PM, and exports setup/enable/disable/init functions to the DU driver.

## Important APIs, Types, and Functions

- `struct rcar_cmm` stores MMIO base and 1D LUT enabled state.
- `rcar_cmm_lut_write()` converts 16-bit DRM LUT entries to 8-bit hardware RGB fields and writes all `CM2_LUT_SIZE` entries.
- `rcar_cmm_setup()` enables/disables the LUT and writes table entries from `struct rcar_cmm_config`.
- `rcar_cmm_enable()` performs `pm_runtime_resume_and_get()`.
- `rcar_cmm_disable()` disables LUT state and calls `pm_runtime_put()`.
- `rcar_cmm_init()` validates that the CMM platform device has probed by checking driver data.
- `rcar_cmm_probe()` allocates state, maps the MMIO resource, and enables runtime PM.
- `rcar_cmm_remove()` disables runtime PM.

## Control Flow

The platform driver probes CMM nodes matching Gen2/Gen3 compatibles. The DU driver later finds CMM devices from `renesas,cmms`, calls `rcar_cmm_init()`, links device PM ordering, then calls `rcar_cmm_enable()` before a CRTC starts and `rcar_cmm_setup()` during atomic color-management updates. Disable clears LUT control and drops runtime PM.

## State and Persistence Behavior

Persistent driver state is `struct rcar_cmm` in platform driver data. LUT enabled state is cached to avoid redundant control writes. Hardware LUT table contents persist while powered, but `rcar_cmm_disable()` documents that internal processing state is lost and must be restored after the next enable.

## Dependencies and Integration Points

- Uses Linux platform, IO, OF, module, and runtime PM APIs.
- Uses DRM color-management helpers for LUT extraction.
- Exports symbols consumed by `rcar_du_crtc.c` and `rcar_du_kms.c`.

## Risks and Edge Cases

- `rcar_cmm_setup()` assumes the unit is powered and clocked; calling it without `rcar_cmm_enable()` can access suspended hardware.
- LUT updates are not double-buffered, so changing entries while scanning out can affect the current frame.
- Enable/disable calls are explicitly not reference-counted; unbalanced calls can mis-handle runtime PM and cached LUT state.
- `rcar_cmm_init()` returns `-EPROBE_DEFER` until probe sets drvdata; caller must propagate deferral.

## Test Signals

- Probe tests should validate MMIO mapping, runtime PM enable, and OF matching for Gen2/Gen3 compatibles.
- Atomic gamma tests should cover exactly 256-entry LUTs, NULL LUT disable, enable/setup/disable cycles, and suspend/resume ordering with DU.
- Visual tests should verify LUT colors and watch for tearing/artifacts during live LUT updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.h

## Purpose

`rcar_cmm.h` defines the DU-facing CMM API and configuration structure. It also provides no-op or error-returning stubs when CMM support is not compiled.

## Important APIs, Types, and Functions

- `CM2_LUT_SIZE` defines the required 256-entry 1D LUT size.
- `struct rcar_cmm_config` carries an optional `drm_color_lut` table; NULL disables LUT processing.
- Real APIs under `CONFIG_DRM_RCAR_CMM`: `rcar_cmm_init()`, `rcar_cmm_enable()`, `rcar_cmm_disable()`, and `rcar_cmm_setup()`.
- Stub APIs return `-ENODEV` for init, success for enable/setup, and no-op for disable.

## Control Flow

DU code can call the same functions regardless of configuration. In disabled builds, `rcar_cmm_init()` tells KMS setup that support is unavailable, while runtime calls become harmless stubs.

## State and Persistence Behavior

The header stores no state. The config object describes one requested CMM state update.

## Dependencies and Integration Points

- Forward declares `struct device` and `struct drm_color_lut`.
- Consumed by CMM implementation, CRTC color-management setup, and KMS CMM discovery.

## Risks and Edge Cases

- Stub `rcar_cmm_enable()` returning success means callers must only call runtime setup when they actually associated a real CMM device.
- The API contract that setup requires prior enable is documented in the C file, not enforced by type or state.

## Test Signals

- Build tests should cover CMM enabled and disabled configurations.
- CRTC gamma tests should reject non-`CM2_LUT_SIZE` LUT blobs before calling setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_cmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.c

## Purpose

`rcar_du_crtc.c` implements R-Car DU CRTC objects and runtime display-channel control. It programs display timings and clocks, handles start/stop, page flips, vblank IRQs, CMM setup, VSP clock/source integration, CRC source control, and CRTC creation for Gen2/Gen3/Gen4 hardware variants.

## Important APIs, Types, and Functions

- Register access helpers offset CRTC registers by `rcrtc->mmio_offset`; `rcar_du_crtc_dsysr_clr_set()` updates cached `dsysr` and writes DSYSR.
- Clock/timing helpers include `rcar_du_dpll_divider()`, `rcar_du_escr_divider()`, and `rcar_du_crtc_set_display_timing()`.
- Plane composition is updated by `rcar_du_crtc_update_planes()`, which sorts visible planes by zpos, writes DS1PR/DS2PR, updates DPTSR association, and restarts groups when required.
- Page flip helpers are `rcar_du_crtc_finish_page_flip()`, `rcar_du_crtc_page_flip_pending()`, and `rcar_du_crtc_wait_page_flip()`.
- CMM helpers `rcar_du_cmm_check()` and `rcar_du_cmm_setup()` validate and apply gamma LUTs.
- Lifecycle helpers are `rcar_du_crtc_get()`, `rcar_du_crtc_put()`, `rcar_du_crtc_start()`, `rcar_du_crtc_disable_planes()`, and `rcar_du_crtc_stop()`.
- Atomic hooks implement check, begin, flush, enable, disable, and mode validation.
- CRC helpers build source names, parse/verify/set CRC source through atomic commits, and expose Gen3 CRC callbacks.
- `rcar_du_crtc_irq()` handles vblank status, acknowledges interrupts, wakes waiters, and completes page flips on Gen2.
- `rcar_du_crtc_create()` creates DRM CRTCs, selects primary plane, wires CMM/color management, requests IRQs, and initializes CRC sources.

## Control Flow

CRTC creation resolves functional and optional external clocks, initializes wait queues/locks/state, selects the primary plane from VSP or DU planes, initializes the DRM CRTC, links CMM and gamma properties if available, registers helper callbacks, requests the correct IRQ, and prepares CRC sources for Gen3+.

Atomic enable powers CMM, gets/enables clocks and group resources, programs display timings and routing, optionally enables LVDS/DSI pixel clocks early, starts the DU group, and applies CMM LUT setup. Atomic begin ensures the CRTC is initialized before plane programming and applies color-management-only updates. Atomic flush updates plane assignment/registers, captures page-flip events under event lock, and flushes VSP if used. Atomic disable stops the CRTC, releases resources, disables companion pixel clocks, and completes any pending event.

Stop sequencing disables planes and waits for vblank so stale framebuffers are not scanned after restart, waits for page flips, turns vblank off, disables VSP and CMM, switches sync mode if supported, and stops the group.

## State and Persistence Behavior

Driver state in `struct rcar_du_crtc` includes cached DSYSR, initialized flag, vblank enabled flag, pending flip event, wait queues, vblank countdown, group/CMM/VSP links, CRC source strings, and writeback connector. Hardware state includes clocks, DPLL/ESCR, timing registers, DSMR polarity, DSYSR start/reset/sync bits, DS1PR/DS2PR plane priorities, DPTSR associations, interrupt enable/status, CMM routing, and bridge-provided pixel clocks.

## Dependencies and Integration Points

- Depends on DRM atomic helpers, vblank, bridge, CRTC state, writeback, GEM DMA scanout, and event locking.
- Integrates with R-Car group, plane, KMS, CMM, VSP, LVDS, MIPI DSI, and register headers.
- Uses media `vsp1_du_crc_config` for CRC source state.

## Risks and Edge Cases

- DPTSR and source changes require group restarts, producing visible flicker by design.
- CMM adds a 25-pixel timing offset and stricter mode-valid constraints; routing CMM when no color management is used is a TODO.
- Page flip timeout forcibly completes the event after 50 ms, which preserves userspace progress but can hide lost interrupts or hardware stalls.
- `drm_crtc_vblank_get()` warning in atomic flush assumes vblank can always be acquired when events are queued.
- DPLL calculations are optimized for 64-bit arithmetic and only used on 64-bit-capable paths; future 32-bit usage could overflow.
- Early LVDS/DSI pixel clock enable/disable must match bridge behavior and output bitmasks exactly.

## Test Signals

- Mode tests should cover interlaced rejection, minimum porch constraints, CMM and non-CMM timing offsets, DPLL channels, external dot clocks, LVDS/DSI clock routing, and Gen2 versus Gen3 limits.
- Atomic tests should validate enable/begin/flush/disable ordering, pending event completion, group restart conditions, and plane priority/zpos ordering.
- IRQ tests should verify vblank ack, vblank wait countdown, page flip completion, and shared IRQ behavior on older hardware.
- CRC tests should list `auto` and `plane<ID>` sources, reject invalid names, and apply source changes through atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.h

## Purpose

`rcar_du_crtc.h` declares the R-Car DU CRTC data structures, state extensions, conversion helpers, and cross-file APIs for CRTC creation, page-flip completion, and DSYSR updates.

## Important APIs, Types, and Functions

- `struct rcar_du_crtc` embeds `struct drm_crtc` and stores DU device/group links, clocks, hardware index, MMIO offset, cached DSYSR, vblank/event state, CMM/VSP/writeback links, and CRC source metadata.
- `struct rcar_du_crtc_state` extends DRM CRTC state with VSP CRC configuration and a bitmask of driven DU outputs.
- `to_rcar_crtc()`, `wb_to_rcar_crtc()`, and `to_rcar_crtc_state()` provide container conversions.
- Exported functions: `rcar_du_crtc_create()`, `rcar_du_crtc_finish_page_flip()`, and `rcar_du_crtc_dsysr_clr_set()`.

## Control Flow

The header supports KMS setup (`rcar_du_crtc_create()`), group start/stop (`rcar_du_crtc_dsysr_clr_set()`), and VSP/writeback/IRQ paths that need to complete page flips.

## State and Persistence Behavior

The structures define the persistent per-CRTC state used for runtime PM, vblank synchronization, page-flip events, output routing, and CRC configuration. `dsysr` is a software cache of a hardware register to keep read/modify/write operations coherent.

## Dependencies and Integration Points

- Includes DRM CRTC/writeback, Linux wait/spinlock/mutex, and media VSP1 CRC definitions.
- Referenced by driver, group, KMS, VSP, writeback, and CRTC implementation files.

## Risks and Edge Cases

- Several fields are touched from IRQ and atomic paths; event and vblank fields require the locks documented by implementation, not enforced in the structure.
- `sources` strings are dynamically allocated for CRC and must be cleaned only on Gen3 paths that allocate them.

## Test Signals

- Build and runtime tests should verify CRTC state duplication/reset preserves CRC defaults and output routing state.
- Lockdep should remain clean for vblank/event wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.c

## Purpose

`rcar_du_drv.c` is the R-Car DU DRM platform driver. It provides SoC-specific capability tables, OF matching, DRM driver operations, suspend/resume integration, probe/remove/shutdown flow, DMA mask setup, and device registration.

## Important APIs, Types, and Functions

- Static `struct rcar_du_device_info` instances describe each supported Renesas SoC generation, features, quirks, channels, output routes, LVDS count, VSP RPF count, DPLL mask, and LVDS/DSI dot-clock masks.
- `rcar_du_of_table` maps compatible strings to those info structures.
- `rcar_du_output_name()` converts output enum values to debug strings.
- `rcar_du_driver` is the DRM driver with GEM, modeset, atomic, dumb-buffer, PRIME import, fbdev DMA, fops, and metadata callbacks.
- `rcar_du_pm_suspend()` and `rcar_du_pm_resume()` call DRM mode-config suspend/resume helpers.
- `rcar_du_probe()` allocates `struct rcar_du_device`, maps MMIO, chooses DMA mask width, initializes modeset, registers DRM, and starts client setup.
- `rcar_du_remove()` unregisters DRM, shuts down atomic state, and finalizes polling; `rcar_du_shutdown()` performs atomic shutdown.

## Control Flow

Probe exits early when firmware-only DRM drivers are requested. Otherwise it allocates a managed DRM device, stores OF match data, maps registers, coerces DMA mask to 40 bits when VSP sources handle memory access or 32 bits for direct DU scanout, initializes KMS objects, registers the DRM device, logs success, and enables generic client setup. Errors after modeset init clean up KMS polling.

Remove unregisters first so userspace cannot submit new work, then shuts down atomic state and polling. PM suspend/resume defers to DRM helpers to suspend active modesets and restore them.

## State and Persistence Behavior

SoC capability tables are immutable. Per-device persistent state lives in `struct rcar_du_device`, allocated as part of the DRM device. Probe records MMIO base, route policy, bridge pointers, CRTC/group/CMM/VSP arrays, properties, and runtime routing defaults through KMS init. DRM registration persists userspace-visible device state until remove.

## Dependencies and Integration Points

- Integrates Linux platform/OF/DMA/PM/module APIs with DRM core, GEM DMA helpers, fbdev DMA helpers, atomic helpers, probe helpers, and managed DRM allocation.
- Calls `rcar_du_modeset_init()` from `rcar_du_kms.c`.
- SoC tables are consumed by KMS, CRTC, group, plane, encoder, VSP, CMM, and bridge-specific code.

## Risks and Edge Cases

- SoC route tables are the source of truth for possible CRTCs and DT port mapping; mistakes lead to missing connectors or invalid routing.
- DMA mask selection assumes VSP-backed DU never performs memory access; mixed paths must preserve that invariant.
- Some route comments mention unsupported outputs such as TCON/analog, so DTs exposing them may be skipped or unsupported.
- Probe deferral handling intentionally avoids `dev_err_probe()` in one path to preserve recorded deferral reason; changing error logging could obscure real probe dependencies.

## Test Signals

- OF probe tests should cover every compatible and route table with representative DT endpoints.
- Build/runtime tests should cover direct scanout versus VSP-backed DMA masks.
- Suspend/resume and shutdown tests should ensure active displays are quiesced and restored without stale scanout.
- Connector enumeration should match expected outputs for each SoC info table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.h

## Purpose

`rcar_du_drv.h` defines the main R-Car DU device model, SoC capability descriptors, output identifiers, feature/quirk flags, MMIO helpers, and cross-file driver utility APIs.

## Important APIs, Types, and Functions

- Feature flags describe per-CRTC IRQs/clocks, VSP1 sources, interlaced support, TVM sync, and no-blending variants.
- `enum rcar_du_output` lists DPAD, DSI, HDMI, LVDS, TCON, and max output identifiers.
- `struct rcar_du_output_routing` maps an output to possible CRTCs and DT port number.
- `struct rcar_du_device_info` is immutable SoC metadata consumed throughout the driver.
- `struct rcar_du_cmm` stores associated CMM device and PM device link.
- `struct rcar_du_device` embeds the DRM device and stores MMIO, CRTC/group/CMM/VSP arrays, LVDS/DSI bridge pointers, shared properties, and runtime output routing selections.
- Inline helpers include `to_rcar_du_device()`, `rcar_du_has()`, `rcar_du_needs()`, `rcar_du_read()`, and `rcar_du_write()`.

## Control Flow

The header has no runtime flow, but its structures define how probe, modeset init, atomic commit, CRTC, group, encoder, and plane code share device-wide state.

## State and Persistence Behavior

`struct rcar_du_device` is the persistent per-device state for the whole DRM driver. Runtime routing fields such as `dpad0_source`, `dpad1_source`, and `vspd1_sink` are updated by atomic/KMS paths and consumed by group register programming.

## Dependencies and Integration Points

- Includes DRM device and local CMM/CRTC/group/VSP headers.
- Used by nearly every R-Car DU source file.

## Risks and Edge Cases

- Arrays are sized by maximum hardware limits; SoC tables and `num_crtcs` must never exceed those limits.
- Runtime routing fields are shared across atomic commit and group setup paths; invalid defaults can program impossible DPAD/VSP routes.
- The inline MMIO helpers perform no bounds checking.

## Test Signals

- Compile-time and probe tests should validate each SoC table fits `RCAR_DU_MAX_*` capacities.
- Atomic routing tests should inspect `dpad0_source`, `dpad1_source`, and `vspd1_sink` changes across connector combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.c

## Purpose

`rcar_du_encoder.c` creates DRM encoders and bridge connectors for DU output routes described by device tree. It handles direct DPAD panels, generic bridges, LVDS/DSI bridge bookkeeping, Gen3 LVDS dual-link/connection filtering, and connector attachment.

## Important APIs, Types, and Functions

- `rcar_du_encoder_count_ports()` counts `port` children under a node or the node itself.
- `rcar_du_encoder_init()` resolves a panel or bridge for one output, allocates `struct rcar_du_encoder`, attaches the bridge without a connector, creates a bridge connector, and attaches it to the encoder.
- `rcar_du_encoder_funcs` is currently empty, relying on DRM managed cleanup/default behavior.

## Control Flow

For DPAD outputs with a single port, the node is treated as a panel and wrapped with a panel bridge. Other outputs locate an existing DRM bridge from the DT node and store LVDS/DSI bridge pointers in the DU device for later pixel-clock control. Gen3 skips LVDS1 when it is a companion in dual-link mode and skips disconnected LVDS outputs. Finally, a managed DRM encoder is allocated, the bridge chain is attached, a connector is created from the bridge chain, and the connector is attached to the encoder.

## State and Persistence Behavior

Persistent state includes the managed `struct rcar_du_encoder` and its output enum. DU device state may store bridge pointers in `rcdu->lvds[]` or `rcdu->dsi[]`. DRM connector/encoder/bridge attachments persist for the DRM device lifetime.

## Dependencies and Integration Points

- Uses OF graph/device nodes, DRM bridge, bridge connector, panel bridge, and local LVDS helpers.
- Called by `rcar_du_kms.c` while iterating endpoints from DT route tables.

## Risks and Edge Cases

- `of_drm_find_bridge()` returning NULL is treated as probe deferral, so absent bridges can defer the whole DU if DT indicates they should exist.
- DPAD single-port heuristic assumes such nodes describe panels; unusual bridge DT layouts could be misclassified.
- Gen3 LVDS filtering depends on `rcar_lvds_dual_link()` and `rcar_lvds_is_connected()` matching hardware topology.

## Test Signals

- DT tests should cover DPAD panel bridge, external bridges, HDMI/LVDS/DSI outputs, disconnected LVDS, and dual-link LVDS companion behavior.
- Connector enumeration should show exactly one connector per usable output pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.h

## Purpose

`rcar_du_encoder.h` declares the R-Car DU encoder wrapper and initialization API used by KMS setup.

## Important APIs, Types, and Functions

- `struct rcar_du_encoder` embeds `struct drm_encoder` and stores the `enum rcar_du_output` route it represents.
- `to_rcar_encoder()` converts DRM encoders to the driver wrapper.
- `rcar_du_encoder_init()` initializes one encoder/bridge/connector chain.

## Control Flow

The header enables KMS code to initialize encoders per DT endpoint and later recover output route information from encoder masks during atomic CRTC checks.

## State and Persistence Behavior

Each encoder's persistent route identity is stored in `output` and consumed by CRTC output-routing state.

## Dependencies and Integration Points

- Includes DRM encoder definitions and depends on `enum rcar_du_output` from the driver header.
- Used by KMS and CRTC code.

## Risks and Edge Cases

- The container conversion assumes all relevant non-writeback encoders are allocated as `struct rcar_du_encoder`; CRTC code explicitly skips virtual writeback encoders.

## Test Signals

- Atomic routing tests should confirm encoder output IDs are reflected in `rcar_du_crtc_state::outputs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.c

## Purpose

`rcar_du_group.c` manages DU semi-global resources shared by one or two CRTCs: extended feature registers, pin/output routing, dot-clock routing, plane/timing associations, group start/stop/restart, DPAD levels, and Gen2/Gen3 VSP/DPAD routing.

## Important APIs, Types, and Functions

- `rcar_du_group_read()` and `rcar_du_group_write()` access group-relative registers.
- Setup helpers program pins (`DEFR6`), output/VSP routing (`DEFR8`), dot-clock routing (`DIDSR`), extended feature registers, CMM enable bits, DORCR, and DPTSR.
- `rcar_du_group_get()` initializes group registers on first use and increments `use_count`; `rcar_du_group_put()` decrements it.
- `rcar_du_group_start_stop()` tracks active CRTCs and starts/stops or restarts the hardware group as needed.
- `rcar_du_group_restart()` toggles reset/start for configuration changes requiring DRES.
- `rcar_du_set_dpad0_vsp1_routing()` updates DEFR8 with temporary clock enable for routes that can be changed while CRTCs are disabled.
- `rcar_du_group_set_routing()` programs DPAD1 source, fixed DPAD output levels, and DPAD0/VSP1 routing.

## Control Flow

The first CRTC to get a group triggers `rcar_du_group_setup()`, which programs generation-specific extended features, CMM routing, dot-clock routing, default plane priorities, and DPTSR. Starting a CRTC increments `used_crtcs`; if another CRTC is already active, the group is briefly stopped before restart because some bits only latch during reset. Stopping decrements `used_crtcs` and stops hardware only when the last CRTC stops.

Routing updates are called during CRTC setup/start. DPAD1 routing is set through DORCR, DPAD pins not currently driven by outputs are forced low through DOFLR, and DPAD0/VSP1 routing is applied through DEFR8 with special Gen2/Gen3 placement rules.

## State and Persistence Behavior

Persistent group state includes `use_count`, `used_crtcs`, `dptsr_planes`, `need_restart`, and generation/channel/CMM masks. Hardware state persists in group registers controlling extended features, CMM routing, dot-clock selection, plane priority/association, DPAD output levels, and start/reset bits.

## Dependencies and Integration Points

- Uses CRTC DSYSR helper, driver SoC info, register definitions, clocks, and group mutex.
- Called by CRTC setup/update paths and plane code when VSP1 sink changes.

## Risks and Edge Cases

- `rcar_du_group_put()` blindly decrements `use_count`; imbalance can underflow.
- Group restart causes visible flicker, and many routing/plane association changes still require it.
- Gen2/Gen3 routing rules are highly SoC-specific; wrong `dpad0_source`, `dpad1_source`, or `vspd1_sink` values program invalid routes.
- `rcar_du_set_dpad0_vsp1_routing()` enables a CRTC clock temporarily and assumes the selected CRTC exists for the group index.

## Test Signals

- Multi-CRTC tests should verify `used_crtcs` start/stop behavior and flicker-causing restart cases.
- Route tests should cover DPAD0/DPAD1, VSP1D to DU0/1/2, Gen2 versus Gen3 DEFR8 behavior, and single-channel Gen3/Gen4 groups.
- Plane association tests should inspect DPTSR and DS1PR/DS2PR after source/CRTC changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.h

## Purpose

`rcar_du_group.h` defines the semi-global DU group object and APIs for group register access, reference management, start/stop/restart, routing, and DPAD/VSP routing updates.

## Important APIs, Types, and Functions

- `struct rcar_du_group` stores DU device pointer, MMIO offset, group index, channel/CMM masks, CRTC counts, use counters, DPTSR lock/state, plane array, and restart flag.
- APIs: `rcar_du_group_read()`, `rcar_du_group_write()`, `rcar_du_group_get()`, `rcar_du_group_put()`, `rcar_du_group_start_stop()`, `rcar_du_group_restart()`, `rcar_du_group_set_routing()`, and `rcar_du_set_dpad0_vsp1_routing()`.

## Control Flow

The header provides the cross-file contract used by KMS setup, CRTC lifecycle, and plane source switching. The group lock protects `dptsr_planes` and DPTSR register updates.

## State and Persistence Behavior

Group objects persist for the DRM device lifetime. `use_count` controls one-time setup, `used_crtcs` controls hardware start/stop, and `need_restart` communicates plane/source changes that require a group restart.

## Dependencies and Integration Points

- Includes `rcar_du_plane.h` because groups own the plane array.
- Used by CRTC, KMS, plane, and group implementation files.

## Risks and Edge Cases

- Counter fields require disciplined caller pairing under mode-config locking; the header cannot enforce this.
- Plane array capacity is fixed at `RCAR_DU_NUM_KMS_PLANES`; setup must keep `num_planes` within that bound.

## Test Signals

- Lockdep and atomic tests should verify DPTSR updates are serialized and restart flags are consumed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.c

## Purpose

`rcar_du_kms.c` initializes R-Car DU KMS objects and implements framebuffer, format, GEM import, dumb buffer, atomic check/commit, encoder discovery, VSP/CMM discovery, and mode-config setup.

## Important APIs, Types, and Functions

- `rcar_du_format_infos[]` maps DRM fourcc formats to V4L2 formats, bpp, plane count, subsampling, and DU register fields.
- `rcar_du_format_info()` looks up the driver format descriptor.
- `rcar_du_gem_prime_import_sg_table()` imports DMA-bufs, using normal DMA GEM import for direct scanout and private noncoherent DMA GEM objects for VSP-backed scanout.
- `rcar_du_dumb_create()` enforces pitch alignment quirks and delegates to GEM DMA dumb allocation.
- `rcar_du_fb_create()` validates supported formats, pitch limits/alignment, and chroma plane pitch relationships before creating GEM framebuffers.
- `rcar_du_atomic_check()` runs DRM atomic helper checks and DU plane allocation for non-VSP hardware.
- `rcar_du_atomic_commit_tail()` records DPAD routing from new CRTC state, applies helper disable/plane/enable sequence, waits for flips, and cleans up planes.
- Encoder/CMM/VSP helpers discover DT endpoints/phandles and initialize companion objects.
- `rcar_du_modeset_init()` creates mode config, properties, vblank, groups, planes/VSPs, CMMs, CRTCs, encoders, writeback connectors, default routing, resets config, and starts polling.

## Control Flow

Modeset init sets global mode limits based on generation, initializes shared properties and vblank, creates groups and direct DU planes when VSP is absent, initializes VSP compositors when present, links CMM devices, creates CRTCs for populated hardware channels, creates encoders from OF graph endpoints, assigns possible CRTCs/clones, optionally creates writeback connectors, initializes default DPAD0 source, resets DRM mode config, and enables connector polling.

Framebuffer creation validates format and pitch differently for Gen2 direct DU scanout and Gen3+ VSP-backed scanout. Atomic commits save output routing before helper commit stages so group/CRTC setup can program DPAD routing during enable.

## State and Persistence Behavior

Persistent state includes mode-config limits/functions, shared colorkey property, vblank setup, group plane allocation state, CMM device links, VSP links, CRTC/encoder/connector objects, writeback connectors, and default/runtime DPAD route fields. Imported DMA-buf GEM objects persist until DRM GEM lifetime release.

## Dependencies and Integration Points

- Uses DRM atomic, framebuffer, GEM DMA, dumb buffers, vblank, managed cleanup, and OF graph/platform APIs.
- Integrates local CRTC, group, plane, encoder, CMM, VSP, writeback, and register code.
- Consumes DT properties `renesas,vsps`/legacy `vsps` and `renesas,cmms`.

## Risks and Edge Cases

- `rcar_du_vsps_init()` computes `cells = ret / rcdu->num_crtcs - 1`; malformed property lengths not divisible by CRTC count can produce unexpected cell interpretation.
- CMM discovery calls `of_find_device_by_node()` and must balance references; cleanup handles `put_device(cmm->dev)` and device links.
- Pitch/chroma validation must match both DU hardware and VSP expectations; unsupported multi-planar formats should fail early.
- If no encoder initializes, probe fails with `-EINVAL`.
- `possible_clones` is set to all encoders, assuming at least one clone path between all outputs; hardware routing constraints are mostly represented by `possible_crtcs`.

## Test Signals

- KMS probe tests should cover DT endpoint discovery, missing/disabled bridges, no encoder, CMM disabled/enabled, VSP phandle variants, and writeback on Gen3+.
- Framebuffer tests should cover supported/unsupported formats, Gen2 pitch limits, 128-byte quirk, Gen3 pitch limits, and chroma pitch mismatch.
- Atomic tests should verify DPAD route fields are updated before enables and direct-DU plane allocation is skipped for VSP-backed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.h

## Purpose

`rcar_du_kms.h` declares the KMS-facing format descriptor and core KMS helper APIs for mode-set initialization, dumb-buffer creation, and PRIME SG-table import.

## Important APIs, Types, and Functions

- `struct rcar_du_format_info` stores DRM fourcc, V4L2 format, bits per pixel, plane count, horizontal subsampling, and DU register fields.
- `rcar_du_format_info()` returns a format descriptor for a DRM fourcc.
- `rcar_du_modeset_init()` initializes all KMS objects for a DU device.
- `rcar_du_dumb_create()` and `rcar_du_gem_prime_import_sg_table()` are exported to DRM driver operations.

## Control Flow

The header is used by the platform driver to wire DRM callbacks and start KMS initialization, and by plane/CRTC code to retrieve format programming data.

## State and Persistence Behavior

No state is stored here. Format descriptors are immutable data in `rcar_du_kms.c`.

## Dependencies and Integration Points

- Forward declares DRM/GEM/DMA-buf types and `struct rcar_du_device`.
- Used by driver, CRTC, plane, and KMS implementation files.

## Risks and Edge Cases

- `pnmr` and `edf` fields are register-level details; consumers must apply generation-specific restrictions before programming them.

## Test Signals

- Format lookup tests should ensure every format exposed by direct-DU planes has a descriptor and unsupported formats return NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.c

## Purpose

`rcar_du_plane.c` implements direct DU KMS planes for R-Car DU hardware. It allocates scarce hardware planes during atomic checks, validates plane state, programs scanout/format/color-key registers, handles memory versus live VSP sources, exposes alpha/zpos/colorkey properties, and creates primary/overlay planes per group.

## Important APIs, Types, and Functions

- Hardware allocator helpers: `rcar_du_plane_needs_realloc()`, `rcar_du_plane_hwmask()`, `rcar_du_plane_hwalloc()`, and `rcar_du_atomic_check_planes()`.
- Register programming helpers: `rcar_du_plane_write()`, `rcar_du_plane_setup_scanout()`, `rcar_du_plane_setup_mode()`, `rcar_du_plane_setup_format_gen2()`, `rcar_du_plane_setup_format_gen3()`, `rcar_du_plane_setup_format()`, and `__rcar_du_plane_setup()`.
- Atomic validation/update: `__rcar_du_plane_atomic_check()`, `rcar_du_plane_atomic_check()`, and `rcar_du_plane_atomic_update()`.
- State/property helpers duplicate, destroy, reset, set, and get `struct rcar_du_plane_state`.
- `rcar_du_planes_init()` creates one primary plane per CRTC plus seven overlays, attaches helper funcs, alpha, immutable/dynamic zpos, and colorkey property.

## Control Flow

Atomic check first identifies disabled planes and planes needing reallocation due to format plane-count or source changes. If reallocation is needed, it locks all planes in affected groups through `drm_atomic_get_plane_state()`, computes free hardware plane masks excluding locally freed planes, and assigns hardware planes, preferring planes already associated with the target CRTC to avoid group restart flicker.

Atomic update programs visible planes only. It writes format, destination, alpha/color-key, scanout address/pitch/source positions, and for two-plane formats configures the adjacent hardware plane. If the source changes between memory and live VSP, it marks the group for restart because the VSPS bit only latches under reset. VSPD1 sink changes update DPAD/VSP routing and also request restart.

## State and Persistence Behavior

Driver plane state persists in `struct rcar_du_plane_state`: selected format descriptor, hardware plane index, source, and colorkey. Hardware state persists in PnMR, PnALPHAR, PnTC2R/PnTC3R, PnDDCR2/PnDDCR4, destination registers, pitch/source registers, DMA base registers, and group routing/restart state.

## Dependencies and Integration Points

- Uses DRM atomic, plane, blend, framebuffer, GEM DMA, fourcc, and helper APIs.
- Depends on R-Car group, KMS format descriptors, driver feature/quirk data, and register definitions.
- Called from CRTC update paths via `rcar_du_plane_setup()` and from KMS atomic checks for non-VSP-backed hardware.

## Risks and Edge Cases

- Hardware plane allocation is complex and can return `-EBUSY` when fragmentation or fixed VSPD source constraints prevent assignment.
- Two-plane formats require adjacent hardware planes with wraparound; allocation and programming must stay synchronized.
- Several scanout coordinate adjustments are based on hardware observations not fully documented, especially interlaced and NV12/NV21 Y positioning.
- Source changes and DPTSR association changes require group restarts and visible flicker.
- Color key property uses bit 24 as enable flag and lower RGB bits as key; userspace must encode it exactly.
- Gen3 no-blending feature strips ALP/EOR bits; incorrect feature flags can produce invisible or incorrectly blended planes.

## Test Signals

- Atomic plane tests should cover enable/disable, one- and two-plane formats, fixed VSPD0/VSPD1 sources, hardware plane exhaustion, zpos ordering, CRTC reassignment, and memory/live source switching.
- Register tests should validate pitch/source/destination/DMA programming for RGB, packed YUV, NV12/NV21/NV16, interlaced, and Gen2 versus Gen3.
- Property tests should cover alpha, primary immutable zpos, overlay zpos range, and colorkey enable/disable and RGB conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.h

## Purpose

`rcar_du_plane.h` declares the R-Car DU plane object, plane-state extension, source enum, hardware/KMS plane capacity constants, and APIs for plane allocation/check/setup.

## Important APIs, Types, and Functions

- `RCAR_DU_NUM_KMS_PLANES` is 9: one primary per CRTC plus up to seven overlays.
- `RCAR_DU_NUM_HW_PLANES` is 8 hardware planes per group.
- `enum rcar_du_plane_source` distinguishes memory scanout, VSPD0 live source, and VSPD1 live source.
- `struct rcar_du_plane` embeds DRM plane and points to its group.
- `struct rcar_du_plane_state` extends DRM plane state with format descriptor, hardware index, source, and colorkey.
- APIs: `rcar_du_atomic_check_planes()`, `__rcar_du_plane_atomic_check()`, `rcar_du_planes_init()`, `__rcar_du_plane_setup()`, and inline `rcar_du_plane_setup()`.

## Control Flow

The header provides the contract between KMS atomic checks, CRTC plane updates, VSP/direct scanout paths, and group-owned plane storage. `rcar_du_plane_setup()` fetches the current driver plane state and delegates to the full setup helper.

## State and Persistence Behavior

Plane state persists across atomic commits through DRM state duplication. `hwindex == -1` indicates no hardware plane is currently allocated, and `source` controls whether scanout comes from memory or VSP live input.

## Dependencies and Integration Points

- Includes DRM plane definitions and forward declares format/group types.
- Included by group, CRTC, KMS, VSP, and plane implementation code.

## Risks and Edge Cases

- The capacity constants encode hardware assumptions; changing group layout or overlay policy requires allocator and init changes.
- `colorkey` is an unsigned int with packed enable/RGB semantics defined in the C file, so external users need the property documentation from KMS/plane code.

## Test Signals

- Atomic state duplication/reset tests should verify `hwindex`, `source`, and `colorkey` defaults and persistence.
- Capacity tests should verify plane creation never exceeds group array bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_plane.h -->
