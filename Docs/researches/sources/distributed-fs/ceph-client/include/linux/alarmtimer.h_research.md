<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alarmtimer.h -->
# sources/distributed-fs/ceph-client/include/linux/alarmtimer.h

## Purpose
`alarmtimer.h` declares the kernel alarm timer abstraction for realtime and boottime alarms built on hrtimers and timerqueue nodes.

## Important APIs, types, and functions
`enum alarmtimer_type` identifies realtime, boottime, and tracing/freezer variants. `struct alarm` stores the timerqueue node, backing hrtimer, callback, type, state flags, and private data. APIs include init, start, relative start, restart, try-cancel, cancel, forward, forward-now, and remaining-time query. `alarmtimer_get_rtcdev()` returns the RTC device when RTC class support exists.

## Control flow
Callers initialize an alarm with type and callback, start it at an absolute or relative expiry, optionally forward periodic expiries, and cancel when no longer needed. Callback execution is driven by the hrtimer/alarmtimer core.

## State and persistence behavior
Each `struct alarm` carries enqueue state and expiry node state. The RTC device association is global subsystem state used for wake-capable alarms.

## Dependencies and integration points
It depends on timekeeping, hrtimer, timerqueue, and optionally RTC class. It integrates POSIX alarm timers, suspend/freezer behavior, and wakeup-capable timers.

## Risks and test signals
Risks include cancel/restart races, wrong clock type, failing to handle inactive state, and RTC absence. Test signals include alarmtimer selftests, suspend wake alarms, periodic forward behavior, cancel return values, and RTC-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alarmtimer.h -->
