# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.c

## Purpose
`intel_pps.c` implements embedded DisplayPort panel power sequencing for i915. It selects and initializes panel power sequencers, manages panel VDD and panel power transitions, applies panel timing delays from BIOS/VBT/spec fallbacks, controls PPS backlight bits, handles Valleyview/Cherryview sequencer stealing and kicking, restores/reset state after suspend or power-well events, exposes panel timing debugfs, and validates legacy PPS register locking.

The code applies only to eDP for most power operations, while several Valleyview/Cherryview helpers are called on all DP ports because those platforms bind PPS ownership to active pipes and DP ports in unusual ways.

## Important APIs, Types, And Functions
`intel_pps_lock()` and `intel_pps_unlock()` are foundational. They acquire a display-core power wakeref before taking `display->pps.mutex`, avoiding the lock ordering problem described in `vlv_pps_reset_all()`. The header macro `with_intel_pps_lock()` wraps this pattern.

Sequencer selection is handled by `pps_initial_setup()`, `vlv_initial_power_sequencer_setup()`, `vlv_power_sequencer_pipe()`, `bxt_power_sequencer_idx()`, and `intel_pps_get_registers()`. These functions map an `intel_dp` to the correct `PP_CONTROL`, `PP_STATUS`, `PP_ON_DELAYS`, `PP_OFF_DELAYS`, and optional `PP_DIVISOR` registers.

