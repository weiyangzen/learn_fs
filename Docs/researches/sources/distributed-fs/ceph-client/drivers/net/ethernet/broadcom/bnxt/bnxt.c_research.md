# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004374`: lines 1-9569, `Docs/researches/chunks/subset-b-004374_research.md`
- `subset-b-004375`: lines 9570-17513, `Docs/researches/chunks/subset-b-004375_research.md`

## Chunk Research

### subset-b-004374: lines 1-9569

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.c lines 1-9569

## Scope

This chunk covers the first 9,569 lines of the Broadcom NetXtreme-C/E/S `bnxt` Ethernet driver implementation. The range includes the device ID table, core TX/RX fast paths, completion/NAPI handling, interrupt doorbells, RX aggregation/TPA/GRO/XDP handling, DMA ring and page-pool allocation, VNIC/filter/RSS setup, HWRM ring/resource/statistics management, interrupt coalescing, and the beginning of host backing-store/context-memory setup. Later lifecycle, probe, link, reset, ethtool, queue-management, and PCI error-recovery code appears after this chunk.

Although this source is located under a `ceph-client` source mirror, the file is Linux kernel network driver code. Its central object is `struct bnxt`, with companion state from `bnxt.h`, HSI request/response structs from `linux/bnxt/hsi.h`, and helper modules such as `bnxt_hwrm`, `bnxt_xdp`, `bnxt_ptp`, `bnxt_sriov`, `bnxt_vfr`, `bnxt_tc`, and `bnxt_devlink`.

## Purpose

`bnxt.c` is the primary data-plane and device-resource implementation for Broadcom NetXtreme adapters. In this chunk it translates Linux netdev operations into hardware descriptor rings and HWRM firmware commands:

- TX path: accepts SKBs from the networking stack, maps packet data for DMA, fills TX descriptors, handles offloads and PTP timestamp requests, rings MMIO doorbells, and frees completed SKBs.
- RX path: posts receive buffers from page pools, consumes RX and aggregation completions, builds SKBs or XDP buffers, handles checksum/VLAN/RSS metadata, performs hardware GRO/TPA completion, and delivers packets to the PF netdev or VF representors.
- Completion/interrupt path: handles MSI-X vectors, P5/P7 notification queues, legacy completion queues, HWRM completions, asynchronous firmware events, NAPI budgeting, doorbell acknowledgement, and DIM interrupt moderation sampling.
- Resource path: allocates and initializes software arrays and DMA rings for RX/TX/completion rings, VNIC attributes, RSS tables, stats buffers, filters, context/backing-store memory, and HWRM DMA pools.
- Firmware/HWRM path: registers the driver, subscribes to async events, allocates/frees hardware rings/VNICs/filter/stat contexts, reserves function resources, configures RSS/TPA/HDS/coalescing, and queries device capabilities.

## Important APIs, Types, And Data Structures

The chunk relies on driver-private types from `bnxt.h`:

- `struct bnxt`: adapter-wide state, including flags/capabilities, netdev and PCI device, ring counts/sizes, HWRM resources, VNIC/filter/RSS state, firmware health, PTP state, ULP/RDMA integration, link information, context memory, and work items.
- `struct bnxt_napi`: one NAPI context that owns a main completion or notification queue plus associated RX and/or TX rings.
- `struct bnxt_tx_ring_info`, `struct bnxt_rx_ring_info`, `struct bnxt_cp_ring_info`: software state for TX descriptor rings, RX/aggregation rings, and completion/notification rings. These hold producer/consumer indexes, DMA descriptor memory, doorbell info, firmware ring IDs, page pools, XDP/TPA state, statistics, and per-ring flags.
- `struct bnxt_ring_mem_info` and `struct bnxt_ring_struct`: generic DMA ring/page-table descriptors used for TX, RX, RX aggregation, completion, notification, and context memory.
- `struct bnxt_vnic_info`: firmware VNIC object state, including RSS contexts, RSS table/key DMA memory, multicast/unicast lists, default ring mappings, VNIC flags, and MRU.
- `struct bnxt_l2_filter` and `struct bnxt_ntuple_filter`: software and firmware filter tracking for L2 MAC/VLAN filters and RFS/ntuple filters. Filters are kept in hash tables, RCU lists, and optional user-filter lists.
- `struct bnxt_ctx_mem_info`, `struct bnxt_ctx_mem_type`, `struct bnxt_ctx_pg_info`: host backing-store metadata for firmware context memory, including entry sizes/counts, persistence flags, split-entry layouts, page-table depth, and trace-buffer bookkeeping.

Important exported or cross-file APIs in this chunk include `bnxt_xmit_get_cfa_action()`, `bnxt_sched_reset_txr()`, `bnxt_alloc_rx_data()`, `bnxt_reuse_rx_data()`, `bnxt_fw_health_readl()`, `bnxt_set_tpa_flags()`, `bnxt_set_ring_params()`, `bnxt_set_rx_skb_mode()`, `bnxt_hwrm_func_drv_rgtr()`, `bnxt_hwrm_func_drv_unrgtr()`, `bnxt_del_l2_filter()`, `bnxt_hwrm_l2_filter_alloc/free()`, `bnxt_hwrm_cfa_ntuple_filter_alloc/free()`, `bnxt_fill_ipv6_mask()`, `bnxt_set_dflt_rss_indir_tbl()`, `bnxt_get_nr_rss_ctxs()`, `bnxt_hwrm_vnic_cfg()`, `bnxt_hwrm_vnic_alloc()`, `bnxt_nq_rings_in_use()`, `bnxt_hwrm_set_ring_coal()`, `bnxt_hwrm_set_coal()`, `bnxt_copy_ctx_mem()`, and `bnxt_free_ctx_mem()`.

The static `bnxt_pci_tbl` maps Broadcom PCI IDs to `enum board_idx` values and device names in `board_info`. The module registers as a GPL Broadcom NetXtreme network driver and imports `NETDEV_INTERNAL`.

## TX Data Path

`bnxt_start_xmit()` is the core `ndo_start_xmit` implementation for this chunk. It selects the TX queue by `skb_get_queue_mapping()`, maps that queue through `bp->tx_ring_map`, and validates descriptor availability with `bnxt_tx_avail()`. If a GSO UDP L4 packet arrives on hardware without UDP GSO capability, it diverts to the software UDP GSO helper in `bnxt_gso`.

Normal TX flow is:

1. Validate fragment count, optionally linearize over-fragmented SKBs.
2. Compute VLAN metadata, CFA action from `METADATA_HW_PORT_MUX`, checksum/LSO flags, no-FCS flags, PTP timestamp flags, and large-send header/MSS fields.
3. If the ring is empty and the packet fits `bp->tx_push_thresh`, use a TX push path: copy packet bytes into a preallocated coherent push buffer, mirror descriptors into the normal ring, and write the push buffer through the doorbell BAR for low-latency small packets.
4. Otherwise pad runt packets, DMA-map skb head and fragments, fill a long TX BD plus extension BD and fragment BDs, mark packet end, update BQL with `netdev_tx_sent_queue()`, and doorbell unless `netdev_xmit_more()` allows batching.
5. On low descriptor availability, clear `NO_CMPL` if needed, kick a pending batch, and stop the netdev queue with `netif_txq_try_stop()`.

