# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/gettimeofday.c

## Purpose
Benchmarks repeated `gettimeofday()` calls, typically exercising VDSO time access.

## Important APIs, Types, and Functions
Defines `test_gettimeofday()` and `main()`, using `timebase_read()`/`timebase_delta()` helpers and `test_harness()`.

## Control Flow
The test loops a fixed number of `gettimeofday(&tv, NULL)` calls, measures elapsed timebase, prints timing, and returns success.

## State and Persistence
No persistent state; only local timing variables.

## Dependencies and Integration Points
Depends on libc `gettimeofday`, PowerPC timebase utilities, and the common harness.

## Risks and Test Signals
Risk is measurement noise. Failure signal is unusual syscall/library failure or harness failure, not a strict performance threshold.
