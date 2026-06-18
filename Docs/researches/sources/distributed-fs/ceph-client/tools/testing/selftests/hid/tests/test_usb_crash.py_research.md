# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_usb_crash.py

Purpose: this small pytest module is a crash regression harness. It creates UHID-emulated devices that claim `BUS_USB` identity and verifies that bound HID drivers do not dereference real USB-only structures when the backing device is actually UHID.

Important APIs, types, and functions: `USBDev` extends `base.UHIDTestDevice` with a minimal mouse report descriptor, an overridden `is_ready()` that avoids waiting for udev-created evdev nodes, and `get_evdev()` returning a sentinel because this test cares about kernel survival rather than input events. `TestUSBDevice.new_uhdev()` consumes a generated `usbVidPid` fixture, loads the named kernel module, and returns `USBDev(input_info=(3, vid, pid))`. `test_creation()` is intentionally just `assert True`.

Control flow: `conftest.py` supplies `(module, vid, pid)` parameter tuples. The fixture loads the candidate module and creates the fake USB UHID device. If driver probing crashes or taints the kernel, shared fixtures such as `check_taint` and the test environment catch it. The test body only asserts that execution reached user space after device creation.

State and persistence: state is limited to fixture attributes `module`, `vid`, and `pid`, the loaded kernel module, and the live UHID device. No persistent files are written.

Dependencies and integration points: integrates with pytest, the local HID selftest `base` framework, kernel module loading, UHID, and the generated `usbVidPid` fixture. The report descriptor is a generic relative mouse descriptor with three buttons and X/Y axes.

Risks: success is mostly negative evidence; if crash/taint detection is disabled, the test can pass despite missing coverage. The fake descriptor is deliberately simple, so it may not exercise deeper driver paths beyond probe and basic parsing. The typo in the comment does not affect behavior.

Test signals: any kernel crash, machine freeze, taint, module-load failure, or UHID creation failure is the meaningful failure. A normal pytest pass means fake USB UHID creation did not hit the known crash class for that module/device tuple.
