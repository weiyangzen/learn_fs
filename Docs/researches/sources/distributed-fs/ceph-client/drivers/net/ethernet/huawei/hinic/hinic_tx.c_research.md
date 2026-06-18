# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_tx.c

## Purpose
Implements the original HiNIC Tx datapath: SKB DMA mapping, SQ WQE construction, checksum/TSO/tunnel/VLAN offload programming, doorbell writes, Tx completion cleanup through NAPI, queue wake logic, stats, and Tx queue lifecycle.

## Important APIs And Functions
Externally visible APIs are `hinic_txq_get_stats()`, `hinic_lb_xmit_frame()`, `hinic_xmit_frame()`, `hinic_init_txq()`, and `hinic_clean_txq()`. Internal helpers include `tx_map_skb()`, `tx_unmap_skb()`, `offload_tso()`, `offload_csum()`, `hinic_tx_offload()`, `free_all_tx_skbs()`, `free_tx_poll()`, `tx_irq()`, and IRQ setup/teardown functions.

## Control Flow And State
Transmit maps skb head and frags into SGEs, reserves an SQ WQE, prepares descriptors, programs offloads, writes the WQE with saved skb metadata, and rings the SQ doorbell unless xmit_more batching delays it. If the ring is full, it stops the subqueue, retries to close the race with completion on another CPU, and returns `NETDEV_TX_BUSY` if still full. Completion NAPI reads hardware CI, compares it with software CI and WQE size, unmaps/free SKBs, advances the SQ consumer, updates stats, and wakes a stopped subqueue when enough WQEBBs are free. Initialization allocates SGE scratch arrays, programs the hardware CI address, sets interrupt coalescing, and requests IRQ.

## Dependencies And Integration Points
It depends on `hinic_hw_qp` SQ helpers, `hinic_hw_wqe` offload bitfields, Linux SKB/DMA/NAPI APIs, `hinic_port` feature configuration, and `hinic_main.c` queue lifecycle. It shares interrupt coalescing settings through `hinic_dev`.

## Risks And Test Signals
Risks include DMA unmap imbalance on partial mapping/offload errors, queue stop/wake races, WQE size miscalculation for fragmented SKBs, offload header parsing bugs for IPv6 extensions and tunnels, and minimum-packet padding behavior. Test signals include TCP/UDP/SCTP checksum, TSO/TSO6, UDP tunnel offloads, VLAN insertion, high-fragment SKBs, ring saturation, Tx timeout diagnostics, loopback xmit, and close under active Tx load.
