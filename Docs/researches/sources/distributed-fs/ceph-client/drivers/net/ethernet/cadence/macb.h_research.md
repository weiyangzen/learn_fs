# sources/distributed-fs/ceph-client/drivers/net/ethernet/cadence/macb.h

## Purpose
`macb.h` is the shared hardware and driver contract for the Cadence MACB/GEM Ethernet implementation. It defines register offsets, bitfield helpers, descriptor layouts, capability flags, statistics descriptors, driver state structures, PTP interfaces, queue metadata, platform data, and ENST/TAPRIO timing helpers used by `macb_main.c`, `macb_ptp.c`, and `macb_pci.c`.

## Important APIs, types, and constants
- Register definitions cover legacy MACB, GEM, per-queue windows, PTP timer registers, PCS/USXGMII, screener/filter registers, and ENST scheduled-traffic registers.
- `MACB_BIT`, `MACB_BF`, `MACB_BFEXT`, `MACB_BFINS` and GEM equivalents centralize bitfield generation/extraction.
- `macb_readl`, `macb_writel`, `gem_readl`, `gem_writel`, `queue_readl`, and `queue_writel` dispatch through `struct macb` MMIO accessor callbacks.
- `struct macb_dma_desc`, `struct macb_dma_desc_64`, and `struct macb_dma_desc_ptp` describe variable DMA descriptor formats.
- `struct macb_tx_skb` tracks skb ownership, DMA mapping, size, and mapping type for TX descriptors.
- `struct macb_or_gem_ops` abstracts MACB versus GEM RX allocation, free, ring init, and RX polling.
- `struct macb_ptp_info` provides optional PTP hooks without forcing `macb_main.c` to depend directly on `macb_ptp.c`.
- `struct macb_queue` stores per-queue IRQ/register offsets, TX/RX rings, DMA addresses, NAPI structures, stats, and ENST register offsets.
- `struct macb` is the central runtime state object for MMIO, clocks, queues, netdev, phylink, PCS, capabilities, DMA/rings, stats, WoL, PTP, flow filters, work items, EEE, interrupt masks, PM state, and USRIO configuration.
- `struct macb_config` and `struct macb_usrio_config` describe platform match data; `struct macb_platform_data` is used by the PCI wrapper.

## Control flow and integration
The header has no standalone execution but is the compile-time integration point for all Cadence files. `macb_main.c` uses it for probe, phylink, DMA, interrupts, ethtool, flow filters, TAPRIO, and PM. `macb_ptp.c` uses descriptor and TSU definitions. `macb_pci.c` uses `struct macb_platform_data`. When `CONFIG_MACB_USE_HWSTAMP` is disabled, PTP helpers become inline no-ops.

## State, risks, and test signals
The declared runtime state lives in netdev private data and hardware registers. `struct macb_pm_data` saves selected registers across suspend. Descriptor ownership bits are critical hardware/software synchronization state. Risks include bitfield drift, descriptor size mistakes, capability flags not matching hardware, and queue register offset mistakes. Tests should cover timestamp and non-timestamp builds, 64-bit DMA, multi-queue hardware, ethtool stats naming, TX/RX ring wrap, TAPRIO unit conversion, and PTP descriptor behavior.
