# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/sb1250-mac.c

## Purpose

`sb1250-mac.c` is a Linux platform driver for Broadcom SiByte SoC built-in Gigabit Ethernet MACs. It predates GENET and implements a standalone netdev driver with SiByte-specific MMIO registers, descriptor rings, bit-banged MDIO, PHY integration, NAPI receive polling, interrupt coalescing, multicast/perfect filters, and platform probe/remove.

## Important APIs, Types, and Functions

Important private types are `struct sbdmadscr` for 128-bit DMA descriptors, `struct sbmacdma` for one TX/RX DMA channel context, and `struct sbmac_softc` for the netdev-private MAC state. State enums model link speed (`sbmac_speed`), duplex (`sbmac_duplex`), flow control (`sbmac_fc`), and channel state (`sbmac_state`).

MDIO is implemented directly through `sbmac_mii_sync`, `sbmac_mii_senddata`, `sbmac_mii_read`, and `sbmac_mii_write`, registered as an `mii_bus`. DMA setup and servicing is handled by `sbdma_initctx`, `sbdma_channel_start`, `sbdma_channel_stop`, `sbdma_add_rcvbuffer`, `sbdma_add_txbuffer`, `sbdma_emptyring`, `sbdma_fillring`, `sbdma_rx_process`, and `sbdma_tx_process`. MAC configuration and lifecycle is handled by `sbmac_initctx`, `sbmac_channel_start`, `sbmac_channel_stop`, `sbmac_set_channel_state`, `sbmac_set_speed`, `sbmac_set_duplex`, `sbmac_promiscuous_mode`, `sbmac_set_iphdr_offset`, `sbmac_setmulti`, `sbmac_open`, `sbmac_close`, `sbmac_poll`, `sbmac_intr`, `sbmac_start_tx`, `sbmac_tx_timeout`, `sbmac_init`, `sbmac_probe`, and `sbmac_remove`.

The driver registers `sbmac_netdev_ops`, supports optional netpoll, exposes module parameters for debug level and coalescing packet/time thresholds, and binds through `module_platform_driver(sbmac_driver)`.

## Control Flow

Platform probe maps the MMIO resource, checks whether firmware left a nonzero Ethernet address in `R_MAC_ETHERNET_ADDR`, allocates an Ethernet device, stores the mapped base, and calls `sbmac_init`. Initialization reads and clears the firmware-provided hardware address, initializes register pointers and DMA contexts, configures netdev ops/NAPI/IRQ/MTU, detects hardware checksum support, creates/registers the MDIO bus, registers the netdev, and logs address/checksum details.

Open clears pending interrupt status, requests the MAC IRQ, resets cached link state, attaches the first PHY on the MDIO bus with GMII mode, starts the channel, starts the TX queue, programs RX mode, starts the PHY, and enables NAPI. Close disables NAPI, stops and disconnects the PHY, stops the channel, stops TX queueing, frees the IRQ, and empties TX/RX rings.

`sbmac_channel_start` clears filters/tables, programs MAC config/FIFO/frame registers, writes station address and perfect filter slot 0, starts RX and TX DMA channel registers, applies cached speed/duplex/flow control, fills the RX ring, enables DMA/MAC, enables coalesced or channel interrupts, accepts unicast/broadcast traffic, marks state on, programs multicast filters, and reapplies promiscuous mode if needed. `sbmac_channel_stop` disables filters/interrupts/MAC, stops both DMA channels, and frees queued SKBs.

TX is single-descriptor per SKB. `sbmac_start_tx` queues the SKB under `sbm_lock` with `sbdma_add_txbuffer`; if the ring is full it stops the queue and returns busy. Completion is processed by `sbdma_tx_process`, which compares software removal pointer with hardware current descriptor, frees completed SKBs, updates netdev stats, advances the removal pointer, and wakes the queue when packets completed. RX processing compares software and hardware descriptor indices, accounts FIFO drops, replaces each completed good receive buffer before passing the old SKB to the stack, handles hardware IPv4/TCP checksum status when supported, updates stats, and either uses `netif_receive_skb` under NAPI or `netif_rx` outside polling.

## State and Persistence Behavior

Device state is all in memory. `struct sbmac_softc` stores mapped register pointers, current speed/duplex/flow-control/link values, cached netdev flags, hardware address, PHY/MDIO handles, NAPI object, spinlock, DMA contexts, and checksum capability. Each DMA context owns aligned descriptor memory, a context table of SKBs, physical descriptor base, add/remove pointers, and coalescing settings. Firmware-provided MAC address is consumed from hardware during init; on init failure the probe path restores it. No persistent disk state exists.

## Dependencies and Integration Points

The driver is specific to SiByte MIPS SoCs and depends on architecture headers under `asm/sibyte`, raw 64-bit MMIO access, platform resources, phylib, MII bus registration, netdev/NAPI, and optional netpoll. It uses `UNIT_INT()` macros derived from SoC configuration to pick MAC IRQs and supports either BCM1x80 or SB1250/BCM112x register/interrupt definitions. PHY interrupts use `K_INT_PHY` if available, otherwise polling.

## Risks and Edge Cases

Descriptor memory is allocated with `kzalloc` and translated with `virt_to_phys`, not the generic DMA mapping API, which is tied to the target architecture's cache/DMA assumptions. RX buffers are carefully cache-line aligned because the MAC writes whole cache lines; changing allocation/alignment can corrupt adjacent memory. RX replacement failure re-adds the old SKB and stops processing, so sustained allocation pressure can stall RX. The multicast implementation uses only perfect filters and does not use the hash filter on overflow, so excess multicast addresses are silently not programmed unless all-multicast is enabled. The PHY link callback restarts the channel under lock when speed/duplex/flow control changes. `sbmac_probe` skips devices whose firmware MAC address register is zero, which is a platform contract.

## Test Signals

Useful validation includes boot/probe on supported SiByte SoCs, firmware MAC address detection and zero-address skip, MDIO read/write/PHY attach, link changes across 10/100/1000 and half/full duplex, flow-control negotiation, TX queue stop/wake under ring-full conditions, RX under allocation pressure, NAPI interrupt masking/re-enable, coalescing module parameters, multicast/all-multicast/promiscuous modes, hardware checksum enable on pass2+ hardware, netpoll when configured, and clean remove after register_netdev failure paths. Runtime counters to watch include `rx_fifo_errors`, `rx_dropped`, `rx_errors`, `tx_errors`, and TX timeout warnings.
