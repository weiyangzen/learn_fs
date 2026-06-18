<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/rtctest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/rtctest.c

## Purpose

RTC kselftest harness program that validates basic RTC date reads, repeated monotonic reads, update interrupts, select/read readiness, and alarm/wakeup-alarm delivery against a configurable RTC device, defaulting to /dev/rtc0.

## Important APIs, Types, and Functions

Uses kselftest_harness FIXTURE/TEST_F/TEST_F_TIMEOUT, Linux RTC ioctls RTC_RD_TIME, RTC_UIE_ON/OFF, RTC_AIE_ON/OFF, RTC_ALM_SET/READ, RTC_WKALM_SET/RD, RTC_PARAM_GET with RTC_PARAM_FEATURES, plus select(), read(), access(), timegm(), gmtime_r(), mktime(), and nanosleep(). Helpers convert rtc_time to time_t, retry interrupted nanosleeps, and classify alarm capability/granularity.

## Control Flow and Integration

main validates an optional device argument and skips when unreadable. Each fixture opens the RTC read-only and closes it after the test. The read-loop test polls time for thirty seconds and asserts that seconds never move backward or jump more than one second. UIE tests enable update interrupts, then block on read or wait with select. Alarm tests program a short second-granularity alarm or a minute-aligned alarm, wait for fd readiness, drain the interrupt word, and compare the final RTC time with the programmed timestamp.

## State and Persistence Behavior

The file does not persist data, but it temporarily changes RTC interrupt enable state and programs alarm registers during execution. It relies on kernel RTC device state and may leave alarm contents changed if a failing assertion exits before cleanup.

## Dependencies and Integration Points

Depends on linux/rtc.h, /dev/rtc*, kselftest harness, readable RTC device permissions, and kernel RTC feature reporting. It integrates with kselftest selftests/rtc and can be run manually with an alternate rtcdev path.

## Risks and Edge Cases

Alarm support varies by hardware; minute-only alarms are skipped in second-granularity cases. Exact timestamp equality can be sensitive to RTC resolution, clock drift, time zone conversion, and delayed scheduling. Tests manipulate real RTC alarms and need care on systems using RTC wake alarms for power management.

## Test Signals

Pass signals are successful kselftest assertions, NUM_UIE interrupts observed, select waking before timeout, and RTC time matching programmed alarm time. Skips identify missing RTC devices or unsupported UIE/alarm features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rtc/rtctest.c -->
