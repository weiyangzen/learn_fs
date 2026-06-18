<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h

## Purpose
`acpi_bus.h` is Linux's main ACPI bus and device-model contract. It defines ACPI device state, driver registration, scan handlers, hotplug contexts, fwnode/property integration, power and wake state, physical-device binding, dependency tracking, PCI root data, DMA/IOMMU helpers, and many utility entry points used by ACPI-aware drivers.

## Important APIs, types, and functions
Core types include `struct acpi_handle_list`, `struct acpi_hotplug_profile`, `struct acpi_scan_handler`, `struct acpi_hotplug_context`, `struct acpi_driver`, `struct acpi_device`, `struct acpi_data_node`, `struct acpi_bus_event`, `struct acpi_bus_type`, and `struct acpi_pci_root`. Important helpers include ACPI method evaluators (`acpi_evaluate_integer`, `acpi_evaluate_reference`, `acpi_execute_simple_method`, `acpi_evaluate_ej0`, `acpi_evaluate_reg`), DSM helpers (`acpi_check_dsm`, `acpi_evaluate_dsm_typed`), discovery helpers (`acpi_dev_found`, `acpi_dev_present`, `acpi_get_physical_device_location`), notify and private-data handlers, driver registration (`acpi_bus_register_driver`, `acpi_bus_unregister_driver`, `module_acpi_driver`), scan/trim APIs, power APIs, wake APIs, dependency APIs, and ACPI device matching/refcount helpers.

## Control flow
ACPI scan code creates `struct acpi_device` instances from namespace nodes, fills status/PNP/power/wakeup/property fields, and either attaches scan handlers or lets registered ACPI drivers match on IDs. Hotplug notifications flow through installed notify handlers into `struct acpi_hotplug_context` callbacks and scan handlers. Power-management paths evaluate `_PSC`, `_PSx`, power resources, wake GPEs, and PM notifiers. Device-link style dependencies are tracked through `struct acpi_dep_data` and cleared when suppliers are enumerated.

## State and persistence behavior
Most state is runtime kernel state attached to `struct acpi_device`: `_STA` status bits, flags, IDs, `_ADR`/`_UID`, current power state, wake resources and counts, physical-node bindings, fwnode properties, software nodes, dependency counts, and driver data. Persistent source-of-truth state remains firmware AML/tables; kernel state is reconstructed at boot or hotplug rescan.

## Dependencies and integration points
This header integrates ACPICA handles with the Linux driver core, `struct device`, fwnode/property APIs, procfs ACPI root, notifier chains, PCI, DMA/IOMMU configuration, PM core, wakeup sources, Kconfig-gated quirk code, and optional ACPI/PM/SLEEP/NUMA features. It is consumed by most Linux ACPI platform, bus, and device drivers.

## Risks and test signals
Risks include lifetime races between ACPI devices, fwnodes, physical devices, and notify handlers; incorrect `_STA` handling; dependency deadlocks; hotplug ordering bugs; PM wake reference leaks; UID type mismatches; Kconfig stub behavior diverging from enabled behavior; and parent-child power sequencing issues. Test signals include ACPI scan on nested namespaces, module ACPI driver bind/unbind, hotplug eject, `_DEP` supplier/consumer enumeration, DSM typed return filtering, fwnode property queries, PCI root discovery, DMA configuration, wake enable/disable, and builds with `CONFIG_ACPI` or `CONFIG_PM` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_bus.h -->
