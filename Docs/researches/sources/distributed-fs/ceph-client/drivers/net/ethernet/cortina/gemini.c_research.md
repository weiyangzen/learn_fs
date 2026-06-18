# sources/distributed-fs/ceph-client/drivers/net/ethernet/cortina/gemini.c

## Purpose
`gemini.c` is the Ethernet driver for the Cortina/StorLink Gemini SL351x dual-GMAC SoC. It manages a shared hardware free queue, per-port RX/TX DMA rings, PHY/link configuration, interrupts, NAPI receive processing, TX offloads, multicast filtering, ethtool controls, and platform-device probe/remove.

## Important APIs, types, and functions
- Core state: `struct gemini_ethernet` holds global registers, two ports, shared free queue, and IRQ/freeq locks. `struct gemini_ethernet_port` holds per-port netdev, MMIO bases, clock/reset, IRQ, RX/TX queues, NAPI, coalescing timer, stats, and MAC state.
- Initialization/probe: `gemini_ethernet_probe()`, `gemini_ethernet_init()`, `gemini_ethernet_port_probe()`, and module init/register functions.
- PHY/link: `gmac_setup_phy()`, `gmac_adjust_link()`, `gmac_set_flow_control()`, `gmac_enable_tx_rx()`, `gmac_disable_tx_rx()`.
- Queue setup: `gmac_setup_txqs()`, `gmac_setup_rxq()`, `geth_setup_freeq()`, `geth_resize_freeq()`, `geth_fill_freeq()`, and cleanup counterparts.
- TX path: `gmac_start_xmit()`, `gmac_map_tx_bufs()`, `gmac_clean_txq()`, `gmac_tx_irq_enable()`, `gmac_tx_irq()`, and `gmac_tx_timeout()`.
- RX path: `gmac_rx()`, `gmac_skb_if_good_frame()`, `gmac_napi_poll()`, and `gmac_coalesce_delay_expired()`.
- Interrupts: `gmac_irq()` handles per-port netdev IRQs; `gemini_port_irq()` and `gemini_port_irq_thread()` handle shared freeq refill IRQs.
- Netdev/ethtool: `gmac_351x_ops`, `gmac_351x_ethtool_ops`, stats, ringparam, coalesce, pause, ksettings, features, MTU, MAC address, and RX mode handlers.

## Control flow and state
Global probe maps common registers and populates child port devices from device tree. Each port probe maps DMA/GMAC registers, enables the port clock, resets the port, stores the port pointer into the global object, performs common interrupt/freeq initialization once both ports are present, sets netdev ops/features/MTU, obtains MAC address from device tree or hardware/random fallback, requests the threaded freeq IRQ, connects PHY, and registers the netdev.

Open flow requests the netdev IRQ, starts PHY, resizes or reuses the shared free queue, allocates per-port RX and TX rings, enables NAPI, starts DMA, enables interrupts and TX/RX, and starts queues. Stop reverses that by cancelling coalescing, stopping queues and DMA, disabling NAPI/IRQs, cleaning RX/TX rings, stopping PHY, freeing IRQ, and refreshing stats.

TX flow checks descriptor space from hardware read/write pointers, cleans completed descriptors if needed, stops the netdev queue and enables an EOF interrupt when space is still insufficient, maps the SKB head/frags into descriptors, sets TOE/TSO/checksum/bypass flags, writes the new write pointer, and cleans completions. RX flow masks/acks RX interrupt, walks RX descriptors until budget or empty, maps each DMA address back to a shared freeq page, builds frag-list SKBs through NAPI, validates hardware status/checksum metadata, performs GRO on EOF, tracks partial packets in `port->rx_skb`/`rx_frag_nr`, and returns pages/references on drops.

The shared free queue persists across both ports and is resized only when the other port is not running. Its page table maps DMA fragments back to pages and uses page references to decide when a page is reusable or must be replaced.

## Dependencies and integration points
The driver integrates platform devices and child OF devices, clocks, reset controls, MMIO, DMA coherent and streaming APIs, PHYLIB, ethtool, NAPI/GRO, netdev queueing, CRC32 multicast hashing, hrtimers, and u64 stats synchronization. It is enabled by `CONFIG_GEMINI_ETHERNET` and uses register/descriptor definitions from `gemini.h`.

## Risks and test signals
High-risk areas include shared freeq lifetime across two ports, page reference accounting, DMA mapping/unmapping on TX and RX, RX partial-frame cleanup, interrupt masking/acking races, queue resize while another port is running, hardcoded device-name-to-port-ID mapping, and TX offload behavior on large non-TCP frames. Test signals include dual-port probe/order, link changes across MII/GMII/RGMII speeds, traffic under GRO/TSO/checksum offloads, jumbo MTU bounds, multicast/promiscuous mode, ethtool ring/coalesce changes while down, freeq refill interrupts, port open/close cycles, TX queue stop/wake, and DMA state dumps on injected errors.
