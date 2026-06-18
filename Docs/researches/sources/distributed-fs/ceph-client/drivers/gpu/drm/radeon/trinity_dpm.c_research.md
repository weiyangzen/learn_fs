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
