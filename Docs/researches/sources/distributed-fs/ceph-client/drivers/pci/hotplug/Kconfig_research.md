<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig

## Purpose
Defines build-time configuration for PCI hotplug support and its platform-specific controller drivers. It gates generic PCI hotplug, ACPI hotplug, CompactPCI, SHPC, native PCIe, PowerNV, RPA, S390, OCTEON, and legacy Compaq/IBM drivers.

## Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. Important symbols include `HOTPLUG_PCI`, `HOTPLUG_PCI_ACPI`, `HOTPLUG_PCI_ACPI_AMPERE_ALTRA`, `HOTPLUG_PCI_ACPI_IBM`, `HOTPLUG_PCI_CPCI`, `HOTPLUG_PCI_CPCI_GENERIC`, `HOTPLUG_PCI_SHPC`, `HOTPLUG_PCI_POWERNV`, `HOTPLUG_PCI_RPA`, `HOTPLUG_PCI_RPA_DLPAR`, and `HOTPLUG_PCI_S390`.

## Control Flow
The top-level `HOTPLUG_PCI` menu depends on PCI and sysfs and defaults to enabled for USB4. Nested symbols become visible only when hotplug is enabled. Dependencies constrain drivers to supported architectures and firmware interfaces, such as ACPI, x86 PCI BIOS, ARM SMCCC discovery, PowerPC EEH, or S390 64-bit.

## State and Persistence
State is the kernel configuration selected at build time. It persists in `.config` and determines which objects are built into the kernel or as modules.

## Dependencies and Integration Points
Integrates with `drivers/pci/hotplug/Makefile` to select object files. The comments and dependencies encode intended ownership boundaries: ACPI hotplug as a fallback, native PCIe/SHPC where available, and platform extensions layered on ACPI hotplug.

## Risks and Edge Cases
Incorrect dependencies can expose unusable drivers on unsupported platforms or hide required hotplug support. `HOTPLUG_PCI_ACPI` is a bool and depends on `HOTPLUG_PCI=y`, so modular combinations are constrained. Platform extensions depend on core ACPI hotplug and must not be enabled without it.

## Test Signals
Run Kconfig dependency checks for representative x86, ARM64, PowerPC, and S390 configs; verify selected symbols build the expected modules; and validate that USB4 configs enable hotplug support by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Kconfig -->
