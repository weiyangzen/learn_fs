# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.c

## Purpose

`idpf_txrx.c` is the central queue, interrupt, RSS, and split-queue datapath implementation for Intel's IDPF network driver. It owns the shared queue lifecycle used by both single-queue and split-queue modes, while delegating the actual single-queue packet fast path to `idpf_singleq_txrx.c`. The file allocates and tears down DMA descriptor rings, software buffer rings, page-pool backed RX buffers, XDP/XSK queue attachments, MSI-X/NAPI vector bindings, and RSS indirection data. It also implements splitq TX submission and completion, splitq RX cleaning, dynamic interrupt moderation, queue-pair hot switching for AF_XDP, and TX timeout reset escalation.

The implementation is tightly coupled to the virtchnl2 hardware contract. Queue model selection, descriptor IDs, queue IDs, interrupt register offsets, RSS key/LUT programming, queue enable/disable, and reset behavior all depend on control-plane messages and capabilities negotiated elsewhere in the driver.

## Important APIs and functions

Public entry points from this file include `idpf_tx_timeout()`, `idpf_rx_bufs_init_all()`, `idpf_vport_init_num_qs()`, `idpf_vport_calc_num_q_desc()`, `idpf_vport_calc_total_qs()`, `idpf_vport_calc_num_q_groups()`, `idpf_vport_queues_alloc()`, `idpf_vport_queues_rel()`, `idpf_qp_switch()`, `idpf_tx_start()`, `idpf_rx_process_skb_fields()`, `idpf_tso()`, `idpf_wait_for_sw_marker_completion()`, `idpf_vport_intr_alloc()`, `idpf_vport_intr_init()`, `idpf_vport_intr_ena()`, `idpf_vport_intr_deinit()`, `idpf_vport_intr_rel()`, `idpf_vport_intr_update_itr_ena_irq()`, `idpf_vport_intr_write_itr()`, `idpf_config_rss()`, `idpf_fill_dflt_rss_lut()`, `idpf_init_rss_lut()`, and `idpf_deinit_rss_lut()`.

Key queue lifecycle helpers include `idpf_tx_desc_alloc_all()`, `idpf_rx_desc_alloc_all()`, `idpf_tx_desc_rel_all()`, `idpf_rx_desc_rel_all()`, `idpf_txq_group_alloc()`, `idpf_rxq_group_alloc()`, and `idpf_vport_init_fast_path_txqs()`. These functions bridge high-level vport queue counts to concrete `idpf_tx_queue`, `idpf_rx_queue`, `idpf_buf_queue`, `idpf_compl_queue`, `idpf_sw_queue`, `idpf_txq_group`, and `idpf_rxq_group` instances.

Splitq TX is centered on `idpf_tx_splitq_frame()`, `idpf_tx_res_count_required()`, `idpf_tso()`, `idpf_tx_tstamp()`, `idpf_tx_splitq_get_ctx_desc()`, `idpf_tx_splitq_map()`, `idpf_tx_splitq_build_ctb()`, `idpf_tx_splitq_build_flow_desc()`, `idpf_tx_buf_hw_update()`, `idpf_tx_clean_complq()`, `idpf_tx_splitq_clean()`, and `idpf_tx_clean_bufs()`. Flow scheduling mode uses TX buffer IDs from a software refill queue; queue scheduling uses the descriptor index as the buffer index.

Splitq RX is centered on `idpf_rx_splitq_clean()`, `idpf_rx_process_skb_fields()`, `__idpf_rx_process_skb_fields()`, `idpf_rx_hash()`, `idpf_rx_csum()`, `idpf_rx_rsc()`, `idpf_rx_hwtstamp()`, `idpf_rx_hsplit_wa()`, `idpf_rx_clean_refillq()`, and `idpf_rx_clean_refillq_all()`. The file uses libeth XDP macros to run the XDP program, finalize RX, and flush XDP TX batches.

Interrupt/NAPI control is implemented by `idpf_vport_intr_alloc()`, `idpf_vport_intr_init()`, `idpf_vport_intr_map_vector_to_qs()`, `idpf_vport_intr_napi_add_all()`, `idpf_vport_intr_req_irq()`, `idpf_vport_splitq_napi_poll()`, `idpf_vport_intr_update_itr_ena_irq()`, `idpf_vport_intr_buildreg_itr()`, `idpf_net_dim()`, `idpf_tx_dim_work()`, and `idpf_rx_dim_work()`.

## Control flow

