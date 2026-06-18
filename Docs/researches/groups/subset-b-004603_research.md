# subset-b-004603 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.c

## Purpose

`qed_iwarp.c` implements the QED slowpath support for iWARP RDMA over TCP. It configures iWARP device limits and parser hardware, creates and destroys iWARP queue pairs, manages active and passive TCP/MPA connection setup, handles listen/accept/reject flows, aligns unaligned MPA FPDUs through LL2 loopback queues, and translates firmware async events into upper-layer RDMA connection-manager callbacks.

The file is hardware-facing. Most externally visible operations build firmware "ramrod" commands with `qed_sp_init_request()` and `qed_spq_post()`, while local driver state tracks endpoint objects, preallocated passive TCP CIDs, MPA private-data buffers, listener lists, and partial FPDU alignment state.

## Important APIs, types, and functions

- `qed_iwarp_init_devinfo()` overrides RDMA device limits with iWARP-specific inline size, QP/CQ counts, and default ORD/IRD resources.
- `qed_iwarp_init_hw()` enables TCP search in the parser for RDMA traffic.
- `qed_iwarp_init_fw_ramrod()` fills iWARP init ramrod fields including LL2 OOO queue index and TCP timers.
- `qed_iwarp_alloc()` allocates the passive TCP CID bitmap, initializes endpoint free-list state, preallocates passive endpoints, and allocates OOO support.
- `qed_iwarp_setup()` initializes iWARP runtime policy, registers the async event callback, sets up OOO, and starts the three LL2 connections used by iWARP.
- `qed_iwarp_stop()` drains preallocated endpoints, waits for TCP and regular CIDs to be cleaned by firmware, then stops LL2 connections.
- `qed_iwarp_resc_free()` releases OOO state, bitmaps, MPA buffers, partial FPDU state, and the intermediate copy buffer.
- `qed_iwarp_create_qp()`, `qed_iwarp_modify_qp()`, `qed_iwarp_destroy_qp()`, `qed_iwarp_fw_destroy()`, and `qed_iwarp_query_qp()` implement QP lifecycle and state translation against the RDMA core's RoCE-oriented state model.
- `qed_iwarp_connect()`, `qed_iwarp_create_listen()`, `qed_iwarp_destroy_listen()`, `qed_iwarp_accept()`, `qed_iwarp_reject()`, and `qed_iwarp_send_rtr()` are the connection-manager entry points used by the RDMA upper layer.
- Static helpers such as `qed_iwarp_tcp_offload()`, `qed_iwarp_mpa_offload()`, `qed_iwarp_mpa_received()`, `qed_iwarp_mpa_complete()`, and `qed_iwarp_async_event()` bridge between endpoint state, firmware completions, and upper-layer callbacks.

The implementation relies heavily on structures declared in `qed_iwarp.h`: `struct qed_iwarp_info`, `struct qed_iwarp_ep`, `struct qed_iwarp_listener`, `struct qed_iwarp_ll2_buff`, `struct qed_iwarp_ll2_mpa_buf`, and `struct qed_iwarp_fpdu`.

## Control flow

Initialization starts with allocation through `qed_iwarp_alloc()`. During initial preallocation, `qed_iwarp_prealloc_ep(init=true)` allocates endpoint objects and full protocol CIDs, then mirrors the low preallocated range into `tcp_cid_map` for passive SYN processing. `qed_iwarp_setup()` later sets receive-window defaults based on chip and port count, enables CRC and enhanced MPA negotiation, initializes locks and lists, registers `qed_iwarp_async_event()`, and starts LL2 resources through `qed_iwarp_ll2_start()`.

Active connection setup begins in `qed_iwarp_connect()`. The function validates ORD/IRD, allocates a CID and endpoint, links the endpoint to the QP, copies MAC and CM tuple data, prepares MPA v2 private data through `qed_iwarp_mpa_v2_set_private()`, clamps MSS to firmware limits, stores the callback, and posts `IWARP_RAMROD_CMD_ID_TCP_OFFLOAD`. The active TCP completion later arrives as `IWARP_EVENT_TYPE_ASYNC_CONNECT_COMPLETE`; `qed_iwarp_connect_complete()` either posts MPA offload or reports a TCP failure.

