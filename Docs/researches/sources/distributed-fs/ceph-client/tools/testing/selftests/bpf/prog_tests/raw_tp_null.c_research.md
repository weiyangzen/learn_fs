# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/raw_tp_null.c

## Purpose
Checks raw tracepoint programs with nullable/null context handling and rejects invalid variants through a fail skeleton. The source was read as a complete 29-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_raw_tp_null()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "raw_tp_null.skel.h"`, `#include "raw_tp_null_fail.skel.h"`.
- Generated skeletons/objects referenced: `raw_tp_null`, `raw_tp_null_fail`.
- Primary APIs and types: `raw_tp_null__open_and_load()`, `raw_tp_null_fail` skeleton load expectation, `trigger_module_test_read()`, and skeleton BSS invocation counters.

## Control Flow
The test loads the accepted skeleton, expects the fail skeleton to be rejected, triggers the test module read path, and checks invocation count from the raw tracepoint program.

## State and Persistence Behavior
BPF-side invocation counter is the observable state; module trigger and skeleton links are temporary.

## Dependencies and Integration Points
Depends on `raw_tp_null.skel.h`, `raw_tp_null_fail.skel.h`, selftests test module trigger, and raw tracepoint support.

## Risks and Edge Cases
Requires the bpf test module path used by `trigger_module_test_read`; fail-log expectations may change with verifier diagnostics.

## Test Signals
Assertions check successful load, trigger success, and expected invocation count. Named assertion/check labels observed in the source include: `raw_tp_null__open_and_load`, `trigger testmod read`, `invocations`.
