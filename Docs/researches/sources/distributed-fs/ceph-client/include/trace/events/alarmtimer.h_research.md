# sources/distributed-fs/ceph-client/include/trace/events/alarmtimer.h

## Purpose
`alarmtimer.h` traces alarmtimer suspend decisions and alarm lifecycle events. It is used to debug wakeup timers and freezer-aware alarm classes.

## Important APIs, types, and functions
The header exports alarm type enum values with `TRACE_DEFINE_ENUM()`, defines `show_alarm_type()`, and declares `alarm_class` for `alarmtimer_fired`, `alarmtimer_start`, and `alarmtimer_cancel`. Under `CONFIG_RTC_CLASS`, it also defines `alarmtimer_suspend`.

## Control flow
Suspend tracing records the expiration and alarm type considered during suspend. Runtime alarm events snapshot the `struct alarm *`, `alarm->type`, `alarm->node.expires`, and the current `ktime_t now` supplied by the caller.

## State and persistence behavior
The header has no persistent state. It records alarm object addresses and expiry/current time values at event emission.

## Dependencies and integration points
It depends on `<linux/alarmtimer.h>`, `<linux/rtc.h>`, and `<linux/tracepoint.h>`. It integrates with the alarmtimer core, RTC class suspend behavior, tracingfs, and tooling that correlates wakeup source timing.

## Risks and test signals
Risks include missing suspend events when RTC class support is disabled, confusing bitflag formatting because the stored event value is an enum index later shifted for printing, and pointer-only alarm identity. Test signals are start/cancel/fire sequences for realtime and boottime alarms and suspend traces with expected expiration values.
