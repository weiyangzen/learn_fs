# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/base.py

## Purpose
`base.py` is the central pytest harness for hid-tools UHID tests. It defines application-to-evdev matching rules, a UHID test device subclass, dataclasses describing kernel modules and HID-BPF objects, the base test fixture lifecycle, debugging helpers, and udev-rule management.

## Important APIs, types, and functions
`application_matches` maps HID application names to `EvdevMatch` requirements and exclusions. `UHIDTestDevice` prefixes device names and supplies those matches to `BaseDevice`. `HidBpf` and `KernelModule` describe optional setup. `BaseTestCase.TestUhid` provides reusable fixtures (`load_kernel_module`, `new_uhdev`, `context`, `check_taint`) and assertions (`assertInputEventsIn`, `assertInputEvents`, `assertName`). `load_hid_bpfs()` and `unload_hid_bpfs()` invoke `udev-hid-bpf` for in-kernel HID-BPF objects. `HIDTestUdevRule` creates and later removes `/run/udev/rules.d` rules to ignore test UHID devices in libinput and hid-bpf auto loading.

## Control flow
For each test, `context` creates the device, installs udev rules, processes skip markers, creates the kernel device, dispatches UHID events until readiness or timeout, optionally loads HID-BPF programs, yields to the test, then unloads BPF programs and tears down. `check_taint` snapshots `/proc/sys/kernel/tainted` before each test and asserts it is unchanged after.

## State and persistence
Class-level lists (`kernel_modules`, `hid_bpfs`) configure subclasses. Per-test state is `self.uhdev`. `HIDTestUdevRule` is a singleton with a reference count and a temporary rules file that persists only while the session/test contexts are active.

## Dependencies and integration points
The file depends on pytest, libevdev, hidtools, system tools (`modprobe`, `udevadm`, `systemd-hwdb`, `udev-hid-bpf`), and `BaseDevice`. It is the integration layer between Python tests, UHID, udev, evdev, kernel modules, and HID-BPF assets.

## Risks and test signals
Risks include root permissions, udev timing, unavailable modules, stale udev rules, and kernel taint changes. Strong signals are successful device creation, evdev node matching, no leftover sync events at creation, clean BPF load/unload, and unchanged kernel taint.
