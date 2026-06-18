# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/leafloop.c

## Purpose
This workload provides stable non-inlined `parent` and `leaf` symbols in a timed CPU loop for perf script/report symbol tests.

## Important APIs, Types, And Functions
It declares and defines `noinline void leaf(volatile int b)` and `noinline void parent(volatile int b)`, plus workload entry `leafloop()`. It uses `signal()`, `alarm()`, `atoi()`, and `DEFINE_WORKLOAD(leafloop)`.

## Control Flow
`leafloop()` parses duration, installs SIGINT/SIGALRM handlers, arms an alarm, and calls `parent(sec)`. `parent()` calls `leaf()`, and `leaf()` increments volatile static `a` until `done` is set.

## State, Dependencies, And Integration
State is `a` and `done`, both process-local. `noinline` is the important integration contract because downstream tests expect visible `parent` and `leaf` symbols rather than optimized-away frames.

## Risks And Test Signals
Changing function names, attributes, or compiler flags can break downstream symbol matching. Success is usually measured outside the workload by perf output containing the expected function symbols for sampled CPU time.