Passive connection setup is driven by LL2 SYN receive completion. `qed_iwarp_ll2_comp_syn_pkt()` validates LL2 errors and TCP checksum flags, parses Ethernet/VLAN/IP/TCP fields using `qed_iwarp_parse_rx_pkt()`, finds a listener with `qed_iwarp_get_listener()`, rejects duplicate active endpoints with `qed_iwarp_ep_exists()`, pulls a preallocated endpoint from the free list, records SYN buffer metadata, and posts TCP offload. On passive TCP completion, `qed_iwarp_connect_complete()` reposts the SYN buffer and either calls `qed_iwarp_mpa_received()` or returns the endpoint to the free list on failure.

MPA negotiation has separate active and passive paths. Passive requests are parsed by `qed_iwarp_mpa_received()`, which extracts MPA v2 ORD/IRD and RTR fields from private data, clamps resource requests to defaults, strips the MPA v2 header before calling the upper-layer `QED_IWARP_EVENT_MPA_REQUEST`, and moves the endpoint to `QED_IWARP_EP_MPA_REQ_RCVD`. `qed_iwarp_accept()` negotiates final ORD/IRD values, may preallocate a replacement passive endpoint, attaches the QP, writes outgoing private data, and calls `qed_iwarp_mpa_offload()`. `qed_iwarp_reject()` uses the same MPA offload helper with no QP, causing a reject ramrod. Active replies are parsed by `qed_iwarp_mpa_reply_arrived()` or by `qed_iwarp_mpa_complete()` if the reply was not processed before handshake completion.

QP state changes are serialized by `iwarp.qp_lock` in `qed_iwarp_modify_qp()`. Legal transitions include IDLE to RTS or ERROR, RTS to CLOSING or ERROR, ERROR back to IDLE for reuse, and terminal/closing transitions. Non-internal transitions that require hardware state changes call `qed_iwarp_modify_fw()` after dropping the lock. Destroy waits up to roughly 20 seconds for an associated endpoint to reach `QED_IWARP_EP_CLOSED`, destroys the endpoint, posts QP destroy, and frees the shared queue page.

MPA unaligned packet handling uses the LL2 MPA connection. `qed_iwarp_ll2_comp_mpa_pkt()` records opaque firmware metadata, computes payload offsets, moves an `mpa_buf` into the pending list, and calls `qed_iwarp_process_pending_pkts()`. `qed_iwarp_process_mpa_pkt()` classifies each FPDU as packed, partial, or unaligned, stores partial data in `partial_fpdus[cid - proto_start]`, copies split FPDUs through `mpa_intermediate_buf` when necessary, and sends aligned loopback packets using `qed_iwarp_send_fpdu()` or right-edge packets using `qed_iwarp_win_right_edge()`. TX completions repost recycled RX buffers and resume pending processing.

Firmware async events are centralized in `qed_iwarp_async_event()`. It reconstructs an endpoint pointer from the firmware async handle, validates it with a signature, and dispatches connect completion, exception, QP error, enhanced MPA reply, MPA handshake completion, CID cleanup, SRQ empty/limit, and CQ overflow events. Most connection-affiliated events call the endpoint callback; SRQ/CQ events use the registered RDMA affiliated event callbacks.

## State and persistence behavior

State is in memory only and is tied to a `struct qed_hwfn`. There is no persistent disk state. The principal state containers are:

- `p_rdma_info->iwarp.ep_list`, `ep_free_list`, and `listen_list`, protected by `iwarp.iw_lock`.
- `p_rdma_info->iwarp.qp_lock`, which serializes QP state transitions that can originate from upper-layer calls and firmware events.
- `p_rdma_info->tcp_cid_map` and `cid_map`, protected by `p_rdma_info->lock`, which track passive TCP and regular iWARP CIDs.
- Per-endpoint DMA memory `qed_iwarp_ep_memory`, containing incoming private data, outgoing private data, and firmware async output data.
- LL2 handles for SYN, OOO, and MPA alignment traffic, plus MPA buffer free/pending lists and partial FPDU records.

