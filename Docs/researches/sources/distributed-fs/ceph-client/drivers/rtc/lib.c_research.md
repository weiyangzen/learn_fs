# sources/distributed-fs/ceph-client/drivers/rtc/lib.c

## Purpose

`lib.c` provides the RTC subsystem's date and time conversion utilities. It converts between POSIX `time64_t`, `ktime_t`, and `struct rtc_time`, computes month and year day counts, and validates user-visible RTC timestamps. These helpers are used by the shared RTC interface and by individual RTC drivers that expose register values as seconds.

## Important APIs, types, and functions

The exported helpers are `rtc_month_days()`, `rtc_year_days()`, `rtc_time64_to_tm()`, `rtc_valid_tm()`, `rtc_tm_to_time64()`, `rtc_tm_to_ktime()`, and `rtc_ktime_to_tm()`. `rtc_days_in_month[]` and `rtc_ydays[][]` provide static calendar tables. `rtc_time64_to_tm()` uses an arithmetic Gregorian conversion that works for large positive ranges and for times since at least 1900 by shifting to a March-based computational calendar.

## Control flow

Month and year-day helpers are direct table lookups with leap-year adjustment. `rtc_time64_to_tm()` first shifts seconds from the POSIX epoch to a non-negative day count relative to 0000-03-01, calculates century, year, month, day, weekday, and yday using integer arithmetic, then fills hour, minute, second, and `tm_isdst`. `rtc_tm_to_time64()` delegates to `mktime64()`. `rtc_ktime_to_tm()` rounds up if nanoseconds are non-zero before converting.

## State and persistence behavior

The file is stateless. It uses only constant lookup tables and caller-provided buffers. No hardware or persistent state is touched.

## Dependencies and integration points

It depends on `linux/rtc.h`, `linux/export.h`, `mktime64()`, `ktime_to_timespec64()`, `ktime_set()`, `is_leap_year()`, and integer division helpers. RTC drivers rely on these functions when converting BCD/calendar register sets to the common RTC ABI or when exposing second counters as wall-clock time.

## Risks and edge cases

`rtc_valid_tm()` rejects years before 1970 and years that overflow `INT_MAX - 1900`; callers dealing with pre-1970 hardware must set ranges and avoid validating unsupported values. `rtc_time64_to_tm()` stores `tm_yday` as `day_of_year + 1`, so consumers expecting the conventional zero-based `tm_yday` should review this behavior in context. `rtc_ktime_to_tm()` rounds nanoseconds upward, which is intentional for alarm deadlines but can surprise callers expecting truncation.

## Test signals

Test conversion round trips at leap days, century boundaries, 1970-01-01, 1999/2000, 2038-adjacent timestamps, very large future values, invalid month/day/hour/minute/second values, and ktime values with non-zero nanoseconds. Cross-check `rtc_month_days()` and `rtc_year_days()` against known leap-year tables.
