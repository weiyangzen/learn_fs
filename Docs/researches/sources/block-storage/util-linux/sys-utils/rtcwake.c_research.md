# File Research: sources/block-storage/util-linux/sys-utils/rtcwake.c

This file implements `rtcwake(8)`, setting an RTC wake alarm and optionally suspending, powering off, waiting on the RTC, disabling the alarm, or showing the current alarm. It uses `/dev/rtc0` by default, RTC ioctls for time/alarm operations, `/sys/class/rtc/<rtc>/device/power/wakeup` to verify wakeup capability, and `/sys/power/state` for suspend modes.

Clock handling supports UTC, local time, or auto mode from the third line of the adjtime file. `get_basetimes()` reads RTC and system time close together, sets `TZ=UTC` when needed, and computes the delta used to translate POSIX alarm times into RTC time. Alarm setup writes `RTC_WKALM_SET`; cleanup disables the alarm unless dry-run or show/no mode prevents it.

Mode handling includes sysfs suspend states, `off` via shutdown/poweroff executable lookup, `on` by blocking on RTC alarm interrupts, `no` for alarm setup without suspend, `disable`, and `show`. The command also supports relative seconds, absolute time_t, parsed timestamp dates, dry-run, mode listing, and verbose diagnostics.
