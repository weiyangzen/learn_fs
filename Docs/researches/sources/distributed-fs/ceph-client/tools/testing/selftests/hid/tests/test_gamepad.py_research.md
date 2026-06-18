# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_gamepad.py

## Purpose
`test_gamepad.py` validates kernel HID parsing and evdev mapping for several gamepad/joystick descriptors, including generic Saitek and Asus devices plus a FR-TEC Raptor Mach 2 path that requires a HID-BPF descriptor fixup.

## Important APIs, types, and functions
`BaseTest.TestGamepad` is a reusable test class layered on `base.BaseTestCase.TestUhid`. It sends an initial neutral report, then checks individual buttons, dual-button transitions, left/right stick axes, and hat-switch directions. Device classes include `SaitekGamepad`, `AsusGamepad`, and `RaptorMach2Joystick`; they define report descriptors, bus/vendor/product identity, supported button ids, axis mappings, and special hat scaling for the Raptor. `TestRaptorMach2Joystick` lists `HidBpf("FR-TEC__Raptor-Mach-2.bpf.o", True)`.

## Control flow
For each concrete test class, pytest creates a virtual device. The autouse fixture sends an empty report to initialize axes. Button tests build reports through `BaseGamepad.event()`, read evdev events, and assert key values. Axis tests move sticks through representative values and check corresponding absolute events. Hat-switch tests are skipped when the descriptor lacks the usage and otherwise validate north/east/south/west mappings. The Raptor test path loads a HID-BPF program and waits for descriptor fixup rebind readiness.

## State and persistence
Gamepad state persists in the virtual device between reports: held buttons, stick coordinates, and hat-switch null/current values. Kernel evdev state is asserted after transitions. No persistent files are created.

## Dependencies and integration points
It depends on pytest markers, libevdev, `base_gamepad.py`, hidtools, and the common HID-BPF loader for Raptor. It integrates with kernel HID input mapping, optional in-tree `drivers/hid/bpf/progs` assets, and evdev reporting.

## Risks and test signals
Risks include descriptor quirks, neutral-axis assumptions, BPF program availability, and differing joystick/gamepad evdev mappings. Test signals are exact button press/release events, axis events only for meaningful changes, correct hat-switch signs, and successful BPF-assisted device readiness.
