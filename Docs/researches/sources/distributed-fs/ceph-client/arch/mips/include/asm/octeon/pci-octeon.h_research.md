# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/pci-octeon.h

Purpose: declares OCTEON-specific PCI/PCIe DMA window constants, IRQ mapping indirection, BAR placement, and DMA BAR type state.

Important APIs/types/functions: `CVMX_PCIE_BAR1_PHYS_BASE`, `CVMX_PCIE_BAR1_PHYS_SIZE`, and `CVMX_PCIE_BAR1_RC_BASE` define the BAR1 physical and root-complex placement. `octeon_pcibios_map_irq` is an extern function pointer used by generic `pcibios_map_irq`. `OCTEON_BAR2_PCI_ADDRESS` defines legacy PCI BAR2 address. `octeon_bar1_pci_phys` holds BAR1 physical mapping for PCI. `enum octeon_dma_bar_type` distinguishes invalid, small, big, PCIe, and PCIe2 DMA mappings. `octeon_dma_bar_type` and `octeon_pci_dma_init()` expose DMA setup state.

Control flow: the header has no inline logic. PCI setup code initializes BAR mappings and DMA type, installs the IRQ mapping callback, and calls `octeon_pci_dma_init` for DMA translation behavior.

State and persistence: global externs hold boot-lifetime PCI mapping state. BAR constants represent hardware address-space layout. No state is persisted beyond runtime.

Dependencies and integration points: includes Linux PCI definitions. It integrates with `pci-octeon.c`, DMA mapping in `dma-octeon.c`, and architecture `pcibios_map_irq`.

Risks: DMA address translation depends on the correct `octeon_dma_bar_type`; a wrong type can produce unreachable or corrupt DMA addresses. IRQ mapping is indirect through a function pointer that must be initialized for PCI versus PCIe host modes. BAR1 hole constants affect available DMA aperture layout.

Test signals: PCI/PCIe enumeration, DMA mapping smoke tests, device IRQ delivery, and BAR1/BAR2 address verification are the relevant signals.
