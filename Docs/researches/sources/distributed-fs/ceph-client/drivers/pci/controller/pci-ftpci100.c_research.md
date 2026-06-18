## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-ftpci100.c

Purpose: Faraday FTPCI100 conventional PCI host controller driver, used for Gemini and dual variants. It implements config cycles through controller registers, optional cascaded INTx, DMA range programming, bus clock setup, and root-bus scanning.

Important APIs, types, and functions: `struct faraday_pci_variant` flags whether the controller has an embedded cascaded IRQ controller. `struct faraday_pci` stores device, MMIO base, irqdomain, scanned bus, and bus clock. `faraday_res_to_memcfg()` converts IO/DMA resource base and power-of-two size to Faraday memory base/size encoding. `faraday_raw_pci_read_config()` and `faraday_raw_pci_write_config()` issue CONFIG/DATA register accesses; `faraday_pci_ops` wraps them for PCI core. IRQ support includes ack/mask/unmask callbacks, `faraday_pci_irq_handler()`, irqdomain map, and `faraday_pci_setup_cascaded_irq()`. `faraday_pci_parse_map_dma_ranges()` writes up to three DMA memory windows. `faraday_pci_probe()` allocates a host bridge, enables clocks, maps registers, configures IO size, command bits, IRQs, bus speed, DMA windows, scans, assigns resources, and adds devices.

Control flow: probe uses firmware-parsed host bridge windows and DMA ranges. It programs the controller before scanning. If `cascaded_irq` is true, it creates mappings for four INTx lines below the child interrupt-controller node. Bus speed is optionally increased to 66 MHz when both clock rate and capability allow it.

State and persistence: volatile state includes controller IO size/protection/control/config registers, PCI config registers on bus 0 device 0, DMA window registers, clock rate, irqdomain, root bus pointer, and scanned PCI devices. No persistent storage.

Dependencies and integration points: PCI host bridge APIs, OF PCI windows and DMA ranges, platform MMIO, clock framework (`PCLK`, `PCICLK`), irqdomain/chained IRQ, and compatible variants `faraday,ftpci100` and `faraday,ftpci100-dual`.

Risks: `faraday_res_to_memcfg()` supports only enumerated power-of-two sizes and warns but truncates low address bits. Only three DMA ranges are programmed; extras are ignored. Config read debug logs print `*value` before it is read. The driver manually scans/adds devices instead of `pci_host_probe()`, so removal support is absent.

Test signals: Gemini boot enumeration, IO size programming, three DMA range mappings, cascaded INTx delivery and masking, 33/66 MHz clock selection, config byte/word/dword access correctness, and rejection of unsupported resource sizes.
