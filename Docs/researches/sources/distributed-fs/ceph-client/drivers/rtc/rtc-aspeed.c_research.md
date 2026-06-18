# sources/distributed-fs/ceph-client/drivers/rtc/rtc-aspeed.c

## Purpose

`rtc-aspeed.c` is the ASPEED AST2400/AST2500/AST2600 RTC driver. It provides simple MMIO read/set support for calendar time and has no alarm or interrupt support.

## Important APIs, types, and functions

`struct aspeed_rtc` stores the mapped base. RTC callbacks are `aspeed_rtc_read_time()` and `aspeed_rtc_set_time()`. The driver uses `RTC_TIME`, `RTC_YEAR`, and `RTC_CTRL` registers with `RTC_UNLOCK` and `RTC_ENABLE` bits.

## Control flow

Probe allocates state, maps the resource, allocates an RTC, sets ops and range 1900 through 3199-12-31, and registers. Read time first rejects disabled hardware, then reads `RTC_YEAR`, `RTC_TIME`, and `RTC_YEAR` again until the year register is stable. Set time encodes day/hour/min/sec and century/year/month, unlocks writes, writes time and year registers, then relocks with enable set.

## State and persistence behavior

Hardware persists time/year and control bits. The driver has no software state beyond the mapped base. Setting time ensures the hardware is enabled after programming.

## Dependencies and integration points

It depends on platform MMIO, OF compatibles for ASPEED AST RTCs, RTC class APIs, and the platform-driver-probe registration pattern.

## Risks and edge cases

There is no alarm, wake, validity, oscillator, or backup-loss check. The `year = tm->tm_year % 100` calculation relies on `tm_year` being years since 1900; for centuries after 1999 that still encodes the low two digits but deserves tests across century boundaries. Register fields are binary rather than BCD. Disabled RTC reads return `-EINVAL` until time is programmed.

## Test signals

Test read failure before enable, set/read round trips for 1900, 1999, 2000, 2099, 2100, and 3199, write unlock/enable behavior, stable read loop around rollover, and userspace absence of alarm ioctls.
