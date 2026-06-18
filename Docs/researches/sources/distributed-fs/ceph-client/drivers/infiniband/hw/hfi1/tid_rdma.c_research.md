# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.c

## Purpose

`tid_rdma.c` implements the HFI1 TID RDMA protocol for RC queue pairs. The feature converts qualifying large RDMA READ and RDMA WRITE operations into HFI1-specific TID RDMA flows so receive buffers can be programmed into the hardware expected receive array and data can move with less copy overhead. The file owns OPFN capability negotiation, per-QP private initialization, hardware TID flow allocation, receive-array programming, READ and WRITE request/response/data/ACK handlers, retry and RESYNC handling, and the TID-specific send engine.

The protocol is only used for RC QPs when the `TID_RDMA` capability is enabled and after OPFN exchange installs remote TID parameters. READ qualification is stricter than ordinary verbs RDMA: large enough, page-sized, page-aligned local SGEs. WRITE qualification checks page-aligned remote address and page-multiple length. The file falls back by leaving the WQE opcode unchanged if qualification or resource allocation fails before conversion.

## Important APIs and Functions

Negotiation and setup:

- `tid_rdma_opfn_init()`, `tid_rdma_conn_req()`, `tid_rdma_conn_reply()`, `tid_rdma_conn_resp()`, and `tid_rdma_conn_error()` encode, decode, install, or clear peer TID RDMA parameters under OPFN/RCU rules.
- `hfi1_kern_exp_rcv_init()` initializes kernel expected receive context state, sets the kernel JKEY, and allocates context receive groups.
- `hfi1_qp_priv_init()` and `hfi1_qp_priv_tid_free()` allocate and release per-WQE and per-ACK-entry TID private storage, timers, queues, per-QP page scratch space, and flow arrays.
- `setup_tid_rdma_wqe()` converts eligible verbs WQEs to `IB_WR_TID_RDMA_READ` or `IB_WR_TID_RDMA_WRITE`, initializes segment counts, flow windows, and PSN ranges.

Expected receive and hardware resource management:

- `hfi1_kern_setup_hw_flow()` and `hfi1_kern_clear_hw_flow()` reserve per-context hardware flow entries, program `RCV_TID_FLOW_TABLE`, manage flow generation numbers, and wake queued QPs.
- `hfi1_kern_exp_rcv_setup()` maps one request segment into page sets, reserves TID groups, programs RcvArray entries, builds TID entries sent to the peer, and advances the request flow circular buffer.
- `hfi1_kern_exp_rcv_clear()` and `hfi1_kern_exp_rcv_clear_all()` unprogram TID groups, unmap DMA pages, reset flow state, and wake waiters.
- `hfi1_qp_kern_exp_rcv_clear_all()`, `hfi1_kern_read_tid_flow_free()`, and `__trdma_clean_swqe()` are cleanup entry points for QP teardown, retry flushing, and WQE cleanup.

READ protocol:

- `hfi1_build_tid_rdma_read_req()` allocates local expected receive resources and builds the READ request header plus TID-entry payload.
- `hfi1_rc_rcv_tid_rdma_read_req()` validates an incoming TID READ request, inserts it into `s_ack_queue`, validates rkey/access, records peer TID flow info, and schedules response sending.
- `hfi1_build_tid_rdma_read_resp()` sends data into the requester's advertised TID entries.
- `hfi1_rc_rcv_tid_rdma_read_resp()` consumes READ responses, performs ACK processing, handles eager fallback for FECN/RSM cases, clears local expected receive resources, and completes or advances the request.

WRITE protocol:

- `hfi1_build_tid_rdma_write_req()` sends a TID WRITE request and waits for responder TID entries.
- `hfi1_rc_rcv_tid_rdma_write_req()` validates the request, installs responder ack-queue state, and calls `hfi1_tid_write_alloc_resources()`.
- `hfi1_tid_write_alloc_resources()` is the responder-side allocator for WRITE segments. It walks queued requests, respects `local->max_write`, handles sync points, queues for flow or RcvArray resources, and may schedule RNR NAKs when called in interrupt context.
- `hfi1_build_tid_rdma_write_resp()` returns responder TID entries to the requester.
- `hfi1_rc_rcv_tid_rdma_write_resp()` accepts those TID entries, validates capacity, advances requester flow setup, and wakes the TID send engine.
- `hfi1_build_tid_rdma_packet()` builds WRITE DATA packets into responder TID buffers.
- `hfi1_rc_rcv_tid_rdma_write_data()` validates flow PSNs, handles FECN eager delivery, clears completed responder resources, updates ACK cursors, and schedules TID ACKs.
- `hfi1_build_tid_rdma_write_ack()` and `hfi1_rc_rcv_tid_rdma_ack()` build and process TID ACK/NAK packets, including coalesced ACKs and completion.

Retry, interlock, and send engine:

- `hfi1_tid_rdma_restart_req()` rewinds flow and SGE cursors for retries.
- `hfi1_add_tid_retry_timer()`, `hfi1_del_tid_retry_timer()`, and `hfi1_tid_retry_timeout()` drive WRITE RESYNC when TID ACK progress stalls.
- `hfi1_build_tid_rdma_resync()` and `hfi1_rc_rcv_tid_rdma_resync()` renumber flow generations and packet sequence ranges after a sync event.
- `hfi1_make_tid_rdma_pkt()`, `_hfi1_do_tid_send()`, `hfi1_schedule_tid_send()`, and `make_tid_rdma_ack()` implement the second-leg TID send path, separate from the ordinary RC send state machine.
- `hfi1_tid_rdma_wqe_interlock()` and `hfi1_tid_rdma_ack_interlock()` prevent normal verbs operations or later read/ack traffic from overtaking incomplete TID WRITE state.

