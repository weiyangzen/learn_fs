# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/ems_pci.c

Purpose: this PCI adapter driver supports EMS CPC-PCI, CPC-104P, and CPC-PCIe cards containing one or more SJA1000-compatible CAN channels. It maps board-specific PCI bridge resources and registers each detected channel with the common SJA1000 SocketCAN core.

Important types and APIs: `struct ems_pci_card` stores version, channel count, PCI device, per-channel netdevs, configuration MMIO, and CAN controller MMIO. Version-specific register accessors handle PITA-2 v1, PLX9030 v2, and ASIX99100 v3 layouts. `ems_pci_check_chan()` probes each channel by switching to PeliCAN mode. The PCI driver entry points are `ems_pci_add_card()` and `ems_pci_del_card()`.

Control flow: probe enables the PCI device, allocates card state, determines hardware version from vendor/device IDs, maps configuration and CAN BARs, validates the EMS signature for v1, deasserts ASIX local reset for v3, resets the board, then iterates possible channels. For each channel it allocates an SJA1000 netdev, sets board private data, IRQ flags, IRQ number, register base and accessors, probes channel presence, assigns clock/OCR/CDR, enables bridge interrupts, and calls `register_sja1000dev()`. Remove unregisters/free all registered netdevs, unmaps resources, frees card state, and disables PCI.

State and persistence: driver state is per-card and per-channel in memory only. Hardware configuration includes bridge interrupt status/control, ASIX reset/interrupt enables, and SJA1000 OCR/CDR settings. No persistent storage is used.

Dependencies and integration points: depends on PCI, MMIO, SocketCAN SJA1000 helper APIs, shared IRQs, and version-specific bridge registers. `priv->post_irq` clears bridge-level interrupt latches after the common SJA1000 ISR handles a channel.

Risks and test signals: cleanup assumes `pci_set_drvdata()` card state exists even on partial failures. The maximum channel define is tied to v2, while v3 also supports four channels; code currently uses `EMS_PCI_MAX_CHAN` from v2. Hardware signature/probe paths are version-specific. Tests should cover all three card generations, absent-channel detection, shared IRQ ack behavior, partial registration failure cleanup, and hot remove.
