# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Kconfig

Purpose: adds the `PDS_VFIO_PCI` tristate for AMD/Pensando PDS VFIO PCI support.

Important configuration: it depends on `PDS_CORE && PCI_IOV`, selects `VFIO_PCI_CORE` and `IOMMUFD_DRIVER`, and documents the module name `pds-vfio-pci` plus the related PDS VFIO documentation.

Control flow and integration: this config enables the PDS VF migration/logging driver built by the local Makefile. The dependencies ensure the PF-side PDS core and SR-IOV support are present.

Risks and test signals: build coverage should verify dependency gating and namespace imports. Runtime behavior is only meaningful for Pensando VF device IDs handled in `pci_drv.c`.
