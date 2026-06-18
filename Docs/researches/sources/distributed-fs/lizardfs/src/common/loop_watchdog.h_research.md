<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.h -->
# sources/distributed-fs/lizardfs/src/common/loop_watchdog.h

## Purpose
Declares watchdog helpers for bounding long loop execution time. The source was read completely for this report.

## Important APIs, Types, And Functions
`SignalLoopWatchdog` uses `setitimer(ITIMER_REAL)`/SIGALRM; `ActiveLoopWatchdog` uses a `Timer`. Both expose `setMaxDuration`, `start`, and `expired`.

## Control Flow
Signal watchdog starts an interval timer and later observes `exit_loop_`. Active watchdog resets a timer and compares elapsed microseconds each poll.

## State And Persistence Behavior
Signal watchdog owns process-global signal/timer state; active watchdog owns only local duration and timer state.

## Dependencies And Integration Points
Depends on `time_utils.h`, signals, sys/time, and assertions. Used by algorithms that need cooperative loop cutoffs.

## Risks And Edge Cases
Signal mode is unsafe around other SIGALRM users and timers; active mode adds per-iteration time checks. Negative/zero durations are not guarded at runtime.

## Test Signals
Tests should cover immediate expiry, non-expiry, reset behavior, and signal-handler conflicts in integration environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/loop_watchdog.h -->
