# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.c

Purpose: SGI O2 MACE Fast Ethernet platform driver. It controls the IP32 MACE Ethernet block, MII PHY probing, DMA rings, interrupt handling, multicast filtering, and netdev operations.

Important types/functions: `struct meth_private` caches MAC/DMA control registers, PHY address, TX ring and skb tracking, RX buffers, multicast filter, and lock. `meth_probe()` allocates/registers the netdev using the global `o2meth_eaddr`. `meth_open()` resets hardware, allocates rings, requests IRQ, enables DMA, and starts the queue. `meth_release()` disables DMA/interrupts and frees rings. Datapath functions are `meth_tx()`, `meth_add_to_tx_ring()`, `meth_rx()`, `meth_tx_cleanup()`, and `meth_interrupt()`.

Control flow: reset toggles MAC reset, loads the MAC, probes MII, configures MAC filtering and DMA offsets, and checks link. RX disables RX interrupts, processes FIFO entries up to the hardware read pointer, validates status/length, replaces or recycles SKBs, remaps buffers, pushes packets to `netif_rx()`, and re-enables RX. TX prepares descriptors differently for short packets, one-page DMA, or two-page DMA, writes the hardware producer pointer, and enables TX interrupts. Completion consumes SKBs and updates counters. Timeout resets hardware, frees/reallocates rings, restarts DMA, and wakes the queue.

State and dependencies: state lives in MACE MMIO globals, DMA coherent TX ring, per-RX SKBs and DMA mappings, and software ring indices. Dependencies include SGI IP32 MACE headers, MII register definitions, CRC32 for multicast hash, DMA APIs, and platform driver registration.

Risks and test signals: risks include old-style global hardware access, RX allocation without explicit NULL checks in ring init, DMA map error handling gaps in TX prep, multicast hash correctness, and timeout reset while interrupts race. Test open/close, link negotiation, RX underflow/overflow, short/one-page/two-page TX, multicast/promiscuous mode, tx timeout, and IRQ cleanup.
