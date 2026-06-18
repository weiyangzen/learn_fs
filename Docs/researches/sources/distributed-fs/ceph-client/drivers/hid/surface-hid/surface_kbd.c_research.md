# sources/distributed-fs/ceph-client/drivers/hid/surface-hid/surface_kbd.c

Purpose: legacy SSAM keyboard HID transport for Surface Laptop 1 and 2.

Important APIs: SSAM KBD command IDs cover descriptor retrieval, caps-lock LED set, generic/hotkey input events, and feature report retrieval. Probe binds to the SSAM controller from an ACPI platform device, synthesizes a fixed SSAM UID, configures notifier/ops, and calls the shared core.

Control flow: descriptor and feature report operations issue synchronous SSAM requests and require exact response lengths. Input notifier manually filters target category/id/instance because registry and target category do not align. Output reports are limited to caps-lock LED; the code locates the LED field in the HID report and sends `SET_CAPSLOCK_LED`.

State and persistence: all state lives in `struct surface_hid_device`; feature report is hard-coded size and read-only. The platform driver matches ACPI ID `MSHW0096`.

Dependencies and integration: depends on Surface Aggregator controller client binding, platform driver core, HID helpers, and shared Surface HID core/PM ops.

Risks: only caps LED output reports are supported, so other output reports return `-EIO`. Manual UID filtering must stay aligned with firmware event routing. Feature report size/report ID assumptions are firmware-specific.

Test signals: ACPI platform probe defer/success, keyboard input and hotkey events, caps-lock LED toggling, feature report readback, and suspend/resume.
