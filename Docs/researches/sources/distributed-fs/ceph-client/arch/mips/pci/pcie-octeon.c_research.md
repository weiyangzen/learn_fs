## sources/distributed-fs/ceph-client/arch/mips/pci/pcie-octeon.c

### Purpose
This file initializes Octeon PCIe root complexes, provides low-level CVMX-style PCIe config/I/O/MEM address helpers, handles Gen1 and Gen2 link bring-up with errata workarounds, implements Linux `pci_ops` per port, creates dummy and real controllers, maps interrupts, and initializes PCIe DMA.

### Important APIs, Types, And Functions
Key state includes module parameter `pcie_disable`, `enable_pcie_14459_war`, `enable_pcie_bus_num_war[]`, and the shared `octeon_pcibios_map_irq`/`octeon_dma_bar_type`. `union cvmx_pcie_address` encodes config/I/O/MEM cycles. Helpers include `cvmx_pcie_get_*_base/size()`, `cvmx_pcie_cfgx_read/write()`, `__cvmx_pcie_build_config_addr()`, width-specific config accessors, `__cvmx_pcie_rc_initialize_config_space()`, Gen1/Gen2 link/root initialization functions, and `cvmx_pcie_rc_initialize()`. Linux-facing functions include `octeon_pcie_pcibios_map_irq()`, `octeon_pcie_read_config()`, `octeon_pcie_write_config()`, per-port wrappers, dummy ops, `device_needs_bus_num_war()`, and `octeon_pcie_setup()`.

### Control Flow
`octeon_pcie_setup()` exits if the chip lacks PCIe, is simulation, or `pcie_disable` is set. It installs the PCIe IRQ mapper, sets the aggregate I/O port base, registers a dummy controller to consume bus 0 for IDT bridge compatibility, determines host mode and DMA BAR type, initializes port 0 and port 1 when root-complex mode is available, fills each controller's mem/I/O windows and offsets, registers successful ports, records IDT bus-number workarounds, applies CN63XX SRIO/PCIe interrupt-map errata, then calls `octeon_pci_dma_init()`. Config reads update primary bus numbers, reject impossible root devices, apply non-existent-device errata workarounds, and optionally retry CRS config reads.

### State, Persistence, And Dependencies
Persistent state is vast: PCIe PEM/NPEI/SLI/DPI/CIU/MIO CSRs, BAR1 index tables, root-complex bus numbers, link state, resource windows, dummy controller bus consumption, workaround flags, and DMA mode. Dependencies include many Octeon CVMX register headers, model/feature/board detection, PCI core, module parameters, delay/cycle timers, and shared Octeon PCI DMA code.

### Integration Points
The file is mutually exclusive with legacy `pci-octeon.c` on PCIe-capable chips. It registers legacy MIPS `pci_controller` objects, but much of the hardware code comes from CVMX root-complex initialization. Interrupts map to `OCTEON_IRQ_PCI_INT0` plus swizzled pin offsets, with EBH5600 bridge correction.

### Risks
The file is highly errata-driven and model-specific; regressions can be board-pass specific. Dummy bus 0 is intentional but can confuse bus-number assumptions. Config-read workarounds for nonexistent devices and CN63XX CRS retry are subtle. Several branches return generic `-1`. Gen1/Gen2 link training, SRIO detection, and BAR overlap rules require hardware validation.

### Test Signals
Exercise PCIe disabled parameter, simulation skip, port0/port1 host and endpoint modes, empty slots, Gen2 fallback to Gen1, IDT bus-number workaround, CN56XX/CN63XX errata paths, config read/write widths, interrupt delivery, DMA through BAR1/BAR2, and multiport resource windows.
