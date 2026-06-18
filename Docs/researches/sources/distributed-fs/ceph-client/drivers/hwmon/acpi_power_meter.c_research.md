# sources/distributed-fs/ceph-client/drivers/hwmon/acpi_power_meter.c

## Purpose
`acpi_power_meter.c` implements the ACPI 4.0 power meter resource as an hwmon power device. It reads platform power through ACPI control methods, exposes average power, averaging interval, cap, alarm, trip, accuracy, battery flag, identity strings, and domain-device links, and reacts to ACPI notifications.

## Important APIs, Types, And Functions
`struct acpi_power_meter_capabilities` mirrors integer fields from `_PMC`; `struct acpi_power_meter_resource` owns the ACPI device, mutex, hwmon device, capabilities, strings, cached power/cap/interval, trip state, domain device references, and symlink kobject. ACPI method wrappers include `_GAI`, `_GHL`, `_PTP`, `_PMM`, `_SHL`, `_PAI`, `_PMC`, and `_PMD` helpers. Modern hwmon integration is via `power_meter_is_visible`, `power_meter_read`, `power_meter_write`, `power_meter_chip_info`, and `hwmon_device_register_with_info`. Extra legacy attributes are grouped under `power_extra_group`.

## Control Flow
Probe obtains the ACPI companion, allocates resource state, optionally waits for ACPI IPMI support on Dell systems, reads capabilities and optional domain devices, registers the hwmon device, and installs an ACPI notify handler. Reads take `resource->lock`, then evaluate the relevant ACPI method or use cached capability data. `update_meter` observes the ACPI sampling time and only refreshes when the cache expires. Notifications rebuild the hwmon device on configuration changes, update cap state on cap changes, set alarm state on capping events, emit sysfs notifications, and generate ACPI netlink events. Remove unregisters notifications, hwmon, symlinks, ACPI device references, strings, and the resource allocation.

## State And Persistence
Capabilities and identity strings are stored in memory after `_PMC`; model, serial, and OEM strings are dynamically allocated. Average power is cached according to firmware sampling time. Cap, interval, and trip setters persist through firmware ACPI methods, not local files. Domain device links hold ACPI device references until removed. Resume refreshes capabilities but does not fully rebuild all domain links.

## Dependencies And Integration Points
The file depends on ACPI evaluation, ACPI platform devices, optional ACPI IPMI readiness, DMI gating for hardware power caps, hwmon channel APIs, sysfs attribute groups, kobjects, and ACPI netlink events. The `force_cap_on` module parameter can expose cap controls even when hardware safety is unknown.

## Risks And Test Signals
Risks include firmware returning malformed packages, unsafe software power capping, unregister/register races during notification rebuilds, stale domain links after configuration changes, units mismatches, and partial resume refresh. Test signals include valid `_PMC` parsing of 14 fields, correct visibility based on capability flags and DMI cap policy, cap/interval range enforcement, sampling-time cache behavior, sysfs notifications for events `0x80` through `0x84`, proper cleanup of `_PMD` symlinks and references, and no use-after-free across notification-driven hwmon re-registration.
