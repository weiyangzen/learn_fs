# sources/distributed-fs/ceph-client/drivers/platform/x86/wireless-hotkey.c

Purpose: ACPI platform driver that turns firmware airplane-mode button notifications into `KEY_RFKILL` input events for AMD, HP, Xiaomi, and LG-style ACPI IDs.

Important APIs and control flow: ACPI IDs include `HPQ6001`, `WSTADEF`, `AMDI0051`, and `LGEX0815`. Probe allocates `struct wl_button`, creates and registers an input device named `Wireless hotkeys`, and installs an ACPI device notify handler. `wl_notify()` only treats event `0x80` as a key press/release pulse; other events are logged. Remove unregisters the notify handler and input device.

State and dependencies: per-device state stores the input device and physical path string. The driver depends on ACPI companion devices, platform-driver ACPI matching, and input core.

Risks and test signals: input allocation is manual rather than devm, making remove/error path correctness important. Unknown event logging can become noisy if firmware emits additional notifications. Tests should cover ACPI matching, event `0x80` press/release ordering, unknown events, probe failure after input registration, and remove-time notify teardown.
