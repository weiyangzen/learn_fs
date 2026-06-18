# sources/distributed-fs/ceph-client/include/linux/hiddev.h

## Purpose
`hiddev.h` defines the in-kernel side of the legacy USB HIDDEV interface, which exposes parsed HID device events and reports to userspace through the hiddev character-device ABI in `uapi/linux/hiddev.h`.

## Important APIs, Types, And Functions
`struct hiddev` stores the minor number, existence/open counters, existence mutex, wait queue, associated `hid_device`, list node, list lock, and initialization flag. When `CONFIG_USB_HIDDEV` is enabled, the header declares `hiddev_connect()`, `hiddev_disconnect()`, `hiddev_hid_event()`, and `hiddev_report_event()`. Disabled builds provide inline stubs where connect fails and event/disconnect calls do nothing.

## Control Flow And State
HID core or USB HID code connects hiddev during `hid_connect()` when requested or forced by quirks. Parsed field/usage events call `hiddev_hid_event()`, and report completion calls `hiddev_report_event()`. Disconnect flips existence state, wakes waiters, and releases the character-device path. State persists per hiddev minor while userspace has files open.

## Dependencies And Integration Points
It includes the userspace ABI header and references HID core structures. It integrates with `struct hid_device` hiddev callback pointers and claimed flags in `hid.h`.

## Risks
Risks include use-after-free across disconnect/open files, stale events after `exist` is cleared, wait queue wakeup omissions, and divergence between parsed HID events and the userspace ABI expectations. Disabled-config stubs returning `-1` rather than a symbolic errno are an integration quirk callers should tolerate.

## Test Signals
Build with and without `CONFIG_USB_HIDDEV`, connect a USB HIDDEV-capable device, read events and reports through the char device, test forced hiddev quirks, disconnect during blocking reads, and ensure callbacks are no-ops in disabled builds.
