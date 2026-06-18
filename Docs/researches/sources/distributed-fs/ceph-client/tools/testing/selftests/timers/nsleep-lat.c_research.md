# sources/distributed-fs/ceph-client/tools/testing/selftests/timers/nsleep-lat.c

## Purpose
Measures `clock_nanosleep()` latency for relative and absolute sleeps across supported clocks.

## Important APIs, Types, and Functions
Defines `UNRESONABLE_LATENCY`, `CLOCK_HWSPECIFIC`, `UNSUPPORTED`, and `SKIPPED_CLOCK_COUNT`. Functions are `clockstring`, `timespec_add`, `timespec_sub`, `nanosleep_lat_test`, and `main`.

## Control Flow
`main()` iterates clocks from realtime through TAI, skipping CPU-time and hardware-specific clocks. For each clock, it tests sleep lengths from 10 ns up to 10 seconds. `nanosleep_lat_test()` checks average relative sleep latency over 10 iterations and average absolute sleep latency over 10 iterations, failing if either exceeds 40 ms.

## State and Persistence Behavior
No persistent state. It only reads clocks and sleeps.

## Dependencies and Integration Points
Depends on POSIX clock APIs, `clock_nanosleep`, and kselftest. Integrates with scheduler/timer latency behavior.

## Risks and Edge Cases
Latency results are workload and scheduler dependent. The threshold is permissive but can still fail under heavy load or virtualized environments. Unsupported clocks are skipped.

## Test Signals
Signals are per-clock pass/skip/fail lines, with failure messages showing large relative or absolute latency.
