# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_rx.c

## Purpose
Implements the original HiNIC Rx datapath: allocating and replenishing receive buffers, handling Rx MSI-X interrupts with NAPI, processing CQEs, checksum/VLAN/LRO metadata, building jumbo packets, updating per-queue stats, and cleaning Rx resources.

## Important APIs And Functions
Externally visible functions are `hinic_rxq_get_stats()`, `hinic_init_rxq()`, and `hinic_clean_rxq()`. Core internals include `rx_alloc_skb()`, `rx_alloc_pkts()`, `free_all_rx_skbs()`, `rx_recv_jumbo_pkt()`, `rxq_recv()`, `rx_poll()`, `rx_irq()`, `rx_request_irq()`, and `rx_free_irq()`. `rx_csum()` decodes checksum status and `hinic_copy_lp_data()` supports loopback test capture.

## Control Flow And State
Initialization sets netdev/RQ pointers, buffer size, stats sync, IRQ name, preposts receive WQEs with DMA-mapped SKBs, then configures NAPI, interrupt coalescing, IRQ, and affinity. On interrupt, the handler disables MSI-X for PFs, records interrupt count, and schedules NAPI. `rxq_recv()` reads completed RQ WQEs until budget or LRO replenish threshold, orders DMA reads, unmaps the buffer, applies checksum state, grows the skb or chains jumbo fragments, releases consumed WQEs, handles VLAN tag insertion, feeds loopback capture, records queue and protocol, and submits to GRO. It then replenishes buffers when the free count exceeds a threshold and updates stats under `u64_stats_sync`.

## Dependencies And Integration Points
It depends on `hinic_hw_qp` wrappers, `hinic_hw_wqe` CQE helpers, netdev/NAPI/SKB/DMA APIs, and `hinic_dev` runtime settings such as Rx weight and coalescing. It is created and destroyed by `hinic_main.c`.

## Risks And Test Signals
Risks include DMA ordering mistakes, skb leak/unmap imbalance, jumbo fragment list errors, LRO byte accounting, checksum false positives, and IRQ/NAPI disable races during close. Test signals include Rx traffic with checksum offload on/off, VLAN receive offload, jumbo frames, LRO traffic, low-memory Rx replenish failures, IRQ affinity/coalescing behavior, loopback test packets, and clean interface teardown under load.
