# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_keyboard.py

## Purpose

This file provides reusable UHID keyboard device models and pytest test classes for Linux HID keyboard input behavior. It covers bitmap-style keyboards, boot-protocol array keyboards, LED-output descriptors, and a Primax-style descriptor ordering edge case. The tests verify key press/release reliability, simultaneous keys, modifier handling, array rollover behavior, and correct parsing when local usages are defined before the final usage page.

## Important APIs, Types, and Functions

- `InvalidHIDCommunication` is declared for consistency with other HID tests but is not used in this file.
- `KeyboardData` is an empty report data carrier. Dynamic attributes are set on it before passing it to `UHIDTestDevice.create_report()`.
- `BaseKeyboard(base.UHIDTestDevice)` is the shared keyboard fixture device. It initializes as application `"Key"` and owns `self.keystates`, a dictionary mapping HID usage names to boolean pressed state.
- `BaseKeyboard._update_key_state(keys)` removes previously released keys, marks currently pressed keys as released, then marks the supplied key names as pressed. This allows callers to send complete current-key sets while still generating release information.
- `BaseKeyboard._create_report_data()` normalizes key names by removing spaces and lowercasing, then sets matching attributes on `KeyboardData`.
- `BaseKeyboard.create_array_report(keys, reportID=None, application=None)` updates state, chooses `self.default_reportID` when needed, builds report data, and calls the hidtools report encoder.
- `BaseKeyboard.event()` creates and sends an input report through UHID, returning the raw report bytes for debug output.
- `PlainKeyboard` defines report ID `1` and a bitmap descriptor: modifier bits plus 152 one-bit keyboard usages.
- `ArrayKeyboard` defines a boot-style array descriptor with 8 modifier bits and six 8-bit key slots. Its `_create_report_data()` separates modifiers from non-modifier keys using `hidtools.hut.HUT`, and emits six `ErrorRollOver` usages when more than six non-modifier keys are pressed.
- `LEDKeyboard` extends the array keyboard descriptor with LED output fields.
- `PrimaxKeyboard` models a descriptor that sets `Usage Page (Keyboard)` after declaring usage min/max values, covering HID spec behavior that local usages are combined with usage pages when a main item is parsed.
- `BaseTest.TestKeyboard` is a reusable nested test mixin containing `test_single_key`, `test_two_keys`, and `test_modifiers`.
- `TestPlainKeyboard`, `TestArrayKeyboard`, `TestLEDKeyboard`, and `TestPrimaxKeyboard` bind the mixin to concrete device descriptors and add descriptor-specific tests.

## Control Flow

Concrete pytest classes implement `create_device()` and inherit the shared UHID setup from `base.BaseTestCase.TestUhid`. Each test sends a full current-key list through `uhdev.event()`, reads synchronized events with `uhdev.next_sync_events()`, logs reports with `debug_reports()`, and asserts expected `libevdev.InputEvent` instances. The shared tests first press and release `KEY_A`, then exercise two-key press/release transitions including no-repeat behavior for keys that remain held, and finally verify modifier mapping for left control, left shift, and equals.

`TestPlainKeyboard.test_10_keys()` presses ten digit keys simultaneously, which the bitmap descriptor can represent, and then verifies all ten release events. `TestArrayKeyboard.test_10_keys()` presses six keys successfully, then sends ten keys and expects no input events because the array report becomes `ErrorRollOver`, then releases and verifies the six earlier keys are released. LED and Primax classes reuse the shared behavioral tests without adding custom assertions.

## State and Persistence

The only durable state across report sends is the in-memory `keystates` dictionary on each `BaseKeyboard` instance. It tracks pressed and recently released keys so report generation can model stateful HID keyboard behavior. No state persists beyond a test instance, and there is no file, network, or database persistence. Kernel input state is observed through libevdev values such as `evdev.value[KEY_A]`.

## Dependencies and Integration Points

The file depends on `.base` for UHID test infrastructure, `hidtools.hid` and `hidtools.hut.HUT` for report generation and usage-name lookup, and `libevdev` for Linux input event constants and assertions. It integrates with the kernel HID parser, HID input mapping layer, UHID transport, and evdev event queues. `test_ite_keyboard.py` imports `ArrayKeyboard` and `TestArrayKeyboard`, so this file is also a local fixture provider for device-specific keyboard tests.

## Risks and Edge Cases

Key names must match hidtools HUT names after normalization. A name mismatch breaks report encoding before kernel behavior is tested. `_update_key_state()` mutates a dictionary while using a list copy only for removal; this is safe for removals, but later iteration over `self.keystates.keys()` relies on no size-changing mutation during that loop. Array rollover behavior intentionally expects no events for over-six-key input, so a kernel change that reports rollover differently could alter test expectations. The Primax descriptor is sensitive to HID parser handling of local/global item ordering; edits that reorder descriptor bytes can remove the coverage.

## Test Signals

Passing tests show that generated reports match descriptors closely enough for the kernel to emit expected `EV_KEY` events, that held keys are not re-emitted unnecessarily, that releases update evdev state, that modifiers map to left-control and left-shift keys, that bitmap descriptors support many simultaneous keys, and that array descriptors suppress normal key events on rollover. Failures localize either to report generation, descriptor parsing, key usage mapping, event synchronization, or kernel input behavior.
