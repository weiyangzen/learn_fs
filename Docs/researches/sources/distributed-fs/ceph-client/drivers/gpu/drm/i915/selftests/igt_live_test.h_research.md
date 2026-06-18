# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_live_test.h

## Purpose
This header declares the live-test guard state and begin/end functions.

## Important APIs, Types, And Functions
`struct igt_live_test` stores the i915 pointer, function/test labels, global reset baseline, and `reset_engine[I915_MAX_GT][I915_NUM_ENGINES]`. It declares `igt_live_test_begin()` and `igt_live_test_end()`.

## Control Flow
Callers allocate the struct on the stack, call begin before GPU work, and call end after cleanup to validate reset/idle state.

## State And Persistence
The struct stores per-test snapshots only. Reset counters it compares are maintained elsewhere in the driver.

## Dependencies And Integration Points
It includes GT and engine constants for array dimensions and is consumed by live request, memory, VMA, and perf helpers.

## Risks
Array dimensions must match engine/GT enumeration limits. The helper assumes tests are not expected to reset the GPU.

## Test Signals
The end function returns `0` for clean execution and `-EIO` for flush failure or reset-count drift.
