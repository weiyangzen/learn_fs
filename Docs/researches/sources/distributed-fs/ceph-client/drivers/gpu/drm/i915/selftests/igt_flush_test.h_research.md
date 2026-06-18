# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_flush_test.h

## Purpose
This header declares the shared `igt_flush_test()` live-test cleanup helper.

## Important APIs, Types, And Functions
It forward-declares `struct drm_i915_private` and declares `int igt_flush_test(struct drm_i915_private *i915)`.

## Control Flow
Consumers call the function after live GPU operations, typically from teardown or explicit cleanup points.

## State And Persistence
The header has no state. The implementation may wedge a GT on timeout.

## Dependencies And Integration Points
It is intentionally lightweight and included by the central selftest runner and live helper files.

## Risks
The API exposes only an i915-wide flush, not per-GT/per-engine control, so callers must treat failure as broad hardware contamination.

## Test Signals
Callers interpret `0` as clean idle and `-EIO` as flush failure or wedge.
