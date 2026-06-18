# sources/distributed-fs/ceph-client/drivers/acpi/device_sysfs.c

## Purpose
Defines ACPI device sysfs attributes, modalias/uevent generation, eject handling, and exposure of ACPI non-device data subnodes. It is the main bridge between ACPI namespace metadata and userspace-visible device attributes.

## Important APIs, Types, And Functions
`acpi_object_path()` formats full ACPI paths. `struct acpi_data_node_attr`, `acpi_data_node_ktype`, `acpi_expose_nondev_subnodes()`, and `acpi_hide_nondev_subnodes()` expose and remove non-device ACPI data nodes recursively.

Modalias helpers are `create_pnp_modalias()`, `create_of_modalias()`, `__acpi_device_uevent_modalias()`, exported `acpi_device_uevent_modalias()`, `__acpi_device_modalias()`, and exported `acpi_device_modalias()`. Device attributes include `modalias`, `real_power_state`, `power_state`, `eject`, `hid`, `cid`, `uid`, `adr`, `path`, `description`, `sun`, `hrv`, and `status`. `acpi_attr_is_visible()` gates attributes dynamically. `acpi_groups` is the attribute-group array consumed by ACPI device registration.

## Control Flow
When device sysfs is built, the group visibility callback checks ACPI capabilities and PNP metadata before exposing each attribute. Reads evaluate ACPI methods such as `_STR`, `_SUN`, `_HRV`, and `_STA` on demand, or return cached PNP/power metadata. `eject_store()` accepts only `"1"`, verifies a hotplug handler or driver and `_EJ0` eligibility, takes an ACPI device reference, schedules ACPI hotplug eject, and reports `_OST` failure if scheduling fails.

Uevent modalias generation writes `MODALIAS=` and fills either ACPI PNP IDs (`acpi:HID:CID:`) or DT-compatible modalias strings for ACPI devices using `ACPI_DT_NAMESPACE_HID`. The sysfs `modalias` attribute can include both ACPI and OF-compatible forms. Non-device subnodes are added recursively as kobjects under the ACPI device kobject and removed in reverse order.

## State And Persistence
Most values are computed on read. Non-device subnode kobjects persist while the parent ACPI device is present and use completions to signal release. Hotplug eject temporarily holds an ACPI device reference until the scheduled hotplug path consumes it or failure releases it.

## Dependencies And Integration Points
Depends on ACPICA name/method/object-info APIs, Linux sysfs/kobject infrastructure, ACPI hotplug scheduling, ACPI PM helpers from `device_pm.c`, modalias matching from `bus.c`, UTF-16 to UTF-8 conversion for `_STR`, and fwnode/ACPI data-node structures. It integrates with userspace module loading through uevent modaliases.

## Risks
Modalias buffers must not overflow or truncate silently because they affect module autoload. Attribute visibility must match firmware support; exposing methods that fail frequently creates noisy user-visible errors. `eject_store()` must correctly handle references and `_OST` failure reporting or hotplug errors can leak references or leave firmware uninformed. Recursive data-node kobject removal must mirror creation order.

## Test Signals
Signals include correct sysfs attributes for devices with HID/CID/UID/ADR/_STR/_SUN/_HRV/_STA/_EJ0, correct uevent `MODALIAS`, module autoload for ACPI IDs, successful eject scheduling and failure `_OST`, valid UTF-8 descriptions, and correct recursive appearance/removal of non-device data nodes. Buffer-boundary tests for many CIDs and OF compatible strings are important.