Vport queue bring-up starts from queue counts negotiated in `struct virtchnl2_create_vport`. `idpf_vport_init_num_qs()` copies TX/RX counts into `struct idpf_q_vec_rsrc`, records user-requested queue counts on initial load, accounts for splitq completion/buffer queues, and reserves XDP TX queue offsets when an XDP program is attached. `idpf_vport_calc_num_q_desc()` chooses descriptor counts from user config or defaults, and splits RX buffer queue descriptor counts across `IDPF_MAX_BUFQS_PER_RXQ_GRP` when splitq is active. `idpf_vport_calc_total_qs()` computes the actual virtchnl vport queue request, including splitq group counts, singleq fanout, and extra XDP send queues.

`idpf_vport_queues_alloc()` allocates queue groups, builds the `vport->txqs` fast-path array, obtains XDP TX queues, allocates TX descriptor and completion rings, and allocates RX descriptor and buffer rings. Errors unroll through `idpf_vport_queues_rel()`, which clears XDP programs from RX queues, releases TX/RX descriptors, returns XDP send queues, releases queue-group objects, and frees `vport->txqs`.

RX buffers are initialized separately through `idpf_rx_bufs_init_all()`. In singleq mode each RX queue creates a libeth page-pool/fill queue and posts `desc_count - 1` buffers through `idpf_rx_singleq_buf_hw_alloc_all()`. In splitq mode the buffer queues create page pools, optionally create header-split page pools, post a working set of buffer descriptors to hardware, and keep the second buffer queue on a smaller truesize derived from the first.

Interrupt bring-up is separate from queue allocation. `idpf_vport_intr_alloc()` allocates `idpf_q_vector` objects and per-vector pointer arrays sized by queue/vector fanout. `idpf_vport_intr_init()` resolves vector indexes, maps RX/TX/buffer/completion queues to vectors, adds NAPI with either splitq or singleq poll functions, calls the device-specific `intr_reg_init` callback, and requests IRQs. `idpf_vport_intr_ena()` initializes DIM, enables NAPI, programs initial ITR values, enables queue interrupts, and enables the no-IRQ writeback vector.

The splitq TX fast path begins in `idpf_tx_start()`, which validates `skb->queue_mapping`, pads too-short packets to the hardware minimum, then dispatches to `idpf_tx_splitq_frame()` or `idpf_tx_singleq_frame()`. Splitq TX counts descriptors and buffer IDs, linearizes oversized non-GSO scatter-gather packets if needed, prepares TSO and optional PTP timestamp context descriptors, checks ring/completion/refill resources, selects queue-based or flow-scheduling descriptor format, maps head and fragments to DMA, writes descriptors, updates BQL, increments pending completions, and writes the tail unless `xmit_more` allows batching.

Splitq TX completion is driven from NAPI through completion queues. `idpf_tx_clean_complq()` walks completion descriptors by generation bit, dispatches RE completions to descriptor-only cleaning, dispatches RS completions to buffer cleaning, updates per-TXQ packet/byte stats, checks completion queue overflow pressure, and wakes stopped netdev subqueues through `__netif_txq_completed_wake()` when descriptors and completion slots are available. `idpf_wait_for_sw_marker_completion()` polls a disabled TX queue's completion queue for a control-plane SW marker before queue destruction.

The splitq RX NAPI path calls `idpf_rx_splitq_clean_all()`, which fairly divides budget among RX queues and then refills all buffer queues assigned to the vector. `idpf_rx_splitq_clean()` consumes RX completion descriptors by generation bit, validates RXDID, locates the backing buffer queue and buffer ID, handles optional header split, accumulates `libeth_xdp_buff` fragments until EOP, posts used buffer IDs to the RX refill queue, runs XDP/pass-to-stack handling, and persists partially received frame state in the queue stash if budget ends mid-packet. Buffer queues are replenished by consuming software refill queues and writing new splitq buffer descriptors back to hardware in aligned strides.

Queue-pair hot switching for AF_XDP uses `idpf_qp_switch()`. It requires the RX and TX queue for `qid` to be on the same vector, builds a queue-set from all vector-associated RX, buffer, TX, completion, XDP, and XSK queues, then either initializes/configures/enables and starts the subqueue or stops the subqueue, disables IRQ/NAPI, sends virtchnl disable, cleans queues, and frees vector XSK send queue state.

RSS setup is straightforward: `idpf_init_rss_lut()` allocates the LUT if needed and fills it round-robin across active RX queues; `idpf_config_rss()` sends virtchnl messages to program key and LUT; `idpf_deinit_rss_lut()` frees the LUT.

## State and persistence behavior

Queue state is in ring pointers (`next_to_use`, `next_to_clean`, `next_to_alloc`), generation bits stored in queue flags, descriptor DMA addresses/sizes, buffer arrays, refill queues, completion counters, and stats protected by `u64_stats_sync`. This state is runtime-only and is rebuilt on vport reset, queue switch, or driver reload. The only persistence beyond queue objects is user configuration stored under `adapter->vport_config[idx]->user_config`, such as requested queue counts, descriptor counts, coalesce settings, and XDP program reference.

