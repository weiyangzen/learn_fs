
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hisi_femac.c

## Purpose

This file implements the Hisilicon Fast Ethernet MAC platform driver for 10/100 Mbps FEMAC devices. It manages clocks/resets, PHY connection, simple TX/RX software queues, hardware address filtering, NAPI interrupt handling, suspend/resume, and netdev registration for FEMAC-compatible device-tree nodes.

## Important APIs, Types, and Functions

- `struct hisi_femac_priv` holds port/global MMIO bases, clock/reset handles, PHY reset delays, link status, TX/RX queues, FIFO usage, and NAPI.
- `hisi_femac_drv_probe()` and `hisi_femac_drv_remove()` implement platform lifecycle.
- `hisi_femac_net_open()` and `hisi_femac_net_close()` reset/program hardware, manage PHY/NAPI/IRQs, and allocate/free active SKBs.
- `hisi_femac_net_xmit()` submits TX buffers to the hardware enqueue registers.
- `hisi_femac_poll()`, `hisi_femac_rx()`, and `hisi_femac_xmit_reclaim()` handle RX and TX completion.
- `hisi_femac_net_set_rx_mode()` programs promiscuous, multicast, and unicast filtering.
- PM callbacks close/reopen the device around clock disable/enable.

## Control Flow

Probe maps port/global registers, enables the clock, resets MAC and optionally PHY using device-tree delays, connects the PHY, obtains or randomizes the MAC address, sets netdev/NAPI/ethtool ops, initializes port registers and software queues, requests the IRQ, and registers the netdev. Open resets the port, programs host MAC, refills RX input queue while hardware is ready, starts queue/NAPI/PHY, clears IRQ raw bits, and enables interrupts. Interrupts disable the mask and schedule NAPI. NAPI reclaims TX, drains RX packets until budget, acknowledges raw interrupt bits, then reenables interrupts when complete.

## State and Persistence

Software state includes TX/RX circular queues of SKB pointers and DMA addresses, `tx_fifo_used_cnt`, link status, PHY reset delays, and NAPI state. Hardware state includes host MAC, forwarding controls, MAC table filters, FIFO depths, RX coalescing, IRQ masks, and port speed/duplex/link bits.

## Dependencies and Integration Points

The driver depends on platform/OF, clocks, reset controllers, PHYLIB, NAPI, DMA API, netdev filtering helpers, and optional PM. It uses `of_phy_get_and_connect()` and PHY ethtool helpers.

## Risks and Edge Cases

`hisi_femac_free_skb_rings()` has a loop path where a NULL RX/TX SKB logs and continues without advancing `pos`, which would loop indefinitely if the inconsistency occurs. TX submission returns `NETDEV_TX_BUSY` after incrementing drop/fifo error stats when hardware or software queue is full. RX length subtracts FCS and checks against max frame size after `skb_put()`. PHY reset delays must be present when a PHY reset control exists. The PHY reset function sleeps the pre-delay twice before asserting reset, which may be intentional but is unusual.

## Test Signals

Signals include probe for all compatible strings, clock/reset sequencing, PHY link changes updating speed/duplex, RX/TX traffic, queue full handling, multicast/unicast filter limits, promiscuous/allmulti behavior, suspend/resume while running and stopped, and no stuck cleanup loops under fault injection.
