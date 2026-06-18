<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c

## Purpose
The Lenovo Yoga Mode Control driver reports convertible posture changes, especially tablet mode, from Lenovo YMC WMI events to the input subsystem and to the ideapad-laptop notifier.

## Important APIs, Types, And Functions
The event GUID is `06129D99-6083-4164-81AD-F092F9D773A6`; the query GUID is `09B0EE6E-C3FD-4243-8DA1-7911FF80BB8C`. `lenovo_ymc_keymap` maps firmware states to `SW_TABLET_MODE`, ignoring uninitialized state and treating tablet, drawing board, and tent as tablet mode. `lenovo_ymc_notify()` queries current mode through `wmi_evaluate_method()`, reports the sparse keymap event, and calls `ideapad_laptop_call_notifier()`. `lenovo_ymc_probe()` gates loading by convertible/detachable DMI chassis type unless `force=1`.

## Control Flow
Probe allocates/registers an input device, sets up the sparse keymap, stores private data, and calls notify once to report initial state. Each WMI event triggers a separate query method call; the event payload itself is not used.

## State And Persistence
Runtime state is only the input device pointer. Mode state is reported through input core; firmware remains authoritative. No settings are persisted by the driver.

## Dependencies And Integration Points
The driver depends on WMI, DMI, input sparse-keymap, ACPI, and `ideapad-laptop` notifier namespace. It imports `IDEAPAD_LAPTOP` to notify other Lenovo code of YMC events.

## Risks And Edge Cases
The DMI table name has a typo (`chasis`) but behavior is clear. Non-integer query results are ignored. The notifier call is made after freeing/handling the ACPI object path with `code`, so unknown key codes still propagate to ideapad listeners.

## Test Signals
Validation should cover convertible and non-convertible DMI matching, `force=1`, initial state report on probe, all keymap states, malformed query returns, and ideapad notifier delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ymc.c -->