TX completion is handled by `__bnxt_tx_int()` and `bnxt_tx_int()`. The completion path walks from `tx_cons` to hardware consumer, validates that each head descriptor still has an SKB, unmaps head and fragment DMA mappings, completes software GSO maps, hands PTP timestamp SKBs to the PTP worker when needed, consumes SKBs with `napi_consume_skb()`, updates `tx_cons`, and wakes the queue with `__netif_txq_completed_wake()`. Invalid completion state triggers `bnxt_sched_reset_txr()`, logs ring indices, marks `bnapi->tx_fault`, and schedules reset work.

TX cleanup paths mirror completion logic. `bnxt_free_one_tx_ring_skbs()` drains outstanding SKBs, XDP redirect frames, push packets, DMA mappings, and software GSO state during close/reset.

## RX, XDP, Aggregation, And TPA

RX buffer allocation is page-pool based. `bnxt_alloc_rx_data()` posts either page-mode buffers from `rxr->page_pool` or skb-head fragments from `rxr->head_pool`; the chosen mode depends on XDP, MTU, aggregation, and `BNXT_FLAG_RX_PAGE_MODE`. RX aggregation buffers are netmem/page-pool objects tracked by `rx_agg_ring`, `rx_agg_bmap`, `rx_agg_prod`, and `rx_sw_agg_prod`.

Packet construction has three variants:

- `bnxt_rx_skb()` builds an SKB directly around a head-pool buffer.
- `bnxt_rx_page_skb()` builds an SKB with a page fragment and copies the Ethernet/IP head into the linear area.
- `bnxt_rx_multi_page_skb()` uses `napi_build_skb()` over a page-mode buffer for larger page-backed frames.

`bnxt_rx_pkt()` is the main RX completion parser. It validates completion pairs, handles partial aggregation completion with `-EBUSY`, checks expected opaque consumer ordering, recycles buffers on L2 errors, and then either runs XDP or builds an SKB. For XDP it initializes a `struct xdp_buff`, attaches aggregation fragments through `bnxt_rx_agg_netmems_xdp()`, and calls `bnxt_rx_xdp()`. If the XDP program passes the packet up, the code builds or copies an SKB, preserves any XDP metadata, and converts XDP frags into SKB frags.

For normal SKBs, RX metadata handling includes:

- RSS hash extraction and hash-type mapping.
- PF versus VF-representor delivery via CFA code (`bnxt_get_pkt_dev()` and `bnxt_vf_rep_rx()`).
- VLAN acceleration for both legacy and v3 RX completion formats.
- RX checksum status, encapsulation checksum level, and software error counters.
- RX hardware timestamp conversion on P5+ via PTP timecounter helpers.
- Delivery through `napi_gro_receive()` for PF packets or VF representor receive path.

Aggregation and hardware GRO/TPA add a second state machine. `bnxt_tpa_start()` moves a head buffer into a `struct bnxt_tpa_info`, records RSS/hash/header/VLAN metadata, maps P5 hardware aggregation IDs to local TPA slots, and posts replacement buffers. `bnxt_tpa_agg()` records P5 aggregation completions in the TPA slot. `bnxt_tpa_end()` reconstructs the final SKB, appends aggregation netmems, restores VLAN/checksum/hash metadata, optionally sets GRO/TSO metadata through `bnxt_gro_skb()`, and returns a complete packet. Error and OOM paths abort TPA and reuse aggregation buffers with `bnxt_reuse_rx_agg_bufs()`.

`bnxt_force_rx_discard()` supports netpoll on combined rings by marking RX completions as errored so `bnxt_rx_pkt()` recycles buffers without delivering packets.

## Completion, Interrupt, And Async Event Flow

Doorbell helpers abstract pre-P5, P5+, and P7 differences. `bnxt_db_nq()`, `bnxt_db_nq_arm()`, and `bnxt_db_cq()` choose 32-bit completion doorbells or 64-bit notification/completion doorbells with P7 epoch/valid handling configured by `bnxt_set_db()` and `bnxt_set_db_mask()`.

`bnxt_msix()` is intentionally small: it increments the completion event counter, prefetches the next descriptor, and schedules NAPI. Actual work happens in polling:

- `__bnxt_poll_work()` consumes TX, RX, HWRM done, forwarded requests, and async event completions from a completion ring. It updates event flags, handles partial RX completions, counts OOM as budget work to prevent endless loops, flushes XDP redirects, and rings TX doorbells for XDP TX events.
- `bnxt_poll_work()` acknowledges the completion ring before returning RX buffers to avoid overflowing the completion ring, then posts updated RX/aggregation producers.
- `bnxt_poll()` is the non-P5 NAPI poller and arms the completion queue when work is complete. It also feeds DIM samples when enabled.
- `bnxt_poll_p5()` handles P5/P7 notification queues (`NQ`) that point at sub-completion queues. It tracks `had_nqe_notify`, toggles, and `has_more_work`, polls each notified CQ, and uses 64-bit NQ/CQ doorbells.
- `bnxt_poll_nitroa0()` is a special Nitro A0 path that discards RX packets while still recycling buffers on a special ring.

`bnxt_hwrm_handler()` demultiplexes HWRM completions. Done completions update HWRM tokens; forwarded VF requests validate source VF IDs and schedule PF service work; async event completions flow to `bnxt_async_event_process()`.

`bnxt_async_event_process()` is a major integration point with firmware. It handles link speed/config/status changes, PF unload, port-module events, VF configuration changes, firmware reset notifications, error-recovery watchdog configuration, debug notifications, ring monitor resets, echo requests, PPS timestamps, thermal/error reports, PHC RTC updates, deferred HWRM responses, and backing-store trace buffer producer notifications. Many events set bits in `bp->sp_event` and queue the special work item via `__bnxt_queue_sp_work()`, while all events are also offered to ULPs through `bnxt_ulp_async_events()`.

## Memory, Ring, And Buffer Lifecycle

`bnxt_set_ring_params()` computes ring page counts, masks, RX buffer sizes, RX aggregation ring sizing, completion ring sizing, jumbo/TPA/HDS flags, and TX ring masks from MTU, feature flags, and configured ring sizes. It constrains jumbo-enabled RX ring sizes and completion pages to hardware limits.

`bnxt_alloc_mem()` is the main software allocation orchestrator for this chunk. On IRQ reinitialization it allocates NAPI contexts, RX/TX rings, TX ring maps, stats, ntuple filter tables, and VNIC containers. It then allocates completion descriptor arrays, initializes generic ring structs, allocates RX page pools and RX/aggregation rings, allocates TX rings and push/inline buffers, allocates completion/NQ/CQ rings, marks default VNIC flags, and allocates VNIC attributes. `bnxt_free_mem()` unwinds the same layers, preserving ring indices for non-IRQ reinit and fully freeing ring/VNIC/stat/NAPI arrays for IRQ reinit.

RX allocation details:

- `bnxt_alloc_rx_page_pool()` creates one page pool for aggregation/page-mode data and either reuses it or creates a separate head pool when pages are unreadable, order is nonzero, or RX head buffers are smaller than a page.
- `bnxt_alloc_rx_rings()` registers `xdp_rxq_info`, registers page-pool memory model for XDP, allocates RX and aggregation descriptor rings, and allocates TPA state when enabled.
- `bnxt_init_rx_rings()` sets page-mode offsets and initializes each RX ring, including XDP program references.

TX allocation details:

