# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_mouse.py

## Purpose

This file provides reusable UHID mouse device models and pytest tests for Linux HID pointer behavior. It covers button state, relative X/Y movement, vertical wheel events, horizontal AC Pan events, high-resolution wheel support through HID resolution multipliers, a Xiaomi/MI dongle mouse with split reports, a failed resolution-multiplier setup path, and a malformed syzbot-derived descriptor that should not crash the kernel. It is both a test suite and a fixture library for HID mouse report generation.

## Important APIs, Types, and Functions

- The libevdev compatibility block defines `REL_WHEEL_HI_RES` and `REL_HWHEEL_HI_RES` aliases when older python-libevdev versions lack them.
- `InvalidHIDCommunication` is raised by fake devices when the kernel sends an unexpected feature report request.
- `MouseData` is a dynamic data carrier passed to `UHIDTestDevice.create_report()`.
- `BaseMouse(base.UHIDTestDevice)` stores persistent button state (`left`, `right`, `middle`) and provides `create_report()` and `event()`. `create_report()` accepts relative movement, optional partial button updates where `None` means "leave unchanged", optional wheel or `(vertical, horizontal)` wheel tuple, and an optional report ID.
- `ButtonMouse` defines a basic 3-button relative mouse descriptor and `fake_report()`, a manual encoder used to validate hidtools report generation and range handling.
- `WheelMouse` adds a vertical wheel and `wheel_multiplier`.
- `TwoWheelMouse` expands to 16 button bits, 16-bit X/Y axes, vertical wheel, and consumer-page `AC Pan` horizontal wheel, with `hwheel_multiplier`.
- `MIDongleMIWirelessMouse` models a USB `0x2717:0x003B` MI wireless mouse. Its `event()` sends report ID `1` for buttons/wheel and report ID `2` for X/Y movement, because this device splits pointer data across reports.
- `ResolutionMultiplierMouse` defines a feature report for `Resolution Multiplier`, defaults to report ID `0x11`, validates a kernel `SET_REPORT` for report ID `0x12` with data `[0x12, 0x1]`, and then sets `wheel_multiplier = 4`.
- `BadResolutionMultiplierMouse` accepts the same setup but returns `32` (`EPIPE`) and resets multipliers to `1`.
- `BadReportDescriptorMouse` uses a malformed syzbot-generated descriptor with zero-sized features. It overrides evdev/event readiness behavior so the test waits for a feature report instead of input nodes, and validates that the kernel sends a one-byte feature report without crashing.
- `ResolutionMultiplierHWheelMouse` adds both vertical and horizontal multiplier feature collections and sets both multipliers to `12` after accepting data `[0x12, 0x5]`.
- `BaseTest.TestMouse` supplies shared `test_buttons()` and `test_relative()` methods for button and relative movement behavior.
- Concrete test classes bind fixtures to descriptors: `TestSimpleMouse`, `TestWheelMouse`, `TestTwoWheelMouse`, `TestResolutionMultiplierMouse`, `TestBadResolutionMultiplierMouse`, `TestResolutionMultiplierHWheelMouse`, `TestMiMouse`, and `TestBadReportDescriptorMouse`.

## Control Flow

For ordinary pointer tests, pytest creates the concrete device, sends reports through `uhdev.event()`, reads `uhdev.next_sync_events()`, and asserts exact or inclusive libevdev events. `test_buttons()` walks right, middle, left, and combined left/right press-release transitions while checking evdev's current button values. `test_relative()` sends relative Y, X, and combined X/Y movement and expects matching `EV_REL` events.

`TestSimpleMouse.test_rdesc()` does not use a kernel event path for its core assertion. It compares `ButtonMouse.fake_report()` with generated reports for multiple button and movement combinations, then verifies that out-of-range Y movement raises `hidtools.hid.RangeError`.

Wheel tests detect kernel high-resolution support by checking evdev capabilities. `TestWheelMouse.test_wheel()` sends wheel deltas pre-multiplied by the device multiplier and expects normal `REL_WHEEL` events plus high-resolution events of 120 units per detent when supported. `TestTwoWheelMouse.test_ac_pan()` mirrors that behavior for horizontal `REL_HWHEEL` and combined vertical/horizontal wheel movement.

Resolution multiplier tests rely on kernel feature-report negotiation during device setup. If high-resolution wheel support is absent, tests skip or assert that no multiplier was triggered. If present, they assert the multiplier divides 120 and then send unit HID wheel reports that accumulate high-resolution deltas; after enough reports to complete one detent, the kernel emits the corresponding low-resolution wheel event. The bad multiplier variant verifies that a failed `SET_REPORT` leaves multipliers at `1`. The MI mouse overrides event assertion to tolerate two SYN frames because the device sends movement and buttons in separate reports.

## State and Persistence

Mouse state is in-memory per test device. Button fields persist across calls so partial button tuples can model holding one button while changing another. Wheel and horizontal wheel multipliers are mutable fields changed by feature-report negotiation callbacks. `BadReportDescriptorMouse.high_resolution_report_called` gates readiness after the kernel issues the expected feature report. No state is persisted outside the test process, but kernel evdev state is queried for current button values and capabilities.

## Dependencies and Integration Points

The file depends on `.base` for UHID fixtures, `hidtools.hid` for report encoding and `RangeError`, `hidtools.util.BusType` and `to_twos_comp`, `libevdev` for input constants/capability checks, and `pytest` for skip and exception assertions. It integrates with Linux UHID, the HID parser, HID input mapping, evdev synchronization, feature report handling through `set_report()`, high-resolution wheel support, and device-specific matching based on USB vendor/product IDs.

## Risks and Edge Cases

High-resolution wheel tests are kernel-capability-dependent and skip or change expectations when support is missing. The compatibility aliases for older libevdev map high-resolution constants to raw relative codes; this keeps tests runnable but can obscure library-version issues. Resolution multiplier setup is hardcoded to expected feature report payloads instead of deriving them from descriptors, which makes descriptor edits risky. `BadReportDescriptorMouse.get_evdev()` intentionally returns a string sentinel to work around fixture expectations, so base fixture changes could break this special case. MI split-report behavior can produce extra SYN frames, requiring custom assertion logic. Range validation is split between hidtools report creation and kernel input behavior, so failures may originate before UHID injection.

## Test Signals

Passing tests show that report descriptors and generated reports map to expected button, relative movement, wheel, and horizontal wheel events; that evdev state reflects button transitions; that report generation rejects out-of-range data; that high-resolution wheel multipliers are negotiated and accumulated correctly when supported; that failed feature negotiation degrades to ordinary wheel behavior; that a split-report MI mouse still produces the effective expected events; and that malformed zero-sized feature descriptors do not crash the kernel. Failures are useful signals for descriptor regressions, hidtools encoding bugs, kernel HID parser issues, feature-report negotiation changes, or evdev event ordering changes.
