# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_ite_keyboard.py

## Purpose

This file adds a device-specific regression test for ITE keyboards handled by the `hid_ite` kernel module. It reuses the generic array keyboard test suite while adding a descriptor that includes keyboard, consumer control, wireless radio, vendor, system-control, and feature-report collections. The specific regression covered is the ITE WiFi key quirk: some devices send no report on key press and only send a null-looking wireless-radio report on release, and the kernel driver should translate that release report into a synthetic RFKILL key press and release.

## Important APIs, Types, and Functions

- `KERNEL_MODULE = base.KernelModule("itetech", "hid_ite")` declares the module dependency for the test class.
- `KbdData` is an empty data carrier class, currently unused in the active logic.
- `ITEKeyboard(ArrayKeyboard)` inherits the report generation and key-state behavior from `test_keyboard.ArrayKeyboard`.
- `ITEKeyboard.report_descriptor` is a multi-application descriptor with report IDs: `0x5a` for vendor feature data, `0x01` for keyboard array input and LEDs, `0x02` for consumer control, `0x03` for wireless radio controls, `0x04` for vendor input, and `0x05` for system control.
- `ITEKeyboard.__init__()` defaults the bus/vendor/product tuple to USB `0x06CB:0x2968`, matching the device identity expected by the kernel quirk.
- `ITEKeyboard.event()` defaults `application` to `"Keyboard"` before delegating to `ArrayKeyboard.event()`, preserving normal keyboard report behavior despite the descriptor's multiple applications.
- `TestITEKeyboard(TestArrayKeyboard)` inherits all generic array-keyboard tests and adds the ITE-specific WiFi-key test.
- `test_wifi_key()` injects raw report bytes `[0x03, 0x00]` and expects `KEY_RFKILL` down and up events in the same kernel event batch.

## Control Flow

The test class loads or requires `hid_ite`, creates an `ITEKeyboard`, and then runs inherited keyboard behavior tests from `TestArrayKeyboard`. For the specific quirk, `test_wifi_key()` bypasses the normal key-name-to-report helper and calls `uhdev.call_input_event([0x03, 0x00])` directly, targeting report ID `3` for the wireless radio collection. It first builds an expected list containing `SYN_REPORT` and `KEY_RFKILL` value `1`, reads `uhdev.next_sync_events()`, and asserts the press is present. It then checks the same already-read event batch for a `KEY_RFKILL` value `0`, relying on the kernel sending the synthetic press and release together.

## State and Persistence

The ITE device inherits `ArrayKeyboard`'s in-memory `keystates` dictionary for normal keyboard reports, but `test_wifi_key()` does not use it. There is no file or external persistence. The relevant state transition is inside the kernel driver quirk: a wireless-radio release report must synthesize a complete RFKILL key click without a preceding hardware press report.

## Dependencies and Integration Points

The file depends on `.test_keyboard.ArrayKeyboard` and `.test_keyboard.TestArrayKeyboard` for generic keyboard behavior, `.base` for UHID fixtures and kernel module declarations, `hidtools.util.BusType` for input identity, and `libevdev` for expected event construction. Its key integration point is the Linux HID ITE driver (`hid_ite`) and the input subsystem mapping to `EV_KEY.KEY_RFKILL`.

## Risks and Edge Cases

The test is sensitive to batching semantics: it assumes the synthetic RFKILL down/up events arrive in one call to `next_sync_events()`. If the kernel changes event framing while preserving user-visible behavior, this test may need adjustment. The raw report `[0x03, 0x00]` is concise but implicit; descriptor changes that alter report ID or wireless radio field layout could break the quirk test. The class also inherits generic array keyboard rollover behavior, so changes to `ArrayKeyboard` can affect this device-specific file.

## Test Signals

Strong signals include inherited generic keyboard tests passing under the ITE descriptor and `test_wifi_key()` observing both `KEY_RFKILL, 1` and `KEY_RFKILL, 0` in the emitted libevdev event stream. Failures indicate module loading problems, mismatched device identity/quirk binding, descriptor parsing errors, missing RFKILL synthesis, or changed event batching.