Endpoint state progresses through `INIT`, `MPA_REQ_RCVD`, `MPA_OFFLOADED`, `ESTABLISHED`, and `CLOSED`. The close path uses `smp_store_release()` when firmware-driven paths mark `ep->state = QED_IWARP_EP_CLOSED`, paired with `READ_ONCE()` polling in QP destroy. Endpoint pointers are passed through firmware handles, so the `QED_EP_SIG` check is the main guard against stale/corrupt async handles.

## Dependencies and integration points

This file depends on QED common context management (`qed_cxt_*`), the slowpath queue (`qed_sp_*`), LL2 (`qed_ll2_*`), RDMA shared structures (`qed_rdma.h`), OOO handling (`qed_ooo_*`), hardware register helpers (`qed_wr`, `qed_get_cm_pq_idx*`), DMA coherent allocation, Linux Ethernet/IP/TCP/VLAN headers, and firmware HSI types such as `iwarp_tcp_offload_ramrod_data`, `iwarp_mpa_offload_ramrod_data`, and async event codes.

Externally, it integrates with the RDMA upper layer through `iwarp_event_handler` callbacks and `qed_iwarp_*` entry points exposed from `qed_iwarp.h`. It also integrates with the firmware event ring via `qed_spq_register_async_cb(PROTOCOLID_IWARP, qed_iwarp_async_event)`, with LL2 for SYN interception and MPA alignment, and with the parser via `PRS_REG_SEARCH_TCP`.

## Risks and edge cases

- Passive SYN processing relies on preallocated endpoints and TCP CIDs to avoid allocation in the LL2 completion path. Exhaustion drops or reposts packets and can prevent passive connection establishment.
- Endpoint lifetime is sensitive because firmware async events carry raw endpoint pointers. The signature check helps, but use-after-free risk depends on teardown ordering and delayed firmware events.
- `qed_iwarp_destroy_qp()` waits for endpoint close using a bounded sleep loop. Timeout logs a notice and proceeds to destroy the endpoint, which can be risky if firmware later references it.
- MPA private data lengths are derived from firmware-provided ULP lengths minus local MPA v2 header size. Corrupt or unexpected lengths could underflow without additional explicit bounds checks in this file.
- MPA unaligned handling performs in-place copying through a shared intermediate buffer and uses LL2 drop/loopback TX completions to recycle buffers. Bugs here can leak RX buffers, stall pending packets, or corrupt FPDU alignment.
- CID cleanup waits for bitmap progress and returns success immediately during device recovery. Normal-stop failures can leave resources uncleared.
- `qed_iwarp_accept()` mutates `iparams->ord` and `iparams->ird` during negotiation, so callers must tolerate in/out behavior.
- Listener lookup supports wildcard IP by all-zero address and exact VLAN/IP otherwise; backlog is stored but not enforced in this file.

## Test signals

Useful validation signals include active connect success and failure cases, passive listen/accept/reject, MPA v1/v2 private-data negotiation, ORD/IRD clamping, RTR negotiation paths, duplicate SYN handling, listener miss loopback behavior, QP state transition rejection, QP destroy while firmware close is pending, CID bitmap cleanup on stop, SRQ/CQ async event delivery, LL2 SYN checksum/error handling, and unaligned MPA FPDU cases spanning one, two, and more than two TCP segments. Recovery-mode stop should also be covered because CID wait semantics change when `recov_in_prog` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.h

## Purpose

`qed_iwarp.h` is the internal iWARP contract for the QED driver. It defines the in-memory iWARP state machine, endpoint/listener structures, LL2 buffer tracking structures, partial FPDU alignment state, and the function prototypes consumed by the RDMA setup and connection-management code.

The header is not a userspace ABI. It binds `qed_iwarp.c` to the rest of the QED RDMA stack through `struct qed_hwfn`, `struct qed_rdma_qp`, `struct qed_rdma_start_in_params`, firmware HSI structures, and callback types from the RDMA interface.

## Important APIs, types, and constants

