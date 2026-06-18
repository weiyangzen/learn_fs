## sources/distributed-fs/ceph-client/drivers/net/ethernet/ezchip/nps_enet.c

## Purpose
Implements the EZchip NPS management Ethernet platform driver. The hardware has no DMA and uses MMIO FIFOs plus RX-ready/TX-done interrupts, so the driver copies packet words directly between SKBs and device buffers.

## Important APIs, Types, and Functions
Important functions include `nps_enet_probe`, `nps_enet_remove`, `nps_enet_open`, `nps_enet_stop`, `nps_enet_start_xmit`, `nps_enet_irq_handler`, `nps_enet_poll`, `nps_enet_rx_handler`, `nps_enet_tx_handler`, `nps_enet_send_frame`, `nps_enet_hw_reset`, `nps_enet_hw_enable_control`, `nps_enet_hw_disable_control`, `nps_enet_set_hw_mac_address`, and `nps_enet_set_rx_mode`.

## Control Flow and State
Probe requires an OF node, allocates the netdev, maps registers, reads or randomizes the MAC address, obtains one IRQ, adds weighted NAPI, and registers the netdev. Open clears private TX/config state, disables hardware, requests the IRQ, enables NAPI, resets PCS/TX FIFO, configures MAC filtering/IFG/preamble/flow-control/max length, enables interrupts and RX/TX, and starts the queue. TX stops the queue, stores one outstanding SKB in `priv->tx_skb`, uses a write memory barrier, writes data words to the TX FIFO, then sets the TX control register. NAPI handles TX completion and at most one RX frame per poll, re-enables interrupts, and reschedules itself if a TX completion was missed while interrupts were masked.

Persistent state is small: `tx_skb`, cached MAC config registers 2/3, NAPI object, IRQ number, and MMIO base. The hardware holds FIFO contents and control bits.

## Dependencies and Integration Points
Depends on OF platform probing, big-endian MMIO access helpers from `nps_enet.h`, NAPI, netdev stats, `of_get_ethdev_address`, and netpoll when configured. It deliberately disables multicast support in `ndev->flags`.

## Risks and Test Signals
Risks include single-outstanding-TX behavior, watchdog behavior if TX-done interrupt is lost, alignment/endian handling for partial FIFO words, RX frame length limits, no DMA/checksum/multicast support, and config cache drift because `nps_enet_set_rx_mode` writes a local copy without updating `priv->ge_mac_cfg_2_value`. Test with management traffic, unaligned SKB data, minimum/maximum frames, CRC/error frames, promisc toggles, TX interrupt loss scenario, netpoll, up/down loops, and watchdog timeout injection.
