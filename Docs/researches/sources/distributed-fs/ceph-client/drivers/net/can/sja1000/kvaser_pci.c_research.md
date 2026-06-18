# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/kvaser_pci.c

Purpose: this PCI driver supports Kvaser PCIcan/PCIcanx boards with up to four SJA1000 channels behind an AMCC S5920/Xilinx interface. It maps common bridge and channel resources, detects channel count, and registers each SJA1000 controller.

Important types and APIs: `struct kvaser_pci` is allocated inside the first channel's SJA1000 private area and tracks PCI device, mapped config/resource windows, Xilinx version, channel count, and slave netdevs. `kvaser_pci_enable_irq()`/`disable_irq()` manipulate S5920 interrupt enable. `number_of_sja1000_chip()` probes channels by setting reset mode. PCI entry points are `kvaser_pci_init_one()` and `kvaser_pci_remove_one()`.

Control flow: probe enables the PCI device, requests regions, maps S5920 config BAR, Xilinx BAR, and channel BAR, counts present SJA1000 chips, then calls `kvaser_pci_add_chan()` for each. Channel 0 initializes Xilinx version, passive PTCR mode, and bridge interrupts; later channels are linked as slaves under the master board object. Each channel gets base address offset by `0x20`, read/write callbacks, shared IRQ, clock/OCR/CDR, dev_id, and registration through `register_sja1000dev()`. Remove calls `kvaser_pci_del_chan()` on the master, then releases regions and disables PCI.

State and persistence: state is anchored in the master netdev's private board structure and slave pointers. Hardware interrupt enable and Xilinx/PTCR state are configured at probe and disabled at removal. No persistence exists beyond device lifetime.

Dependencies and integration points: depends on PCI region management, MMIO, SocketCAN SJA1000 core, and shared interrupts. The master/slave netdev structure means cleanup and drvdata are centered on channel 0.

Risks and test signals: if channel registration fails after one or more slaves, cleanup depends on master linkage being correct. `number_of_sja1000_chip()` uses reset-bit behavior as presence detection. Tests should cover one to four channel cards, registration failure at each channel index, bridge IRQ enable/disable, Xilinx version reporting, and shared IRQ behavior under simultaneous channel traffic.