- `enum qed_iwarp_qp_state` defines the QED iWARP QP states: `IDLE`, `RTS`, `TERMINATE`, `CLOSING`, and `ERROR`.
- `qed_roce2iwarp_state()` maps the common RDMA/RoCE state vocabulary into iWARP state for shared QP handling.
- `QED_IWARP_PREALLOC_CNT` is 256, matching the passive endpoint/TCP CID reserve used by SYN processing.
- LL2 sizing constants define SYN TX/RX depth, OOO defaults, OOO maximum RX size, and invalid LL2 handle value.
- `struct qed_iwarp_ll2_buff` wraps a DMA buffer posted to LL2 and optionally chains a `piggy_buf` that should be reposted or freed with it.
- `struct qed_iwarp_ll2_mpa_buf` tracks firmware opaque unaligned-packet metadata, the LL2 buffer, TCP payload length, and placement offset while the MPA alignment path processes pending packets.
- `struct qed_iwarp_fpdu` records a partial or current FPDU's header DMA address, MPA fragment virtual/physical address, fragment length, total FPDU length, remaining incomplete bytes, and header size.
- `struct qed_iwarp_info` is the per-hwfn iWARP runtime state: listener, endpoint, free endpoint, MPA buffer lists, locks, receive-window policy, local MAC, MPA policy flags, LL2 handles, partial FPDU array, MPA buffer array, intermediate buffer, and partial-FPDU capacity.
- `enum qed_iwarp_ep_state` tracks endpoint lifecycle from `INIT` to `CLOSED`.
- `union async_output` overlays firmware MPA response and TCP async completion data in endpoint DMA memory.
- `struct qed_iwarp_ep_memory` reserves 512-byte incoming and outgoing private-data buffers plus async output storage.
- `struct qed_iwarp_ep` represents one TCP/iWARP endpoint and stores list linkage, QP association, DMA private-data memory, state, signature, CM tuple, connect mode, MPA/RTR negotiation state, CIDs, MSS, MAC addresses, passive SYN metadata, and event callback.
- `struct qed_iwarp_listener` stores listen callback context, backlog, IP address, port, VLAN, and IP version.

The exported prototypes cover allocation/setup/stop/free, firmware init, hardware init, QP create/modify/destroy/query, active connect, passive listen/accept/reject/destroy, and RTR send.

## Control flow represented by the header

The header divides iWARP behavior into three state domains. Device-level state lives in `struct qed_iwarp_info`, initialized by `qed_iwarp_alloc()` and `qed_iwarp_setup()`, and released by `qed_iwarp_stop()` plus `qed_iwarp_resc_free()`. QP-level state is represented by `enum qed_iwarp_qp_state` and manipulated through `qed_iwarp_create_qp()`, `qed_iwarp_modify_qp()`, `qed_iwarp_destroy_qp()`, and `qed_iwarp_query_qp()`. Connection-level state lives in `struct qed_iwarp_ep` and is driven by `qed_iwarp_connect()`, `qed_iwarp_create_listen()`, `qed_iwarp_accept()`, `qed_iwarp_reject()`, `qed_iwarp_destroy_listen()`, and `qed_iwarp_send_rtr()`.

The LL2 and FPDU structures expose the private machinery used by `qed_iwarp.c` to intercept passive SYNs and realign MPA traffic. The split between `qed_iwarp_ll2_buff` and `qed_iwarp_ll2_mpa_buf` allows LL2 buffer ownership to be kept separate from pending alignment metadata.

## State and persistence behavior

All declarations describe volatile kernel-driver state. There is no persistence across device teardown, module unload, or PCI reset. Runtime state is anchored below `p_hwfn->p_rdma_info->iwarp` and depends on list heads and spinlocks initialized in the implementation.

The header makes several ownership rules visible:

- Endpoint DMA memory is owned by `struct qed_iwarp_ep`.
- Listener and endpoint objects are linked into per-hwfn lists.
- Passive SYN data is retained by `struct qed_iwarp_ep` until TCP offload completion reposts the original LL2 buffer.
- Partial FPDU records are indexed by CID offset and therefore depend on CID allocation staying within `max_num_partial_fpdus`.
- The event callback and context in both listener and endpoint records are the bridge back to RDMA upper-layer code.

## Dependencies and integration points

