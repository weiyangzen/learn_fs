# sources/distributed-fs/ceph-client/drivers/pci/endpoint/Makefile

## Purpose
Builds the PCI endpoint core, optional configfs support, optional MSI doorbell support, and endpoint function subdirectory according to Kconfig selections.

## Important APIs, Types, And Functions
Object rules include `pci-ep-cfs.o` for `CONFIG_PCI_ENDPOINT_CONFIGFS`, `pci-epc-core.o`, `pci-epf-core.o`, `pci-epc-mem.o`, and `functions/` for `CONFIG_PCI_ENDPOINT`, plus `pci-ep-msi.o` for `CONFIG_PCI_ENDPOINT_MSI_DOORBELL`.

## Control Flow
No runtime flow exists. Kbuild evaluates `obj-$(CONFIG_...)` assignments and descends into `functions/` only when endpoint core is enabled.

## State And Persistence
The file persists build graph state only. Its ordering ensures endpoint core and memory helpers are built with endpoint function support.

## Dependencies And Integration Points
Consumes symbols from endpoint Kconfig and links core endpoint infrastructure used by endpoint controller drivers and endpoint function modules.

## Risks
If the `functions/` directory is not tied to `CONFIG_PCI_ENDPOINT`, function objects could build without core APIs. Adding new endpoint core objects requires updating this Makefile and the matching Kconfig dependency.

## Test Signals
Check `make drivers/pci/endpoint/` with endpoint options toggled, verify function subdir inclusion only when expected, and confirm module/object names align with Kconfig symbols.
