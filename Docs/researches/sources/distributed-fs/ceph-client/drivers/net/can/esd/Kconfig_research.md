# sources/distributed-fs/ceph-client/drivers/net/can/esd/Kconfig

Purpose: Kconfig entry for the esd electronics CAN-PCI(e)/402 family driver.

Important symbol: `CAN_ESD_402_PCI` builds support for C402 card family devices based on the ESDACC CAN controller. It depends on `PCI && HAS_DMA`, matching the PCIe and coherent DMA requirements in the implementation.

Control flow and state: no runtime code; it enables the `esd_402_pci` module and documents supported form factors. Integration points are PCI enumeration, DMA API availability, and the Makefile that links `esdacc.o` with `esd_402_pci-core.o`. Risks are limited configurability: the driver is only available where PCI and DMA are present. Test signals are Kconfig visibility under PCI/HAS_DMA, module build as `esd_402_pci`, and dependency-driven exclusion on non-PCI or no-DMA configurations.
