# sources/distributed-fs/ceph-client/drivers/acpi/dock.c

## Purpose
Implements ACPI dock station and bay support. It tracks dock stations, dependent ACPI devices, dock/undock notifications, hotplug fixups, sysfs controls, and userspace dock/undock uevents.

## Important APIs, Types, And Functions
`struct dock_station` stores the ACPI handle, flags, last dock time, dependent device list, list node, and platform dock device. `struct dock_dependent_device` links dependent ACPI devices. Public helpers are `register_dock_dependent_device()`, exported `is_dock_device()`, `dock_notify()`, and `acpi_dock_add()`.

Dock operations include `dock_present()` for `_STA`, `handle_dock()` for `_DCK`, `dock()` and `undock()`, `handle_eject_request()` for removal, `hot_remove_dock_devices()` and `hotplug_dock_devices()` for dependent devices, and `dock_event()` for uevents and hotplug callbacks. Sysfs attributes are `docked`, `flags`, `undock`, `uid`, and `type`. The `immediate_undock` module parameter controls whether eject notifications undock immediately.

## Control Flow
`acpi_dock_add()` creates a `dock` platform device, initializes the station, classifies it as dock, ATA bay, or battery bay, creates sysfs attributes, adds the station as dependent on itself, links it globally, and marks the ACPI device as a dock station.

`dock_notify()` translates dock-station `DEVICE_CHECK` to eject when `_DCK` indicates a dock. On bus/device check for an unenumerated device, it begins docking, evaluates `_DCK(1)`, checks presence, runs dependent-device fixups and hotplug handlers, scans unenumerated dependents, completes docking, emits dock events, locks the dock with `_LCK(1)`, and updates GPEs. If a dock is no longer present, it treats the event as surprise removal. Eject requests begin undock and either call `handle_eject_request()` immediately or emit an undock event for userspace to trigger the `undock` sysfs write.

`handle_eject_request()` rejects active docking, emits the undock event before device removal, invokes dependent hot-remove handlers in reverse order, trims ACPI devices, evaluates `_DCK(0)`, unlocks with `_LCK(0)`, evaluates `_EJ0`, verifies absence, and completes undocking.

## State And Persistence
Global `dock_stations` and `dock_station_count` track registered stations. Per-station flags include docking/undocking in progress and type bits. `last_dock_time` suppresses false dock events shortly after docking. Dependent-device lists persist for the lifetime of the dock platform device. Sysfs `undock` writes drive state transitions; no state is stored across boots.

## Dependencies And Integration Points
Depends on ACPI scan/hotplug, ACPICA `_STA/_DCK/_LCK/_EJ0/_UID`, platform devices, sysfs, kobject uevents, ACPI hotplug callback structures, ACPI scan locking, and GPE update helpers. It integrates with other ACPI drivers through `register_dock_dependent_device()` and `is_dock_device()`.

## Risks
Docking hardware can emit duplicate or false events; `dock_in_progress()` and `last_dock_time` mitigate but can also suppress legitimate rapid transitions. Surprise removal must remove dependents in reverse order to respect dependencies. Immediate undock for ATA bays is disabled by default behavior because storage removal may need userspace coordination. Errors after `_EJ0` can leave firmware and kernel state partially changed.

## Test Signals
Signals include dock platform devices with correct sysfs files, dock/undock uevents, dependent device hotplug callbacks in expected order, ACPI bus scans for newly enumerated devices, safe sysfs-driven undock, surprise removal handling, and `_LCK/_EJ0/_DCK` method traces. Regression tests should include normal docks, ATA bays, battery bays, duplicate notifications, and failed undock presence checks.
