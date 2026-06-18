<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h

## Purpose
`acpi_drivers.h` provides legacy/common ACPI driver constants and declarations shared by Linux ACPI drivers, especially fabricated Linux-specific HIDs, PCI interrupt-link helpers, PCI root scanning hooks, and dock-station matching.

## Important APIs, types, and functions
Important constants include `ACPI_MAX_STRING`, Linux pseudo-HIDs such as `ACPI_POWER_HID`, `ACPI_PROCESSOR_OBJECT_HID`, `ACPI_SYSTEM_HID`, `ACPI_THERMAL_HID`, `ACPI_BUTTON_HID_POWERF`, `ACPI_BUTTON_HID_SLEEPF`, `ACPI_VIDEO_HID`, `ACPI_BAY_HID`, `ACPI_DOCK_HID`, `ACPI_ECDT_HID`, SMBus HIDs, and `ACPI_FIXED_HARDWARE_EVENT`. Public declarations include `acpi_irq_penalty_init()`, `acpi_pci_link_allocate_irq()`, `acpi_pci_link_free_irq()`, `acpi_get_pci_dev()`, `pci_acpi_scan_root()`, `pci_acpi_crs_quirks()`, and `is_dock_device()`, with Kconfig stubs where appropriate.

## Control flow
There is no local implementation. ACPI PCI code calls the interrupt-link helpers to allocate/free GSIs and trigger/polarity information. PCI root scan code calls the arch hook to add a bus. Fixed ACPI button events are translated to a synthetic notification value so fixed hardware and namespace devices can share driver paths.

## State and persistence behavior
No state is owned here. PCI interrupt-link state, dock state, and PCI device references are maintained by implementation files and driver core objects. Firmware-provided PCI routing and ACPI namespace data are the persistent inputs.

## Dependencies and integration points
The header depends on ACPI bus types and optionally PCI, x86, and ACPI dock Kconfig features. It bridges ACPI namespace devices to Linux PCI devices and legacy ACPI drivers that predate newer fwnode/property abstractions.

## Risks and test signals
Risks include pseudo-HID collisions, incorrect fixed-event notification mapping, PCI interrupt resource conflicts, stubs hiding missing PCI/dock support, and x86 CRS quirks affecting resource windows. Test signals include ACPI button devices and fixed buttons, PCI root scan on ACPI systems, PCI link allocation/free with IRQ polarity/trigger checks, SMBus HID matching including IBM quirks, and builds with `CONFIG_PCI` or `CONFIG_ACPI_DOCK` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_drivers.h -->
