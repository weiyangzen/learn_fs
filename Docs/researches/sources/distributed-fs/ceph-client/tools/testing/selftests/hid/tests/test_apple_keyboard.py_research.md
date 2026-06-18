# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_apple_keyboard.py

## Purpose
`test_apple_keyboard.py` emulates an Apple Wireless Keyboard and validates `hid-apple` function-key behavior, especially interactions between the Fn state report, top-row function keys, media/application mappings, and arrow-key page navigation mappings.

## Important APIs, types, and functions
`KERNEL_MODULE` identifies `hid-apple`. `AppleKeyboard` extends `ArrayKeyboard`, supplies a multi-report descriptor with keyboard, consumer, battery, Fn/vendor, media, and feature reports, sets Bluetooth Apple VID/PID input info, and defines `send_fn_state()` to emit report ID 17 with usage `0xff0003`. `TestAppleKeyboard` extends `TestArrayKeyboard`, loads the apple module, creates the virtual device, and contains focused event-order tests.

## Control flow
Tests create the Apple keyboard through the common UHID fixture. They send key array reports with `uhdev.event([...])`, send Fn state reports with `send_fn_state()`, read evdev sync events, and assert both emitted events and persistent evdev key values. Cases cover plain F4 mapping to `KEY_ALL_APPLICATIONS`, Fn+F4 mapping to `KEY_F4`, releasing Fn before function key release, pressing Fn after a top-row key, multiple function keys, transition cases, and Fn+UpArrow producing `KEY_PAGEUP`.

## State and persistence
State lives in the virtual keyboard and kernel input device: pressed key arrays, Fn key state, and evdev key values. No repository or disk state is written. The test intentionally checks persistent key values after intermediate reports to catch stuck-key regressions.

## Dependencies and integration points
It depends on `test_keyboard.ArrayKeyboard`, `TestArrayKeyboard`, libevdev, hidtools bus metadata, and the `hid-apple` kernel module. It integrates with the common uhid/udev/evdev lifecycle from `base.py`.

## Risks and test signals
Risks include hid-apple keymap changes, event ordering subtleties, and dependence on exact Apple descriptor semantics. Strong signals are expected `EV_KEY` transitions, absence of incorrect alternate key states, and stable behavior across press/release ordering permutations.
