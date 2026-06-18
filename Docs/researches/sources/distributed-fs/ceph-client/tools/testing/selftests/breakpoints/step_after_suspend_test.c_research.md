# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/step_after_suspend_test.c

## Purpose

This kselftest verifies that `PTRACE_SINGLESTEP` still works on every available CPU after an optional suspend/resume cycle. It targets debug/single-step state restoration across system suspend.

## Important APIs, Types, and Functions

Functions are `child`, `run_test`, `get_suspend_success_count_or_fail`, `suspend`, and `main`. It uses CPU affinity APIs, `PTRACE_TRACEME`, `PTRACE_SINGLESTEP`, `PTRACE_CONT`, wait status inspection, `/sys/power/suspend_stats/success`, `/sys/power/state`, `timerfd_create(CLOCK_BOOTTIME_ALARM)`, and kselftest constants.

## Control Flow

`main` parses `-n` to skip suspend, enumerates available CPUs, optionally calls `suspend`, sets a test plan, and runs one test per CPU. Each child pins itself to a CPU, enters ptrace stop, and exits after being continued. The parent single-steps the child, expects a SIGTRAP stop, continues it, expects normal exit, and reports pass/skip/fail.

## State and Persistence Behavior

The test temporarily triggers system suspend unless `-n` is provided and creates a boottime alarm timerfd to wake the system. It reads suspend success counters but does not persist files.

## Dependencies and Integration Points

It depends on root privileges for suspend, working `/sys/power` suspend support, timerfd wake alarms, ptrace single-step support, CPU affinity, and kselftest.

## Risks and Test Signals

Risks include disrupting the host by suspending it, unsupported single-step returning `EIO`, suspend failure, CPU hotplug/race behavior, and timer wake failure. Signals are increased suspend success count, SIGTRAP after single-step for each CPU, normal child exit after continue, and skip output for unsupported single-step.
