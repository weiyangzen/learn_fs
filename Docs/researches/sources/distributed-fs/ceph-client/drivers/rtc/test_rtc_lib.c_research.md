## sources/distributed-fs/ceph-client/drivers/rtc/test_rtc_lib.c

Purpose: Provides KUnit coverage for RTC library date conversion, specifically `rtc_time64_to_tm`, across long Gregorian-calendar intervals.

Important APIs/types/functions: `advance_date` is a local reference model for incrementing date, day-of-year, and weekday by one day. `rtc_time64_to_tm_test_date_range` drives the conversion under test for a caller-specified number of years. Test entry points are `rtc_time64_to_tm_test_date_range_1000` and slow `rtc_time64_to_tm_test_date_range_160000`, registered in `rtc_lib_test_cases` and `rtc_lib_test_suite`.

Control flow: The test computes total seconds for whole 400-year cycles because the Gregorian calendar repeats every 146097 days. It starts from 1900-01-01 Monday, adds a fixed `01:02:03` time offset, and iterates one day at a time. For each day it calls `rtc_time64_to_tm`, asserts year/month/day/yday/hour/min/sec/wday against the reference state, then advances the reference date. The 1000-year case is normal; the 160000-year case is marked `KUNIT_CASE_SLOW`.

State and persistence: No persistent state exists. State is local loop variables and KUnit result recording. The test intentionally exercises very large positive `time64_t` values.

Dependencies/integration: Depends on KUnit and `linux/rtc.h`, built as part of RTC library tests when enabled. It validates shared RTC core logic used by many drivers in this subset.

Risks: The reference model depends on `rtc_month_days`, so it is not fully independent of RTC date helpers. The computed total seconds truncates to whole 400-year groups for non-multiple inputs, which is intentional for test ranges used here. Runtime can be high for the slow case.

Test signals: Passing KUnit output for both normal and slow cases, especially leap-year boundaries, yday reset at Jan 1, weekday modulo behavior, and large `time64_t` conversion stability.
