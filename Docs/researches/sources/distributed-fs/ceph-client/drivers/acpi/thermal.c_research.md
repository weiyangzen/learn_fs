# sources/distributed-fs/ceph-client/drivers/acpi/thermal.c

## Purpose

`thermal.c` is the ACPI thermal zone platform driver. It evaluates ACPI thermal-zone methods, registers Linux thermal zones and trips, binds ACPI-listed cooling devices, handles thermal notifications, applies DMI/module-parameter quirks, and drives thermal-zone updates through a dedicated workqueue.

## Important APIs, types, and functions

Module parameters `act`, `crt`, `tzp`, `off`, and `psv` alter active, critical, polling, disable, and passive behavior. Private state is held in `struct acpi_thermal`, which stores the ACPI device, current/last deci-Kelvin temperatures, polling frequency, trip data, thermal zone pointer, Kelvin offset, work item, mutex, and refcount. Trip metadata is stored in `struct acpi_thermal_trip`, `struct acpi_thermal_passive`, `struct acpi_thermal_active`, and `struct acpi_thermal_trips`. Main functions include temperature/polling readers, trip initialization/update helpers, thermal-zone callbacks, notify handler, AML dependency workaround, offset heuristic, probe/remove, PM prepare/complete, DMI callbacks, and module init/exit.

## Control flow

Probe allocates state, sets active cooling mode with `_SCP`, pre-evaluates AML methods in firmware-safe order, reads passive/active/critical/hot trips, reads `_TMP`, determines `_TZP` or parameter polling, guesses the Kelvin conversion offset, builds a thermal trip table, registers and enables a thermal zone, initializes async check work, logs the zone, and installs an ACPI notify handler. Temperature notifications queue work; threshold/device notifications update trip temperatures or handle lists via thermal-core trip iteration, update thermal trip temperatures, queue a check, and emit netlink events. The work item serializes `thermal_zone_device_update()`. Remove unregisters notify, flushes work, unregisters the thermal zone, frees handle lists, and frees state.

## State and persistence

Thermal-zone state persists per platform device. ACPI trip temperatures are stored in firmware deci-Kelvin while Linux thermal trips use millicelsius after offset conversion. Cooling-device binding state is the ACPI handle lists from `_PSL` and `_ALx`. Workqueue and module parameters persist for module lifetime. DMI quirks adjust module parameter defaults during init.

## Dependencies and integration points

The file depends on ACPI thermal methods (`_TMP`, `_TZP`, `_SCP`, `_CRT`, `_HOT`, `_PSV`, `_ACx`, `_PSL`, `_ALx`, `_TC1`, `_TC2`, `_TFP`, `_TSP`), helper functions from `thermal_lib.c`, ACPI handle-list helpers from `utils.c`, Linux thermal framework, platform driver matching on `ACPI_THERMAL_HID`, ACPI netlink events, sysfs links, PM callbacks, and DMI.

## Risks

Firmware thermal data is often wrong or order-dependent, hence the AML dependency workaround and validity filtering. Critical-trip overrides or disabling can affect system safety. Asynchronous update coalescing must avoid stale trips while preventing unbounded queued work. Cooling-device binding assumes ACPI handle identity with `cdev->devdata`. Changing Kelvin offset heuristics can alter visible temperatures and trip behavior.

## Test signals

Validate thermal-zone registration for ACPI thermal devices, current temperature reads, active/passive/hot/critical trip creation, cooling-device binding from `_PSL`/`_ALx`, threshold/device notification updates, PM flush/update behavior, module parameters and DMI quirks, no-trip firmware handling, and critical/hot netlink plus thermal-core actions.
