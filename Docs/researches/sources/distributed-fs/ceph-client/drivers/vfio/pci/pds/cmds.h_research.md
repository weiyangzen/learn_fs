# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/cmds.h

Purpose: declares the PDS admin-command API consumed by migration, dirty tracking, and PCI driver code.

Important APIs: prototypes cover client lifecycle, suspend/resume, migration state size/save/restore, host-VF migration status, dirty status/enable/disable, and seq/ack bitmap exchange.

Control flow and integration: this header is the narrow boundary between high-level VFIO state code and low-level PDS PF firmware commands. It intentionally exposes no structures beyond the PDS VFIO device pointer and command parameters.

Risks and test signals: signature changes ripple across `lm.c`, `dirty.c`, and `pci_drv.c`; compile tests catch most integration drift, while runtime tests must validate command ordering.
