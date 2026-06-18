# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_hid_core.py

## Purpose

This file is a narrowly scoped UHID selftest for generic HID core behavior, not for a particular end-user device class. It creates an artificial mouse report descriptor with deeply nested collections to exercise the HID parser collection stack reallocation path in `hid-core.c`. The test is intentionally a negative/crash regression check: successful execution mainly proves that creating and probing the device did not oops or crash the kernel while parsing the descriptor.

## Important APIs, Types, and Functions

- `TestCollectionOverflow(base.BaseTestCase.TestUhid)` is the only test class. It uses the shared HID selftest fixture that creates a UHID device, waits for the kernel-side input path, and exposes debug/assertion helpers.
- `create_device()` builds a `base.UHIDTestDevice` with `application="Mouse"` and a handcrafted byte-list report descriptor.
- `test_rdesc()` is intentionally empty. The assertion is implicit in fixture setup and teardown: if descriptor parsing triggers the historical collection-stack bug, the kernel or test environment fails before the no-op test can pass.
- The local `logger` uses the `hidtools.test.hid` namespace but is not used directly in this file.

## Control Flow

Pytest discovers `TestCollectionOverflow`, the base fixture calls `create_device()`, and `base.UHIDTestDevice` sends the descriptor through UHID to the kernel. The descriptor opens many nested logical collections, defines button bits, relative X/Y axes, a resolution multiplier feature report, and a wheel input report, then closes the collections. Once the fixture has created the device, `test_rdesc()` executes `pass`; there are no explicit input reports or event assertions.

## State and Persistence

The file has no persistent storage and no mutable test state beyond the UHID device created by the base fixture. All meaningful state lives in the kernel HID parser while it consumes the nested collection hierarchy. The test descriptor itself is static, deterministic, and recreated per test instance.

## Dependencies and Integration Points

The test depends on the local `.base` module for `BaseTestCase.TestUhid` and `UHIDTestDevice`. It integrates with the Linux UHID interface and the kernel HID core parser. The descriptor models a mouse application so it also touches the kernel's HID input mapping path enough to instantiate the device, but the target behavior is the generic descriptor parser collection stack.

## Risks and Edge Cases

The primary risk is false confidence: the test has no positive assertion and can only detect severe failures such as kernel crashes, probe failures, or fixture errors. Because the bug depends on memory layout and parser stack behavior, a pass does not prove the original defect is absent in every configuration. The descriptor is intentionally unusual, so changes that simplify or "clean up" nested collections could remove the stress condition. The test also assumes the base fixture treats device creation failure as a test failure.

## Test Signals

The signal is binary and indirect. A passing run means the UHID device was created and torn down without crashing the kernel or failing descriptor parsing. A failing run will likely appear as fixture setup failure, kernel crash/oops, device creation timeout, or UHID communication failure rather than as an assertion inside `test_rdesc()`.
