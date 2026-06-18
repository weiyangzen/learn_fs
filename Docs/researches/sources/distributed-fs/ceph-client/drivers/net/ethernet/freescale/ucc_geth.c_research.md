# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth.c

## Purpose
Implements the Freescale/NXP QE UCC Gigabit Ethernet netdevice driver. It binds an Open Firmware platform device, configures UCC Fast/QE register state, allocates QE MURAM parameter blocks and external buffer descriptor rings, connects phylink, and moves packets through the Linux networking stack with NAPI.

## Important APIs, Types, And Functions
The driver centers on `struct ucc_geth_private` and `struct ucc_geth_info` from `ucc_geth.h`. Entry points are `ucc_geth_probe()`, `ucc_geth_remove()`, `ucc_geth_open()`, `ucc_geth_close()`, `ucc_geth_start_xmit()`, `ucc_geth_irq_handler()`, `ucc_geth_poll()`, `ucc_geth_suspend()`, and `ucc_geth_resume()`. Initialization helpers include `ucc_struct_init()`, `ucc_geth_startup()`, `ucc_geth_alloc_tx()`, `ucc_geth_alloc_rx()`, `rx_bd_buffer_set()`, and `init_*` register encoders. Link integration is through `ugeth_mac_ops`, especially `ugeth_mac_link_up()`, `ugeth_mac_link_down()`, and `ugeth_mac_config()`.

## Control Flow
Probe reads device-tree UCC number, clocks, register resource, IRQ, PHY mode, optional TBI node, and creates a `net_device` with NAPI, phylink, ethtool, timeout work, and netdev ops. Open attaches PHY, initializes the UCC/MAC, requests the IRQ, starts phylink, enables NAPI, and starts the queue. Startup validates queue/ring parameters, initializes UCC Fast, maps UCC registers, allocates Tx/Rx BD rings, allocates many QE MURAM PRAM blocks, fills InitEnet thread entries/SNUMs, loads Rx buffers, and issues `QE_INIT_TX_RX`. Tx maps an skb into a Tx BD, advances ring indices, and optionally rings Tx-on-demand/scheduler state. IRQ masks RX/TX events and schedules NAPI; NAPI reclaims Tx BDs, receives completed Rx BDs, refills buffers, then rearms events.

## State And Persistence
Runtime state is in memory and device registers: BD rings, skb arrays, ring pointers, QE MURAM offsets, SNUM ownership, phylink state, multicast hash lists, statistics PRAM, WoL flags, and timeout work. No durable storage is used. Cleanup is `ucc_geth_stop()` plus `ucc_geth_memclean()`, which frees UCC Fast state, MURAM blocks, InitEnet SNUM/thread entries, skb rings, hash lists, and ioremaps.

## Dependencies And Integration Points
Depends on Linux netdev/NAPI/DMA/skbuff APIs, phylink/PHY/OF helpers, platform driver APIs, QE/UCC Fast SoC support, and optional PM/netpoll. It shares ethtool support with `ucc_geth_ethtool.c` via `uec_set_ethtool_ops()`.

## Risks
The startup path has many staged allocations; partial failure relies on the caller invoking stop/cleanup. DMA mappings are mostly tracked through BDs, so mismatched ring status or missing unmap can leak mappings. Tx ring wrap assumes power-of-two ring lengths through `TX_RING_MOD_MASK(size)`. `ugeth_graceful_stop_*()` do not return timeout failures despite waiting. Link-mode reconfiguration quiesces NAPI and IRQs, which needs careful ordering to avoid lost interrupts or deadlocks. Suspend/resume behavior diverges depending on whether QE survives sleep.

## Test Signals
Useful signals are successful platform probe/register_netdev, open/close cycles with phylink up/down, packet Tx/Rx under NAPI, multicast/promiscuous mode updates, ethtool stats/register reads, ring size validation, suspend/resume with and without MAC WoL, and fault injection through allocation/DMA-map failures in startup and Rx refill.
