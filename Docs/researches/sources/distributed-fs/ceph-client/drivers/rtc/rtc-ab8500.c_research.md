# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab8500.c

## Purpose

`rtc-ab8500.c` is the RTC driver for the AB8500 PMIC. It exposes a minute-based PMIC clock with fractional seconds, minute-resolution alarms, wake IRQ support, and a sysfs calibration attribute.

## Important APIs, types, and functions

The RTC callbacks are `ab8500_rtc_read_time()`, `ab8500_rtc_set_time()`, `ab8500_rtc_read_alarm()`, `ab8500_rtc_set_alarm()`, and `ab8500_rtc_irq_enable()`. Calibration helpers `ab8500_rtc_set_calibration()` and `ab8500_rtc_get_calibration()` back the `rtc_calibration` sysfs attribute. `rtc_alarm_handler()` reports `RTC_AF`. Probe sets `RTC_FEATURE_ALARM_RES_MINUTE`, clears update interrupt support, sets a 24-bit-minute range, and enables `set_start_time` from year 2000.

## Control flow

Probe gets the named `ALARM` IRQ, performs an RTC supply test by setting and reading `RTC_STATUS_DATA`, initializes wakeup, allocates the RTC, requests the threaded IRQ, associates it as wake IRQ, adds the calibration sysfs group, and registers. Read time requests a latched read, polls until the read request bit clears, reads five time registers, combines 24-bit minutes and seconds counter ticks, and converts to `rtc_time`. Set time converts seconds to minutes plus fractional second counts and writes the same registers, then requests a write. Alarm operations read/write three minute alarm registers and toggle `RTC_ALARM_ENA`.

## State and persistence behavior

Persistent state is in AB8500 RTC registers: watch time, alarm minutes, status/control bits, calibration, and backup/supply status. The RTC class offset/range support is used to present a range starting at 2000 even though hardware stores a limited minute count.

## Dependencies and integration points

The driver depends on ABX500/AB8500 MFD register helpers, platform IDs, named platform IRQs, RTC class APIs, PM wake IRQ helpers, sysfs attributes, and OF/module platform binding.

## Risks and edge cases

Alarms have minute resolution only; seconds are discarded. The read-time poll exits after one second but does not explicitly return timeout if the request bit remains set, so stale reads may be possible. Calibration uses sign-magnitude conversion and rejects `-128`; sysfs parsing uses `sscanf`. Register access is interruptible and can fail at many points. Range expansion through `set_start_time` must stay aligned with the core interface behavior.

## Test signals

Test supply-failure detection, time read latch polling, set/read around minute boundaries, minute-resolution alarm rounding through the RTC core, wake IRQ from suspend, calibration sysfs read/write including limits `-127..127`, and error propagation from ABX500 register helpers.
