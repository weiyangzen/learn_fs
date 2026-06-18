# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.c

## Purpose
`otx2_txrx.c` is the core RVU NIC packet data path. It polls CQEs through NAPI, builds SKBs from RX buffers, handles XDP and AF_XDP, completes TX, constructs SQEs for normal TX, TSO, timestamping, VLAN/checksum offload, CN10K IPsec, and drains/cleans queues during teardown.

## Important APIs, Types, and Functions
Exports include `otx2_napi_handler()`, `otx2_refill_pool_ptrs()`, `otx2_sq_append_skb()`, `otx2_cleanup_rx_cqes()`, `otx2_cleanup_tx_cqes()`, `otx2_rxtx_enable()`, `otx2_free_pending_sqe()`, `otx2_xdp_sqe_add_sg()`, `otx2_read_free_sqe()`, and `otx2_xdp_sq_append_pkt()`. Internal anchors include `otx2_rx_napi_handler()`, `otx2_tx_napi_handler()`, `otx2_rcv_pkt_handler()`, `otx2_snd_pkt_handler()`, `otx2_sqe_add_hdr/ext/sg/mem()`, and TSO/PTP helpers.

## Control Flow
NAPI walks up to four CQ types per interrupt context, polls RX and TX CQ tails, processes CQEs, returns CQEs to hardware, refills pools, and re-enables interrupts if the budget is not exhausted. RX validates parser errors, optionally runs XDP, builds skb frags from SG descriptors, sets hash/checksum/mark/timestamp metadata, and submits GRO frags. TX completion unmaps DMA, returns XDP frames or AF_XDP completions, handles PTP TX timestamps, completes netdev queues, and wakes stopped queues. TX submission checks SQE space, handles software TSO fallback, maps fragments, fills descriptors, appends timestamp memory ops if needed, and flushes through LMT.

## State and Persistence
Ring state lives in `otx2_snd_queue` producer/consumer indices and SG side arrays, CQ head/tail/pend counters, page pools, AF_XDP pools, and hardware aura/pool pointers. Packet lifetime state is tracked by DMA mappings in `sg_list`, skb/xdp frame pointers, timestamp scratch buffers, and CQE invalidation fields. Hardware RX/TX enablement persists through NIX mailbox messages.

## Dependencies and Integration Points
This file consumes descriptor definitions from `otx2_struct.h`, queue definitions from `otx2_txrx.h`, hardware operations from `otx2_common.h`, PTP helpers, CN10K IPsec, XDP/XSK APIs, page pool, GRO, net DIM, DMA/IOMMU translation, and NIX register access. VF, PF, QoS, representor, and XSK modules call its exported queue functions.

## Risks and Edge Cases
SQE space accounting and SG array limits control backpressure; bugs can corrupt rings or leak DMA mappings. RX error handling must free buffers only when packets are dropped. XDP paths differ for page-pool vs AF_XDP buffers and must update `pool_ptrs` accurately. PTP one-step timestamping rewrites packet payload and may need UDP checksum repair. Software TSO stores mappings on the first SQE while completion arrives on the last segment. Cleanup paths must not race live NAPI.

## Test Signals
Run TCP/UDP/IPv4/IPv6 traffic with checksum, VLAN, TSO/GSO UDP, XDP PASS/TX/DROP/REDIRECT, AF_XDP zero-copy TX/RX, PTP RX/TX and one-step sync, IPsec offload, representor mode, queue stop/wake, RXALL error delivery, MTU extremes, interface close while traffic is active, and net DIM/adaptive interrupt coalescing.
