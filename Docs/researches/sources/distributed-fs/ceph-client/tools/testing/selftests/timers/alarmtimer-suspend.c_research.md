# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/alarmtimer-suspend.c

## Purpose
Destructive test for alarm timers and RTC wakeup across suspend. It arms realtime and boottime alarm timers and verifies wake latency while repeatedly suspending the system.

## Important APIs, Types, and Functions
Globals include `alarmcount`, `alarm_clock_id`, `start_time`, and `final_ret`. Functions are `clockstring`, `timespec_sub`, signal handler `sigalarm`, and `main`.

## Control Flow
`main()` installs a real-time signal handler, loops over `CLOCK_REALTIME_ALARM` and `CLOCK_BOOTTIME_ALARM`, creates an interval timer firing every 15 seconds, waits for five alarms without suspend, then enters suspend loops by writing `mem` to `/sys/power/state` until ten alarms have fired or suspend fails. `sigalarm()` computes latency from expected interval count and flags excessive latency over five seconds.

## State and Persistence Behavior
It creates POSIX timers and writes to `/sys/power/state`, changing global system power state. It does not persist files, but it can suspend the machine and depends on RTC wake alarms.

## Dependencies and Integration Points
Depends on alarmtimer support, RTC wake capability, permissions to suspend, signal delivery, and kselftest. Integrates with kernel alarmtimer, suspend/resume, and clock code.

## Risks and Edge Cases
This test is disruptive and can suspend active systems. Hardware without RTC wake support, disabled suspend, or delayed resume can fail. It breaks from the clock loop if `timer_create` fails for an alarm clock.

## Test Signals
Signals include alarm latency lines marked OK, successful suspend/resume cycles, and kselftest fail if latency exceeds the threshold.
