# sources/distributed-fs/ceph-client/kernel/watchdog_perf.c

## Purpose
`watchdog_perf.c` implements a hard-lockup detector backend using perf events, typically NMI-capable hardware PMU events. It creates a pinned per-CPU perf counter whose overflow callback runs in an NMI-like context and asks the generic watchdog core to check for a hard lockup on that same CPU. It also supports timestamp filtering to reduce false positives caused by PMU frequency behavior, raw perf-event configuration from the boot command line, and global stop/restart hooks for architecture quirks.

## Important APIs, types, and functions
The file owns per-CPU `struct perf_event *watchdog_ev` and an atomic count of enabled watchdog CPUs. The main event attributes are `wd_hw_attr` and `fallback_wd_hw_attr`, both defaulting to pinned `PERF_TYPE_HARDWARE` / `PERF_COUNT_HW_CPU_CYCLES` counters. Important functions are `watchdog_overflow_callback()`, `hardlockup_detector_event_create()`, `watchdog_hardlockup_enable()`, `watchdog_hardlockup_disable()`, `hardlockup_detector_perf_adjust_period()`, `hardlockup_detector_perf_stop()`, `hardlockup_detector_perf_restart()`, weak `arch_perf_nmi_is_available()`, `watchdog_hardlockup_probe()`, and `hardlockup_config_perf_event()`.

When `CONFIG_HARDLOCKUP_CHECK_TIMESTAMP` is enabled, timestamp-related state includes per-CPU `last_timestamp`, per-CPU `nmi_rearmed`, and global `watchdog_hrtimer_sample_threshold`. The exported-to-core function `watchdog_update_hrtimer_threshold()` updates that threshold when the generic sample period changes.

## Control flow
The generic watchdog core first probes this backend by calling `watchdog_hardlockup_probe()`. Probe checks whether the architecture reports perf NMI availability, verifies that `hw_nmi_get_sample_period(watchdog_thresh)` returns a usable period, then tries to create a temporary kernel perf counter on the current CPU. Success releases the temporary event and returns zero; failure logs that the perf NMI watchdog is disabled and returns the perf error.

Enabling a CPU through `watchdog_hardlockup_enable()` asserts the target CPU is local, creates a perf event with `hardlockup_detector_event_create()`, logs a one-time PMU counter consumption message when the first CPU is enabled, warns if an old per-CPU event pointer leaked, stores the event in `watchdog_ev`, initializes timestamp filtering state, and enables the perf event. Event creation first tries `wd_hw_attr` with a sample period derived from `watchdog_thresh`; if that fails, it retries with `fallback_wd_hw_attr`.

When the perf counter overflows, `watchdog_overflow_callback()` resets `event->hw.interrupts` to prevent perf throttling, exits if panic is in progress, applies optional timestamp filtering, and calls `watchdog_hardlockup_check(smp_processor_id(), regs)`. The generic core decides whether to print diagnostics or panic based on hrtimer/touch state and configured policy.

Disabling a CPU through `watchdog_hardlockup_disable()` disables and releases the per-CPU perf event, clears `watchdog_ev`, and decrements the enabled CPU count. `hardlockup_detector_perf_adjust_period()` changes the active event period after CPU frequency changes when the hard watchdog is enabled and the current period differs. `hardlockup_detector_perf_stop()` and `hardlockup_detector_perf_restart()` iterate online CPUs under the CPU hotplug read lock and disable or re-enable existing events; these are special x86-facing hooks for perf hyperthreading issues.

`hardlockup_config_perf_event()` parses a hexadecimal raw event ID from the `nmi_watchdog=r...` boot option path. It accepts either a plain raw event string or a comma-terminated component, converts it with `kstrtoull()`, and changes `wd_hw_attr` to `PERF_TYPE_RAW` with that config.

## State and persistence behavior
State is runtime-only. Each participating CPU may own one kernel perf event pointer in `watchdog_ev`; the atomic `watchdog_cpus` tracks how many CPUs currently have active events and gates the informational message. Timestamp filtering state is per CPU and is reset whenever the event is enabled. Attribute changes from `hardlockup_config_perf_event()` affect runtime boot configuration but are not persisted beyond the running kernel.

The timestamp filter is specifically defensive. The generic hrtimer should run faster than the NMI watchdog, but CPU-cycle PMU events can overflow sooner than nominal under turbo or frequency effects. `watchdog_check_timestamp()` suppresses samples that arrive before `watchdog_hrtimer_sample_threshold`, but after repeated rearming it allows progress so stale time bases do not suppress real lockups forever.

## Dependencies and integration points
This backend integrates with the perf event subsystem, hardware PMU/NMI support, `hw_nmi_get_sample_period()`, generic hardlockup policy in `watchdog.c`, panic state, architecture availability hooks, CPU hotplug locking, and architecture-specific callers that stop/restart perf events or adjust periods. It also shares the boot command parser path in `watchdog.c` for `nmi_watchdog=r...` raw event selection.

## Risks and test signals
Risks include inability to allocate a pinned PMU counter, architectures without NMI-capable perf events, event creation success during probe but later per-CPU failures, leaked per-CPU events, false positives from PMU overflow timing, and period-adjustment failures during CPU frequency changes. The overflow callback runs in a sensitive context, so it must avoid blocking and must keep diagnostics delegated to the generic hardlockup path.

Useful test signals include backend probe success and failure; fallback attribute creation after primary event failure; enable/disable cycles across CPU hotplug; one-time PMU consumption logging; no `watchdog_ev` leak warnings; raw event parsing from `nmi_watchdog=r...`; timestamp filter suppression and eventual rearm escape; period adjustment after frequency changes; perf stop/restart under CPU lock; and hardlockup reports generated from a perf overflow with valid register state.
