# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/vfio_dev.h

Purpose: declares the PDS VFIO device object and shared helper APIs.

Important types and APIs: `struct pds_vfio_pci_device` embeds `vfio_pci_core_device`, active migration files, dirty state, state mutex, current VFIO migration state, notifier block, VF id, and PDS client id. It declares ops lookup, drvdata conversion, reset helper, and device/pci conversion helpers.

Control flow and integration: used by every PDS implementation file as the central state container. It ties together VFIO core, live migration, dirty logging, PDS notifications, and command client identity.

Risks and test signals: shared state must be protected consistently by `state_mutex`; compile tests catch cross-file API drift, and runtime tests should validate cleanup when any embedded subsystem is active.
