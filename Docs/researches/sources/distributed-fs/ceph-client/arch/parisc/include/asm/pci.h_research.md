# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pci.h

Purpose: defines PA-RISC PCI host-bridge integration, DMA addressing policy, bus/resource helpers, and platform-specific PCI data.

Important APIs/types/functions: provides `struct pci_hba_data`, PCI DMA/resource constants, `pcibios_*` hooks, `PCI_DMA_BUS_IS_PHYS`, and helpers for bus-to-resource mapping.

Control flow: PCI initialization discovers LBA/SBA host bridges, assigns resources, configures IRQs, and supplies DMA/IOMMU behavior to devices.

State and persistence: PCI host bridge data, bus resources, and DMA masks persist after enumeration. Dependencies and integration: ties together `ropes.h`, `io.h`, DMA mapping, IOSAPIC, and generic PCI core.

Risks and test signals: wrong bus/resource translation breaks all PCI devices. Test with PCI enumeration, DMA-capable devices, MSI/IRQ routing where supported, and config-space access.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
