# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base_gamepad.py

## Purpose
`base_gamepad.py` provides reusable virtual gamepad and joystick device models for the pytest HID suite. It maps HID usages into evdev button and axis expectations and generates input reports with persistent button, stick, and hat-switch state.

## Important APIs, types, and functions
`InvalidHIDCommunication` reports attempts to set unsupported buttons. `GamepadData` is a dynamic data container passed to hidtools report creation. `AxisMapping` maps HID axis names to libevdev `EV_ABS` bits. `BaseGamepad` extends `BaseDevice`, defining default button maps, stick maps, report state, `create_report()`, and `event()`. `JoystickGamepad` adjusts button mappings and right-stick axes to joystick conventions.

## Control flow
Tests call `event()` with optional left/right stick tuples, hat-switch value, and button dictionary. `create_report()` validates button ids, merges `None` values with prior state, stores axes into a `GamepadData` instance, sets `hatswitch`, and delegates actual report serialization to `BaseDevice.create_report()`. The resulting report is sent via `call_input_event()`.

## State and persistence
Each device instance persists `_buttons`, `left`, `right`, and `hat_switch` values across generated reports so tests can model partial state changes. `default_reportID` is inherited from `BaseDevice` and can be set by subclasses.

## Dependencies and integration points
It depends on libevdev, hidtools bus metadata, and `BaseDevice`. It is consumed by `test_gamepad.py` and device-specific classes to test kernel HID parsing into evdev events.

## Risks and test signals
Risks include mismatched HID usage names, wrong evdev mappings for device classes, and persistent state hiding test setup mistakes. Signals are button press/release events, axis movement events only when values differ from neutral, and hat-switch mapping to `ABS_HAT0X/Y`.