## Control Flow

The top-level lifecycle starts at QP creation. `hfi1_qp_priv_init()` maps the QP to an HFI receive context, initializes TID state and timers, allocates per-SWQE private request objects, and allocates per-ACK-entry TID requests for responder operations. OPFN negotiation later stores remote parameters in `priv->tid_rdma.remote` with RCU and computes packet-per-segment and timeout shift values.

On send queue processing, `hfi1_setup_tid_rdma_wqe()` decides whether an RDMA READ or WRITE is eligible. A READ requester then uses `hfi1_build_tid_rdma_read_req()` to allocate one local expected receive segment at a time, building a request whose payload is a TID entry array. The responder accepts it in `hfi1_rc_rcv_tid_rdma_read_req()`, validates the target memory, and sends `READ_RESP` data packets directly into the requester's advertised TID entries. The requester receives the last response for each segment in `hfi1_rc_rcv_tid_rdma_read_resp()`, clears the segment's local expected receive resources, and completes the WQE when all segments and RC ACK processing are done.

A WRITE requester first sends a `WRITE_REQ` with no payload. The responder records the request and allocates expected receive resources for up to the negotiated window. It returns TID entries in `WRITE_RESP` packets. The requester stores those entries and uses the TID send worker to transmit `WRITE_DATA` packets into the responder's TID buffers. The responder clears a segment when its last packet arrives and sends TID ACKs, possibly coalesced across segments. Completion happens at the requester when `hfi1_rc_rcv_tid_rdma_ack()` advances `ack_seg` to `total_segs` and calls ordinary RC completion.

Resource pressure feeds back through two wait queues in the receive context: `flow_queue` for hardware flow entries and `rarr_queue` for receive-array/TID entries. QPs are queued with reference holds, woken by flow/TID clear paths, and scheduled on the appropriate CPU via workqueue helpers.

## State and Persistence

The state is entirely in kernel memory and device registers. There is no durable persistence. Important mutable state includes:

- Per-QP private flags and counters in `hfi1_qp_priv`: flow allocation state, TID wait list entry, pending read/write segments, RNR NAK state, retry counters, timers, and TID send state.
- Per-request `struct tid_rdma_request`: circular flow indices (`setup_head`, `clear_tail`, `flow_idx`, `acked_tail`), segment counters (`cur_seg`, `comp_seg`, `ack_seg`, `alloc_seg`), SG cursor state, and state enum.
- Per-flow `struct tid_rdma_flow`: advertised TID entries, page sets, hardware TID node allocations, flow generation, TID PSNs, IB PSNs, sent counters, and retry/resync offsets.
- Per-context hardware state: `rcd->flow_mask`, `rcd->flows[]`, TID group lists, JKEY, and `RCV_TID_FLOW_TABLE` registers.

Locking is explicit. QP send state is protected by `qp->s_lock`, receive state by `qp->r_lock`, and expected receive resource pools by `rcd->exp_lock`. Several helper comments document required lock ordering. Remote parameters are accessed under RCU. Timers are stopped or deleted under QP locks or synchronously during teardown.

## Dependencies and Integration Points

This file integrates with the rdmavt QP model (`struct rvt_qp`, SWQEs, ACK queue, `do_rc_ack()`, `do_rc_completion()`), HFI1 device context structures, expected receive helpers (`exp_rcv.h`, TID group manipulation, `hfi1_put_tid()`), PIO/SDMA send scheduling (`iowait`, `hfi1_verbs_send()`), RC receive and retry logic (`hfi1_restart_rc()`, `rvt_rc_error()`), and tracepoints from `trace.h` and `trace_tid.h`.

The TID packet format depends on HFI1 KDETH fields, TID RDMA opcodes, JKEY layout, BTH PSN semantics, and RcvArray entry encoding. The code also depends on page and DMA APIs (`virt_to_page()`, `dma_map_page()`, `dma_unmap_page()`), kernel timers, workqueues, atomics, and RCU.

## Risks and Edge Cases

- Resource accounting is complex. Incorrect updates to circular indices or counters can leak TID entries, double-unprogram RcvArray slots, or stall queued QPs.
- Retry and RESYNC behavior renumbers flow generations and PSNs. Off-by-one errors around reserved RESYNC PSNs or `MAX_TID_FLOW_PSN` can corrupt ordering.
- FECN/RSM eager fallback paths copy payload into SGEs when expected packets arrive eagerly. These paths must preserve PSN tracking and length validation.
- RNR NAK scheduling mutates `r_psn`, ack-queue head pointers, and NAK state. Races with send-engine response generation could create hard-to-debug retry exhaustion.
- DMA mapping failures are translated into waiting or `-ENOMEM`; callers must not proceed with partially mapped page sets.
- Lock ordering between `s_lock`, `r_lock`, and `exp_lock` is critical. Violations can deadlock under high resource pressure.
- Remote OPFN parameters are RCU-protected. Packet builders assume a valid remote pointer after WQE conversion; disconnect or negotiation failure paths need coverage.

## Test Signals

Useful dynamic signals include tracepoints for OPFN params, TID request/flow transitions, TID entries, flow allocation, KDETH errors, TID ACKs, retry timeouts, RC ACKs, QP sleep/wakeup, and input/output headers. Tests should exercise large aligned READ and WRITE success paths, non-qualified fallback, resource exhaustion queues, RNR NAK/retry, RESYNC after retry timeout, FECN eager fallback, duplicate requests, PSN sequence errors, QP teardown while queued, and timer cleanup. Static checks should focus on lockdep annotations, timer deletion paths, RCU dereferences, DMA map/unmap balance, and circular buffer arithmetic.
