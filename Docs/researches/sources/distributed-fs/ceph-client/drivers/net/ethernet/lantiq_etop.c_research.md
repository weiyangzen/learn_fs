# sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_etop.c

## Purpose
`lantiq_etop.c` implements the older Lantiq XWAY ETOP Ethernet MAC as a platform driver. It uses fixed Lantiq DMA channels for one TX and one RX path, provides an MDIO bus, connects to a PHY through phylib, and exposes a multi-queue netdev that effectively selects queue zero.

## Important APIs, Types, And Functions
Runtime state is split between `struct ltq_etop_priv` and `struct ltq_etop_chan`. `ltq_etop_priv` stores the netdev, platform device, board/platform Ethernet data, MII bus, channel array, DMA burst lengths, and a spinlock. Each channel wraps a `struct ltq_dma_channel`, a NAPI object, channel index, TX free pointer, and skb array.

Core functions include `ltq_etop_probe()`, `ltq_etop_init()`, `ltq_etop_hw_init()`, `ltq_etop_hw_exit()`, `ltq_etop_open()`, `ltq_etop_stop()`, `ltq_etop_tx()`, `ltq_etop_poll_rx()`, `ltq_etop_poll_tx()`, `ltq_etop_dma_irq()`, `ltq_etop_mdio_init()`, `ltq_etop_mdio_probe()`, `ltq_etop_mdio_rd()`, `ltq_etop_mdio_wr()`, `ltq_etop_change_mtu()`, and `ltq_etop_tx_timeout()`.

## Control Flow
The module registers a platform driver through `platform_driver_probe()`. Probe maps the ETOP register range, allocates an Ethernet device with four queues, reads required `lantiq,tx-burst-length` and `lantiq,rx-burst-length` properties, attaches weighted NAPI instances to the fixed TX channel 1 and RX channel 6, then registers the netdev. Netdev `.ndo_init` runs `ltq_etop_init()`, which enables PPE, configures MII/RMII mode, enables CRC generation, initializes the DMA port, allocates TX/RX channels and IRQs, sets MTU and MAC address, configures multicast filtering, creates an MDIO bus, finds the first PHY, connects it, limits it to 100 Mbps, and exposes PHY ethtool operations.

Open enables DMA and NAPI per fixed channel, starts the PHY, and starts all TX queues. RX NAPI consumes completed descriptors, allocates a replacement skb under lock, closes DMA on allocation failure, passes the received skb with `netif_receive_skb()`, and acks DMA IRQs on completion. TX pads short frames, checks descriptor availability, maps the skb, writes a burst-aligned DMA address and ownership bits, advances the ring, and stops the queue if the next descriptor is owned. TX NAPI frees completed skbs and wakes queues.

## State And Persistence
The global `ltq_etop_membase` holds the single mapped register base used by access macros. Per-device state includes platform data MAC/MII mode, DMA ring descriptors inside `ltq_dma_channel`, per-channel skb arrays, current DMA descriptor indexes, PHY connection state, and burst length configuration. Hardware register state is reconstructed during `.ndo_init`, timeout recovery, and remove cleanup.

## Dependencies And Integration Points
This file depends on Lantiq SoC headers (`lantiq_soc.h`, `xway_dma.h`, `lantiq_platform.h`), PMU/PPE controls, platform data, Linux phylib/mdiobus, NAPI, DMA mapping, and generic netdev APIs. It exposes ethtool link settings through phylib and uses `phy_do_ioctl` for MII ioctls.

## Risks
The driver mixes `dma_map_single()` with an immediate overwrite of RX descriptor `addr` using `CPHYSADDR()`, and TX also uses `CPHYSADDR()` for offset calculation; this is architecture-specific and risky on systems where DMA addresses differ from physical addresses. MDIO read/write busy loops have no timeout. `ltq_etop_init()` error paths call `unregister_netdev()` and `free_netdev()` from `.ndo_init`, which is unusual because registration is in progress. `ltq_etop_hw_init()` does not unwind already allocated/requested channels if a later channel setup fails. Remove calls hardware and MDIO cleanup even though netdev initialization may have failed partway.

## Test Signals
Coverage should include MII and RMII platform modes, missing burst properties, invalid MAC fallback, PHY absent and PHY connect failure, repeated register/unregister, open/stop cycles, TX timeout recovery, RX allocation failure, DMA IRQ handling, queue stop/wake, MTU updates, multicast/promiscuous filtering, and DMA address correctness on the target Lantiq architecture.