The header depends on Linux list/spinlock/DMA types through included QED headers, firmware HSI types such as `struct unaligned_opaque_data`, `enum mpa_negotiation_mode`, `enum mpa_rtr_type`, and `enum tcp_connect_mode`, RDMA QP and connection-management structures from the QED RDMA interface, and Ethernet constants such as `ETH_ALEN`.

It is included by the iWARP implementation and by other QED RDMA setup paths that need to call iWARP allocation, setup, teardown, QP, or connection APIs.

## Risks and edge cases

- `struct qed_iwarp_ep` stores raw callback pointers and raw endpoint pointers are later passed through firmware async handles, so object lifetime and signature validation are critical.
- `QED_MAX_PRIV_DATA_LEN` is fixed at 512 bytes; callers and firmware paths must ensure private data plus MPA v2 header fit this buffer.
- `QED_IWARP_PREALLOC_CNT` fixes the passive SYN reserve. If workload or firmware assumptions change, passive connection scalability and memory consumption both change.
- Partial FPDU indexing depends on CID ranges matching `max_num_partial_fpdus`; invalid CIDs must be rejected by the implementation.
- The header exposes mutable connection information inside `struct qed_iwarp_ep`, so callback consumers must treat pointers as transient and not persistent ownership.

## Test signals

Header-level validation is mostly compile-time and integration-focused: all prototypes should match their definitions, structure fields should match firmware HSI expectations, `QED_MAX_PRIV_DATA_LEN` should be sufficient for negotiated MPA private data, endpoint state names should cover all transitions used in `qed_iwarp.c`, and LL2/FPDU structures should remain layout-compatible with the unaligned packet path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iwarp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.c

## Purpose

`qed_l2.c` implements the QED Ethernet/L2 slowpath operations. It allocates L2 queue bookkeeping, converts logical queue parameters into firmware CIDs and absolute resource IDs, starts/stops vports and RX/TX queues, updates RSS/TPA/filter modes, programs unicast/multicast/aRFS filters, reads and resets Ethernet statistics, configures tunnel ports, and publishes the `qed_eth_ops` table consumed by the upper Ethernet driver.

The file is the main bridge between the protocol-facing `linux/qed/qed_eth_if.h` operations and QED firmware ramrods. It handles both PF and VF flows, using direct SPQ ramrods for PFs and VF/PF mailbox helpers for VFs.

## Important APIs, types, and functions

- `struct qed_l2_info` holds the number of L2 queues and a per-queue-zone bitmap of queue usage indices protected by a mutex.
- `qed_l2_alloc()`, `qed_l2_setup()`, and `qed_l2_free()` allocate, initialize, and release L2 queue bookkeeping.
- `qed_eth_queue_to_cid()` and `_qed_eth_queue_to_cid()` allocate or derive firmware CIDs and fill `struct qed_queue_cid` with relative and absolute vport, queue, stats, status-block, VF, and queue-zone usage metadata.
- `qed_eth_queue_cid_release()` releases firmware CIDs for PF queues, clears queue-zone usage for self-owned queues, and frees the queue handle.
- `qed_sp_eth_vport_start()`, `qed_sp_vport_update()`, and `qed_sp_vport_stop()` build vport start/update/stop ramrods.
- `qed_eth_rxq_start_ramrod()`, `qed_eth_rx_queue_stop()`, `qed_eth_txq_start_ramrod()`, and `qed_eth_tx_queue_stop()` build queue start/stop ramrods and release queue handles on successful stop.
- `qed_sp_eth_filter_ucast()`, `qed_mcast_bin_from_mac()`, and the filter command helpers program unicast, multicast, VLAN, VNI, and accept-mode filtering.
- Statistics helpers read MSTORM, USTORM, TSTORM, PSTORM, and MCP port stats into `struct qed_eth_stats`; public functions are `qed_get_vport_stats()`, `qed_get_vport_stats_context()`, and `qed_reset_vport_stats()`.
- `qed_arfs_mode_configure()` and `qed_configure_rfs_ntuple_filter()` configure accelerated RFS search profiles and individual GFT ntuple filters.
- `qed_get_queue_coalesce()`, `qed_get_rxq_coalesce()`, and `qed_get_txq_coalesce()` read queue coalescing values from CAU and storm memories.
- `qed_get_eth_ops()` exports the `qed_eth_ops_pass` operation table.

