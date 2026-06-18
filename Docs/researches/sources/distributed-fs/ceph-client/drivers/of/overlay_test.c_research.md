# sources/distributed-fs/ceph-client/drivers/of/overlay_test.c

## Purpose
Provides KUnit tests for test-managed device-tree overlays, verifying node creation, platform-device creation, and automatic cleanup.

## Important APIs, types, and functions
Test cases are `of_overlay_apply_kunit_apply()`, `of_overlay_apply_kunit_platform_device()`, and `of_overlay_apply_kunit_cleanup()`. The helper `of_overlay_bus_match_compatible()` supports platform-bus lookup by compatible string.

## Control flow
Tests apply `kunit_overlay_test` with `of_overlay_apply_kunit()`, then look up the `kunit-test` node and associated platform device. Cleanup uses a fake KUnit context, applies an overlay, calls `kunit_cleanup()`, and verifies both node and compatible platform device are gone.

## State and persistence behavior
Overlay lifetime is owned by the KUnit test context. References are released through KUnit and OF/device put helpers.

## Dependencies and integration points
Depends on KUnit OF helpers, OF overlay support, early flattree support, platform bus lookup, and generated KUnit overlay fixture data.

## Risks and edge cases
Cleanup validation is skipped without suitable OF root or overlay/flattree support. Failures indicate leaked test-managed overlays or devices.

## Test signals
The file is direct KUnit coverage for overlay apply and cleanup behavior.
