# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/brstack.c

## Purpose
This workload generates predictable branch-stack activity for perf tests: direct calls, returns, a conditional branch, an unconditional loop branch, and an indirect call.

## Important APIs, Types, And Functions
Local functions are `brstack_bar()`, `brstack_foo()`, `brstack_bench()`, and workload entry `brstack()`. It uses `atoi()` for optional loop count parsing and `DEFINE_WORKLOAD(brstack)` for registration. The static volatile `cnt` prevents the compiler from fully collapsing the branch behavior.

## Control Flow
`brstack()` defaults to `BENCH_RUNS` loops, optionally overrides it from `argv[0]`, then loops until `cnt` exceeds the threshold. Each iteration calls `brstack_bench()`, which increments `cnt`, conditionally calls `brstack_foo()`, calls `brstack_bar()` directly, and calls `brstack_foo()` through a function pointer.

## State, Dependencies, And Integration
State is a process-local volatile counter. The workload is integrated through perf's workload registry and is intended to be run under perf record/script/report branch sampling tests.

## Risks And Test Signals
Compiler optimization and inlining are the main risks because the test relies on recognizable call/branch shape; the simple function boundaries and volatile counter mitigate this. The signal is not an assertion here but downstream perf output containing the expected branch types and symbols.
