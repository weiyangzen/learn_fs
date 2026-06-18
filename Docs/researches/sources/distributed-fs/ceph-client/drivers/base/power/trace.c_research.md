# sources/distributed-fs/ceph-client/drivers/base/power/trace.c

## Purpose
This file implements the legacy PM trace facility for diagnosing suspend/resume hangs when normal storage or logging may be unavailable. It encodes compact hashes of a trace point and device into RTC time fields, then decodes and matches those hashes after reboot.

## Important APIs, Types, And Functions
Public symbols are `pm_trace_rtc_abused`, `set_trace_device()`, `generate_pm_trace()`, and `show_trace_dev_match()`. Internal helpers include `set_magic_time()`, `read_magic_time()`, `hash_string()`, `show_file_hash()`, `show_dev_hash()`, `pm_trace_notify()`, `early_resume_init()`, and `late_resume_init()`.

## Control Flow And State
`set_trace_device()` hashes `dev_name(dev)` with `DEVSEED` into `dev_hash_value`. `generate_pm_trace()` hashes file/line trace data plus the current device hash and writes the combined value into RTC year/month/day/hour/minute fields with `mc146818_set_time()`, setting `pm_trace_rtc_abused`. On boot, `early_resume_init()` reads the RTC-derived value and registers a PM notifier. `late_resume_init()` splits the value into user/file/device hashes, logs the magic number, scans linker-provided `__tracedata` records for file matches, and scans `dpm_list` for matching devices. The notifier warns after suspend/hibernate if the RTC was intentionally abused.

## Dependencies And Integration Points
This is x86 legacy RTC-specific through `mc146818rtc` and `x86_platform.legacy.rtc`. It integrates with PM notifier hooks, core/late initcalls, linker trace-data sections, the global device PM list, and `/sys/power/pm_trace_dev_match`-style consumers via `show_trace_dev_match()`.

## Risks And Test Signals
The scheme is lossy by design: 24-bit-ish space can collide, RTC values are corrupted intentionally, and systems with slow reboot or no legacy RTC cannot use it. Tests are mostly integration/manual: enable PM trace, force a suspend hang, reboot, confirm magic number and candidate device/file matches, and verify RTC-abuse warning after resume.
