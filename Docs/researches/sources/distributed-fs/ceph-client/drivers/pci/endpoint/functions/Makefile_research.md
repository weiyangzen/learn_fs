# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Makefile

## Purpose
Maps PCI endpoint function Kconfig symbols to their endpoint function driver objects.

## Important APIs, Types, And Functions
Build rules are `pci-epf-test.o` for `CONFIG_PCI_EPF_TEST`, `pci-epf-ntb.o` for `CONFIG_PCI_EPF_NTB`, `pci-epf-vntb.o` for `CONFIG_PCI_EPF_VNTB`, and `pci-epf-mhi.o` for `CONFIG_PCI_EPF_MHI`.

## Control Flow
No runtime flow exists. Kbuild includes only object files whose Kconfig symbol is enabled.

## State And Persistence
The Makefile stores build-time mapping state. Runtime registration is handled by each endpoint function driver module or built-in init function.

## Dependencies And Integration Points
Consumes symbols from `functions/Kconfig` and is reached from the parent endpoint Makefile when `CONFIG_PCI_ENDPOINT` is enabled.

## Risks
Whitespace or object-name drift can break module builds. New endpoint function drivers require matching additions here and in Kconfig. A rule without a matching dependency could build a function driver without required subsystem APIs.

## Test Signals
Enable each endpoint function symbol independently and verify only the expected object builds and links. Module autoload names should match the registered `pci_epf_driver` names in the corresponding C files.
