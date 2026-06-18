# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.c

## Purpose
`nicvf_queues.c` implements ThunderX VF queue-set resource management and packet buffer movement. It allocates coherent descriptor rings, maps receive buffers, configures RQ/SQ/CQ/RBDR hardware registers and PF mailbox routing, builds send descriptors for normal, TSO, timestamped, and XDP traffic, reconstructs SKBs from receive buffer pointers, refills RBDRs, and decodes completion errors into driver stats.

## Important APIs, Types, and Functions
Queue lifecycle entry points are `nicvf_set_qset_resources`, `nicvf_config_data_transfer`, `nicvf_qset_config`, `nicvf_cmp_queue_config`, `nicvf_sq_enable`, `nicvf_sq_disable`, `nicvf_sq_free_used_descs`, and `nicvf_config_vlan_stripping`. Data-path APIs used by `nicvf_main.c` include `nicvf_sq_append_skb`, `nicvf_xdp_sq_append_pkt`, `nicvf_xdp_sq_doorbell`, `nicvf_get_rcv_skb`, `nicvf_rbdr_task`, and `nicvf_rbdr_work`. Interrupt helpers are `nicvf_enable_intr`, `nicvf_disable_intr`, `nicvf_clear_intr`, and `nicvf_is_intr_enabled`; stats/error helpers are `nicvf_update_rq_stats`, `nicvf_update_sq_stats`, `nicvf_check_cqe_rx_errs`, and `nicvf_check_cqe_tx_errs`.

## Control Flow and Integration
On enable, `nicvf_config_data_transfer` allocates RBDR, SQ, and CQ resources, then programs SQ, CQ, RBDR, and RQ hardware in that order. SQ and RQ configuration use PF mailbox messages to route queues to completion queues and buffer rings; CQ and RBDR base addresses are written directly into VF queue registers. On disable, the order reverses: RQs are disabled and synchronized through PF, RBDRs are reclaimed, SQs are stopped/reset, CQs are reset, and coherent memory plus SKB/page state is freed.

Transmit starts by calculating required subdescriptors, reserving SQ entries, writing a header subdescriptor plus gather descriptors, mapping SKB head/frags with `dma_map_page_attrs`, and ringing the SQ doorbell after a write barrier. Software TSO builds segment headers in preallocated DMA-coherent storage; hardware TSO on T88 may add dummy CQE descriptors. Receive buffer refill uses page recycling and DMA mapping to populate RBDR entries; low-memory refill switches from tasklet atomic context to delayed work in process context.

## State and Persistence
The file maintains ring state in `struct queue_set`, `struct rbdr`, `struct snd_queue`, and `struct cmp_queue`: descriptor memory, head/tail indices, free counts, page cache entries, SKB arrays, XDP page arrays, TSO header storage, interrupt thresholds, and per-queue stats. State is volatile, reconstructed on interface open, and synchronized with hardware through queue registers, doorbells, and PF mailbox commands.

## Dependencies and Risks
The code depends on exact descriptor layouts from `q_struct.h`, queue constants and types from `nicvf_queues.h`, mailbox definitions from `nic.h`, NIC register definitions, DMA/IOMMU APIs, TSO helpers, XDP APIs, and netdev queue/BQL semantics. Risk areas are DMA unmap correctness on partial mapping failures, page reference accounting for XDP recycling, queue free-count races, endian/bitfield descriptor mismatches, RBDR reclaim edge cases when FIFO is in fail state, and the use of `virt_to_phys` in software TSO payload handling.

## Test Signals
Useful signals include stress TX/RX under small rings, fragmented SKBs, software and hardware TSO, checksum offload, VLAN stripping toggles, XDP pass/drop/tx paths, memory pressure during RBDR refill, repeated open/stop cycles, DMA mapping fault injection, queue error interrupt recovery, per-queue stats validation, and lockdep/KASAN/KCSAN runs around NAPI and tasklet/delayed-work refill.
