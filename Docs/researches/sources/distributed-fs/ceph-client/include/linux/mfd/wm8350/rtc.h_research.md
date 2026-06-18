<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h

## Purpose
`rtc.h` defines the WM8350 RTC and alarm register layout, time-control bits, tick-control bits, RTC IRQ numbers, and runtime RTC child state.

## Important APIs, types, and functions
The main data type is `struct wm8350_rtc`, storing the platform device, `rtc_device`, and suspend/resume booleans for alarm and update interrupts. Macros define time registers for seconds/minutes, hours/day, date/month, year, alarm equivalents, and control fields such as `WM8350_RTC_BCD`, `WM8350_RTC_12HR`, `WM8350_RTC_SET`, `WM8350_RTC_ALMSET`, periodic interval selection, digital square wave selection, tick status/source/trim, and IRQs `WM8350_IRQ_RTC_PER`, `WM8350_IRQ_RTC_SEC`, and `WM8350_IRQ_RTC_ALM`.

## Control flow
The RTC driver reads split time/date registers, converts binary or BCD fields, stops or sets the RTC with control bits when updating time, programs alarm fields with optional `DONT_CARE` sentinels, and handles periodic/second/alarm IRQs through the core IRQ helpers.

## State and persistence behavior
Time, alarm, format mode, periodic interrupt mode, square-wave mode, and trim are hardware-backed RTC state. `alarm_enabled` and `update_enabled` preserve interrupt enable intent across suspend/resume.

## Dependencies and integration points
The header depends on `platform_device` and implicitly on `rtc_device`. It integrates with WM8350 core IRQ registration, Linux RTC class operations, power management, and board clock/trim policy.

## Risks and test signals
Risks include BCD/binary month conversion errors, 12-hour AM/PM mishandling, invalid `-1` alarm wildcard propagation into bit fields, stopping the clock without restart, and lost wake alarms over suspend. Test signals include set/read time round trips, BCD mode tests, alarm wildcard tests, periodic IRQ tests, suspend wake tests, and trim register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/rtc.h -->
