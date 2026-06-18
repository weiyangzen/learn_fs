# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/clocksource-switch.c

## Purpose
Destructive test that cycles available clocksources and runs timer consistency checks after each switch.

## Important APIs, Types, and Functions
Functions are `get_clocksources`, `get_cur_clocksource`, `change_clocksource`, `run_tests`, and `main`. It reads and writes sysfs clocksource files and invokes companion tests.

## Control Flow
The test reads available clocksources, records the current one, switches to each available source via sysfs, runs timer checks for a requested duration or default, and finally restores the original clocksource. Companion checks include consistency and skew-related timer tests.

## State and Persistence Behavior
It modifies `/sys/devices/system/clocksource/clocksource0/current_clocksource`, affecting global timekeeping source selection. It attempts to restore the original source.

## Dependencies and Integration Points
Depends on root privileges, clocksource sysfs, available alternative clocksources, companion timer binaries, and kselftest. Integrates with kernel clocksource switching and timekeeping consistency.

## Risks and Edge Cases
Switching clocksources can affect the whole system. Some clocksources may be unstable or unavailable for writing. Failure before restore can leave a non-default clocksource.

## Test Signals
Signals include successful enumeration, successful switch to each source, companion test success, and restoration of the original clocksource.
