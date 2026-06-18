<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h

## Purpose
Holds compile-time constants for cpufreq-bench. It defines the initial calibration loop count, scheduler policy, priority aliases, and `dprintf` as either `printf` under DEBUG or a no-op otherwise.

## Important APIs, Types, And Functions
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Control Flow
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## State And Persistence
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Dependencies And Integration Points
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Risks And Edge Cases
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.

## Test Signals
There is no control flow except preprocessor selection. State is compile-time only. Dependencies are `sched_get_priority_max/min()` and `SCHED_OTHER` being visible before priority macros are used. Risks include macro name collision with POSIX `dprintf`, priority macros evaluating scheduler functions at use sites, and DEBUG altering runtime verbosity/performance. Test signals are builds with and without DEBUG and code paths using `PRIORITY_HIGH/LOW` after including scheduler headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/config.h -->