TX flow scheduling persists buffer ownership through a software refill queue. `idpf_tx_get_free_buf_id()` consumes buffer IDs with a software generation bit; completions call `idpf_post_buf_refill()` to return IDs. Error unwind must restore `next_to_clean` and generation state or buffer IDs leak permanently until queue reset. `num_completions_pending` and completion queue `num_completions` are monotonically compared with wrap-aware arithmetic to throttle TX when completion pressure is high.

RX splitq persists buffer ownership across RX queues, buffer queues, and refill queues. RX completion consumes a buffer ID from hardware, clears the libeth FQE `netmem` field to transfer ownership into the XDP/SKB path, posts the ID to the RX refill queue, then buffer-queue cleaning allocates replacement page-pool memory and writes a new descriptor. Header split introduces parallel header and payload page pools that must be kept in lockstep by buffer ID.

NAPI and interrupt state persists in `idpf_q_vector`: queue pointer arrays, DIM state, configured ITR values/modes, writeback-on-ITR flag, event count, and MSI-X register addresses. `wb_on_itr` deliberately changes interrupt behavior while NAPI polling is incomplete or busy-polling may continue, then is cleared when interrupts are re-enabled.

## Dependencies and integration points

The file depends on Linux networking (`net_device`, NAPI, BQL, GRO, checksum offload, RSS, SKB GSO/TSO), DMA APIs, page pool/libeth buffer abstractions, XDP and AF_XDP helper code from local `xdp.h` and `xsk.h`, PTP timestamp helpers from `idpf_ptp.h`, virtchnl2 descriptor and queue-control messages from `idpf_virtchnl.h`, hardware descriptor definitions from `idpf_lan_txrx.h` and `virtchnl2_lan_desc.h`, and device-specific register callbacks installed by PF/VF device files.

External callers include `idpf_lib.c` for vport bring-up, RSS programming, and queue/interrupt lifecycle; `idpf_ethtool.c` for queue-vector lookup and RSS/coalesce interactions; `xsk.c` for queue-pair switching; `idpf_main.c` and device init code for ops setup; and netdev ops via `.ndo_start_xmit = idpf_tx_start`.

## Risks and correctness considerations

Ring generation-bit handling is critical. Incorrect flips on RX queues, TX completion queues, TX/RX refill queues, or SW marker polling can cause stale descriptors to be treated as new, new descriptors to be ignored, permanent stalls, or buffer ID leaks. The long comment behind `IDPF_RX_BUFQ_DESC_COUNT()` explains a specific hardware overrun failure mode where too many buffer descriptors for a completion queue can make software wait forever.

Splitq flow scheduling has multiple resource domains: TX descriptors, completion queue capacity, and free buffer IDs. `idpf_tx_maybe_stop_splitq()` must consider all three, and DMA-map rollback must restore refill queue state. Any future changes to descriptor counting, TSO context descriptors, PTP timestamp descriptors, or RE descriptor spacing need to preserve those accounting rules.

RX header split has a workaround path for header-buffer overflow or parse failure. It copies a small amount of payload into the header buffer to synthesize a valid SKB layout. This path must not run on unsupported netmem-backed buffers and must adjust offsets exactly once; otherwise packets can be corrupted or dropped.

XDP/XSK integration changes queue ownership and cleanup paths. XSK queues use special init/clear/clean routines and queue-pair switching can allocate `q_vector->xsksq` dynamically. Error paths in `idpf_qp_enable()` after queue initialization may leave initialized queues if virtchnl config/enable fails, so callers must exercise disable/reset recovery paths.

Interrupt moderation and NAPI completion are race-sensitive. The writeback-on-ITR transition intentionally triggers software interrupts when leaving polling to avoid missed writebacks. Removing or reordering those writes can produce latency spikes or lost interrupts.

PTP TX timestamp slots are finite and guarded by locks. Timestamp requests are skipped for TSO and when no capability/slot exists. Completion paths must preserve the SKB until timestamp status work can consume it.

## Test signals

Useful validation signals include vport bring-up and teardown under both splitq and singleq models; queue count and descriptor count negotiation with default, user-requested, and XDP-enabled configurations; traffic with SKB frags above 16 KiB to exercise descriptor splitting; non-GSO over-scatter packets to exercise linearization; TSO TCPv4/TCPv6/UDP-L4 packets; checksum offload success and error counters; RSS LUT distribution across active RX queues; XDP pass/drop/redirect/TX and AF_XDP zero-copy queue switching; header split enabled with normal packets and forced header-buffer overflow; RSC/GRO hardware coalescing; TX timeout reset scheduling; completion queue pressure and stopped subqueue wakeups; dynamic ITR changes under traffic; PTP TX/RX timestamp paths; and fault-injection of DMA allocation/mapping failures through queue allocation and TX mapping rollback paths.
