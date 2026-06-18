# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00link.c

## Purpose
Implements common rt2x00 link-quality tracking, software antenna diversity, periodic link tuning, gain/VCO calibration scheduling, LED quality updates, and watchdog scheduling.

## Important APIs, Types, And Functions
Exports `rt2x00link_update_stats()`, `rt2x00link_start_tuner()`, `rt2x00link_stop_tuner()`, `rt2x00link_reset_tuner()`, `rt2x00link_start_watchdog()`, `rt2x00link_stop_watchdog()`, and `rt2x00link_register()`. Private helpers manage EWMA RSSI, antenna RSSI history, antenna sample/evaluation transitions, link quality reset, station-mode tuning, and delayed work callbacks.

## Control Flow
RX completion calls `rt2x00link_update_stats()` for STA interfaces; it increments RX success and updates global and antenna RSSI EWMA only for beacons from the associated BSS. Starting the tuner skips monitor-only and scanning states, resets tuner state, and queues delayed work. Each tuner tick exits if radio is off or scanning, locks `conf_mutex`, asks chip code for link stats, updates FCS error counts and RSSI fallback, calls chip `link_tuner()` if supported, updates quality LED, evaluates antenna diversity, runs gain calibration every four seconds and VCO calibration every ten seconds when supported, then reschedules. Watchdog work calls chip `watchdog()` at the configured interval while radio is enabled.

## State And Persistence
Uses `rt2x00dev->link.count`, `link.qual`, `link.ant`, EWMA RSSI state, delayed work objects, watchdog interval, and low-level stats. Antenna diversity persists current active antenna, history RSSI, and sampling mode flags. Reset preserves `vgc_level_reg` while clearing measurement counters.

## Dependencies And Integration Points
Depends on mac80211 delayed work scheduling, rt2x00 config antenna path, chip-specific `link_stats`, `reset_tuner`, `link_tuner`, `gain_calibration`, `vco_calibration`, and `watchdog` callbacks, LED quality helper, and RX descriptor `MY_BSS`/RSSI flags.

## Risks
Tuning races with channel/antenna config are mitigated by `conf_mutex`, but start/stop/scanning/radio flags still require careful ordering. Antenna diversity changes call back into config and reset quality counters, so repeated RSSI oscillation can cause churn. DEFAULT_RSSI forces maximum sensitivity when samples are missing, which may increase false CCA. Watchdog runs on mac80211 delayed work and can schedule recovery paths; callbacks must avoid deadlocks.

## Test Signals
STA association with stable and changing RSSI, software antenna diversity switching, scan start/complete suppressing tuner, channel/antenna changes resetting tuner, gain/VCO calibration cadence, quality LED updates, watchdog-triggered recovery, and low-level FCS/TX/RX statistic updates.
