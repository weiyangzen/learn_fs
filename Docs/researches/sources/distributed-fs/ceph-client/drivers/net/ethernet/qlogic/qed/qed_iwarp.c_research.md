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
