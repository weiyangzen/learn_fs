## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.c

Purpose: PowerMac `macio` driver for the AMD/Apple MACE Ethernet controller using DBDMA for TX and RX.

Important APIs/types: `struct mace_data` stores MACE MMIO, TX/RX DBDMA registers and command rings, SKB rings, chip revision, AAUI/GPSI port selection, TX timeout state, and a spinlock. Primary functions include `mace_probe()`, `mace_reset()`, `mace_open()`, `mace_close()`, `mace_xmit_start()`, `mace_interrupt()`, `mace_rxdma_intr()`, and `mace_tx_timeout()`. Module parameter `port_aaui` can force the physical port.

Control flow: probe checks macio resources, obtains `mac-address` or `local-mac-address`, allocates one global dummy RX buffer, maps controller and two DBDMA channels, chooses port mode, resets the chip, requests controller/TX/RX IRQs, and registers the netdev. Open resets hardware, allocates RX SKBs and DBDMA descriptors, arms RX and TX descriptor loops, enables TX/RX, and masks receive-chip interrupts because RX completion is DMA-driven. TX fills a descriptor if the ring has space, starts at most `MAX_TX_ACTIVE` transfers, and arms a timer. The main MACE interrupt drains transmit statuses, handles underrun/collision/carrier/retry errors, includes a special two-byte runt workaround, completes SKBs, and starts later queued descriptors. RX DMA interrupt processes descriptors, handles missing status words, validates appended MACE receive status, adjusts frame length for Ethernet vs 802.3 FCS behavior, submits SKBs, and refills descriptors.

State and persistence: state is private driver memory plus hardware registers/descriptors; nothing persists across unload. Close disables MAC and DMA and frees rings. Timeout recovery resets TX/RX paths, discards or advances one failed packet, restarts RX DMA, and re-enables MAC.

Dependencies/integration: depends on `macio`, DBDMA, Open Firmware, netdev, CRC multicast hashing, and `mace.h` register definitions. It integrates with the kernel network stack via `net_device_ops`; no ethtool-specific ops are provided.

Risks: hardware workarounds are subtle, especially `BROKEN_ADDRCHG_REV` and the bad-runt TX workaround. The driver uses legacy bus mappings and busy-wait register loops. RX length correction depends on header interpretation and appended status bytes. The TX timeout timer and interrupt path share mutable state under a spinlock.

Test signals: compile for PowerMac MACE configs, boot/probe with correct chip revision, open/close, AAUI/GPSI port selection, multicast/promiscuous updates, TX underrun/collision recovery, RX under allocation pressure using `dummy_buf`, and timeout reset behavior.
