# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.h



Source read size: 577 lines, 25785 bytes.



Purpose: SH7786 PCI Express register map and bitfield catalog used by SH7786 PCIe config and initialization code.

Important APIs/types/functions: base addresses for the three controllers, config-space offsets, PHY command/ack bits, interrupt masks such as `MASK_INT_TX_CTRL`, inbound `PCIELAR/LAMR` windows, outbound `PCIEPAR/PAMR/PTCTLR` macros, PCIe capability register offsets, DMA register offsets, and inline `pci_read_reg()`/`pci_write_reg()`.

Control flow: no runtime control flow; macros are consumed by `ops-sh7786.c` and `pcie-sh7786.c` to program controller, PHY, MSI, DMA, link, and translation registers.

State and persistence: constants describe MMIO-backed hardware state; inline helpers perform raw 32-bit register accesses.

Dependencies and integration points: tightly coupled to the SH7786 hardware manual, PCIe root-complex driver, and SH raw I/O accessors.

Risks and test signals: any offset or bit error can corrupt PCIe training, config access, or address translation. Test by comparing register traces against datasheet values, enumerating devices on each port, and exercising memory/I/O windows.
