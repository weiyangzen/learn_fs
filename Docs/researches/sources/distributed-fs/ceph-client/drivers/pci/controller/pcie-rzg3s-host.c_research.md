# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rzg3s-host.c

Purpose: Implements the built-in Renesas RZ/G3S and RZ/G3E PCIe root-complex driver. It manages SYSC mode/reset signals, runtime PM clocks, reset controls, PHY programming, config-space access, inbound/outbound windows, INTx/MSI domains, link-speed selection, and noirq suspend/resume.

Important APIs/types/functions: Major types are `struct rzg3s_pcie_host`, `struct rzg3s_pcie_msi`, `struct rzg3s_pcie_soc_data`, `struct rzg3s_sysc`, and `struct rzg3s_pcie_port`. PCI access uses separate `rzg3s_pcie_root_ops` for root config mapping and `rzg3s_pcie_child_ops` for child bus PIO requests. Key functions include `rzg3s_pcie_host_setup()`, `rzg3s_pcie_probe()`, `rzg3s_pcie_host_init()`, `rzg3s_pcie_parse_map_dma_ranges()`, `rzg3s_pcie_parse_map_ranges()`, `rzg3s_pcie_init_irqdomain()`, `rzg3s_pcie_init_msi()`, and `rzg3s_pcie_set_max_link_speed()`.

Control flow: Probe allocates a host bridge, maps AXI/config registers, parses child port vendor/device IDs and reference clock, obtains the SYSC regmap, sets RC mode/reset signals, obtains/deasserts reset controls, enables runtime PM, sets up inbound/outbound windows and IRQ domains, initializes config/header/PHY/reset state, optionally raises link speed, then registers root and child PCI ops with `pci_host_probe()`. Child config cycles program request address, byte enables, Type 0/Type 1 read/write transaction type, issue the request, and poll completion. MSI setup allocates DMA pages, finds an enabled AXI window containing the DMA address, aligns an MSI window, programs receive registers, and creates a generic MSI parent domain.

State and persistence: Persistent hardware state includes SYSC function bits, reset deassertion state, CFGU permission windows, vendor/device/class/bus registers, AXI/P-window mappings, MSI receive window, INTx/MSI masks, PHY tables, and negotiated link speed. Driver state includes IRQ domains, MSI bitmap/DMA page, reset arrays, raw hardware lock, and parsed port IDs.

Dependencies/integration: Depends on Linux PCI host bridge APIs, generic config helpers, MSI library, irqdomain/chained IRQs, runtime PM, reset framework, regmap/syscon, OF PCI max-link-speed, clock framework, and Renesas DT bindings.

Risks: Child config writes smaller than 32 bits use read-modify-write and warn about RW1C corruption. MSI requires the allocated DMA address to fall within an already enabled AXI window. Window splitting must obey power-of-two and alignment constraints with only eight windows. Suspend failure recovery is complex because SYSC/reset/clock ordering is strict. `sysc_np` must exist in DT for `syscon_node_to_regmap()`.

Test signals: Probe on both `renesas,r9a08g045-pcie` and `renesas,r9a09g047-pcie`, config reads on root and child buses, MSI and INTx delivery, DMA through inbound windows, link speed capping from DT, noirq suspend/resume, reset error paths, and PHY-setting validation against hardware manuals.
