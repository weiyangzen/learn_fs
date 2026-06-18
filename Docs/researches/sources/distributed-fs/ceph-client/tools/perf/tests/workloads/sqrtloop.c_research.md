# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/sqrtloop.c

## Purpose
This workload generates floating-point/libm activity in a child process so perf tests can exercise profiling across forked workloads and math-library symbols.

## Important APIs, Types, And Functions
Functions are `__sqrtloop(int sec)` and workload entry `sqrtloop()`. It uses `fork()`, `wait()`, `signal()`, `alarm()`, `sqrt()`, `rand()`, `atoi()`, and `DEFINE_WORKLOAD(sqrtloop)`.

## Control Flow
The parent parses an optional duration and forks. The child installs SIGALRM handling, arms the alarm, and repeatedly calls `sqrt(rand())` until done. The parent waits for the child and returns success unless `fork()` failed.

## State, Dependencies, And Integration
State is only the child process's signal flag. Dependencies include libc process control and libm. It integrates with perf tests that need child-process sampling or dynamic/library call activity.

## Risks And Test Signals
The workload depends on fork support and libm linkage. It ignores the child's exact exit status by using `wait(NULL)`, so downstream tests should validate perf data rather than workload return detail. Success is a bounded child process with samples around `sqrt`/random computation.
