# sources/distributed-fs/ceph-client/drivers/platform/surface/surfacepro3_button.c

Purpose: Handles nonstandard ACPI button notifications for Surface Pro 3/4 era devices using `MSHW0028` or selected `MSHW0040` nodes, reporting power, Windows/home, and volume keys through the input subsystem.

Important APIs and types: ACPI ids are `MSHW0028` and `MSHW0040`; valid object basename is `VGBI`. `surface_button_notify()` maps ACPI notify codes to `KEY_POWER`, `KEY_LEFTMETA`, `KEY_VOLUMEUP`, and `KEY_VOLUMEDOWN`. `surface_button_check_MSHW0040()` evaluates a DSM method to avoid binding newer incompatible `MSHW0040` devices.

Control flow: Platform probe verifies ACPI object name and DSM/platform revision, allocates `struct surface_button` and an input device, registers key capabilities, enables wakeup, and installs an ACPI device notify handler. Notifications report wakeup events on press while suspended, suppress normal input reports while suspended, and emit press/release events when active. PM callbacks toggle the `suspended` flag. Remove unregisters the handler, disables wake, unregisters input, and frees state.

State and persistence: Runtime state tracks the input device, phys string, and suspend flag. Wake capability is registered with the PM core. No event state persists beyond input reports.

Dependencies and integration points: Uses ACPI notify/DSM APIs, platform ACPI matching, input, and PM wakeup helpers. It complements generic `soc_button_array` for older Surface systems that do not follow the standard button-array model.

Risks: `MSHW0040` is shared by newer systems, so the DSM filter is essential to prevent duplicate or wrong drivers. The `pushed` field is unused. Tablet-mode notify `0xc8` is intentionally unsupported. Press events during suspend wake the device but are not replayed to input after resume.

Test signals: Probe only on `VGBI` companion nodes; input events for all four buttons; wake from suspended power-button press; no binding on MSHW0040 systems with nonzero OEM platform revision; handler removal under module unload.
