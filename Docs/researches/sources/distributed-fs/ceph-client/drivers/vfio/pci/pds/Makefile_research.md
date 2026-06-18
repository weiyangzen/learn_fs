# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/Makefile

Purpose: composes the PDS VFIO PCI module.

Important build behavior: `pds-vfio-pci.o` is built when `CONFIG_PDS_VFIO_PCI` is set and includes `cmds.o`, `dirty.o`, `lm.o`, `pci_drv.o`, and `vfio_dev.o`.

Dependencies and integration: the object split mirrors the runtime architecture: PF admin commands, dirty tracking, live-migration files, PCI driver registration, and VFIO device operations.

Risks and test signals: stale object lists would omit migration or logging functionality; build tests should cover module and built-in configurations.
