# sources/distributed-fs/ceph-client/kernel/time/alarmtimer.c

Purpose: implements alarm timers, a hrtimer-like abstraction that can program an RTC alarm to wake the system from suspend. It backs `CLOCK_REALTIME_ALARM` and `CLOCK_BOOTTIME_ALARM` POSIX clocks and exposes exported kernel helpers such as `alarm_init()`, `alarm_start()`, `alarm_cancel()`, `alarm_forward()`, and `alarmtimer_get_rtcdev()`.

Important state and control flow: `alarm_bases[]` holds one timerqueue, spinlock, base clock id, and time reader per alarm type. `alarm_start()` records an absolute expiry, queues the alarm under the base lock, and arms the embedded hrtimer. `alarmtimer_fired()` dequeues the alarm and invokes the caller callback with current base time. Suspend scans all bases and freezer sleep state for the earliest expiry, bounds the delta via RTC limits, then starts `rtctimer`; resume cancels it. POSIX timer flow converts clock ids through `clock2alarm()`, requires `CAP_WAKE_ALARM`, and wires alarm callbacks into `common_timer_*`.

Dependencies and integration: depends on hrtimers, timerqueue, RTC class, platform driver PM callbacks, POSIX timer internals, freezer state, tracepoints, and time namespaces for absolute alarm nanosleep conversion. The device init path registers the RTC class interface and `alarmtimer` platform driver.

Risks and test signals: correctness depends on lock ordering between base locks, `freezer_delta_lock`, and hrtimer cancellation waits. RTC absence returns `-EOPNOTSUPP` or `-EINVAL`, so tests need both RTC and no-RTC configurations. Suspend wake tests should cover near-expiry `-EBUSY`, bounded RTC alarm ranges, namespace-adjusted absolute sleeps, restart-block behavior, and `CAP_WAKE_ALARM` permission failures.
