# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/time.h

## Purpose
Provides `gettimeofday` compatibility for nolibc.

## APIs, Types, and Functions
Defines `_sys_gettimeofday` and `gettimeofday`, with a fallback through `_sys_clock_gettime` when native gettimeofday is not available.

## Control Flow, State, and Persistence
The wrapper populates caller-provided `timeval` and optional timezone data, translating syscall errors. It persists no state.

## Dependencies and Integration
Depends on `../time.h`, `../types.h`, and syscall availability. It integrates with programs expecting `<sys/time.h>` rather than `<time.h>`.

## Risks and Test Signals
Risks include timezone argument compatibility, time64 conversion on 32-bit, and syscall fallback precision differences. Test signals are non-null and null timeval calls, monotonicity sanity checks, 32-bit builds, and invalid pointer fault handling in negative tests.