## Control flow

L2 allocation begins with `qed_l2_alloc()`, which exits early for non-L2 personalities. PF queue count comes from `RESC_NUM(QED_L2_QUEUE)`, while VF queue count is the max of VF RX and TX queues reported by the PF. The function allocates one bitmap per queue zone, each sized for `MAX_QUEUES_PER_QZONE`. `qed_l2_setup()` initializes the mutex after allocation.

Queue start flows first allocate a queue CID. For PFs, `qed_eth_queue_to_cid()` acquires a protocol CID from context management unless the queue is a legacy VF CID. `_qed_eth_queue_to_cid()` translates relative vport and L2 queue IDs to firmware absolute IDs, handles VF-specific stats and queue metadata, and allocates a queue-zone usage index unless VF parameters already supply one. RX start initializes the PF producer GTT memory to zero before posting `ETH_RAMROD_RX_QUEUE_START`; VF RX start delegates to `qed_vf_pf_rxq_start()`. TX start posts `ETH_RAMROD_TX_QUEUE_START`, selects a PQ with `qed_get_cm_pq_idx_mcos()`, and returns a doorbell address for PF queues.

Queue stop flows post RX or TX stop ramrods for PFs or VF mailbox requests for VFs. RX stop chooses CQE and EQE completion flags based on whether the queue belongs to the PF itself, whether only EQ completion is requested, and whether CQE completion is forced. On successful stop, the queue CID is released, which also clears the queue-zone usage bit for self-owned queues.

Vport start is exposed externally by `qed_start_vport()`. It loops over hardware functions, fills `qed_sp_vport_start_params`, posts PF or VF vport start, starts fastpath hardware with `qed_hw_start_fastpath()`, and optionally resets stats. Vport update translates protocol-level flags to `qed_sp_vport_update_params`, optionally prepares per-hwfn RSS parameters, and posts one update per hwfn. In CMT mode, RSS indirection entries are split by queue owner; if an engine would use only one queue, RSS is disabled for that update.

Filtering has three main paths. Accept-mode changes build a vport update with RX/TX accept flags. Unicast filter commands translate high-level add/delete/replace to firmware filter actions, support MAC, VLAN, MAC/VLAN, inner MAC/VLAN, MAC/VNI, and VNI forms, and can emit two firmware commands for move or replace. Multicast programming hashes MACs into approximate multicast bins using CRC32C and posts a vport update; ADD is treated as setting the full bin vector while REMOVE clears it.

Statistics are gathered per hwfn. PFs acquire a PTT and read fixed storm memory offsets; VFs read addresses and lengths supplied by the PF in the acquire response. The leading PF also reads MCP public port statistics and link-change count. `qed_reset_vport_stats()` zeroes per-vport storm stats and stores a baseline snapshot for port stats that cannot necessarily be reset.

The exported operation table wires these internals into the public Ethernet interface: device info, vport start/stop/update, queue start/stop, filter configuration, fastpath stop, CQE completion, stats, tunnel configuration, ntuple/aRFS, coalescing, MAC validation, and VF bulletin MAC update.

## State and persistence behavior

State is volatile kernel and device state. `struct qed_l2_info` persists only for the lifetime of the hwfn L2 personality and tracks queue-zone usage. Each started queue returns a dynamically allocated `struct qed_queue_cid` handle that owns the firmware CID and queue-zone usage index until queue stop releases it.

Firmware/device state is mutated through SPQ ramrods and direct register or memory writes. Examples include vport active/accept/RSS/TPA/filter state, RX/TX queue state, producer initialization in MSTORM GTT memory, approximate multicast bins, GFT filter entries, tunnel port configuration, and storm statistics reset writes. No on-disk persistence exists.

The code handles multi-hwfn devices by iterating `for_each_hwfn()` and splitting queue IDs/RSS tables by `rss_num % cdev->num_hwfns`. VF state changes generally route through VF/PF helpers rather than direct firmware ramrods.

## Dependencies and integration points

