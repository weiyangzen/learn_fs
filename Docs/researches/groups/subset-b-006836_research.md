# Research: subset-b-006836

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_hid_core.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_hid_core.py

### Purpose

This file is a narrowly scoped UHID selftest for generic HID core behavior, not for a particular end-user device class. It creates an artificial mouse report descriptor with deeply nested collections to exercise the HID parser collection stack reallocation path in `hid-core.c`. The test is intentionally a negative/crash regression check: successful execution mainly proves that creating and probing the device did not oops or crash the kernel while parsing the descriptor.

### Important APIs, Types, and Functions

- `TestCollectionOverflow(base.BaseTestCase.TestUhid)` is the only test class. It uses the shared HID selftest fixture that creates a UHID device, waits for the kernel-side input path, and exposes debug/assertion helpers.
- `create_device()` builds a `base.UHIDTestDevice` with `application="Mouse"` and a handcrafted byte-list report descriptor.
- `test_rdesc()` is intentionally empty. The assertion is implicit in fixture setup and teardown: if descriptor parsing triggers the historical collection-stack bug, the kernel or test environment fails before the no-op test can pass.
- The local `logger` uses the `hidtools.test.hid` namespace but is not used directly in this file.

### Control Flow

Pytest discovers `TestCollectionOverflow`, the base fixture calls `create_device()`, and `base.UHIDTestDevice` sends the descriptor through UHID to the kernel. The descriptor opens many nested logical collections, defines button bits, relative X/Y axes, a resolution multiplier feature report, and a wheel input report, then closes the collections. Once the fixture has created the device, `test_rdesc()` executes `pass`; there are no explicit input reports or event assertions.

### State and Persistence

The file has no persistent storage and no mutable test state beyond the UHID device created by the base fixture. All meaningful state lives in the kernel HID parser while it consumes the nested collection hierarchy. The test descriptor itself is static, deterministic, and recreated per test instance.

### Dependencies and Integration Points

The test depends on the local `.base` module for `BaseTestCase.TestUhid` and `UHIDTestDevice`. It integrates with the Linux UHID interface and the kernel HID core parser. The descriptor models a mouse application so it also touches the kernel's HID input mapping path enough to instantiate the device, but the target behavior is the generic descriptor parser collection stack.

### Risks and Edge Cases

The primary risk is false confidence: the test has no positive assertion and can only detect severe failures such as kernel crashes, probe failures, or fixture errors. Because the bug depends on memory layout and parser stack behavior, a pass does not prove the original defect is absent in every configuration. The descriptor is intentionally unusual, so changes that simplify or "clean up" nested collections could remove the stress condition. The test also assumes the base fixture treats device creation failure as a test failure.

### Test Signals

