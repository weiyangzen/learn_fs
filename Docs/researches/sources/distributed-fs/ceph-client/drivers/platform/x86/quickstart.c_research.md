# sources/distributed-fs/ceph-client/drivers/platform/x86/quickstart.c

Purpose: This ACPI Direct App Launch driver supports PNP0C32 quickstart buttons. It exposes a generic input key with a user-space-remappable scancode and publishes the vendor-defined GHID button role through a read-only sysfs attribute.

Important APIs, types, and functions: `struct quickstart_data` stores the device, input lock, input device, formatted names, and GHID id. `quickstart_get_ghid()` evaluates ACPI `GHID` as a byte/word/dword little-endian buffer. `quickstart_notify()` handles runtime notify event `0x80`, reports scancode `0x1` through sparse-keymap, and generates an ACPI netlink event. `button_id_show()` exposes the decoded GHID.

Control flow: Probe obtains the ACPI handle, allocates state and mutex, enables wakeup before evaluating `GHID` because the method can emit pending wake notifications, creates and registers an input device, installs an ACPI notify handler, and registers a devm cleanup action. Notifications lock `input_lock`, report a press/release event with autorelease, and then send netlink notification.

State and persistence: State is per-device and devm-managed. The decoded GHID is cached in `data->id`. Wake capability is enabled on the device. The button's semantic role is intentionally left to user space via hwdb remapping.

Dependencies and integration points: The driver integrates with ACPI PNP0C32, input sparse-keymap, sysfs attribute groups, device wakeup, and ACPI netlink event generation. It uses `PROBE_PREFER_ASYNCHRONOUS`.

Risks and edge cases: `quickstart_get_ghid()` leaks the ACPI buffer if `buffer.pointer` is NULL after a successful evaluation, though that path is unusual. Unknown GHID buffer lengths fail probe. Only runtime event `0x80` is acted on; the pre-boot/off event is indirectly consumed by GHID evaluation. Because all keys report `KEY_UNKNOWN`, user-space mapping is required for useful behavior.

Test signals: Test PNP0C32 probe, GHID lengths of 1/2/4 bytes, invalid GHID lengths, wake-button pending notification behavior, sysfs `button_id`, input event generation, and cleanup of notify handler on driver detach.