This file depends on Linux DMA, CRC32C, bit operations, vmalloc, Ethernet helpers, and QED subsystems: context allocation (`qed_cxt`), slowpath queue (`qed_sp`), hardware/PTT/register access (`qed_hw`, `qed_dev_api`, `qed_reg_addr`), interrupts/status blocks (`qed_int`), MCP public data (`qed_mcp`), SR-IOV VF/PF mailbox (`qed_sriov`), DCB and PTP operation tables, tunnel configuration, and firmware HSI ramrod structures.

External integration is through `qed_get_eth_ops()` and `qed_put_eth_ops()` exports. The returned `qed_eth_ops` table is consumed by the Ethernet client driver and references shared common, IOV, DCB, and PTP operation tables when configured.

## Risks and edge cases

- `qed_l2_alloc()` can leak earlier allocations if a later queue bitmap allocation fails; cleanup is deferred to caller paths only if they call `qed_l2_free()`.
- Queue-zone usage is protected by a mutex, but invalid queue IDs or exhausted per-zone usage return failure and can prevent queue start.
- The queue start wrappers mutate `p_params->queue_id` by dividing it by `num_hwfns`; callers must not assume the original value remains intact after the call.
- RSS update silently disables RSS if the CMT split degenerates to one queue per engine, by clearing `params->update_rss_flg` after `qed_update_vport_rss()` returns an error.
- Multicast REMOVE clears the entire approximate multicast vector rather than selectively removing only supplied addresses.
- Many operations are per-hwfn loops with partial failure risk; if a later hwfn fails, earlier hwfns may already have been configured.
- VF paths rely on PF-provided resource counts, stats addresses, and mailbox helpers. Incorrect PF/VF capability negotiation can affect queue, stats, XDP, or filter behavior.
- Statistics reset stores a baseline for non-resettable port stats; consumers must understand that returned values are adjusted by `cdev->reset_stats`.
- aRFS VF filter configuration rewrites `vport_id` and `qid` when `b_is_vf` is set, so caller-provided queue targeting is intentionally ignored for VF filters.

## Test signals

Important coverage includes PF and VF L2 allocation/free, queue-zone bitmap exhaustion, RX/TX queue start and stop for PF, VF, and legacy VF modes, vport start/update/stop, GRO/TPA parameter programming, RSS table programming on single-hwfn and CMT devices, accept-mode transitions for normal/promisc/multicast-promisc, unicast add/delete/replace/move for MAC/VLAN/VNI forms, multicast bin hashing and full-vector updates, stats read/reset for PF and VF, tunnel port bulletin propagation to VFs, aRFS enable/disable and ntuple add/delete/drop, coalescing reads for RX/TX queues, and partial-failure handling across multi-hwfn loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.h

## Purpose

`qed_l2.h` declares the internal L2/Ethernet slowpath contract used by QED. It defines RSS, TPA/GRO, filter, accept-mode, vport update, aRFS, queue CID, and VF queue parameter structures, plus the internal functions used to allocate L2 state, start/stop vports and queues, program filters, collect stats, configure aRFS, and read/write queue coalescing.

The header sits between the public `linux/qed/qed_eth_if.h` interface and the driver implementation in `qed_l2.c`. It also exposes selected helpers to other QED modules such as SR-IOV and device setup.

## Important APIs, types, and constants

- `struct qed_rss_params` carries RSS update flags, engine ID, capabilities, indirection table of RX queue handles, table size log, and RSS key.
- `struct qed_sge_tpa_params` describes TPA/GRO enable flags and aggregation sizing.
- `enum qed_filter_opcode` defines add, remove, move, replace, and flush semantics.
- `enum qed_filter_ucast_type` covers MAC, VLAN, MAC/VLAN, inner variants, MAC/VNI, inner MAC/VNI, and VNI filters.
- `struct qed_filter_ucast` and `struct qed_filter_mcast` are firmware-facing filter command inputs.
- `enum qed_tpa_mode` defines no TPA, unused, GRO, and max values.
- `struct qed_sp_vport_start_params` and `struct qed_sp_vport_update_params` are the internal vport ramrod input structures.
- `struct qed_filter_accept_flags` defines RX/TX accept-mode update flags and bitmasks for matched/unmatched unicast, multicast, broadcast, any VNI, and accept-none behavior.
- `struct qed_arfs_config_params` carries aRFS protocol-family and mode configuration.
- `MAX_QUEUES_PER_QZONE` and `QED_QUEUE_CID_SELF` define queue-zone usage indexing and self-owned queue identity.
- `struct qed_queue_cid_vf_params` carries PF-side metadata needed when opening queues for VFs, including legacy behavior flags.
- `struct qed_queue_cid` is the queue handle returned to callers and passed back for queue stop, coalescing, RSS indirection, and ramrod programming.

