# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.c

## Purpose

`ani.c` implements ath5k Adaptive Noise Immunity. It dynamically tunes PHY sensitivity/noise-immunity parameters based on OFDM and CCK timing errors relative to channel listen time. It supports auto mode, manual low/high presets, interrupt-driven hardware PHY error counters on newer chips, and frame-by-frame PHY error reporting on older chips.

## Important APIs And Functions

- `ath5k_ani_set_noise_immunity_level()` writes desired-size, AGC coarse, and FIR power fields.
- `ath5k_ani_set_spur_immunity_level()` writes OFDM self-correlation threshold.
- `ath5k_ani_set_firstep_level()` writes firstep threshold.
- `ath5k_ani_set_ofdm_weak_signal_detection()` and `ath5k_ani_set_cck_weak_signal_detection()` toggle weak-signal detection behavior.
- `ath5k_ani_raise_immunity()` increases immunity based on current levels, OFDM vs CCK trigger, opmode, RSSI, and band.
- `ath5k_ani_lower_immunity()` decreases immunity after a long low-error period.
- `ath5k_hw_ani_get_listen_time()` updates ath common cycle counters under `cc_lock` and returns listen time.
- `ath5k_ani_save_and_clear_phy_errors()` reads/reset hardware PHY error counters and accumulates OFDM/CCK error counts.
- `ath5k_ani_calibration()` is the main periodic algorithm.
- `ath5k_ani_mib_intr()` handles PHY error counter MIB interrupts and schedules the ANI tasklet.
- `ath5k_ani_phy_error_report()` counts timing errors on older hardware without PHY error counters.
- `ath5k_ani_init()` initializes mode, defaults, max spur level, and error-source plumbing.

## Control Flow

Initialization is skipped before AR5212. Valid mode initialization clears `ah->ani_state`, sets chip-specific `max_spur_level`, applies mode defaults, and enables either PHY error counters or `AR5K_RX_FILTER_PHYERR` in auto mode.

Calibration always updates listen time. In auto mode it merges pending PHY errors, computes high/low OFDM/CCK thresholds as listen-time-scaled values, raises immunity when high thresholds are exceeded, or lowers immunity after more than five listen periods with low errors. The raise path prioritizes noise immunity, then OFDM spur immunity, then opmode/RSSI-specific firstep and weak-signal decisions. The lower path reverses conservatively, lowering firstep in AP/STA cases, then spur, then noise immunity.

Interrupt-driven hardware counters are cleared quickly in `ath5k_ani_mib_intr()` to avoid repeated interrupts. Older hardware increments software counters from RX PHY error reports.

## State And Persistence Behavior

`ah->ani_state` persists mode, parameter levels, `max_spur_level`, active counters (`listen_time`, `ofdm_errors`, `cck_errors`), and debug snapshots/totals. Register writes persist in hardware until reset, mode reinit, or later ANI adjustment. `ath5k_ani_period_restart()` preserves last-period debug values while clearing active counters.

## Dependencies And Integration Points

The file depends on `ath5k.h`, `reg.h`, `debug.h`, and `ani.h`; ath common cycle counters; beacon RSSI EWMA; current channel/opmode; interrupt/tasklet scheduling; RX descriptor PHY error paths; calibration timers; and sysfs/debug manual controls.

## Risks

Threshold math is sensitive to listen-time windows and busy-channel behavior. Hardware counter reset ordering matters for interrupt storms and lost counts. RSSI heuristics are global in IBSS despite a comment noting per-neighbor RSSI would be safer. Manual setters can be overwritten by automatic calibration. CCK weak-signal handling is less symmetric than OFDM and contains a TODO. Register constants are hardware-tuned and need RF validation before changes.

## Test Signals

Clean RF should eventually lower immunity. Injected OFDM timing errors should raise noise/spur/OFDM-related immunity; injected CCK errors should raise noise/firstep behavior. Hardware-counter devices should reset counters without repeated interrupts. Older devices should enable PHY error RX filtering in auto mode. Sysfs/debug manual controls should update registers/state and reject out-of-range levels.
