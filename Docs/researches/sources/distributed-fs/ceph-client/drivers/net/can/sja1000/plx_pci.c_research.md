# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/plx_pci.c

Purpose: this generic PLX90xx PCI bridge adapter supports many two-channel SJA1000 CAN cards from Adlink, esd, Marathon, TEWS, IXXAT, Connect Tech, Elcus, MOXA, and ASEM. It describes each board's BAR layout, reset routine, clock/OCR/CDR, and PCI IDs, then registers detected channels with the SJA1000 core.

Important types and APIs: `struct plx_pci_card_info` is the board descriptor containing name, channel count, CAN clock, OCR/CDR, config map, per-channel maps, and reset callback. `struct plx_pci_card` stores detected channels, netdevs, mapped config base, and reset callback. Register access is byte MMIO. Reset helpers cover common PLX9030/9050/9052, PLX9056/PEX8311 reload, Marathon PCI/PCIe special reset windows, and ASEM dual-CAN GPIO reset. `plx_pci_check_sja1000()` validates reset-mode register values and PeliCAN transition.

Control flow: probe enables PCI, allocates card state, maps the descriptor-specified config BAR, runs the descriptor reset function, then iterates expected channels. Each channel maps its own BAR/offset, allocates an SJA1000 netdev, assigns shared IRQ, read/write callbacks, private card pointer, clock/OCR/CDR, dev_id, probes channel presence, and registers it. If any channels exist, bridge interrupts are enabled using either PLX INTCSR or PLX9056 INTCSR depending on device ID. Remove unregisters/free channels, unmaps per-channel and config spaces, resets the card, disables bridge interrupts, frees state, and disables PCI.

State and persistence: all driver state is per-card in memory. Hardware state includes PLX interrupt enables, local reset state, optional EEPROM configuration reload, and SJA1000 register configuration. No filesystem persistence.

Dependencies and integration points: depends on PCI IDs/subsystem IDs, PLX bridge registers, SocketCAN SJA1000 core, MMIO, delays, and shared IRQ operation. The descriptor table is the key integration surface for adding supported PLX-based boards.

Risks and test signals: descriptor BAR/offset mistakes can map the wrong hardware without compile-time detection. Some reset paths map extra BARs temporarily and tolerate failures by logging. Failure cleanup calls the remove path, so it assumes partial card fields are initialized safely. Tests should cover each descriptor family, PLX9056 vs non-9056 interrupt setup, absent channels, reset side effects, partial BAR mapping failures, and simultaneous traffic on both channels.
