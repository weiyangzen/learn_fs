
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.c

## Purpose
`hinic3_rx.c` implements hinic3 receive queue allocation, page-pool backed buffer provisioning, CQE interpretation, SKB construction, checksum/VLAN/LRO metadata handling, GRO handoff, and RX polling.

## Important APIs, Types, And Functions
- `hinic3_alloc_rxqs()`/`hinic3_free_rxqs()` allocate static `struct hinic3_rxq` objects for all possible queues and initialize stats/geometric fields.
- `hinic3_alloc_rxqs_res()` allocates per-active-RQ dynamic resources: `rx_info`, coherent CQE array, page pool, and initial page fragments.
- `hinic3_configure_rxqs()` binds dynamic resources and NIC I/O RQs into live RX queue objects, associates CQEs with RQ WQEs, and posts initial buffers.
- `hinic3_rx_poll()` is the NAPI poll function for one RX queue.
- `rx_alloc_mapped_page()`, `hinic3_rx_fill_buffers()`, `hinic3_fetch_rx_buffer()`, `packaging_skb()`, `hinic3_add_rx_frag()`, and `recv_one_pkt()` implement buffer lifecycle and SKB construction.
- `hinic3_rx_csum()` interprets CQE offload status and sets `skb->ip_summed`/`csum_level`.
- `hinic3_lro_set_gso_params()` converts hardware LRO count into GSO metadata.

## Control Flow
Resource allocation first creates RX queue objects for `max_qps`, then allocates dynamic resources for configured RQs. Each RQ receives a coherent CQE array and a page pool configured for DMA-from-device fragments. `hinic3_configure_rxqs()` wires each software RXQ to the underlying RQ WQ, writes the fixed CQE DMA address into every RQ WQE, and posts page buffers by filling WQE buffer addresses and ringing the RQ doorbell.

During polling, `hinic3_rx_poll()` checks the CQE at `cons_idx & q_mask`. If `RXDONE` is not set it stops. Otherwise it reads VLAN/length after an `rmb()`, builds an SKB from one or more page-pool fragments, handles checksum/VLAN/LRO metadata, records queue id, sets protocol, and submits to GRO or `netif_receive_skb()` for frag-list packets. It clears CQE status, accounts LRO replenishment pressure, and refills buffers once `delta >= HINIC3_RX_BUFFER_WRITE`.

## State And Persistence Behavior
RX queue state is per queue and runtime-only: ring indices (`cons_idx`, `next_to_alloc`, `next_to_update`, `delta`), page-pool pages in `rx_info`, coherent CQE arrays, MSI-X/vector state, queue geometry, and DIM/coalescing fields. Page ownership transitions from page pool to hardware, then to SKB/page recycle or back to the page pool.

## Dependencies And Integration Points
The file depends on Linux netdevice, VLAN, GRO, and page-pool APIs plus `hinic3_nic_io.h` for RQ doorbells/WQ access. It integrates with NAPI through `rxq->irq_cfg->napi`, with TX/RX queue allocation orchestration through dynamic resource structs, and with hardware through CQEs and RQ WQEs.

## Risks And Edge Cases
- CQE status is the ownership/completion marker; memory ordering via `rmb()` must remain before reading packet length/offload fields.
- `hinic3_rx_fill_buffers()` posts `delta - 1` entries, preserving a ring sentinel; bad delta accounting can starve RX or overrun the ring.
- Small packets are copied into the SKB linear area and full pages are returned; larger packets become frags marked for recycle. Incorrect page clearing would double-free or leak page-pool pages.
- `hinic3_pull_tail()` assumes at least one frag for nonlinear SKBs and enough header bytes in the first frag.
- LRO path increments `num_wqe` only when `num_lro` is set; replenish threshold behavior depends on `lro_replenish_thld`.

## Test Signals
Tests should cover small/large packets, multi-fragment packets, VLAN tag insertion, RX checksum on/off and error CQEs, VXLAN checksum level, LRO/GSO metadata, RX refill under pressure, allocation failure paths, queue wraparound, and repeated open/close with page-pool destruction.
