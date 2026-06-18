## sources/distributed-fs/ceph-client/arch/mips/pci/pci-octeon.c

### Purpose
This file initializes legacy PCI/PCI-X host mode on Cavium Octeon systems without PCIe. It configures Octeon NPI PCI controller registers, DMA BAR mappings, config-space access, board-specific interrupt routing, platform PCI device setup, EDAC device registration, and PCI DMA initialization.

### Important APIs, Types, And Functions
Global state includes `octeon_bar1_pci_phys`, `octeon_pcibios_map_irq`, and `octeon_dma_bar_type`. `union octeon_pci_address` encodes Octeon PCI config/I/O/MEM addresses. `pcibios_map_irq()` delegates to the selected Octeon mapper. `pcibios_plat_dev_init()` sets cache line, latency, parity/SERR, bridge controls, PCIe/AER reporting where present, and clears AER status. `octeon_get_pci_interrupts()` and `octeon_pci_pcibios_map_irq()` implement board IRQ mapping. `octeon_read_config()`/`octeon_write_config()` provide `pci_ops`. `octeon_pci_initialize()` and `octeon_pci_setup()` perform host bring-up.

### Control Flow
`octeon_pci_setup()` exits on PCIe-capable chips or endpoint mode, selects small or big DMA BAR mode, sets I/O port base, initializes the PCI controller, programs memory access endian/snoop attributes, remaps BAR2, configures BAR0/BAR1 differently for big versus small BAR modes, fills BAR1 index registers, sets device memory aperture, registers the controller, clears pending errors, registers `octeon_pci_edac`, and calls `octeon_pci_dma_init()`.

### State, Persistence, And Dependencies
Persistent state is extensive CSR/NPI hardware configuration, PCI resource windows, BAR mappings, global IRQ-mapping function pointer, and DMA translation mode. Dependencies include Octeon model/feature detection, CVMX NPI/PCI register unions, board type data, SWIOTLB for small BAR mode, platform device registration, and generic PCI/AER helpers.

### Integration Points
It shares `octeon_pcibios_map_irq` and `octeon_dma_bar_type` with `pcie-octeon.c`, while serving only non-PCIe chips. It integrates with EDAC through a simple platform device and with the common MIPS PCI core through `register_pci_controller()`.

### Risks
Hardware programming is highly model- and pass-specific. The AER section appears to test ECRC capability against the wrong local variable after reading `PCI_ERR_CAP`, so ECRC enablement deserves review. Big/small BAR setup must match DMA constraints or bus mastering can target unmapped memory.

### Test Signals
Validate host-mode detection, PCI/PCI-X status and clock logs, board-specific IRQ routing, config reads/writes, DMA under big and small BAR modes, EDAC device creation, and absence of pending NPI PCI errors after scan.
