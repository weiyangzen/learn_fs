<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c

## Purpose
`pci_root.c` is the ACPI PCI root bridge scan handler. It recognizes root bridge devices, derives domain and bus ranges, negotiates PCIe/CXL `_OSC` ownership, scans PCI buses, manages hot-add/remove, and provides reusable helpers for ACPI-backed root-bus resource probing and creation.

## Important APIs, Types, and Functions
Public helpers include `acpi_is_root_bridge()`, `acpi_pci_find_root()`, `acpi_get_pci_dev()`, `acpi_pci_probe_root_resources()`, `acpi_pci_root_create()`, and `acpi_pci_root_init()`. Internals include `_OSC` decoding and negotiation helpers, `calculate_support()`, `calculate_control()`, CXL support/control calculators, `acpi_pci_root_add()`, `acpi_pci_root_remove()`, resource validation/remapping helpers, and host-bridge release callbacks.

## Control Flow and State
The scan handler attaches to `PNP0A03` root bridges. Attach reads `_SEG`, reads bus number range from `_CRS` or falls back to `_BBN`/0, marks bridge type from HID (`PNP0A08` for PCIe, `ACPI0016` for CXL), obtains `_CBA`, negotiates `_OSC`, scans the root with `pci_acpi_scan_root()`, optionally disables ASPM, installs ACPI PM notifiers, handles hot-add resource assignment/IOAPIC discovery, and adds devices under rescan/remove locking. Remove stops and removes the root bus, tears down IOAPIC/DMAR/PM notifier state, and frees root data. `acpi_pci_root_create()` prepares resources, inserts host-bridge windows, creates the root bus, applies native-service flags from `_OSC`, powers up children with `_ADR`, scans, and records release data.

## State and Persistence
Per-root `struct acpi_pci_root` stores segment, bus range, MCFG address, bridge type, bus pointer, and granted `_OSC` control masks. Resource windows are inserted into global I/O and memory resource trees until host-bridge release. ACPI root device `driver_data` ties firmware nodes to PCI root state.

## Dependencies and Integration Points
Dependencies include ACPI scan/hotplug, PCI core, PCIe ASPM/AER/DPC/EDR/hotplug capabilities, CXL `_OSC`, DMAR, IOAPIC hotplug, architecture root scanning via `pci_acpi_scan_root()`, CRS quirks, and ACPI power/PM notifier code. `acpi_get_pci_dev()` bridges ACPI physical-node links to PCI device references.

## Risks and Test Signals
Risks include firmware missing `_CRS` bus ranges, `_OSC` fallback changing CXL roots to PCIe mode, Apple `_OSC` special-casing, native service flags being wrong if control masks are stale, resource-window overlap pruning, and hot-remove ordering around PCI/IOAPIC/DMAR. Test signals include root bridge logs, correct domain:bus ranges, `_OSC` granted/retained messages, PCI enumeration under boot and hot-add, ASPM behavior when FADT forbids it, CXL error-control negotiation, and clean hot-remove without resource leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/pci_root.c -->
