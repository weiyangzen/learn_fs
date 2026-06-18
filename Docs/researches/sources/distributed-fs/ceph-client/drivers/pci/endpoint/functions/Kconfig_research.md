# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/Kconfig

## Purpose
Defines selectable PCI endpoint function drivers: test, NTB, virtual NTB, and MHI endpoint. It exposes function-level dependencies and help text under the PCI Endpoint menu.

## Important APIs, Types, And Functions
Kconfig symbols are `PCI_EPF_TEST`, `PCI_EPF_NTB`, `PCI_EPF_VNTB`, and `PCI_EPF_MHI`. `PCI_EPF_TEST`, `PCI_EPF_NTB`, and `PCI_EPF_VNTB` select `CONFIGFS_FS`; `PCI_EPF_TEST` selects `CRC32`; `PCI_EPF_VNTB` depends on `NTB`; `PCI_EPF_MHI` depends on `MHI_BUS_EP`.

## Control Flow
No runtime code executes. The configuration controls which function driver object files are built by the endpoint functions Makefile and which userspace configfs endpoint functions can be instantiated.

## State And Persistence
State is compile-time kernel configuration. Module selection determines whether named endpoint function drivers register on the `pci_epf` bus at runtime.

## Dependencies And Integration Points
Integrates with endpoint core (`PCI_ENDPOINT`), configfs endpoint composition, NTB subsystem, MHI endpoint core, CRC helper library, and `drivers/pci/endpoint/functions/Makefile`.

## Risks
Function drivers rely on endpoint controller capabilities such as BARs, MSI/MSI-X, and secondary EPC support, but Kconfig cannot express most hardware feature requirements. Selecting configfs from multiple function drivers broadens userspace ABI even if no endpoint controller is present.

## Test Signals
Build each function as built-in and module, verify dependency rejection when `PCI_ENDPOINT`, `NTB`, or `MHI_BUS_EP` is unavailable, and instantiate configfs functions for selected drivers.
