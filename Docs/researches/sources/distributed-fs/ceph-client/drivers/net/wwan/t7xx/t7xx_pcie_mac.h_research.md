# sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_pcie_mac.h

This header exposes PCIe MAC helpers and the `IREG_BASE(t7xx_dev)` accessor for internal PCIe MAC registers. It defines the integration surface used by PCI probe/resume, modem reset/RGU handling, and MHCCIF interrupt setup.

The API covers global interrupt enable/disable, ATR initialization, individual interrupt mask set/clear, interrupt status clear, and MSI-X count programming. It has no own persistent state, but callers rely on it to update hardware state that gates all T7xx interrupts and register translations. Dependencies are `struct t7xx_pci_dev` and `enum t7xx_int`. Risks are unsafe calls before BAR mapping or after remove, and interrupt masking mismatches between hardware and callback arrays. Tests should verify interrupt delivery and register access after probe, resume, and reprobe.
