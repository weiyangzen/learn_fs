# subset-b-004484 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_vf_dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_vf_dev.c

## Purpose

`idpf_vf_dev.c` installs the virtual-function-specific device operations for the IDPF driver. It maps VF mailbox, interrupt, reset, and IDC behavior into the generic `adapter->dev_ops` callback table used by the rest of the driver. Unlike the datapath file, this file does not allocate packet queues or process traffic; it tells shared IDPF code how to find VF hardware registers and how to trigger VF reset/control-plane behavior.

## Important APIs and functions

The exported entry point is `idpf_vf_dev_ops_init(struct idpf_adapter *adapter)`. It calls `idpf_vf_reg_ops_init()`, assigns IDC initialization, and records static VF register resource ranges.

Register callback helpers are `idpf_vf_ctlq_reg_init()`, `idpf_vf_mb_intr_reg_init()`, `idpf_vf_intr_reg_init()`, `idpf_vf_reset_reg_init()`, and `idpf_vf_trigger_reset()`. `idpf_idc_vf_register()` wraps IDC auxiliary-device registration for VF mode.

`idpf_vf_ctlq_reg_init()` fills mailbox TX/RX control queue register offsets and masks for `IDPF_CTLQ_TYPE_MAILBOX_TX` and `IDPF_CTLQ_TYPE_MAILBOX_RX`. `idpf_vf_mb_intr_reg_init()` initializes the mailbox interrupt register set from negotiated `adapter->caps.mailbox_dyn_ctl` plus VF interrupt cause masks. `idpf_vf_intr_reg_init()` maps per-vport queue-vector dynamic control and ITR registers using vector register data returned by `idpf_get_reg_intr_vecs()`. `idpf_vf_reset_reg_init()` maps the VF reset status register. `idpf_vf_trigger_reset()` sends `VIRTCHNL2_OP_RESET_VF` for function resets except during driver removal.

## Control flow

During device selection, `idpf_main.c` calls `idpf_vf_dev_ops_init()` for VF devices. That function installs VF register ops into `adapter->dev_ops.reg_ops`, installs `adapter->dev_ops.idc_init`, and sets `adapter->dev_ops.static_reg_info[0]` to the VF mailbox register window and `[1]` to the VF reset-status register window.

Later, shared control queue setup calls the installed `ctlq_reg_init` callback. The VF callback subtracts the mailbox resource start from absolute VF register constants so the control queue code can use resource-relative offsets. It fills head, tail, length, base-address high/low, enable, length, and head masks for the admin transmit and receive queues.

Mailbox interrupt setup calls `mb_intr_reg_init`, which uses the mailbox dynamic control value from capabilities and maps the VF admin-queue interrupt enable register. Vport interrupt setup calls `intr_reg_init`, which allocates temporary `idpf_vec_regs`, asks shared code for interrupt vector register offsets, validates enough registers exist for the requested queue vectors, and fills each `idpf_q_vector::intr_reg` with dynamic-control fields plus RX/TX ITR register addresses. It also configures the no-IRQ data vector used for queues that rely on writeback without normal interrupts.

Reset setup calls `reset_reg_init`, which records the VF reset status register and mask. Reset execution calls `trigger_reset`; for host-requested function reset it sends a virtchnl2 reset message unless removal is already in progress, avoiding unnecessary mailbox traffic during unload.

IDC registration calls `idpf_idc_vf_register()`, which delegates to `idpf_idc_init_aux_core_dev(adapter, IIDC_FUNCTION_TYPE_VF)` so auxiliary consumers see a VF function type.

## State and persistence behavior

This file persists VF behavior by assigning function pointers and resource ranges in `adapter->dev_ops`. The register addresses written into `adapter->mb_vector.intr_reg`, `adapter->reset_reg`, and each `idpf_q_vector::intr_reg` remain valid for the lifetime of the current hardware mapping and are consumed by shared queue, mailbox, interrupt, and reset paths.

`idpf_vf_intr_reg_init()` uses temporary heap state only for `reg_vals`; it frees it before returning. The no-IRQ dynamic-control address and enable value are stored in `struct idpf_q_vec_rsrc` so shared interrupt enable/disable code can write them later.

Reset behavior is state-sensitive: `idpf_vf_trigger_reset()` checks `IDPF_REMOVE_IN_PROG` and suppresses the reset mailbox message during unload. It does not set reset flags itself; it is a callback invoked after shared reset logic has selected a trigger cause.

## Dependencies and integration points

The file depends on `idpf.h` for adapter/vport/dev-ops structures, `idpf_lan_vf_regs.h` for VF register constants and masks, and `idpf_virtchnl.h` for virtchnl2 messaging. It integrates with shared control queue initialization, mailbox interrupt handling, vport interrupt initialization in `idpf_txrx.c`, reset handling, IDC auxiliary-device setup, and device selection in `idpf_main.c`.

`idpf_vf_intr_reg_init()` depends on shared vector helpers such as `idpf_get_reserved_vecs()`, `idpf_get_reg_intr_vecs()`, `idpf_get_reg_addr()`, and `IDPF_ITR_IDX_SPACING()`. The ITR spacing fallback is VF-specific (`IDPF_VF_ITR_IDX_SPACING`), but it uses the shared spacing macro from `idpf_txrx.h`.

## Risks and correctness considerations

Register offset mistakes are high impact. The control queue setup subtracts `static_reg_info[0].start` from mailbox registers, so incorrect resource ranges or register constants will misprogram admin queues. Interrupt register setup indexes `reg_vals` by `rsrc->q_vector_idxs[i] - IDPF_MBX_Q_VEC`; off-by-one errors around the mailbox vector or no-IRQ vector can bind queues to the wrong MSI-X register or write the wrong dynamic-control register.

`idpf_vf_intr_reg_init()` validates `num_regs < num_vecs`, but it later reads the no-IRQ vector using the loop index after processing all queue vectors. Correct operation therefore relies on `idpf_get_reserved_vecs()` and the allocated register data covering the extra reserved no-IRQ vector as well as normal data vectors.

Reset triggering must preserve unload behavior. Sending `VIRTCHNL2_OP_RESET_VF` during removal can race with mailbox teardown, while failing to send it for real host-requested resets can leave the VF wedged until a broader reset.

Because this file installs callbacks into shared ops tables, missing one callback can fail much later in generic code. VF probe coverage needs to exercise mailbox, reset, queue interrupt setup, and IDC init rather than just checking that `idpf_vf_dev_ops_init()` returns.

## Test signals

Useful validation includes VF probe and remove, mailbox control queue bring-up, mailbox interrupt delivery, vport queue interrupt allocation with multiple vector counts, no-IRQ vector programming, queue traffic under dynamic ITR, host-requested VF reset, unload while reset paths are possible, IDC auxiliary registration, and negative tests where vector register enumeration returns too few entries. Register-level tests should verify that mailbox TX/RX head/tail/length/base offsets are relative to `VF_BASE`, that reset status uses `VFGEN_RSTAT`, and that RX/TX ITR addresses honor either hardware-provided spacing or the VF fallback spacing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_vf_dev.c -->
