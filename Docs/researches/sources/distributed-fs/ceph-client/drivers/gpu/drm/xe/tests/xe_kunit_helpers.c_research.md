# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_kunit_helpers.c

## Purpose

`xe_kunit_helpers.c` provides reusable helpers to allocate fake Xe DRM devices for unit tests and prepare live Xe devices for live KUnit suites.

## Important APIs, Types, and Functions

- `xe_kunit_helper_alloc_xe_device()` allocates a `struct xe_device` embedded in a KUnit DRM device.
- `xe_kunit_helper_xe_device_test_init()` allocates a fake parent device, allocates an Xe device, initializes it through `xe_pci_fake_device_init`, restores prior `test->priv` through a KUnit action, and stores the fake device in `test->priv`.
- `xe_kunit_helper_xe_device_live_test_init()` obtains a live device from `test->param_value`, checks it is not wedged, takes runtime PM, registers a runtime-PM put action, and stores it in `test->priv`.

## Control Flow

Fake init allocates resources with KUnit-managed helpers, initializes fake PCI/platform data, registers a cleanup action to restore original private data, and returns zero or aborts through KUnit assertions. Live init uses the parameterized device pointer, resumes runtime PM, registers cleanup, and returns zero.

## State and Persistence Behavior

Fake-device state is KUnit-managed and freed with the test. The helper temporarily overwrites `test->priv` and restores it through an action. Live helper holds a runtime PM reference for the test duration and releases it through a KUnit action.

## Dependencies and Integration Points

It depends on DRM KUnit helpers, `xe_pci_fake_device_init`, Xe PM runtime APIs, and KUnit visibility exports. It is used by most Xe unit and live KUnit suites in this group.

## Risks and Edge Cases

- Tests that rely on incoming `test->priv` fake data must call the helper before overwriting it themselves.
- Live tests abort if the device is wedged, so failure can mean environment/device state rather than test logic.
- Missing cleanup actions would leak runtime PM references or leave `test->priv` altered.

## Test Signals

Signals include fake device initialization success, correct parameterized live device binding, runtime PM get/put balance, and stable use by dependent suites.
