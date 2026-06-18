# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.c



Source read size: 607 lines, 14972 bytes.



Purpose: full SH7786 PCI Express root-complex initialization, including port discovery, clocks, PHY programming, link training, address windows, DMA offsets, and host registration.

Important APIs/types/functions: `sh7786_pcie_init()`, `sh7786_pcie_core_init()`, `sh7786_pcie_init_hw()`, `pcie_clk_init()`, `phy_init()`, `pcie_init()`, `pcie_reset()`, `phy_write_reg()`, `pci_wait_for_irq()`, `pcibios_bus_add_device()`, `pcibios_map_platform_irq()`, and the root-complex BAR fixup.

Control flow: arch init selects hardware ops, derives port count from mode pins, optionally enables a platform clock, prunes unavailable memory windows, schedules asynchronous per-port initialization, and waits for all ports. Each port sets up function/PHY clocks, writes PHY tuning registers, resets the core, configures PCIe capabilities and memory inbound windows, trains the link, sets transaction parameters, programs outbound windows for each resource, then registers the PCI controller in order.

State and persistence: global port array, port clocks, PHY state, PCIe controller config space, inbound/outbound address windows, link state, and DMA direct offsets persist for devices.

Dependencies and integration points: depends on SH7786 CPG clocks, mode pins, async init, PCI core, DMA direct mapping, `pcie-sh7786.h`, memory_start/end, and board FPGA clock/mux setup.

Risks and test signals: PHY magic constants, asynchronous port ordering, memory-window pruning, and DMA offset calculations are all hardware-sensitive; link-down ports still register for future hotplug. Test all port-count modes, endpoint/root-complex mode, link-up/down, DMA to system RAM, resource windows, and SDK7786 slot mux.
