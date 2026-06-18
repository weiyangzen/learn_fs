# sources/distributed-fs/ceph-client/include/acpi/button.h

Purpose: Provides ACPI button hardware IDs and the lid-state query API used by power-management and input/display code.

Important APIs, types, and functions: Defines `ACPI_BUTTON_HID_POWER`, `ACPI_BUTTON_HID_LID`, `ACPI_BUTTON_HID_SLEEP`, and `acpi_lid_open()`. If `CONFIG_ACPI_BUTTON` is unavailable, `acpi_lid_open()` is an inline stub returning open.

Control flow: Enabled builds call into the ACPI button driver for current lid state. Disabled builds force callers down a non-blocking “lid open” path.

State and persistence: Runtime lid state lives in the ACPI button driver/device, not this header.

Dependencies and integration points: Integrates with ACPI device matching, input subsystem, display backlight/panel policy, suspend handling, and platform power-button events.

Risks and test signals: Risks include stale lid state, callers caching disabled-stub behavior, and policy differences when the button driver is modular or absent. Test HID matching, lid open/close notifications, suspend/resume with closed lid, and builds without `CONFIG_ACPI_BUTTON`.