- `bnxt_alloc_tx_rings()` allocates descriptor rings, optional coherent TX push buffers, optional software UDP GSO inline buffers, queue IDs, and XDP TX locks.
- `bnxt_init_tx_rings()` computes the wake threshold and binds TX netdev queues to NAPI contexts.

Completion allocation details:

- `bnxt_alloc_cp_rings()` allocates main completion or notification rings. On P5+ it also creates per-NAPI sub-CQ arrays for RX and TX, maps RX rings to RX CQs and TX rings to TX CQs, and carries software stats pointers into subrings.
- `bnxt_init_cp_rings()` initializes firmware IDs and default RX coalescing values.

HWRM ring allocation uses `hwrm_ring_alloc_send_msg()` for NQ/CQ/TX/RX/RX_AGG rings. `bnxt_hwrm_ring_alloc()` allocates NQ or completion rings first, sets async event completion ring 0, then allocates TX rings, RX rings, P5+ sub-CQs, and aggregation rings. Freeing is ordered in reverse by `bnxt_hwrm_ring_free()`: TX, RX, aggregation, interrupt disable/synchronize, sub-CQs, and main NQ/CQ rings.

## Filters, RSS, VNICs, And Packet Steering

The chunk manages two software filter hash tables. L2 filters are keyed by destination MAC plus VLAN and protected by RCU plus `ntp_fltr_lock` when inserting/deleting. `bnxt_alloc_l2_filter()` shares existing filters by incrementing a refcount; `bnxt_alloc_new_l2_filter()` enforces uniqueness for explicit user filters. Firmware L2 allocation/free uses `HWRM_CFA_L2_FILTER_ALLOC/FREE`, optional VF target IDs, VNIC destination IDs, outermost match flags, MAC masks, and VLAN masks.

Ntuple/RFS filters are allocated under `HWRM_CFA_NTUPLE_FILTER_ALLOC`. The request is populated from `struct flow_keys` and `struct bnxt_flow_masks`, supports IPv4/IPv6, source/destination ports and masks, optional tunnel matching, drop actions, destination VNICs, RSS contexts, and RFS ring-table indexes. `bnxt_toeplitz()` computes the software-side RFS hash using the configured RSS key and enabled hash tuple types.

VNIC setup includes:

- `bnxt_alloc_vnics()` sizing default, RFS/ntuple, per-RX-ring, Nitro A0, and RSS-context VNIC needs.
- `bnxt_alloc_vnic_attributes()` allocating unicast/multicast lists, ring-group ID arrays, RSS tables, and hash keys.
- `bnxt_init_vnics()` initializing firmware IDs, copying or generating RSS hash keys, and caching `toeplitz_prefix`.
- `bnxt_hwrm_vnic_alloc/free()`, `bnxt_hwrm_vnic_ctx_alloc/free()`, and `bnxt_hwrm_vnic_cfg()` creating firmware VNIC and RSS/COS/LB context objects, setting default RX rings or ring groups, MRU, VLAN strip mode, and RoCE VNIC mode.

RSS setup differs by generation. Pre-P5 uses ring-group IDs in a fixed indirection table. P5+ writes RX ring ID plus completion ring ID pairs into a larger RSS table, potentially across multiple RSS contexts. `bnxt_hwrm_vnic_set_rss()` and `bnxt_hwrm_vnic_set_rss_p5()` program RSS hash type, hash key DMA address, table DMA address, IPsec hash support on P7, and hash-type delta include/exclude semantics.

TPA/HDS is VNIC-level firmware configuration. `bnxt_hwrm_vnic_set_tpa()` enables/disables TPA/GRO/encap-TPA, computes max aggregate segment counts from MTU and page size, sets min aggregation length, and enables tunnel TPA bits for VXLAN, VXLAN-GPE, and Geneve ports when firmware supports them. `bnxt_hwrm_vnic_set_hds()` configures jumbo placement and header-data split thresholds.

## HWRM Resources, Stats, And Coalescing

`bnxt_hwrm_func_drv_rgtr()` registers the Linux driver with firmware, reports version/OS, advertises hot reset, error recovery, master support, NPAR support, OVS 64-bit flow handles, PF VF-request forwarding, and async event subscriptions. It records `BNXT_STATE_DRV_REGISTERED` and detects IF_CHANGE support from the response. `bnxt_hwrm_func_drv_unrgtr()` clears registration.

Function resource management is split between querying, reserving, and testing resources:

- `bnxt_hwrm_get_rings()` reads current reserved rings, VNICs, RSS contexts, stats contexts, ring groups, and IRQs from `HWRM_FUNC_QCFG`.
- `bnxt_get_total_resources()` computes desired resources from current RX/TX/CP rings, aggregation, ULP/RDMA needs, VNIC count, and RSS context count.
- `bnxt_need_reserve_rings()` detects reservation drift.
- `bnxt_hwrm_reserve_pf_rings()` and `bnxt_hwrm_reserve_vf_rings()` send PF or VF resource requests.
- `__bnxt_reserve_rings()` trims ring counts to available reservations, disables LRO/aggregation fallback if needed, handles RSS table loss, and partitions ULP MSI-X/stat resources.
- `bnxt_hwrm_check_rings()` sends silent asset-test requests on newer firmware.

Stats management allocates coherent hardware stats, software accumulators, and counter masks. `bnxt_init_stats()` queries extended hardware stat masks when possible, otherwise fills generation-specific fallback masks. Port stats and extended port stats are optional for PFs. `bnxt_hwrm_stat_ctx_alloc/free()` allocates per-completion-ring firmware stats contexts and stores IDs in `grp_info`.

Coalescing support begins with `bnxt_hwrm_coal_params_qcaps()`, which reads hardware bounds and timer units for completion/NQ interrupt moderation. `bnxt_hwrm_set_coal_params()` clamps user-driver coalescing fields to hardware caps, translates microseconds to hardware timer units, sets min/max latency and DMA aggregation timers, and enables ring-idle behavior when supported. `bnxt_hwrm_set_coal()` applies RX and TX coalescing across rings, including P5+ split RX/TX CQs and NQ minimum-latency parameters.

## Context Memory And Backing Store

The chunk includes the first part of backing-store setup. This is host memory that firmware uses for contexts such as QP, SRQ, CQ, VNIC, STAT, TQM, MRAV, TIM, and P5/P7 trace buffers.

`bnxt_hwrm_func_backing_store_qcaps()` queries legacy or v2 context-memory capabilities. The v2 path iterates valid context types, records flags, entry sizes, min/max entries, instance bitmaps, entry multiples, init patterns, split-entry descriptors, and persistence/trace flags. If persistent memory remains valid and size-compatible, it is retained; otherwise `bnxt_free_one_ctx_mem()` frees it.

`bnxt_setup_ctxm_pg_tbls()` clamps requested entries to min/max/multiple constraints, computes memory size, and allocates one or more `bnxt_ctx_pg_info` page-table structures. `bnxt_alloc_ctx_pg_tbls()` supports direct pages, one-level page tables, and two-level page tables. `bnxt_init_ctx_mem()` applies firmware-specified initializer bytes to whole pages or per-entry offsets.

