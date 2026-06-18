# sources/distributed-fs/ceph-client/include/acpi/battery.h

Purpose: Defines the ACPI battery class name, notification codes, and hook registration API for auxiliary drivers that attach behavior to ACPI battery power-supply devices.

Important APIs, types, and functions: Exports `ACPI_BATTERY_CLASS`, notify values `ACPI_BATTERY_NOTIFY_STATUS`, `ACPI_BATTERY_NOTIFY_INFO`, and `ACPI_BATTERY_NOTIFY_THRESHOLD`, `struct acpi_battery_hook`, and registration functions `battery_hook_register()`, `battery_hook_unregister()`, and `devm_battery_hook_register()`.

Control flow: Hook users register callbacks; the battery core calls `add_battery()` when a matching `power_supply` is available and `remove_battery()` during teardown. The devm variant binds lifetime to a device.

State and persistence: Hook state is list-linked via `struct list_head` in each hook. Battery status/capacity is external ACPI/power-supply state, not persisted here.

Dependencies and integration points: Depends on Linux device, list, and power-supply APIs. Integrates with ACPI battery driver, platform extensions, vendor drivers, and power-management notification handling.

Risks and test signals: Risks are hook lifetime bugs, missing remove callbacks, list corruption, and incorrect behavior when battery devices appear/disappear during suspend/resume. Test hook registration/unregistration, devm cleanup, ACPI notify events `0x80`-`0x82`, hotplug/removal, and disabled extension modules.
