# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_reset.c

Purpose: performs a hardware reset of an mthca PCI/PCI-X/PCIe HCA while preserving and restoring required PCI configuration space.

Important APIs/functions: exports `mthca_reset`. It saves HCA config header dwords, optionally finds and saves the associated Tavor bridge config, writes the reset register at BAR0 offset `0xf0010`, waits for the device to reappear, and restores bridge/HCA PCI-X or PCIe control registers plus core header fields.

Control flow: for non-PCIe devices it searches for a Mellanox bridge with device id `pdev->device + 2` on the parent bus. It allocates header buffers, reads config dwords except offsets 22 and 23, locates PCI-X/PCIe capabilities, ioremaps the reset register, writes the reset value, sleeps one second, polls config space up to ten seconds, then restores bridge split-transaction controls, COMMAND registers last, HCA PCI-X/PCIe controls, and HCA header registers.

State and persistence: transiently stores PCI config headers in heap buffers; the lasting effect is a reset HCA with restored PCI config. It also takes a reference to any bridge via `pci_get_device` and releases it at exit.

Dependencies and integration: used during mthca probe/recovery; depends on Linux PCI, ioremap/writel, sleeps, device flags identifying PCIe, and mthca logging.

Risks: reset is hardware- and bus-topology-sensitive. Failure to restore config can leave the device or bridge unusable. The code only saves 256 bytes and notes uncertainty about full PCIe 4K config space. It skips two dwords with special meaning and assumes bridge discovery by device id.

Test signals: cold probe with reset enabled on Tavor/Arbel/Sinai, PCIe and PCI-X systems, reset failure injection for config reads/writes, and post-reset firmware initialization success.