Legacy backing-store configuration uses `bnxt_hwrm_func_backing_store_cfg()` to write page attributes, page directories, entry counts, and split MRAV/TQM fields into `HWRM_FUNC_BACKING_STORE_CFG`. The v2 path uses `bnxt_hwrm_func_backing_store_cfg_v2()` per context type and can preserve trace-buffer offsets using `bnxt_bs_trace_avail()` and `bnxt_bs_trace_init()`. `bnxt_copy_ctx_mem()` supports debug dumping by copying context pages across instances and page-table levels.

The chunk ends inside `bnxt_alloc_ctx_mem()` immediately after TIM backing-store allocation for RDMA-capable P5+ devices. The remaining STQM/FTQM allocation and final backing-store configuration are outside this chunk.

## State And Persistence Behavior

Most state here is runtime state, but several lifetimes matter:

- Descriptor rings, completion rings, RSS tables, multicast tables, stats blocks, and HWRM request buffers are coherent DMA memory owned jointly by host and NIC until close/reset/free.
- RX page-pool pages/netmems are recycled on normal RX, explicit error paths, TPA aborts, close, and OOM recovery. The bitmap state for aggregation buffers must stay consistent with posted descriptors.
- Firmware object IDs (`fw_ring_id`, `fw_vnic_id`, `fw_rss_cos_lb_ctx`, `fw_grp_id`, `hw_stats_ctx_id`, filter IDs) persist in driver memory only while corresponding HWRM allocations remain live. Teardown sets them back to invalid IDs.
- `bp->state` bits (`BNXT_STATE_DRV_REGISTERED`, firmware reset/fatal/open/NAPI flags) coordinate workqueue, poll, reset, and HWRM behavior across threads and interrupt context.
- RSS hash keys can persist across VNIC reinitialization in `bp->rss_hash_key`; a newly generated key updates `toeplitz_prefix` for software RFS hash matching.
- User/requested filters are tracked in `usr_fltr_list` and may be kept across partial filter cleanup while transient filters are removed.
- Backing-store context memory may persist across firmware resets when firmware marks a context type with `BNXT_CTX_MEM_PERSIST` and dimensions still match.
- Firmware event and health state persists in `bp->fw_health`, including heartbeat/reset counters, reset timing windows, echo request data, and fatal/nonfatal reset counters.

Persistent adapter storage is not modified in this chunk. Tunnel port IDs, VNIC/filter/ring IDs, and context memory are firmware/runtime resources, not NVM state.

## Dependencies And Integration Points

- Linux netdev core: queue selection, BQL, `netif_txq_try_stop()`, `napi_gro_receive()`, `eth_type_trans()`, netdev feature flags, RX queue/NAPI binding, queue stats, and `netdev_update_features()`.
- PCI/DMA APIs: coherent DMA allocation, DMA map/unmap for SKBs and fragments, BAR MMIO doorbells, IRQ synchronization, and NUMA-aware page-pool placement.
- Page pool and netmem APIs: RX head/data allocation, direct recycling, unreadable netmem support, DMA sync for CPU/device, and XDP memory model registration.
- XDP/BPF: RX XDP program references, `xdp_buff` construction, fragmented XDP, XDP redirect flush, XDP TX rings, and conversion back to SKBs.
- HWRM firmware ABI: all `hwrm_req_init/send/hold/drop` calls, HSI request/response structs, ring/VNIC/filter/stat/resource/backing-store commands, and async event formats.
- PTP: TX/RX timestamp request parsing, TX timestamp completions, P5 timestamp conversion, PPS events, PHC RTC updates, and timecounter locks.
- SR-IOV and VF representors: VF PCI IDs, VF target IDs, VF forwarded requests, VF configuration-change events, VF VLAN/trust state, and CFA code routing to representor netdevs.
- RDMA/ULP: async event forwarding, ULP MSI-X/stat reservations, RoCE VNIC mode, and RDMA-driven context-memory sizing.
- DIM: NAPI completion sampling for adaptive interrupt moderation and cancellation during ring teardown.

## Risks And Sharp Edges

- Descriptor ownership and ordering are fragile. TX uses `wmb()` before doorbells, RX/completion consumption uses valid-bit checks followed by `dma_rmb()`, and completion acknowledgement is intentionally ordered before reposting buffers.
- RX opaque consumer mismatches trigger ring resets. Any bug that advances `rx_next_cons`, reuses buffers, or handles TPA start/end out of order can deadlock RX or corrupt page-pool ownership.
- Aggregation bitmap consistency is critical. `bnxt_alloc_rx_netmem()` can reuse the same software index as a consumed buffer, so the code carefully clears consumed entries before allocating replacements.
- PTP timestamp SKBs have unusual ownership. P5 non-completion timestamp handling can transfer ownership to a worker; TX error handling must mark timestamp slots as failed to avoid leaks.
- P5/P7 completion topology is different from earlier devices. Notification queues, sub-CQs, doorbell key types, CQ handles, and RSS table contents must be generated from the right chip flags.
- Firmware resources can be partially reserved. `__bnxt_reserve_rings()` mutates ring counts and feature flags after reservation; callers must recompute ring params and RSS maps when counts shrink.
- Filter lifetime spans RCU, refcounts, firmware IDs, bitmaps, and user lists. A missing ref drop, duplicate insert, or firmware-free/order mismatch can leak filters or remove a still-referenced L2 filter.
- Backing-store persistence intentionally avoids freeing some context memory unless forced. Capability changes, entry-size changes, or incorrect persistence flags can leave stale host memory configured to firmware.
- OOM paths are part of normal RX correctness. `-ENOMEM` is counted against NAPI budget to avoid endless loops; aggregation/TPA OOM must recycle all fragments exactly once.
- Netpoll discard modifies completion error fields in memory to force recycle. Any change to completion format handling must preserve this special path.

## Test And Validation Signals

- Build coverage for `bnxt.c` with relevant configs: `CONFIG_BNXT`, `CONFIG_BNXT_SRIOV`, `CONFIG_RFS_ACCEL`, `CONFIG_INET`, XDP/BPF, PTP, and page-pool/netmem support.
- Probe/open/close smoke tests should show successful HWRM driver registration, ring reservation, stats context allocation, ring allocation, VNIC allocation, RSS setup, interrupt enablement, and full teardown with invalidated firmware IDs.
- TX traffic tests should cover small TX push packets, fragmented SKBs, checksum offload, VLAN insertion, TCP GSO, UDP GSO fallback, queue stop/wake, PTP timestamp TX, and DMA-map failure injection if available.
- RX traffic tests should cover copybreak packets, page-mode packets, jumbo MTUs, RX aggregation, hardware GRO/TPA, VLAN receive offload, checksum offload, RSS hash reporting, VF representor delivery, RX timestamps, and RX ring reset paths.
- XDP tests should cover pass/drop/tx/redirect, fragmented XDP with aggregation buffers, XDP program attach/detach in page mode, and XDP redirect flush signaling from NAPI.
- Firmware async tests should exercise link change, reset notify, error recovery watchdog, echo request, PHC update, debug notification, ring monitor reset, and thermal/error report handling.
- Resource pressure tests should force trimmed ring reservations, limited MSI-X/stat contexts, disabled aggregation fallback, RSS indirection loss, VNIC allocation failures, and backing-store allocation failures.
- Filter/RFS tests should verify MAC/VLAN L2 filters, ntuple IPv4/IPv6 and tunnel filters, drop rules, RSS context destinations, VF target IDs, duplicate filter rejection, and teardown while NAPI is disabled.
- Coalescing tests should validate ethtool moderation values against hardware caps and observe DIM updating without racing ring teardown.

