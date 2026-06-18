<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi.h

## Purpose
`linux/acpi.h` is the main Linux ACPI interface header. It bridges ACPICA types with Linux devices, firmware nodes, table parsing, interrupt routing, resources, DMA/IOMMU setup, power management, hotplug, properties, platform matching, topology, and ACPI-disabled stubs.

## Important APIs, types, and functions
Major surfaces include companion helpers (`ACPI_COMPANION`, `ACPI_HANDLE`, `has_acpi_companion()`), IRQ model enums, table parsing APIs, debugger ops, CPU/NUMA mapping, GSI/IOAPIC/PCI IRQ helpers, WMI calls, video/backlight flags, thermal trip helpers, resource conversion (`acpi_dev_get_resources()` and friends), `_OSC` context/capability macros, matching/enumeration helpers, GTDT, GPIO/property APIs, probe-table macros, SPCR/watchdog helpers, IRQ affinity, PPTT topology helpers, FFH/PCC init, device notification, sleep/PM hooks, and ACPI logging macros. The non-`CONFIG_ACPI` half provides stubs returning `NULL`, false, zero, or `-ENODEV`.

## Control flow
ACPI boot code initializes tables, parses subtables, configures interrupt domains, maps CPUs/NUMA nodes, and enumerates devices. Driver probe paths use companion/fwnode helpers, resources, DMA/IOMMU configuration, and property APIs. Power paths call ACPI PM attach/suspend/resume hooks. `_OSC` helpers negotiate platform capability ownership.

## State and persistence behavior
Declared global state includes ACPI IRQ model, SCI IRQ metadata, OSI/video support flags, `_OSC` acknowledgements, PNP ACPI state, CMOS RTC presence, and platform quirk flags. Many APIs expose firmware-derived persistent configuration that affects device lifetime and migration-independent boot behavior.

## Dependencies and integration points
The header has very high fanout: ACPICA, firmware tables, Linux driver core/fwnode/property APIs, IRQ domains, PCI, WMI, thermal, GPIO, DMA/IOMMU, PM, topology, and architecture ACPI hooks. It is intentionally full of conditional stubs so generic drivers can compile without ACPI.

## Risks and test signals
Risks include stub behavior diverging from enabled behavior, table parser bounds mistakes, resource translation errors, incorrect `_OSC` ownership, IRQ trigger/polarity mismatches, and device lifetime bugs around ACPI companions. Test signals include ACPI boot on multiple architectures, table parser tests, driver probe with ACPI and non-ACPI configs, suspend/resume, hotplug, GPIO/resource translation, and sparse/compile coverage of disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi.h -->
