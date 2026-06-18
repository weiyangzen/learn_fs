# sources/distributed-fs/ceph-client/drivers/net/ethernet/lantiq_xrx200.c

## Purpose
`lantiq_xrx200.c` implements the Lantiq/Intel XRX200 PMAC Ethernet interface. It presents a netdev for the CPU-facing PMAC/DMA path, configures PMAC header/CRC behavior, uses one RX and one TX Lantiq DMA channel, and handles large packets through RX fragment chaining.

## Important APIs, Types, And Functions
`struct xrx200_priv` owns the clock, RX/TX channels, buffer sizing, netdev, device pointer, and PMAC register mapping. `struct xrx200_chan` wraps one `ltq_dma_channel`, a NAPI object, skb or RX fragment arrays, TX cleanup pointer, in-progress RX skb chain, and backpointer to private state.

Important functions are `xrx200_probe()`, `xrx200_remove()`, `xrx200_dma_init()`, `xrx200_hw_cleanup()`, `xrx200_open()`, `xrx200_close()`, `xrx200_start_xmit()`, `xrx200_poll_rx()`, `xrx200_hw_receive()`, `xrx200_tx_housekeeping()`, `xrx200_change_mtu()`, `xrx200_dma_irq()`, and PMAC register helpers `xrx200_pmac_r32()`, `xrx200_pmac_w32()`, and `xrx200_pmac_mask()`.

## Control Flow
Probe allocates a managed Ethernet device, sets MTU bounds from the DMA data limit, maps PMAC registers, reads named RX/TX IRQs, enables a clock, obtains or randomizes the MAC address, initializes Lantiq DMA rings, enables the clock gate, configures PMAC inter-packet gap and header/CRC controls, adds RX and TX NAPI, stores platform data, and registers the netdev. Open enables TX NAPI/DMA/IRQ, enables RX NAPI/DMA, flushes bootloader-leftover RX packets, enables RX IRQ, and wakes the queue. Close stops the queue, disables NAPI, and closes DMA channels.

RX NAPI loops over completed descriptors, replaces the buffer first, builds an skb from the old fragment, and either starts a new chained skb on SOP, appends fragments to `frag_list`, or submits the complete packet on EOP. TX maps a padded skb, computes a burst-alignment offset from the DMA mapping, writes descriptor address/control ownership, advances the ring, stops the queue when full, and accounts with BQL. TX NAPI consumes completed descriptors, updates stats and BQL, frees skbs, clears descriptors, and wakes the queue.

## State And Persistence
Persistent runtime state consists of DMA descriptor rings and indexes, RX fragment buffers, any partially assembled RX `skb_head`/`skb_tail`, TX skb slots, clock state, PMAC register configuration, and computed `rx_buf_size`/`rx_skb_size`. `xrx200_change_mtu()` updates buffer sizing and, for MTU increases, temporarily closes RX DMA, drains pending packets, reallocates each RX buffer, then reopens RX if the interface was running.

## Dependencies And Integration Points
The driver depends on platform Device Tree compatible `lantiq,xrx200-net`, named `rx` and `tx` IRQs, one MMIO resource, a clock, `xway_dma.h`, Linux NAPI, BQL, DMA mapping, and `of_get_ethdev_address()`. It does not connect to phylib directly in this file; it handles the CPU PMAC data path and leaves switch/PHY details elsewhere in the platform.

## Risks
RX buffer cleanup checks `priv->chan_rx.skb[i]` in one error path even though RX buffers are stored in the `rx_buff` union member, so that condition may not reflect allocation state. `xrx200_start_xmit()` stores the skb before DMA mapping; on mapping failure it frees the skb but does not clear the ring slot, which can make the descriptor appear busy later. RX multi-fragment assembly assumes an EOP will follow a SOP; malformed descriptor sequences can leave `skb_head` held. MTU reallocation frees old fragments after allocating replacements, but rollback after partial failure leaves a mixed ring that must be tested on hardware.

## Test Signals
Test signals include probe with missing IRQ/clock/resource, random MAC fallback, open/close cycles, RX flushing after bootloader traffic, fragmented RX packet assembly, malformed SOP/EOP descriptor sequences, TX ring full and DMA mapping failures, BQL accounting, MTU increase/decrease and rollback, removal after failed probe steps, and traffic under PMAC header/CRC configuration.