## Research Notes

This chunk is the driver core up to the middle of backing-store allocation. The merge lane should connect it with later code that calls these primitives from probe/open/close/reset/link/ethtool paths. In particular, later sections complete `bnxt_alloc_ctx_mem()`, implement device open/close sequencing around `bnxt_alloc_mem()` and `bnxt_hwrm_ring_alloc()`, bind netdev operations to `bnxt_start_xmit()`, handle feature changes that call `bnxt_set_ring_params()`, and perform firmware reset recovery using the state and helpers introduced here.

### subset-b-004375: lines 9570-17513

# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt.c lines 9570-17513

## Scope

This chunk covers the second half of the Broadcom NetXtreme `bnxt` Ethernet driver implementation. It starts in the firmware backing-store/crash-dump setup area and runs through firmware capability discovery, resource and VNIC setup, interrupt/NAPI management, link and PHY programming, NIC open/close, feature reconfiguration, stats, RX mode, reset and firmware health recovery, traffic-control and RFS integration, queue-management callbacks, PCI probe/remove, suspend/resume, PCI error recovery, and module registration.

The earlier part of `bnxt.c` defines many lower-level helpers used here, including ring allocation/free routines, HWRM request helpers, TX/RX datapath pieces, device event handling, memory allocation helpers, tunnel-port HWRM functions, filter helpers, XDP handlers, and several firmware registration routines. This chunk is where those primitives are assembled into the driver lifecycle exposed to PCI, netdev, ethtool, devlink, TC, RFS, PM, and AER.

## Purpose

The code in this range is the main control plane for the `bnxt` netdevice. It translates kernel lifecycle callbacks and asynchronous firmware events into HWRM commands and local state transitions. The core responsibilities are:

- Query firmware and hardware capabilities, including resource limits, PTP, debug/crash dump support, error recovery, queue profiles, link/PHY/FEC/EEE state, LED support, WoL, and flow-management capabilities.
- Allocate and configure rings, completion rings, stat contexts, VNICs, RSS contexts, TPA/LRO/GRO settings, filters, interrupts, NAPI instances, XPS mappings, and default ring reservations.
- Bring the NIC up and down through `bnxt_open()`, `bnxt_close()`, `__bnxt_open_nic()`, and `__bnxt_close_nic()`.
- Maintain link state and user-requested link settings through HWRM `PORT_PHY_QCFG` and `PORT_PHY_CFG`.
- Periodically collect stats, monitor firmware health, retry failed PHY/filter work, and run slow-path events in `bnxt_sp_task()`.
- Recover from TX timeout, RX ring faults, firmware fatal/non-fatal resets, PCI AER, suspend/resume, and shutdown.
- Register the driver with the PCI core and bind the netdev operations, queue-management operations, stats operations, XDP metadata operations, and PCI error handlers.

## Important APIs, Types, And Functions

Primary state is carried by `struct bnxt *bp`, especially these fields:

- `bp->dev`, `bp->pdev`, `bp->bar0`, `bp->bar1`, `bp->bar2`: netdevice, PCI device, and mapped device windows.
- `bp->fw_cap`, `bp->fw_dbg_cap`, `bp->flags`, `bp->rss_cap`, `bp->phy_flags`, `bp->mac_flags`: capability and mode bitfields discovered from firmware, PCI IDs, chip family, and link probing.
- `bp->hw_resc`: minimum, maximum, and reserved firmware resources for rings, VNICs, RSS contexts, stat contexts, MSIX/NQ resources, and flow records.
- `bp->link_info`, `bp->eee`, `bp->link_lock`: cached PHY/link settings, requested settings, EEE configuration, and serialized link updates.
- `bp->fw_health`: firmware heartbeat/reset counters, health registers, reset sequence, wait intervals, reliability flags, and recovery counters.
- `bp->state` and `bp->sp_event`: driver state bits and slow-path event bits used to coordinate open/close, reset, stats, link changes, filter retry, and firmware work.
- `bp->bnapi`, `bp->rx_ring`, `bp->tx_ring`, `bp->vnic_info`, `bp->irq_tbl`: runtime datapath resources managed by open/close, queue APIs, IRQ paths, and reset paths.
- `bp->net_stats_prev`, `bp->ring_drv_stats_prev`, port stats memory, and per-ring `bnxt_stats_mem`: accumulated counters preserved across closes and resets.

Firmware capability and initialization functions:

- `bnxt_hwrm_ver_get()` queries HWRM and firmware versions, command timeout limits, chip id/revision, short-command support, Kong mailbox, trusted VF support, advanced CFA flow support, and supported HWRM request lengths.
- `bnxt_hwrm_func_qcaps()` wraps `__bnxt_hwrm_func_qcaps()`, debug qcaps, queue port config, context memory allocation, and resource qcaps. It populates `fw_cap`, `flags`, `hw_resc`, PF/VF FIDs, MAC addresses, VF ranges, WoL/PTP support, and max TSO segments.
- `bnxt_hwrm_func_resc_qcaps()` reads resource min/max limits and PF VF reservation strategy. On P5-plus hardware it maps `max_msix` into NQ resources and treats max ring groups as max RX rings.
- `bnxt_hwrm_queue_qportcfg()` reads traffic-class queue IDs/profiles, filters CNP queues when RoCE is unavailable, and derives `max_tc`, `max_lltc`, `max_q`, `q_ids`, and `tc_to_qidx`.
- `bnxt_fw_init_one_p1()`, `bnxt_fw_init_one_p2()`, `bnxt_fw_init_one_p3()`, and `bnxt_fw_init_one()` are the staged firmware bring-up path used during probe and reset recovery.
- `bnxt_hwrm_error_recovery_qcfg()`, `bnxt_map_fw_health_regs()`, `bnxt_try_map_fw_health_reg()`, and `bnxt_remap_fw_health_regs()` discover and map firmware health registers for later polling and reset.
- `bnxt_alloc_crash_dump_mem()`, `bnxt_hwrm_crash_dump_mem_cfg()`, and `bnxt_free_crash_dump_mem()` allocate host DDR crash-dump backing memory and advertise it to firmware when debug qcaps allow it.

NIC resource and open/close functions:

- `bnxt_init_chip()` allocates stat contexts, rings, ring groups, default VNIC, RSS contexts, RFS VNICs, TPA settings, VF MAC state, default L2 filter, RX mask, coalescing, and Nitro A0 special VNICs.
- `bnxt_shutdown_nic()` and `bnxt_hwrm_resource_free()` unwind VNICs, rings, ring groups, stats contexts, and tunnel ports.
- `bnxt_init_nic()` initializes local ring/VNIC structures and delegates firmware allocation to `bnxt_init_chip()`.
- `bnxt_init_int_mode()`, `bnxt_setup_int_mode()`, `bnxt_change_msix()`, `bnxt_clear_int_mode()`, `bnxt_request_irq()`, and `bnxt_free_irq()` handle MSIX allocation, dynamic MSIX growth/shrink, IRQ names, affinity hints, RFS CPU rmap, TPH Steering Tag setup, and notifier teardown.
- `bnxt_init_napi()`, `bnxt_enable_napi()`, `bnxt_disable_napi()`, and `bnxt_del_napi()` bind NAPI poll functions to completion rings and ensure an RCU grace period before freeing NAPI structures.
- `__bnxt_open_nic()`, `bnxt_open_nic()`, and `bnxt_open()` reserve rings, allocate memory, initialize interrupts and hardware resources, apply link settings, enable interrupts/TX, start timers, restore RSS contexts and filters, and restart VF representors/PTP.
- `__bnxt_close_nic()`, `bnxt_close_nic()`, and `bnxt_close()` stop VF representors, disable TX, wait for slow-path and stats readers, clear RSS contexts, free HWRM resources, save stats, delete NAPI, free IRQs/memory, shut down link when allowed, and send interface-down notification to firmware.

