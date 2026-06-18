# sources/distributed-fs/ceph-client/drivers/net/ethernet/faraday/ftmac100.c

## Purpose
This file implements the Faraday FTMAC100 10/100 Ethernet platform driver. It binds to the `andestech,atmac100` compatible string, allocates a standard `net_device`, maps the controller MMIO region, registers NAPI and ethtool hooks, and drives the hardware through RX/TX DMA descriptor rings declared in `ftmac100.h`.

## Important APIs, Types, and Functions
The central private state is `struct ftmac100`, which stores MMIO base, IRQ, DMA-coherent descriptor memory, RX/TX ring cursors, a TX spinlock, `net_device`, `device`, NAPI object, and `mii_if_info`. Probe/remove are handled by `ftmac100_probe()` and `ftmac100_remove()`. Netdev entry points are `ftmac100_open()`, `ftmac100_stop()`, `ftmac100_hard_start_xmit()`, `ftmac100_change_mtu()`, `ftmac100_set_rx_mode()`, and `ftmac100_do_ioctl()`. Hardware setup is centralized in `ftmac100_reset()`, `ftmac100_start_hw()`, and `ftmac100_stop_hw()`. MDIO access is provided through `ftmac100_mdio_read()` and `ftmac100_mdio_write()`, feeding generic MII ethtool/ioctl helpers.

## Control Flow
Probe obtains memory and IRQ resources, allocates `alloc_etherdev()`, populates netdev ops and ethtool ops, resolves a platform MAC address or later randomizes one, maps registers, initializes MII metadata, and registers the netdev. Open allocates the coherent descriptor block plus RX pages, requests the IRQ, resets ring cursors, starts hardware, enables NAPI, starts the TX queue, and unmasks interrupts. The IRQ handler disables all interrupts and schedules NAPI. `ftmac100_poll()` reads ISR, drains RX packets up to budget, completes TX descriptors, accounts status bits, handles MII link changes, and re-enables interrupts once the poll cycle completes. Stop masks interrupts, stops queueing, disables NAPI, shuts down MACCR, frees IRQ, unmaps/free buffers.

## State and Persistence
State is in memory only: descriptor rings, RX page pointers, TX skb backpointers, ring indices, MII status, netdev counters, and MACCR programming. No persistent storage is touched. RX descriptor `rxdes3` stores a `struct page *`, and TX descriptor `txdes3` stores an `sk_buff *`; this is convenient but assumes pointer width fits in `unsigned int`, which is a portability risk on 64-bit systems. Descriptor ownership is exchanged with DMA through OWN bits and explicit DMA map/unmap calls.

## Dependencies and Integration Points
The driver depends on platform device resources, OF matching, Linux netdev, NAPI, ethtool, MII helpers, DMA mapping, `platform_get_ethdev_address()`, and raw MMIO accessors. It integrates with multicast filtering through hash table registers, with PHY management through `generic_mii_ioctl()` and `mii_ethtool_*()`, and with normal Ethernet stack receive/transmit paths through `netif_receive_skb()` and `ndo_start_xmit`.

## Risks
The implementation supports only single-segment TX and RX; oversized TX packets are dropped and multi-segment RX packets are dropped. `ftmac100_rx_packet()` allocates a small skb shell then attaches a page; failed page replacement after consuming the old page is not checked, so sustained allocation failures can deplete RX descriptors. The pointer-in-32-bit descriptor scratch fields are risky on 64-bit builds. `ftmac100_change_mtu()` writes MACCR even when the device may be down, so tests should cover closed-device MTU changes. Interrupt handling always returns `IRQ_HANDLED` after masking interrupts.

## Test Signals
Useful validation includes probe/remove on a DT-backed platform, open/close cycles, ping/iperf traffic, jumbo-MTU boundary tests up to `MAX_PKT_SIZE - VLAN_ETH_HLEN`, multicast/allmulti/promiscuous mode changes, MDIO ethtool operations, TX timeout/error injection, low-memory RX allocation behavior, and NAPI budget behavior under RX load.