The signal is binary and indirect. A passing run means the UHID device was created and torn down without crashing the kernel or failing descriptor parsing. A failing run will likely appear as fixture setup failure, kernel crash/oops, device creation timeout, or UHID communication failure rather than as an assertion inside `test_rdesc()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_hid_core.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_ite_keyboard.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_ite_keyboard.py

### Purpose

This file adds a device-specific regression test for ITE keyboards handled by the `hid_ite` kernel module. It reuses the generic array keyboard test suite while adding a descriptor that includes keyboard, consumer control, wireless radio, vendor, system-control, and feature-report collections. The specific regression covered is the ITE WiFi key quirk: some devices send no report on key press and only send a null-looking wireless-radio report on release, and the kernel driver should translate that release report into a synthetic RFKILL key press and release.

### Important APIs, Types, and Functions

- `KERNEL_MODULE = base.KernelModule("itetech", "hid_ite")` declares the module dependency for the test class.
- `KbdData` is an empty data carrier class, currently unused in the active logic.
- `ITEKeyboard(ArrayKeyboard)` inherits the report generation and key-state behavior from `test_keyboard.ArrayKeyboard`.
- `ITEKeyboard.report_descriptor` is a multi-application descriptor with report IDs: `0x5a` for vendor feature data, `0x01` for keyboard array input and LEDs, `0x02` for consumer control, `0x03` for wireless radio controls, `0x04` for vendor input, and `0x05` for system control.
- `ITEKeyboard.__init__()` defaults the bus/vendor/product tuple to USB `0x06CB:0x2968`, matching the device identity expected by the kernel quirk.
- `ITEKeyboard.event()` defaults `application` to `"Keyboard"` before delegating to `ArrayKeyboard.event()`, preserving normal keyboard report behavior despite the descriptor's multiple applications.
- `TestITEKeyboard(TestArrayKeyboard)` inherits all generic array-keyboard tests and adds the ITE-specific WiFi-key test.
- `test_wifi_key()` injects raw report bytes `[0x03, 0x00]` and expects `KEY_RFKILL` down and up events in the same kernel event batch.

### Control Flow

The test class loads or requires `hid_ite`, creates an `ITEKeyboard`, and then runs inherited keyboard behavior tests from `TestArrayKeyboard`. For the specific quirk, `test_wifi_key()` bypasses the normal key-name-to-report helper and calls `uhdev.call_input_event([0x03, 0x00])` directly, targeting report ID `3` for the wireless radio collection. It first builds an expected list containing `SYN_REPORT` and `KEY_RFKILL` value `1`, reads `uhdev.next_sync_events()`, and asserts the press is present. It then checks the same already-read event batch for a `KEY_RFKILL` value `0`, relying on the kernel sending the synthetic press and release together.

### State and Persistence

The ITE device inherits `ArrayKeyboard`'s in-memory `keystates` dictionary for normal keyboard reports, but `test_wifi_key()` does not use it. There is no file or external persistence. The relevant state transition is inside the kernel driver quirk: a wireless-radio release report must synthesize a complete RFKILL key click without a preceding hardware press report.

### Dependencies and Integration Points

The file depends on `.test_keyboard.ArrayKeyboard` and `.test_keyboard.TestArrayKeyboard` for generic keyboard behavior, `.base` for UHID fixtures and kernel module declarations, `hidtools.util.BusType` for input identity, and `libevdev` for expected event construction. Its key integration point is the Linux HID ITE driver (`hid_ite`) and the input subsystem mapping to `EV_KEY.KEY_RFKILL`.

### Risks and Edge Cases

The test is sensitive to batching semantics: it assumes the synthetic RFKILL down/up events arrive in one call to `next_sync_events()`. If the kernel changes event framing while preserving user-visible behavior, this test may need adjustment. The raw report `[0x03, 0x00]` is concise but implicit; descriptor changes that alter report ID or wireless radio field layout could break the quirk test. The class also inherits generic array keyboard rollover behavior, so changes to `ArrayKeyboard` can affect this device-specific file.

### Test Signals

Strong signals include inherited generic keyboard tests passing under the ITE descriptor and `test_wifi_key()` observing both `KEY_RFKILL, 1` and `KEY_RFKILL, 0` in the emitted libevdev event stream. Failures indicate module loading problems, mismatched device identity/quirk binding, descriptor parsing errors, missing RFKILL synthesis, or changed event batching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_ite_keyboard.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_keyboard.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_keyboard.py

### Purpose

This file provides reusable UHID keyboard device models and pytest test classes for Linux HID keyboard input behavior. It covers bitmap-style keyboards, boot-protocol array keyboards, LED-output descriptors, and a Primax-style descriptor ordering edge case. The tests verify key press/release reliability, simultaneous keys, modifier handling, array rollover behavior, and correct parsing when local usages are defined before the final usage page.

### Important APIs, Types, and Functions

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

### Control Flow

Concrete pytest classes implement `create_device()` and inherit the shared UHID setup from `base.BaseTestCase.TestUhid`. Each test sends a full current-key list through `uhdev.event()`, reads synchronized events with `uhdev.next_sync_events()`, logs reports with `debug_reports()`, and asserts expected `libevdev.InputEvent` instances. The shared tests first press and release `KEY_A`, then exercise two-key press/release transitions including no-repeat behavior for keys that remain held, and finally verify modifier mapping for left control, left shift, and equals.

`TestPlainKeyboard.test_10_keys()` presses ten digit keys simultaneously, which the bitmap descriptor can represent, and then verifies all ten release events. `TestArrayKeyboard.test_10_keys()` presses six keys successfully, then sends ten keys and expects no input events because the array report becomes `ErrorRollOver`, then releases and verifies the six earlier keys are released. LED and Primax classes reuse the shared behavioral tests without adding custom assertions.

### State and Persistence

The only durable state across report sends is the in-memory `keystates` dictionary on each `BaseKeyboard` instance. It tracks pressed and recently released keys so report generation can model stateful HID keyboard behavior. No state persists beyond a test instance, and there is no file, network, or database persistence. Kernel input state is observed through libevdev values such as `evdev.value[KEY_A]`.

### Dependencies and Integration Points

The file depends on `.base` for UHID test infrastructure, `hidtools.hid` and `hidtools.hut.HUT` for report generation and usage-name lookup, and `libevdev` for Linux input event constants and assertions. It integrates with the kernel HID parser, HID input mapping layer, UHID transport, and evdev event queues. `test_ite_keyboard.py` imports `ArrayKeyboard` and `TestArrayKeyboard`, so this file is also a local fixture provider for device-specific keyboard tests.

### Risks and Edge Cases

Key names must match hidtools HUT names after normalization. A name mismatch breaks report encoding before kernel behavior is tested. `_update_key_state()` mutates a dictionary while using a list copy only for removal; this is safe for removals, but later iteration over `self.keystates.keys()` relies on no size-changing mutation during that loop. Array rollover behavior intentionally expects no events for over-six-key input, so a kernel change that reports rollover differently could alter test expectations. The Primax descriptor is sensitive to HID parser handling of local/global item ordering; edits that reorder descriptor bytes can remove the coverage.

### Test Signals

Passing tests show that generated reports match descriptors closely enough for the kernel to emit expected `EV_KEY` events, that held keys are not re-emitted unnecessarily, that releases update evdev state, that modifiers map to left-control and left-shift keys, that bitmap descriptors support many simultaneous keys, and that array descriptors suppress normal key events on rollover. Failures localize either to report generation, descriptor parsing, key usage mapping, event synchronization, or kernel input behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_keyboard.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_mouse.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_mouse.py

### Purpose

This file provides reusable UHID mouse device models and pytest tests for Linux HID pointer behavior. It covers button state, relative X/Y movement, vertical wheel events, horizontal AC Pan events, high-resolution wheel support through HID resolution multipliers, a Xiaomi/MI dongle mouse with split reports, a failed resolution-multiplier setup path, and a malformed syzbot-derived descriptor that should not crash the kernel. It is both a test suite and a fixture library for HID mouse report generation.

### Important APIs, Types, and Functions

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

### Control Flow

For ordinary pointer tests, pytest creates the concrete device, sends reports through `uhdev.event()`, reads `uhdev.next_sync_events()`, and asserts exact or inclusive libevdev events. `test_buttons()` walks right, middle, left, and combined left/right press-release transitions while checking evdev's current button values. `test_relative()` sends relative Y, X, and combined X/Y movement and expects matching `EV_REL` events.

`TestSimpleMouse.test_rdesc()` does not use a kernel event path for its core assertion. It compares `ButtonMouse.fake_report()` with generated reports for multiple button and movement combinations, then verifies that out-of-range Y movement raises `hidtools.hid.RangeError`.

Wheel tests detect kernel high-resolution support by checking evdev capabilities. `TestWheelMouse.test_wheel()` sends wheel deltas pre-multiplied by the device multiplier and expects normal `REL_WHEEL` events plus high-resolution events of 120 units per detent when supported. `TestTwoWheelMouse.test_ac_pan()` mirrors that behavior for horizontal `REL_HWHEEL` and combined vertical/horizontal wheel movement.

Resolution multiplier tests rely on kernel feature-report negotiation during device setup. If high-resolution wheel support is absent, tests skip or assert that no multiplier was triggered. If present, they assert the multiplier divides 120 and then send unit HID wheel reports that accumulate high-resolution deltas; after enough reports to complete one detent, the kernel emits the corresponding low-resolution wheel event. The bad multiplier variant verifies that a failed `SET_REPORT` leaves multipliers at `1`. The MI mouse overrides event assertion to tolerate two SYN frames because the device sends movement and buttons in separate reports.

### State and Persistence

Mouse state is in-memory per test device. Button fields persist across calls so partial button tuples can model holding one button while changing another. Wheel and horizontal wheel multipliers are mutable fields changed by feature-report negotiation callbacks. `BadReportDescriptorMouse.high_resolution_report_called` gates readiness after the kernel issues the expected feature report. No state is persisted outside the test process, but kernel evdev state is queried for current button values and capabilities.

### Dependencies and Integration Points

The file depends on `.base` for UHID fixtures, `hidtools.hid` for report encoding and `RangeError`, `hidtools.util.BusType` and `to_twos_comp`, `libevdev` for input constants/capability checks, and `pytest` for skip and exception assertions. It integrates with Linux UHID, the HID parser, HID input mapping, evdev synchronization, feature report handling through `set_report()`, high-resolution wheel support, and device-specific matching based on USB vendor/product IDs.

### Risks and Edge Cases

High-resolution wheel tests are kernel-capability-dependent and skip or change expectations when support is missing. The compatibility aliases for older libevdev map high-resolution constants to raw relative codes; this keeps tests runnable but can obscure library-version issues. Resolution multiplier setup is hardcoded to expected feature report payloads instead of deriving them from descriptors, which makes descriptor edits risky. `BadReportDescriptorMouse.get_evdev()` intentionally returns a string sentinel to work around fixture expectations, so base fixture changes could break this special case. MI split-report behavior can produce extra SYN frames, requiring custom assertion logic. Range validation is split between hidtools report creation and kernel input behavior, so failures may originate before UHID injection.

### Test Signals

Passing tests show that report descriptors and generated reports map to expected button, relative movement, wheel, and horizontal wheel events; that evdev state reflects button transitions; that report generation rejects out-of-range data; that high-resolution wheel multipliers are negotiated and accumulated correctly when supported; that failed feature negotiation degrades to ordinary wheel behavior; that a split-report MI mouse still produces the effective expected events; and that malformed zero-sized feature descriptors do not crash the kernel. Failures are useful signals for descriptor regressions, hidtools encoding bugs, kernel HID parser issues, feature-report negotiation changes, or evdev event ordering changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_mouse.py -->
