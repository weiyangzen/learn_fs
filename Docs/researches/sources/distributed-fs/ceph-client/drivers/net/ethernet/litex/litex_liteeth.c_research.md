# sources/distributed-fs/ceph-client/drivers/net/ethernet/litex/litex_liteeth.c

## Purpose
`litex_liteeth.c` is a small platform netdev driver for the LiteX LiteEth FPGA Ethernet core. It accesses LiteX CSR registers and shared slot buffers through MMIO, handles simple interrupt-driven RX/TX events, and exposes a basic Ethernet interface with software statistics.

## Important APIs, Types, And Functions
`struct liteeth` stores CSR base, buffer bases, slot size/counts, current TX/RX slot indexes, device, and netdev. The main routines are `liteeth_probe()`, `liteeth_open()`, `liteeth_stop()`, `liteeth_interrupt()`, `liteeth_rx()`, `liteeth_start_xmit()`, `liteeth_get_stats64()`, and `liteeth_setup_slots()`. Integration is through `liteeth_netdev_ops`, `liteeth_of_match`, and `liteeth_driver`.

## Control Flow
Probe allocates a managed Ethernet device, allocates per-CPU software stats, gets the platform IRQ, maps named resources `mac` and `buffer`, reads optional slot properties (`litex,rx-slots`, `litex,tx-slots`, `litex,slot-size`) with defaults of two slots and 0x800 bytes, divides the buffer region into RX slots followed by TX slots, obtains or randomizes the MAC address, attaches netdev ops, and registers the netdev with devres.

Open clears pending reader/writer events, requests the IRQ, enables writer and reader event interrupts, marks carrier on, and starts the queue. The IRQ handler acknowledges TX reader events and wakes the queue if stopped, then handles writer events by reading one received frame from the indicated slot and acknowledging pending bits. TX checks `LITEETH_READER_READY`, stops the queue and returns busy if hardware is not ready, rejects packets larger than `slot_size`, copies skb data into the current TX slot, writes slot/length/start CSRs, updates software stats, advances the TX slot modulo count, and frees the skb.

## State And Persistence
Runtime state is minimal: current `tx_slot`, configured slot counts/size, mapped CSR/buffer bases, IRQ, netdev carrier/queue state, and per-CPU software stats. There is no PHY, MDIO, DMA mapping, NAPI, or persistent hardware configuration in this driver. Slot layout is derived at probe time from Device Tree.

## Dependencies And Integration Points
The driver depends on LiteX CSR accessors (`litex_read8/16/32`, `litex_write8/16`), platform MMIO resources named `mac` and `buffer`, Device Tree compatible `litex,liteeth`, `of_get_ethdev_address()`, `devm_register_netdev()`, and the generic Ethernet stack. Kconfig requires `OF && HAS_IOMEM`.

## Risks
The interrupt handler processes at most one RX frame per interrupt and uses `netif_rx()` rather than NAPI, so heavy traffic may suffer drops or interrupt pressure. `liteeth_rx()` validates length only against a hard-coded 2048, not `slot_size`, which can be inconsistent if DT sets a smaller slot. TX queue stopping relies on a later reader event to wake it. There is no explicit carrier/PHY negotiation, so carrier is forced on at open. Buffer resource sizing is not checked against `num_rx_slots + num_tx_slots` times `slot_size`.

## Test Signals
Test with default and explicit slot DT properties, invalid or missing MAC, oversized TX frames, hardware-not-ready TX, RX zero length, RX length above 2048, interrupt storms, queue wake events, stats64 accuracy, open/close IRQ lifetime, and buffer resource bounds on FPGA designs with nondefault slot layouts.