Link, PHY, and module functions:

- `bnxt_update_link()` sends `HWRM_PORT_PHY_QCFG`, copies the full response into `link_info->phy_qcfg_resp`, updates link speed, duplex, pause, autoneg, partner advertisements, EEE, FEC, media, module status, and link-down reason, and reports carrier transitions when requested.
- `bnxt_hwrm_phy_qcaps()` and `bnxt_hwrm_mac_qcaps()` discover PHY/EEE/speed and MAC capabilities, including disabled-link detection for newer firmware.
- `bnxt_hwrm_set_link_common()`, `bnxt_hwrm_set_pause_common()`, `bnxt_hwrm_set_pause()`, `bnxt_hwrm_set_eee()`, and `bnxt_hwrm_set_link_setting()` translate requested autoneg, forced speed, PAM4/speeds2, pause, EEE, and TX LPI settings into `HWRM_PORT_PHY_CFG`.
- `bnxt_update_phy_setting()` compares requested settings against current firmware state and reissues PHY config only when link, pause, or EEE settings need correction.
- `bnxt_hwrm_shutdown_link()` forces link down on last close for single-PF cases where firmware and SR-IOV policy allow it.
- `bnxt_get_port_module_status()` reports unqualified SFP module states such as disabled TX, powerdown, or warning mode.
- `bnxt_hwrm_port_phy_read()` and `bnxt_hwrm_port_phy_write()` implement netdev MII ioctl access via HWRM MDIO read/write, including Clause 45 address decoding.

Feature, filtering, and offload functions:

- `bnxt_fix_features()` enforces driver constraints for NTUPLE/RFS, UDP GSO, LRO/GRO_HW, VLAN RX acceleration, XDP, and VF VLANs.
- `bnxt_set_features()` computes new driver flags, decides whether a full or partial reinit is required, updates TPA state in-place when possible, and clears user filters when NTUPLE is disabled.
- `bnxt_set_rx_mode()` and `bnxt_cfg_rx_mode()` maintain unicast/multicast filter lists and RX mask bits, fall back to all-multicast when multicast filter programming fails, and suppress promiscuous mode for untrusted VFs without a default VLAN.
- `bnxt_rx_flow_steer()`, `bnxt_insert_ntp_filter()`, `bnxt_lookup_ntp_filter_from_idx()`, `bnxt_del_ntp_filter()`, and `bnxt_cfg_ntp_filters()` implement accelerated RFS/ntuple filters using flow dissector keys, L2 filter references, RCU hash tables, bitmap IDs, aging, and deferred HWRM allocation.
- `bnxt_setup_tc()` integrates TC block flower offload and mqprio traffic class setup. `bnxt_setup_mq_tc()` closes and reopens the device as needed to reallocate ring resources for traffic classes.
- `bnxt_udp_tunnel_set_port()` and `bnxt_udp_tunnel_unset_port()` expose VXLAN, Geneve, and P7 VXLAN-GPE tunnel-port offload tables through `udp_tunnel_nic_info`.

Reset, health, and async work functions:

- `bnxt_timer()` is the periodic scheduler for firmware health polling, stats collection, TC flow stats, RFS filter aging/programming, PHY-setting retry, L2 filter retry, and P5 missed-IRQ checks.
- `bnxt_sp_task()` drains `bp->sp_event`: ULP restart, RFS filter work, HWRM forwarded requests, PF unload notice, periodic stats, link change, PHY update retry, module checks, TC flow stats, missed IRQ checks, echo replies, thermal notifications, RX mask retry, reset tasks, RX ring reset, firmware reset notify, and firmware exception handling.
- `bnxt_reset_task()` performs close/open reset for TX timeout or slow-path reset events. `bnxt_rx_ring_reset()` attempts targeted RX ring reset and falls back to global reset on unsupported or failed HWRM reset.
- `bnxt_fw_health_check()`, `bnxt_fw_exception()`, `bnxt_force_fw_reset()`, `bnxt_fw_reset()`, `bnxt_fw_reset_task()`, `bnxt_reset_all()`, and `bnxt_fw_reset_abort()` implement firmware fatal/non-fatal recovery as a state machine covering VF polling, firmware down polling, host/Kong/OP-TEE reset, PCI re-enable, HWRM readiness polling, device reopen, ULP restart, SR-IOV restore, health reporter updates, and abort.
- `bnxt_hwrm_if_change()` notifies firmware when the driver interface goes up/down, recovers from transient firmware errors, handles hot reset done, resource changes, capability changes, context memory freeing, DCB teardown, firmware reinitialization, IRQ mode clearing, and reservation cancellation.

PCI/netdev registration functions:

- `bnxt_init_board()` enables PCI, requests BARs, sets DMA masks, maps BAR0 and BAR4, initializes work items, locks, timers, ring sizes, and tunnel-port IDs.
- `bnxt_init_one()` is the PCI probe routine. It allocates the netdev, initializes firmware and resources in stages, maps the doorbell BAR, sets netdev feature flags, initializes MAC/PHY/rings/interrupts/devlink/TC/aux devices, selects queue management ops, registers the netdev, creates health reporters, and saves PCI state.
- `bnxt_remove_one()` unregisters the netdev, disables SR-IOV and aux devices, cancels work, unregisters devlink, frees filters, HWRM resources, PTP, hwmon, ethtool, DCB, health, PCI mappings, context memory, crash dump memory, RSS tables, stats, and the netdev.
- `bnxt_shutdown()`, `bnxt_suspend()`, and `bnxt_resume()` implement system shutdown and PM sleep transitions with netdev locking, ULP stop/start, driver unregister/register, crash-dump reconfiguration, PTP reinit, WoL state, and optional reopen.
- `bnxt_io_error_detected()`, `bnxt_io_slot_reset()`, and `bnxt_io_resume()` implement PCI error recovery and coordinate firmware reset state, device detach/attach, PCI enable/disable, context memory teardown, HWRM function reset, ring reservation, interrupt reinit, ULP restart, and SR-IOV restore.
- `bnxt_netdev_ops`, `bnxt_stat_ops`, `bnxt_queue_mgmt_ops`, `bnxt_pci_driver`, `bnxt_init()`, and `bnxt_exit()` bind these routines to kernel subsystems.

## Control Flow

Probe begins at `bnxt_init_one()`. It rejects PCI bridges and devices without MSIX, clears stale DMA after kdump, allocates the netdev with enough TX/RX queues for the PCI MSIX table, marks VF devices, and calls `bnxt_init_board()` to enable PCI, request regions, configure DMA, map BARs, and initialize timers/work. Firmware phase 1 then queries HWRM versions and resets the function. Firmware phase 2 queries capabilities, error recovery, driver registration, crash-dump memory, VNIC/LED/ethtool/PTP/DCB/hwmon capabilities, and queue profiles. After the doorbell BAR is mapped, probe sets netdev feature masks, initializes MAC and PHY settings, builds filter tables, ring parameters, aux devices, default ring reservations, coalescing, interrupts, TC/devlink, queue management ops, and finally registers the netdev.

