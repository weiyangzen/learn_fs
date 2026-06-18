# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.c

## Purpose
This file provides begin/end guards for live hardware selftests. It ensures GTs are idle before a test and detects unexpected global or per-engine resets after the test.

## Important APIs, Types, And Functions
- `igt_live_test_begin()` stores the i915 pointer, function/name labels, baseline global reset count, and per-engine reset counts.
- `igt_live_test_end()` flushes the GPU, compares reset counters against the baseline, and reports unexpected reset activity.

## Control Flow
Begin iterates all GTs, waits indefinitely for idle, then records reset counts for each engine. End calls `igt_flush_test()`, checks global reset count, then checks every engine reset count. Any mismatch returns `-EIO`.

## State And Persistence
State is held in the caller-provided `struct igt_live_test`. The implementation reads persistent driver reset counters and may observe wedge state through `igt_flush_test()`.

## Dependencies And Integration Points
It depends on GT idle wait, reset-count helpers, GT logging, and `igt_flush_test`. Live tests in request and VMA files use it to bracket hardware exercises.

## Risks
Tests that intentionally reset hardware must not be wrapped by this helper or must bracket reset separately, because any reset count change is treated as failure.

## Test Signals
Failure logs identify `func(name)` and the reset count delta for global or engine-specific resets. Success means no unexpected reset and clean idle flush.
