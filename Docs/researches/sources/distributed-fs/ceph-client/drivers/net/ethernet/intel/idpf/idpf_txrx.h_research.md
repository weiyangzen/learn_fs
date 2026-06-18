# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.h

## Purpose

`idpf_txrx.h` defines the queue, interrupt, descriptor, statistics, and helper contract shared by IDPF TX/RX implementation files. It is the structural map for `idpf_txrx.c`, `idpf_singleq_txrx.c`, XDP/XSK support, ethtool queue lookup/coalescing code, and vport lifecycle code. The header encodes hardware limits, descriptor alignment rules, queue model defaults, splitq refill metadata, offload flags, and the cacheline-oriented layout of hot-path queue objects.

## Important APIs, types, and macros

Queue sizing and hardware limit macros include `IDPF_LARGE_MAX_Q`, `IDPF_MAX_Q`, `IDPF_MIN_Q`, `IDPF_MIN_TXQ_DESC`, `IDPF_MIN_RXQ_DESC`, `IDPF_MIN_TXQ_COMPLQ_DESC`, `IDPF_MAX_QIDS`, `IDPF_REQ_DESC_MULTIPLE`, `IDPF_REQ_RXQ_DESC_MULTIPLE`, `IDPF_MAX_TXQ_DESC`, `IDPF_MAX_RXQ_DESC`, `IDPF_DFLT_*_Q_DESC_COUNT`, `IDPF_RX_BUFQ_DESC_COUNT()`, `IDPF_RX_BUFQ_WORKING_SET()`, `IDPF_TX_DESC_NEEDED`, and `IDPF_TX_MAX_DESC_DATA_ALIGNED`.

Queue state helpers include `IDPF_RX_BUMP_NTC()`, `IDPF_SINGLEQ_BUMP_RING_IDX()`, `IDPF_DESC_UNUSED()`, `IDPF_TX_COMPLQ_PENDING()`, `IDPF_TX_COMPLQ_OVERFLOW_THRESH()`, `idpf_queue_set()`, `idpf_queue_clear()`, `idpf_queue_change()`, `idpf_queue_has()`, `idpf_queue_has_clear()`, and `idpf_queue_assign()`. These are central to generation-bit and flag management in the datapath.

Major data structures are `union idpf_tx_flex_desc`, `struct idpf_tx_offload_params`, `struct idpf_tx_splitq_params`, `struct idpf_vec_regs`, `struct idpf_intr_reg`, `struct idpf_q_vector`, `struct idpf_rx_queue_stats`, `struct idpf_tx_queue_stats`, `struct idpf_rx_queue`, `struct idpf_tx_queue`, `struct idpf_buf_queue`, `struct idpf_compl_queue`, `struct idpf_sw_queue`, `struct idpf_rxq_set`, `struct idpf_bufq_set`, `struct idpf_rxq_group`, and `struct idpf_txq_group`.

Inline helpers include `idpf_q_vector_to_mem()`, `idpf_size_to_txd_count()`, `idpf_tx_singleq_build_ctob()`, `idpf_tx_splitq_build_desc()`, `idpf_vport_intr_set_wb_on_itr()`, and `idpf_tx_splitq_get_free_bufs()`.

Declared cross-file APIs include queue lifecycle (`idpf_vport_queues_alloc()`, `idpf_vport_queues_rel()`, `idpf_rx_bufs_init_all()`), interrupt lifecycle (`idpf_vport_intr_alloc()`, `idpf_vport_intr_init()`, `idpf_vport_intr_ena()`, `idpf_vport_intr_deinit()`, `idpf_vport_intr_rel()`), RSS (`idpf_config_rss()`, `idpf_init_rss_lut()`, `idpf_fill_dflt_rss_lut()`, `idpf_deinit_rss_lut()`), TX/RX fast-path helpers (`idpf_tx_start()`, `idpf_tx_singleq_frame()`, `idpf_tx_res_count_required()`, `idpf_tx_drop_skb()`, `idpf_rx_process_skb_fields()`, `idpf_rx_singleq_buf_hw_alloc_all()`), ethtool queue lookup (`idpf_find_rxq_vec()`, `idpf_find_txq_vec()`), queue-pair switching (`idpf_qp_switch()`), and TSO/SW-marker helpers.

## Control flow encoded by the header

The header separates queue model concerns through shared structures. Singleq RX uses `idpf_rx_queue::rx_buf`, `pp`, `tail`, base/flex descriptor IDs, and singleq bump macros. Splitq RX uses `idpf_rxq_group::splitq`, `idpf_rxq_set`, `idpf_bufq_set`, `idpf_buf_queue`, and software refill queues to decouple RX completions from buffer posting. Splitq TX uses `idpf_txq_group::complq`, `idpf_compl_queue`, completion counters, and optional flow-scheduling refill queues.

