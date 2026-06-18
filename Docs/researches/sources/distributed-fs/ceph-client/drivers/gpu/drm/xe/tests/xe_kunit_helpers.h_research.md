# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.h

## Purpose

`xe_kunit_helpers.h` declares the shared Xe KUnit helper API for fake and live device setup.

## Important APIs, Types, and Functions

- Forward declarations for `struct device`, `struct kunit`, and `struct xe_device`.
- `xe_kunit_helper_alloc_xe_device(struct kunit *test, struct device *dev)`.
- `xe_kunit_helper_xe_device_test_init(struct kunit *test)`.
- `xe_kunit_helper_xe_device_live_test_init(struct kunit *test)`.

## Control Flow

There is no executable logic in the header. Test suites include it and assign the init helpers to KUnit suite `.init` callbacks or call allocation directly.

## State and Persistence Behavior

No state is stored here. The declared functions manage KUnit device state and runtime PM in the implementation.

## Dependencies and Integration Points

It provides the public test helper contract for Xe KUnit files, avoiding direct dependence on implementation details in each suite.

## Risks and Edge Cases

- Prototype drift will break many test suites.
- The header intentionally uses forward declarations to keep includes light; implementation-specific types must not leak into it unnecessarily.

## Test Signals

Successful compilation of all dependent KUnit suites is the main signal; runtime signals come from fake/live initialization in `xe_kunit_helpers.c`.
