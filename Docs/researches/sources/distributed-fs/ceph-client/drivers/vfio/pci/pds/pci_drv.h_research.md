# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.h

Purpose: minimal include guard for PDS PCI driver declarations.

Important content: includes `<linux/pci.h>` but currently declares no functions or types.

Integration: included by `pci_drv.c`, likely reserved for future PCI-driver shared declarations.

Risks and test signals: no runtime risk. Compile tests catch include guard or dependency issues.