Power and VDD APIs include `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, `intel_pps_vdd_on()`, `intel_pps_vdd_off()`, `intel_pps_vdd_off_sync()`, `intel_pps_on_unlocked()`, `intel_pps_off_unlocked()`, `intel_pps_on()`, `intel_pps_off()`, `intel_pps_wait_power_cycle()`, and `intel_pps_have_panel_power_or_vdd()`.

Backlight APIs include `intel_pps_backlight_on()`, `intel_pps_backlight_off()`, and `intel_pps_backlight_power()`. Initialization and reset APIs include `intel_pps_init()`, `intel_pps_init_late()`, `intel_pps_encoder_reset()`, `intel_pps_setup()`, `vlv_pps_pipe_init()`, `vlv_pps_pipe_reset()`, `vlv_pps_port_enable_unlocked()`, `vlv_pps_port_disable()`, `vlv_pps_reset_all()`, and `bxt_pps_reset_all()`.

## Control Flow
Initialization starts with `intel_pps_setup()` choosing the MMIO base. `intel_pps_init()` marks PPS as initializing, initializes delayed VDD-off work, initializes timestamps, selects an initial sequencer, initializes delays, programs registers, and tracks BIOS-left-on VDD. `intel_pps_init_late()` reruns after VBT parsing, optionally adjusts PPS index, reinitializes delays/registers, clears the initializing flag, and schedules delayed VDD off if needed.

Delay initialization combines three sources. `pps_init_delays_bios()` reads current hardware registers, `pps_init_delays_vbt()` reads panel VBT timings and applies quirks such as increased T12 delay, and `pps_init_delays_spec()` provides eDP-spec upper-limit fallbacks. `pps_init_delays()` chooses max(BIOS,VBT) per field or spec when both are zero, converts PPS units to milliseconds for software waits, overrides hardware backlight delays to one unit because software waits manually, and rounds power-cycle delay to hardware granularity.

Register initialization writes PP_ON/PP_OFF delay registers, port-select bits on platforms that need them, and either PP_DIVISOR or the BXT/CNP+ power-cycle field in PP_CONTROL. Optional `force_disable_vdd` clears stale VDD on sequencers before they are attached to a port.

VDD-on flow cancels delayed VDD-off work, records `want_panel_vdd`, obtains AUX power-domain wakeref if VDD is not already on, waits for power-cycle if panel power is off, sets `EDP_FORCE_VDD`, and delays before AUX access when needed. VDD-off can be delayed by `edp_panel_vdd_schedule_off()` or immediate through `intel_pps_vdd_off_sync_unlocked()`, which clears `EDP_FORCE_VDD`, records power-off time when panel power is off, invalidates source OUI, and releases the AUX wakeref.

Panel power-on waits for power-cycle, optionally toggles `PANEL_POWER_RESET` for Ironlake, applies WA 22019252566 DPLS gating around the sequence on display versions 13/14, sets `PANEL_POWER_ON` and reset, waits for PP_STATUS on-idle, and records `last_power_on`. Panel power-off requires VDD ownership, clears panel power/reset/VDD/backlight bits, waits for off-idle, records `panel_power_off_time`, invalidates source OUI, and releases the AUX wakeref.

## State And Persistence Behavior
Persistent per-panel state lives in `intel_dp->pps`: selected PPS index or VLV pipe, active VLV pipe, reset flags, initialized delays, BIOS delay snapshot, software millisecond delays, timestamps, `want_panel_vdd`, `vdd_wakeref`, delayed VDD-off work, and initializing flag.

The code persists `panel_power_off_time`, `last_power_on`, and `last_backlight_off` so later power-cycle and backlight waits honor panel timing even when hardware status bits are already idle. BIOS-left-on VDD is reconciled by taking the missing power-domain reference and scheduling VDD off instead of assuming software owns nothing.

Valleyview/Cherryview state is unusually dynamic. A PPS can be stolen from another encoder, detached by clearing port-select bits, kicked by temporarily enabling the DP port, and reset globally without taking the PPS mutex. Correct use requires a display-core wakeref plus PPS mutex when reading or mutating VLV PPS ownership.

## Dependencies And Integration Points
This file depends on Intel MMIO helpers, display power domains, DP/eDP connector and encoder state, DPIO/PLL helpers for VLV/CHV sequencer kicks, LVDS/DP port-enabled readout, VBT panel data, quirks, debugfs, delayed workqueues, jiffies/ktime delay helpers, and PPS register definitions from `intel_pps_regs.h`.

It integrates with AUX transactions through `intel_pps_check_power_unlocked()`, with DP enable/disable on VLV through port enable/disable hooks, with suspend/resume or power-well reset via encoder reset and reset-all helpers, with backlight sysfs through `intel_pps_backlight_power()`, and with connector debugfs through `i915_panel_timings`.

## Risks And Edge Cases
Lock ordering is a major risk. PPS operations must use `intel_pps_lock()`/`with_intel_pps_lock()` so a power-domain reference is acquired before `pps.mutex`. Taking locks in the wrong order can deadlock with power-domain code.

VDD wakeref lifetime is another critical risk. If VDD is already on from BIOS, software must take a wakeref; if VDD/panel power is later turned off, the wakeref must be released exactly once. The code uses `fetch_and_zero()` to avoid double puts.

Panel timing regressions can cause visible flicker, failed panel wake, or AUX failures. The code manually waits for backlight timing and power-cycle timing in addition to hardware PP_STATUS polling, and VBT/spec/quirk interactions must remain conservative.

VLV/CHV PPS selection is fragile because power sequencers can be shared, stolen, or not yet locked to a port. The kick path temporarily forces PLL/PHY state and toggles DP port enable; failures here can leave VDD force ineffective.

Register layout varies by platform: VLV/CHV and PCH split use different MMIO bases; BXT/CNP+ move power-cycle delay into PP_CONTROL; multi-PPS systems need valid PPS index selection and PCH-specific second PPS IO selection checks.

## Test Signals
Useful test signals include eDP boot, suspend/resume, VBT late init, repeated AUX access with panel off, panel on/off cycles, backlight sysfs toggling, and VLV/CHV DP/eDP port enable/disable sequences. Hardware tests should watch for PP_STATUS timeouts, PPS state mismatch logs, VDD already-on/not-on warnings, and power sequencer mismatch warnings.

Debugfs `i915_panel_timings` exposes computed software delays for connected eDP panels. Runtime logs from `drm_dbg_kms()` and `drm_err()` around PP_STATUS/PP_CONTROL values are essential for diagnosing timing and register-programming failures.
