# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/netdev.c

## Purpose
`netdev.c` is the main Intel VF network driver implementation. It registers the PCI driver, creates the netdev, manages TX/RX descriptor rings, handles MSI-X interrupts and NAPI, implements reset/open/close/MTU/MAC/VLAN/filter operations, updates VF statistics, handles watchdog and TX timeout recovery, and supports suspend/resume plus PCI error recovery.

## Important APIs, Types, And Functions
Key lifecycle functions are `igbvf_probe()`, `igbvf_remove()`, `igbvf_open()`, `igbvf_close()`, `igbvf_up()`, `igbvf_down()`, `igbvf_reinit_locked()`, and `igbvf_reset()`. RX/TX paths include `igbvf_alloc_rx_buffers()`, `igbvf_clean_rx_irq()`, `igbvf_clean_tx_irq()`, `igbvf_xmit_frame()`, `igbvf_tso()`, `igbvf_tx_csum()`, `igbvf_tx_map_adv()`, and `igbvf_tx_queue_adv()`. Interrupt and polling functions include `igbvf_request_msix()`, `igbvf_configure_msix()`, `igbvf_intr_msix_tx()`, `igbvf_intr_msix_rx()`, `igbvf_msix_other()`, and `igbvf_poll()`. Netdev ops are collected in `igbvf_netdev_ops`.

## Control Flow
Probe enables PCI memory access, maps BAR0, initializes software and hardware ops, sets features, performs a PF-mediated reset/MAC read, initializes timers/work, resets hardware, registers the netdev, and initializes stats baselines. Opening allocates rings, configures hardware, requests MSI-X vectors, enables NAPI/interrupts, and starts the watchdog. RX interrupts schedule NAPI; NAPI cleans RX descriptors, builds skbs, handles checksum/VLAN, returns buffers, and reenables interrupts. TX maps skb data/frags into descriptors, optionally emits context descriptors for TSO/checksum/VLAN, updates the tail, and completion interrupts reclaim DMA mappings and wake the queue. Watchdog checks link through mailbox, updates carrier/stats, flushes stalled TX on link loss, and kicks RX cleanup. Reset paths serialize on `__IGBVF_RESETTING` and run down/up around PF reset handshakes.

## State And Persistence
The netdev-private `igbvf_adapter` owns persistent driver state: rings, MSI-X entries, NAPI, timers, work items, active VLAN bitmap, netdev features, mailbox-backed hardware state, counters, link speed/duplex, and reset state bits. Ring state includes DMA-coherent descriptors, per-buffer skb/page DMA mappings, producer/consumer indices, interrupt throttle values, and stats. VF hardware counters do not clear on read, so software tracks last and base values.

## Dependencies And Integration Points
The file integrates with PCI core, netdev ops, NAPI/GRO, DMA mapping, skb offload helpers, VLAN core, ethtool registration, mailbox/MAC ops from `vf.c` and `mbx.c`, and hardware register constants from `vf.h`/`regs.h`. The PCI ID table binds Intel 82576 VF and I350 VF devices.

## Risks
Concurrency spans hard IRQ, NAPI, timers, workqueues, ethtool, and netdev operations. Reset serialization is essential. RX packet-split page reuse and DMA unmapping must stay balanced. TX descriptor accounting needs gaps to avoid tail/head ambiguity. PCI error recovery and suspend/resume must not leave interrupts or NAPI enabled against freed rings. Mailbox failures can prevent link/MAC/VLAN operations. The code supports MSI-X only; failure to allocate three vectors prevents operation.

## Test Signals
Exercise probe/remove, open/close, traffic under RX/TX checksum and TSO, VLAN add/remove, multicast/unicast filters, MTU changes up to 9216, link up/down, PF reset, VF reset, TX timeout, suspend/resume, PCI error recovery, ethtool ring resize/coalescing, and stats monotonicity. Watch for DMA mapping errors, allocation failures, carrier changes, and reset loop logs.