Declared functions include L2 lifecycle (`qed_l2_alloc/setup/free`), queue CID conversion and release, vport start/update/stop, queue start/stop ramrods, unicast filtering, RX queue update, stats get/reset, aRFS mode and ntuple configuration, multicast bin hashing, and coalescing get/set helpers.

## Control flow represented by the header

The header's data model makes queue setup a two-step operation: first convert common queue parameters into a `qed_queue_cid`, then issue RX or TX queue start ramrods using that handle. The same handle is later supplied to stop and coalescing helpers and is also used in RSS indirection tables.

Vport control flows are represented by start/update/stop parameter structs. A vport can be started with MTU, VLAN stripping, TPA mode, PTP handling, TTL0 drop, TX switching, and control-frame checks. Later updates can independently change active flags, VLAN behavior, default VLAN, TX switching, multicast bins, anti-spoofing, accept-any-VLAN, RSS, accept flags, SGE/TPA parameters, and control-frame checks.

Filter flow is split between generic accept-mode flags, exact unicast-style filter commands, and approximate multicast bin vectors. aRFS flow is represented by a mode configuration struct plus ntuple filter parameters from the public Ethernet interface.

## State and persistence behavior

The header defines transient runtime structures. `struct qed_queue_cid` is the most important ownership object: it stores relative and absolute vport/queue/stats IDs, status-block identity, firmware CID, opaque FID, RX/TX direction, VF identity, queue-zone usage index, legacy VF flags, and owning hwfn. The queue handle persists while a queue is started and is released by queue stop or explicit release on failure.

RSS indirection state stores queue handles rather than queue numbers, so callers must keep those queue handles alive while RSS updates are built. Vport and filter structs are command payloads, not persistent owners. Accept/filter constants encode desired firmware state and are not durable outside device configuration.

## Dependencies and integration points

The header includes Linux type and IO headers, `linux/qed/qed_eth_if.h`, and QED core headers for `struct qed_hwfn`, hardware access, and SPQ completion types. It depends on public Ethernet constants such as `QED_RSS_IND_TABLE_SIZE`, `QED_RSS_KEY_SIZE`, `QED_MAX_MC_ADDRS` behavior, `struct qed_eth_stats`, and `struct qed_ntuple_filter_params`.

Other modules use this header when they need direct L2 queue/vport/filter helpers, especially PF-side SR-IOV code that constructs queue CIDs for VF queues and non-Linux VF support that updates RX queues.

## Risks and edge cases

- `struct qed_rss_params` stores `void *` queue handles, so type safety depends on callers passing valid `struct qed_queue_cid` handles.
- `MAX_QUEUES_PER_QZONE` is tied to one `unsigned long` worth of bits; queue-zone sharing behavior changes if firmware or platform expectations exceed that.
- VF queue CID fields are meaningful only on PF-created queue handles for VF queues, which can be misused if callers treat them as normal VF-local state.
- Filter opcode support differs by filter type; multicast explicitly does not support MOVE, while unicast supports richer move/replace behavior.
- Coalescing setters are declared here but implemented elsewhere in the QED L2/coalescing path, so users of the header must link the complete driver objects.
- Vport update uses many independent `update_*` flags; missing a flag can make a populated value a no-op, while setting an update flag with stale values can unintentionally change firmware state.

## Test signals

Header-driven integration tests should compile PF, VF, SR-IOV, DCB, and PTP configurations; validate that queue handles flow correctly through start, RSS update, coalescing, and stop; exercise vport update combinations with and without update flags; verify filter opcode/type combinations; validate multicast maximum address limits; cover legacy VF queue flags; and ensure all prototypes match the implementations used by `qed_eth_ops_pass`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_l2.h -->
