# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac.c

Purpose: Shared Broadcom iProc/BCMA GMAC Ethernet implementation. Bus-specific files provide accessors and feature flags; this file owns DMA descriptors, RX/TX datapath, MAC reset/init, interrupts, NAPI, netdev operations, phylib link adjustment, ethtool stats, and shared probe/remove/PM helpers.

Important APIs/functions: DMA helpers include `bgmac_dma_alloc()`, `bgmac_dma_init()`, `bgmac_dma_cleanup()`, `bgmac_dma_tx_add()`, `bgmac_dma_tx_free()`, and `bgmac_dma_rx_read()`. Chip paths include `bgmac_chip_reset()`, `bgmac_chip_init()`, `bgmac_enable()`, `bgmac_mac_speed()`, and `bgmac_miiconfig()`. Netdev ops are `bgmac_open()`, `bgmac_stop()`, `bgmac_start_xmit()`, `bgmac_set_mac_address()`, and `bgmac_change_mtu()`. Exported APIs include `bgmac_alloc()`, `bgmac_enet_probe/remove()`, `bgmac_enet_suspend/resume()`, `bgmac_adjust_link()`, and `bgmac_phy_connect_direct()`.

Control flow: Shared probe validates/assigns MAC, enables core clock, resets chip, allocates coherent DMA rings, installs NAPI, connects PHY through the front-end callback, sets offload features, registers the netdev, and leaves carrier off. Open resets/init hardware, initializes RX buffers and TX rings, enables MAC/interrupts, requests IRQ, enables NAPI/PHY, and starts the queue. IRQ disables interrupts and schedules NAPI. NAPI acknowledges status, reclaims TX, reads RX frames, and re-enables interrupts when budget is not exhausted. Stop and suspend disable PHY/NAPI/queue, reset chip, and clean DMA.

State/persistence: `struct bgmac` stores ring descriptors, per-slot SKB/buffer mappings, MIB snapshots, interrupt mask, current MAC speed/duplex, feature flags, PHY address, and callback table. RX uses allocated fragments with poison headers to detect DMA failures; TX tracks start/end ring indices modulo slot count.

Dependencies/integration: Uses netdevice/NAPI/DMA APIs, phylib/fixed PHY, ethtool, bcm47xx NVRAM for some chip reset policy, local `unimac.h`, and callback operations supplied by BCMA/platform wrappers.

Risks/test signals: High-risk areas are DMA error unwinding for fragmented TX, RX buffer replacement before unmapping old buffers, unaligned DMA ring handling, interrupt mask policy, feature-flag reset sequences, and queue stop/wake. Test SG/checksum TX, RX under load, ring wrap, DMA allocation failure, IRQ storms, all supported chip feature combinations, MTU changes, ethtool stats, phylib speed/duplex changes, and suspend/resume.
