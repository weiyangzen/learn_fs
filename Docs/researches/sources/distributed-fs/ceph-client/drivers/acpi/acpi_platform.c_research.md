# sources/distributed-fs/ceph-client/drivers/acpi/acpi_platform.c

## Purpose
`acpi_platform.c` converts eligible ACPI namespace devices into Linux platform devices, including resource translation, parent selection, DMA mask setup, and hot-remove handling.

## Important APIs, Types, And Functions
The exported API is `acpi_create_platform_device(struct acpi_device *adev, const struct property_entry *properties)`. Supporting pieces include `forbidden_id_list`, `acpi_platform_device_find_by_companion()`, `acpi_platform_device_remove_notify()`, `acpi_platform_fill_resource()`, `acpi_platform_resource_count()`, and `acpi_platform_init()`.

## Control Flow
Initialization registers an ACPI reconfiguration notifier. Device creation first skips ACPI nodes that already have physical devices except backlight cases, rejects forbidden legacy IDs, handles the SMBus virtual-device exception, collects `_CRS` resources for ordinary ACPI device nodes, copies resources while setting PCI parent resource pointers when needed, fills `platform_device_info` with parent, ACPI fwnode, optional properties, resources, and DMA mask, then calls `platform_device_register_full()`. On ACPI reconfiguration removal, the notifier finds the companion platform device and unregisters it.

## State And Persistence
Created platform devices persist in the Linux device model until unregistered. Temporary resource arrays are freed after registration because the platform core copies them. No extra file-local runtime state is kept beyond the notifier.

## Dependencies And Integration Points
It depends on ACPI scan/reconfiguration, ACPI resources, platform bus, PCI resource parenting, DMA capability checks, fwnode/property infrastructure, and legacy-device filtering coordinated with PNP support.

## Risks
Eligibility decisions are subtle: creating a platform device for a legacy PNP, IOAPIC, PIC, timer, or already-bound ACPI node can create duplicate drivers. The SMBus virtual-device exception depends on absence of resources. Hot-remove relies on ACPI companion matching and reference handling (`put_device()` after unregister).

## Test Signals
Tests should cover forbidden IDs, allowed resource-less SMBus virtual device, resource-bearing rejection, parent PCI resource assignment, DMA mask selection, physical-node skip behavior, successful platform registration, and ACPI reconfiguration removal.
