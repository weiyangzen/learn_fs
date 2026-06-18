<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile

## Purpose
Maps hotplug Kconfig symbols to object files and composite modules for the PCI hotplug subsystem.

## Important APIs, Types, and Functions
This is build metadata. It defines objects for `pci_hotplug`, `acpiphp`, `cpqphp`, `ibmphp`, `pciehp`, `shpchp`, `rpaphp`, `rpadlpar_io`, `pnv-php`, and platform-specific single-object drivers. It conditionally includes `cpci_hotplug_core.o`, `cpci_hotplug_pci.o`, and `acpi_pcihp.o` in the core `pci_hotplug` object depending on config symbols.

## Control Flow
Object order is meaningful: native hotplug drivers are linked before `acpiphp` so they can bind before ACPI fallback. `acpiphp_ibm` is linked after `acpiphp` because it registers attention callbacks against the ACPI hotplug core.

## State and Persistence
The file persists build composition only. Runtime state is in the compiled modules and drivers selected by this metadata.

## Dependencies and Integration Points
Integrates Kconfig with kbuild. It aligns ACPI helper inclusion with `CONFIG_ACPI` and CompactPCI core inclusion with `CONFIG_HOTPLUG_PCI_CPCI`.

## Risks and Edge Cases
Changing object order can alter driver binding precedence. Missing conditional object inclusion can produce unresolved symbols or remove helper exports. Composite object lists must match source files and symbol dependencies.

## Test Signals
Build hotplug configurations for ACPI-only, CPCI, native PCIe, IBM/Compaq legacy, and allmodconfig; inspect module contents and link order for expected object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/Makefile -->