Open begins at `bnxt_open()`. It first recovers from an aborted firmware reset if needed, sends the firmware interface-up notification through `bnxt_hwrm_if_change()`, then calls `__bnxt_open_nic()`. The open path reserves rings, allocates ring/VNIC memory, creates NAPI, requests IRQs, allocates HWRM rings/groups/VNICs/filters, enables NAPI, applies PHY settings, resets tunnel port notifications and XPS mappings, enables interrupts/TX, starts the timer, polls link/module status, restores VF representors, PTP timestamp filters, RSS contexts, and user filters.

Close runs through `bnxt_close()`, which calls `bnxt_close_nic()`, optionally forces link down, and sends interface-down to firmware. `__bnxt_close_nic()` stops VF representors, marks TX rings closing, drops carrier, waits for slow-path/stats readers, clears multi-RSS contexts, frees HWRM resources, exits debug support, disables NAPI, deletes the timer, saves ring stats, frees IRQ/NAPI state, and frees memory. It preserves accumulated stats and enough configuration state to reopen with the same user-facing settings.

Link updates are serialized by `bp->link_lock`. Events enqueue `BNXT_LINK_CHNG_SP_EVENT`, and `bnxt_sp_task()` optionally refreshes speed capabilities, calls `bnxt_update_link()`, and refreshes ethtool link settings after firmware link-config changes. `bnxt_update_link()` is also called during open and module checks. If firmware reports that advertised speeds are no longer supported, it trims the advertisement mask and reissues link settings.

Feature changes enter through `bnxt_set_features()`. The function computes new driver mode flags from netdev features, decides whether TPA can be toggled in-place or the NIC must close/reopen, and performs a full IRQ reinit for NTUPLE changes because those alter VNIC/RSS resources. MTU and MAC address changes also close/reopen when the device is running.

The timer and slow-path workqueue split fast periodic checks from work that may sleep or issue HWRM commands. `bnxt_timer()` only enqueues work when the device is open and interrupts are not administratively disabled. `bnxt_sp_task()` then handles stats HWRM requests, link events, RFS aging, RX mask retry, firmware event replies, and reset requests. Some slow-path handlers temporarily drop `BNXT_STATE_IN_SP_TASK` before taking the netdev instance lock so close can wait safely without deadlock.

Firmware reset has a multi-stage state machine. Health polling or firmware events set fatal/non-fatal condition bits and schedule reset. The reset path stops ULPs, sets `BNXT_STATE_IN_FW_RESET`, closes the NIC, waits for registered VFs when necessary, optionally polls firmware shutdown, triggers a host, Kong, or OP-TEE reset, re-enables PCI, polls HWRM readiness, reopens via `bnxt_open()`, restarts ULPs/SR-IOV/VF representors, reapplies PTP PPS, and updates devlink health state. Abort paths clear reset state, mark abort, close the netdev, and may defer recovery until the next open.

Queue-management callbacks provide live RX queue replacement for the netdev queue API. `bnxt_queue_mem_alloc()` clones and allocates an RX ring with a requested page size. `bnxt_queue_stop()` disables VNIC MRU use of the RX ring, frees the HWRM RX/agg rings, disables direct page-pool recycling, stops shared TX if needed, disables NAPI after ring-free completions, and snapshots ring state into the queue memory. `bnxt_queue_start()` copies the clone into the active ring, reallocates HWRM rings, arms doorbells/NQ, re-enables page pools and NAPI, restarts shared TX, and restores VNIC/RSS-context MRUs.

## State And Persistence Behavior

Driver state persists primarily in `bp` across netdev opens. User-visible feature choices, requested link settings, ring counts, coalescing defaults, WoL state, RSS hash configuration, traffic-class counts, and filter lists are kept in memory and reapplied after close/open or firmware reset. Probe and firmware reinitialization rebuild firmware-facing resources from this cached state.

`bp->state` is the central concurrency guard. `BNXT_STATE_OPEN` gates datapath and timer work. `BNXT_STATE_NAPI_DISABLED`, `BNXT_STATE_HALF_OPEN`, `BNXT_STATE_IN_SP_TASK`, `BNXT_STATE_READ_STATS`, `BNXT_STATE_IN_FW_RESET`, `BNXT_STATE_ABORT_ERR`, `BNXT_STATE_FW_RESET_DET`, `BNXT_STATE_L2_FILTER_RETRY`, `BNXT_STATE_FW_FATAL_COND`, `BNXT_STATE_FW_NON_FATAL_COND`, and PCI channel state bits coordinate asynchronous close, stats reads, NAPI state, resets, and retries. Memory barriers around state transitions ensure close sees in-progress stats or slow-path work before freeing shared structures.

Firmware capabilities and resource limits are reloaded after probe, firmware reset, resume, and PCI error recovery. `bnxt_clear_reservations()` resets reservation counters and sometimes ring counts, while `bnxt_cancel_reservations()` refreshes qcaps and clears reservation state. New resource-manager firmware requires explicit reservation state; older firmware paths often derive availability directly from max limits.

Statistics are accumulated to survive hardware counter wrap and device close. `bnxt_accumulate_all_stats()` folds DMA hardware stats into software counters, with a P5-plus workaround that ignores intermittent zero counter reads. Before shutdown with IRQ reinit, `__bnxt_close_nic()` saves netdev and ring driver stats into `net_stats_prev` and `ring_drv_stats_prev`; later `bnxt_get_stats64()` adds current live stats to the saved base or returns the saved base when closed.

Link state is cached in `bp->link_info` and `bp->eee`. `bnxt_update_link()` rewrites most live fields from firmware. Requested settings such as autoneg, advertised speeds, requested forced speed, requested duplex, requested pause, and EEE settings persist in the cache and are reapplied by `bnxt_update_phy_setting()` or `bnxt_hwrm_set_link_setting()`.

Firmware health state persists in `bp->fw_health`: register locations, mapped offsets, heartbeat/reset counts, wait intervals, primary/master status, reset sequences, and reliability booleans. Register mappings are invalidated when firmware goes down and remapped after interface-up, PCI reset, or health-reg rediscovery.

Hardware state is recreated on open and reset. Rings, VNICs, RSS contexts, L2/ntuple filters, TPA, coalescing, tunnel ports, IRQ affinity hints, TPH entries, page pools, and doorbells are volatile firmware or PCI resources. The driver treats them as disposable and reconstructs them from cached `bp` fields after close/open.

## Dependencies And Integration Points

Internal driver dependencies include helper families defined earlier in `bnxt.c` or companion `bnxt_*` files:

- HWRM request helpers: `hwrm_req_init()`, `hwrm_req_send()`, `hwrm_req_hold()`, `hwrm_req_drop()`, `hwrm_req_timeout()`, `hwrm_req_flags()`, `hwrm_req_dma_slice()`, short request setup, and many generated HWRM request/response structs.
- Ring/resource helpers: `bnxt_alloc_mem()`, `bnxt_free_mem()`, `bnxt_alloc_ring()`, `bnxt_free_ring()`, HWRM ring/stat/VNIC/RSS/context/free helpers, and context memory allocation/free.
- Datapath and XDP helpers: `bnxt_start_xmit`, `bnxt_poll`, `bnxt_poll_p5`, `bnxt_xdp`, `bnxt_xdp_xmit`, RX page-pool and TPA helpers, and TX/RX skb cleanup helpers.
- Filter and TC helpers: L2 filter allocation/free, ntuple HWRM allocation/free, TC flower offload helpers, devlink health helpers, VF representor helpers, SR-IOV helpers, and aux-device/ULP helpers.
- PTP, DCB, hwmon, ethtool, devlink, debug, and firmware reporter subsystems initialized or called from this chunk.

Kernel subsystem integration points:

- `net_device_ops` for open/close, TX, stats, RX mode, MDIO ioctl, MAC/MTU changes, feature negotiation, TX timeout, SR-IOV callbacks, TC setup, RFS steering, XDP, bridge mode, and hardware timestamping.
- `netdev_stat_ops` and `netdev_queue_mgmt_ops` for per-queue stats and live queue replacement/page-size management.
- PCI driver callbacks for probe, remove, shutdown, PM sleep, SR-IOV configuration, and PCI AER.
- Workqueues, timers, NAPI, MSIX, IRQ affinity, RFS CPU rmap, page pool, XDP RXQ info, netdev locks, rtnl locking during shutdown, and RCU for ntuple filter lifetime.
- Firmware/management integration through HWRM commands for resource qcaps, function qcaps/reset/config/registration, interface change, queue qportcfg, PHY qcfg/cfg/MDIO, stats, VNIC/RSS/filter/ring operations, crash dump config, error recovery, FW reset, echo response, LED qcaps, WoL, and tunnel ports.

Hardware dependencies include PCI BAR0/BAR1/BAR4 mappings, MSIX tables and dynamic MSIX allocation, DMA mask support, P5/P7/Nitro chip differences, TPH support, firmware health registers in BAR/config/GRC windows, doorbell BAR sizing, and reset behavior during fatal PCI errors.

## Risks And Edge Cases

- Many paths assume firmware is responsive enough for HWRM. VF paths special-case `-ENODEV` when PF is unavailable, but other errors during open, close, filter programming, or reset can leave deferred retry bits or abort state that only a later open can clear.
- Firmware reset recovery is highly stateful. Incorrect ordering of `BNXT_STATE_IN_FW_RESET`, `fw_reset_state`, netdev locking, PTP seqlock handling, ULP stop/start, and PCI enable/disable can race with stats, close, PTP reads, SR-IOV, or representor operations.
- `bnxt_sp_task()` intentionally releases `BNXT_STATE_IN_SP_TASK` before taking the netdev instance lock in some paths. New slow-path work must follow that pattern when it can block behind close, otherwise close can deadlock waiting for slow-path state to clear.
- Resource reservation math differs across old RM, new RM, P5-plus, Nitro A0, shared rings, XDP rings, traffic classes, RoCE ULP reservations, aggregate RX rings, and dynamic MSIX. Off-by-one or stale reservation state can surface as open failures, broken TC setup, or missing IRQs.
- Link capability changes can silently trim user advertisement masks when firmware reports supported speeds dropped. This protects invalid configs but mutates requested link state.
- `bnxt_hwrm_shutdown_link()` does not always force link down. Multi-PF, SR-IOV, and firmware-managed link-down policy can leave physical link state under firmware or other functions' control.
- RX mode programming can partially succeed. Unicast filter programming failure on VFs may defer retry, multicast filter failure falls back to all-multicast, and promiscuous mode can be cleared for untrusted VFs even when the netdev flag is set.
- Stats reads race with close unless `BNXT_STATE_READ_STATS` and memory barriers are respected. New stats paths must either use the same guard or avoid freed ring/stat memory.
- Queue-management start/stop depends on HWRM ring-free completions being processed by NAPI before NAPI is disabled. Reordering can permit DMA into freed queue memory.
- Firmware health register mappings can be unreliable or invalidated after resets. The code downgrades reliability for GRC mappings on interface-down and remaps later; consumers must check reliability flags.
- RFS/ntuple filters combine RCU hash lookup, bitmap IDs, user-filter lists, and L2 filter references. Failure paths must drop L2 references and avoid freeing filters still reachable by RCU readers.
- TPH affinity notifiers can restart RX queues when IRQ affinity changes. This path assumes the netdev lock and queue-management restart are safe in the current device state.
- PM, shutdown, AER, firmware reset, and normal close share cleanup routines but have different PCI and firmware availability assumptions. HWRM errors in these paths may be expected and should not be handled like normal runtime failures.

## Test Signals

Strong validation signals for this chunk include:

- Probe/remove: load/unload the driver on PF and VF devices, verify BAR mappings, HWRM registration/unregistration, devlink registration, aux device lifecycle, health reporters, and no leaks after `bnxt_remove_one()`.
- Open/close: repeatedly bring the netdev up/down with PF, VF, SR-IOV enabled, XDP attached, RFS enabled, multi-RSS contexts, and TC mqprio settings. Confirm rings, VNICs, IRQs, NAPI, filters, timers, and stats survive cycles.
- Link: exercise autoneg and forced speeds, pause on/off/autoneg, EEE on/off, FEC reporting, module warning states, link down reasons, and speed capability changes. Confirm `netif_carrier_*`, `bnxt_report_link()`, and ethtool settings match HWRM state.
- Resource pressure: test limited MSIX, limited rings, RoCE reservations, dynamic MSIX growth/shrink, Nitro A0, aggregate ring disable fallback, and default ring trimming on multi-port systems.
- Feature toggles: enable/disable GRO_HW, LRO, NTUPLE, VLAN RX acceleration, UDP GSO, XDP, and MTU changes while open. Confirm the code chooses in-place TPA update versus close/open reinit correctly.
- RX mode and filters: overflow UC/MC address limits, untrusted VF promiscuous requests, PF unavailable VF filter retries, all-multicast fallback, RFS insertion/aging/deletion, and user filter restoration after reset.
- Stats: verify counter wrap handling, P5-plus zero-counter ignore behavior, saved stats across close, per-queue stats, and no use-after-free during concurrent close and stats reads.
- Firmware health: simulate heartbeat stalls, reset-counter changes, fatal firmware events, echo requests, OP-TEE reset request, reset abort, firmware readiness timeout, and successful reopen. Confirm devlink health state and ULP/SR-IOV restart behavior.
- PCI/PM: suspend/resume, shutdown with WoL, PCI AER frozen/non-fatal/permanent failure, slot reset, and resume. Confirm PCI state, context memory, reservations, interrupts, ULPs, and carrier are restored.
- Queue-management API: live RX queue stop/start with alternate page sizes on supported chips, shared-ring TX stop/start, TPH enabled, TPA enabled, aggregate rings, and failure injection in HWRM ring allocation.

## Cross-Chunk Notes

- Lower-level TX/RX datapath, memory allocation, ring helper, filter helper, HWRM wrapper, event decode, and many feature-specific helpers are defined before line 9570. This chunk depends on them but primarily covers orchestration and lifecycle.
- The file ends at line 17513, so module registration, PCI driver wiring, and netdev operation tables are complete within this chunk. The final merged per-file report should reconcile this lifecycle view with the earlier chunk's datapath and helper implementations.