The hot-path queue structures are arranged into cacheline groups. Read-mostly fields hold descriptor ring pointers, tail registers, queue flags, queue indexes, and static backreferences. Read-write groups hold `next_to_*` cursors, stats, refill state, DIM state, XDP stash state, and counters. Cold groups hold queue IDs, DMA metadata, sizes, and vector backreferences. The `libeth_cacheline_*_assert()` checks make layout a compile-time contract rather than a comment.

The queue flags enum is used as a common state machine across queue types. `GEN_CHK` tracks descriptor generation bits for splitq rings, `RFL_GEN_CHK` tracks software refill generation state, `FLOW_SCH_EN` selects flow scheduling, `SW_MARKER` tracks queue-disable marker completion, `CRC_EN`, `RSC_EN`, `HSPLIT_EN`, and `PTP` enable optional offloads, `NOIRQ` marks polling-only queues, and `XDP`/`XSK` redirect queue cleanup and allocation paths.

Descriptor-building helpers establish the TX data path contract. Singleq descriptors are built as a packed 64-bit command/tag/offset/size value. Splitq descriptors dispatch to queue-based or flow-based builders depending on `params->dtype`. The size helper assumes large TX fragments must be split into 12 KiB chunks after accounting for 4 KiB read request alignment.

## State and persistence behavior

The header does not persist state by itself, but it defines all in-memory runtime state used by the datapath. Persistent-in-practice fields across a queue's lifetime include descriptor DMA addresses, descriptor counts, queue IDs, hardware tail pointers, page pools, XDP/XSK pool references, queue flags, completion counters, and NAPI/DIM state. These are allocated during vport bring-up or queue-pair enable, updated in NAPI/TX paths, and destroyed on queue teardown or reset.

State encoded in macros is also part of the persistence contract. `IDPF_TX_COMPLQ_PENDING()` implements wrap-aware arithmetic between producer-side pending completion counts and completion-queue completions. `IDPF_RX_BUFQ_DESC_COUNT()` prevents a hardware-visible RX buffer/completion mismatch that can otherwise permanently lose buffers. `IDPF_DESC_UNUSED()` leaves one descriptor empty to distinguish full and empty rings.

## Dependencies and integration points

The header depends on Linux DIM, TCP/GSO helpers, XDP types, netdev queue APIs, libeth cache/type abstractions, IDPF LAN descriptor headers, and virtchnl2 descriptor definitions. It is included by the main IDPF driver headers and implementation files that need queue structures or datapath helpers. It exports APIs consumed by `idpf_lib.c`, `idpf_ethtool.c`, `idpf_singleq_txrx.c`, `xdp.c`, `xsk.c`, and device setup paths.

The layout is integrated with kernel cacheline assertions and therefore changes to structure fields can break compilation if the hot/cold grouping expectations are violated. Queue structures also embed libeth and kernel objects (`xdp_rxq_info`, `page_pool`, `napi_struct`, `dim`, `u64_stats_sync`) whose lifecycle must match the implementation.

## Risks and correctness considerations

The largest risk in this header is that constants and structure layout encode hardware assumptions. Changing descriptor counts, buffer queue ratios, completion queue overflow thresholds, or descriptor size helpers without matching firmware/hardware behavior can create data loss or hard queue stalls. The RX buffer queue count macro is explicitly documented as preventing completion ring overrun and permanent buffer loss.

Queue flags are shared across different queue object types. Adding a flag or reusing a flag with queue-specific semantics requires auditing every `idpf_queue_has()` call, because the same bitmap helpers are used for TX queues, RX queues, buffer queues, completion queues, and software refill queues.

The unions inside `idpf_rx_queue` and `idpf_tx_queue` depend on queue mode and queue type. Code that reads a union member must first establish whether the queue is singleq, splitq, XDP, or XSK. Incorrect assumptions can turn a valid pointer for one mode into invalid state for another.

Cacheline assertions are useful test signals but also create maintenance friction. Any field movement should be intentional, measured, and compiled across relevant configurations, especially with `CONFIG_PTP_1588_CLOCK`, XDP, and AF_XDP enabled.

## Test signals

Compile coverage should include splitq, singleq, XDP, AF_XDP, and PTP timestamp configurations. Runtime tests should validate queue bring-up with minimum, default, and maximum descriptor counts; queue count negotiation up to `IDPF_LARGE_MAX_Q`; RX buffer queue sizing when two buffer queues are active; TX fragment splitting for fragments larger than 16 KiB; completion queue wrap handling; dynamic interrupt moderation state; XDP/XSK queue layout; ethtool per-queue coalescing lookup; and teardown paths that free page pools, DMA rings, XSK pools, and NAPI vectors without leaks.
