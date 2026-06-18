# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/prog_tests_framework.c

## Purpose
Self-tests the `test_progs` framework itself: subtest counting, output capture, failure emission, and dummy test registration behavior. The source was read as a complete 182-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `clear_test_state()`, `test_prog_tests_framework()`, `dummy_emit()`.
- Includes and fixtures: `#include "test_progs.h"`, `#include "testing_helpers.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `test__start_subtest()`, framework state globals, `open_memstream()`/capture helpers, `ASSERT_*` macros, and `dummy_emit()`.

## Control Flow
The test clears framework state, starts nested/numbered subtests, emits dummy pass/fail output, and compares captured output to expected framework formatting.

## State and Persistence Behavior
Mutates global test framework state, stdout/stderr capture buffers, and subtest counters. `clear_test_state()` resets these between checks.

## Dependencies and Integration Points
Depends on `test_progs.h` and `testing_helpers.h`; no BPF object is loaded.

## Risks and Edge Cases
Very sensitive to formatting changes in the framework; tests can fail due to expected text drift rather than kernel behavior.

## Test Signals
Assertions check subtest number accounting and captured expected output strings. Named assertion/check labels observed in the source include: `subtest_num_check`, `expected output`, `, `.
