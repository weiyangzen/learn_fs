# sources/distributed-fs/ceph-client/drivers/platform/x86/acer-wireless.c

Purpose: Minimal Acer airplane-mode hotkey driver that turns ACPI notifications from device `10251229` into `KEY_RFKILL` input events.

Important APIs and types: ACPI match table `acer_wireless_acpi_ids` binds HID `10251229`. `acer_wireless_notify()` handles ACPI device notifications. Probe creates a devm-managed input device named "Acer Wireless Radio Control" with `KEY_RFKILL`.

Control flow: Platform probe allocates/registers the input device and installs an ACPI notify handler. Notify accepts event `0x80`, emits a press and release of `KEY_RFKILL`, and logs unknown events. Remove unregisters the ACPI notify handler; devm handles input cleanup.

State and persistence: The input device pointer is stored as platform driver data. There is no rfkill state cache; the driver reports a hotkey event and leaves policy/action to input consumers.

Dependencies and integration points: Depends on ACPI platform enumeration and input subsystem. Uses PCI vendor ID constants only for input identity. Complements, rather than replaces, full Acer WMI/rfkill drivers.

Risks: Only event `0x80` is recognized; firmware variants with different event codes only log notices. It emits a key event without querying actual radio state, so userspace must decide how to toggle airplane mode. Handler installation after input registration means an install failure leaves probe failing cleanly via devm.

Test signals: ACPI modalias autoload for `10251229`; input device appears with `KEY_RFKILL`; pressing airplane hotkey emits one press/release pair; unknown events are logged; module unload removes notify handler.
