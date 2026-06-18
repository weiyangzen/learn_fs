# subset-b-003930 research

Work item: `subset-b-003930`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.h

## Purpose

`tid_rdma.h` declares the HFI1 TID RDMA public interface and the main in-memory protocol data structures shared by the TID RDMA implementation and the rest of the HFI1 RC send/receive path. It defines segment sizing, circular buffer helpers, private QP flag bits, OPFN negotiation parameters, per-request and per-flow state, page/TID allocation descriptors, and exported functions for setup, packet construction, receive handling, cleanup, timers, and scheduling.

## Important APIs, Types, and Constants

The file fixes the current TID RDMA segment size at 256 KiB with `TID_RDMA_MIN_SEGMENT_SIZE`, `TID_RDMA_MAX_SEGMENT_SIZE`, `TID_RDMA_MAX_PAGES`, and `TID_RDMA_SEGMENT_SHIFT`. `CIRC_ADD`, `CIRC_NEXT`, and `CIRC_PREV` wrap ring cursors for the flow windows.

`HFI1_S_TID_BUSY_SET`, `HFI1_R_TID_RSC_TIMER`, `HFI1_S_TID_WAIT_INTERLCK`, `HFI1_R_TID_WAIT_INTERLCK`, `HFI1_S_TID_RETRY_TIMER`, and `HFI1_R_TID_SW_PSN` are private flags stored in `hfi1_qp_priv->s_flags`. They intentionally share the same bit field as ordinary QP send flags, with comments documenting reserved bits.

Key types:

- `struct tid_rdma_params` carries OPFN-advertised capabilities: TID QP number, max segment length, JKEY, read/write segment windows, timeout, urgent support, and version.
- `struct tid_rdma_qp_params` stores local parameters, an RCU-protected remote pointer, and the trigger work item used to resume TID waiters.
- `struct tid_flow_state` stores the currently allocated hardware flow generation, PSN, flow index, and last index.
- `enum tid_rdma_req_state` models request states from inactive/init through active, resend, queued, sync, RNR NAK, and complete.
- `struct tid_rdma_request` is the protocol request object embedded behind SWQEs or ACK entries. It tracks the owning QP/context, flow ring, SGE cursor, segment counters, PSN cursors, ACK counters, and state.
- `struct flow_state` tracks TID and IB PSN ranges for one flow, including responder IB PSN and generation.
- `struct tid_rdma_pageset`, `struct kern_tid_node`, and `struct tid_rdma_flow` describe physical page chunks, allocated TID groups, TID entries, packet counters, offsets, and retry/resync state for one segment.
- `enum tid_rnr_nak_state` separates RNR NAK creation, sending, and sent states for WRITE responder resource pressure.

Function declarations expose OPFN negotiation, QP private init/free, expected receive setup/clear, READ and WRITE packet builders and receive handlers, KDETH error handling, WQE conversion, retry/reap timer deletion, RESYNC, the TID send worker, and interlocks.

## Control Flow and Integration

The header is included by HFI1 RC, QP, verbs, expected receive, and packet-building code that needs to identify TID-capable WQEs or dispatch TID RDMA opcodes. The inline `hfi1_setup_tid_rdma_wqe()` is the gateway from normal RDMA READ/WRITE WQEs to the TID path. It checks that private storage exists, the opcode is READ or WRITE, and the length meets the minimum segment size before calling the implementation.

The declared receive handlers map directly to packet opcodes: read request/response, write request/response/data, ACK, and RESYNC. The declared builders are called by the RC and TID send paths to construct headers and payload SGEs. Cleanup declarations are used by QP reset/error paths to clear locally programmed expected receive resources.

## State and Persistence

All structures declared here are transient kernel state. They persist for the life of a QP, WQE, ACK entry, or in-flight segment, but not across driver unload or reboot. The most important persistence boundary is the pairing between WQE/ACK private storage and flow allocation state: cleanup functions must be called when QPs reset, WQEs are flushed, or ACK entries are reused.

## Risks and Test Signals

The header's main risks are ABI drift and state mismatch between declarations and implementation. Segment size constants, ring size assumptions, and bit assignments must remain consistent with `tid_rdma.c`, expected receive group sizing, hardware TID entry format, and trace decoding. Tests should verify that converted WQEs always have initialized private request storage, that cleanup can run idempotently on inactive requests, that flag bits do not collide with active QP flags, and that all declared packet handlers remain wired to opcode dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/tid_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.c

## Purpose

`trace.c` provides the implementation backing HFI1 tracepoint formatting helpers and debug trace functions. With `CREATE_TRACE_POINTS` defined before including `trace.h`, it instantiates the tracepoints declared across the HFI1 trace headers. It also parses and formats packet headers, extended verbs headers, SDMA flags, TID entries, and receive-context histogram output used by trace events.

## Important APIs and Functions

Header sizing and parsing:

- `hfi1_trace_packet_hdr_len()` and `hfi1_trace_opa_hdr_len()` compute dynamic extended header lengths for incoming packets and outgoing OPA headers, supporting both 9B and 16B formats.
- `hfi1_trace_parse_9b_bth()`, `hfi1_trace_parse_16b_bth()`, `hfi1_trace_parse_9b_hdr()`, and `hfi1_trace_parse_16b_hdr()` extract fields into trace entry storage.
- `hfi1_trace_fmt_lrh()` and `hfi1_trace_fmt_rest()` format LRH/16B and BTH/L4 portions into `trace_seq` buffers.

Extended header formatting:

- `parse_everbs_hdrs()` decodes immediate data, RETH, AETH, DETH, IETH, atomic headers, and HFI1 TID RDMA headers for WRITE_REQ, WRITE_RESP, WRITE_DATA, READ_REQ, READ_RESP, ACK, and RESYNC.
- `parse_syndrome()` converts AETH syndrome classes to ACK, RNRNAK, or NAK labels.
- `hfi1_trace_get_tid_ctrl()`, `hfi1_trace_get_tid_len()`, and `hfi1_trace_get_tid_idx()` expose TID entry fields to trace headers.

Other helpers:

- `parse_sdma_flags()` prints SDMA descriptor state.
- `print_u32_array()` formats arrays for trace output.
- `hfi1_trace_print_rsm_hist()` maintains and prints an atomic receive-side mapping histogram.
- `__hfi1_trace_fn(...)` instances implement formatted debug trace functions for AFFINITY, PKT, PROC, SDMA, LINKVERB, DEBUG, SNOOP, CNTR, PIO, DC8051, FIRMWARE, RCVCTRL, TID, MMU, and IOCTL.

## Control Flow and State

Trace events in headers capture raw fields in `TP_fast_assign` and call these helpers from `TP_printk`. The helper functions do not drive device behavior, but they are part of runtime observability and must be safe when tracing arbitrary packets. The file keeps only a small static `hfi1_ctxt_hist` counter array for RSM histogram traces; other state is derived from packet/header arguments.

## Dependencies and Integration Points

The file depends on HFI1 packet structures, InfiniBand header accessors, opcode length tables, TID RDMA header layouts, expected receive TID-entry macros, SDMA descriptor masks, and Linux tracepoint/trace_seq APIs. It integrates with `trace_ibhdrs.h`, `trace_ctxts.h`, `trace_tx.h`, and `trace_dbg.h`.

## Risks and Test Signals

Formatting code can still break kernel tracing if dynamic header lengths are wrong, if opcode-specific unions are decoded with the wrong layout, or if endian conversion differs from packet encoding. TID RDMA decoding is especially useful for validating `tid_rdma.c`: packet traces should show matching TID flow PSNs, flow QPs, JKEYs, verbs PSNs, AETH syndromes, and TID entry fields through read/write success and retry paths. Tests should exercise trace formatting for 9B, 16B, management packets, ordinary RC packets, and every TID RDMA opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.h

## Purpose

`trace.h` is the umbrella include for HFI1 tracepoint definitions. It defines common packet receive-type symbolic formatting and includes the individual trace systems for debug, miscellaneous device events, context setup, packet headers, RC, receive path, transmit path, MMU, iowait, and TID.

## Important APIs and Integration

`packettype_name()` and `show_packettype()` map `RHF_RCV_TYPE_*` values to printable trace symbols. The included trace headers each set their own `TRACE_SYSTEM` and provide their own `TRACE_INCLUDE_FILE` footer, so this umbrella is primarily a convenience include used by implementation files such as `trace.c` and `tid_rdma.c`.

The include order matters because some trace headers use common helpers or macros from earlier includes, and `trace.c` relies on this file after defining `CREATE_TRACE_POINTS` to instantiate all included events in one compilation unit.

## State, Risks, and Test Signals

This header has no runtime state. Risks are build-time and trace-generation oriented: include guard mistakes, duplicate `TRACE_SYSTEM` handling, missing trace header includes, or stale receive-type mappings can break tracepoint generation or reduce diagnostic value. Test signals are successful compilation with tracepoints enabled and runtime availability of expected HFI1 trace systems under ftrace/perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ctxts.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ctxts.h

## Purpose

`trace_ctxts.h` defines tracepoints for HFI1 user/context data and receive-side mapping histogram output. These events make context allocation and runtime packet distribution visible.

## Important Events

- `hfi1_uctxtdata` records device name, context/subcontext, PIO credits and hardware free counter, PIO base address, receive header queue count and DMA address, eager buffer count/DMA address, and subcontext count.
- `hfi1_ctxt_info` records user-visible context configuration such as eager TID count, eager receive size, receive header queue count and entry size, and SDMA ring size.
- `ctxt_rsm_hist` calls `hfi1_trace_print_rsm_hist()` to emit a compact histogram of receive-side mapping context use.

## Control Flow and State

The header declares only trace events. Event state is captured when callers invoke the tracepoints. The histogram state lives in `trace.c`; this header only declares the formatting helper and event.

## Dependencies and Integration Points

The events depend on `struct hfi1_devdata`, `struct hfi1_ctxtdata`, `struct hfi1_ctxt_info`, context credit fields, eager buffer metadata, and common `DD_DEV_ENTRY` trace macros. They integrate with context initialization and receive path diagnostics.

## Risks and Test Signals

The most likely risk is dereferencing partially initialized context fields if events are placed too early or too late in lifecycle code. Useful tests confirm that context open/init paths emit sane counts and DMA addresses, and that `ctxt_rsm_hist` remains bounded and readable under multi-context traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ctxts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_dbg.h

## Purpose

`trace_dbg.h` defines the HFI1 formatted debug trace facility. It provides a shared trace event template for printf-style debug messages and generates one trace function/event pair per debug category.

## Important APIs

`hfi1_trace_template` stores the caller function name and formatted message using `__vstring`. `__hfi1_trace_def(lvl)` declares `__hfi1_trace_<lvl>()` and defines the corresponding `hfi1_<lvl>` trace event. `__hfi1_trace_fn(lvl)` provides the implementation body used in `trace.c`.

The file declares categories including AFFINITY, PKT, PROC, SDMA, LINKVERB, DEBUG, SNOOP, CNTR, PIO, DC8051, FIRMWARE, RCVCTRL, TID, MMU, and IOCTL. `hfi1_cdbg(which, fmt, ...)` and `hfi1_dbg(fmt, ...)` are the call-side macros. `hfi1_dbg_early()` can map to `trace_printk()` when `HFI1_EARLY_DBG` is explicitly enabled.

## Control Flow and State

Callers invoke the macros with a category and format string. The generated function packages the varargs into `struct va_format`, calls the tracepoint, and returns. The tracepoint stores only event data; no driver state is mutated.

## Dependencies and Risks

The file depends on Linux tracepoint support, `trace_seq`, `va_format`, and HFI1 headers. It suppresses GCC `-Wsuggest-attribute=format` around the trace template declarations because the generated trace machinery does not match normal format attribute inference.

Risks include format-string/type mismatches in callers, overly long messages making console trace output hard to read, and accidentally enabling early debug tracing in committed code. Test signals are successful compilation of all generated trace functions and readable category-specific events during driver debug sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ibhdrs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ibhdrs.h

## Purpose

`trace_ibhdrs.h` declares packet header tracepoints for incoming and outgoing HFI1 packets. It provides symbolic opcode printing, helper prototypes implemented in `trace.c`, and event classes that capture 9B/16B LRH/BTH fields plus dynamic extended headers.

## Important APIs and Events

`show_ib_opcode()` maps RC, UC, UD, CNP, and HFI1 TID RDMA opcodes to names. Helper prototypes cover header-length calculation, 9B/16B parsing, LRH/rest formatting, packet L2/L4 string conversion, and extended header formatting.

`hfi1_input_ibhdr_template` captures receive packet type, LRH/16B fields, BTH fields, QP/PSN, optional management QPNs, and a dynamic copy of extended headers. It instantiates `input_ibhdr`.

`hfi1_output_ibhdr_template` captures the same style of data from outgoing `hfi1_opa_header` values and instantiates `pio_output_ibhdr`, `ack_output_ibhdr`, and `sdma_output_ibhdr`.

## Control Flow and State

The event fast-assign blocks parse fields based on packet type. Bypass packets use 16B parsing; normal packets use 9B parsing. Management packets avoid BTH extended header copying. For other opcodes, the dynamic `ehdrs` array is copied and later formatted through `parse_everbs_hdrs()`.

The header owns no persistent state. It relies on `trace.c` for helper implementations and on the caller to pass packet/header structures with `packet->ohdr` already set correctly.

## Integration, Risks, and Test Signals

This trace surface is central for validating RC and TID RDMA packet construction. It must stay aligned with opcode definitions, `hdr_len_by_opcode`, packet union layouts, and TID RDMA extended headers. Risks include dynamic length mismatches, copying from a NULL `ohdr`, or formatting stale union members for management packets. Tests should enable input/output header tracepoints for 9B, 16B, SDMA, PIO, ACK, and all TID RDMA opcodes and compare decoded fields with packet-builder expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_ibhdrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_iowait.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_iowait.h

## Purpose

`trace_iowait.h` defines tracepoints for `struct iowait` flag changes. Iowait state coordinates deferred send work, pending IB/TID work, and wakeups when transmit resources become available.

## Important Events

`hfi1_iowait_template` records the iowait object address, current wait flags, the single flag being changed as a bit mask, and the owning QP number. It instantiates `hfi1_iowait_set` and `hfi1_iowait_clear`.

## Control Flow and State

The tracepoints observe state changes but do not mutate state. Callers in the send and scheduling paths can emit events around `iowait_set_flag()` and clear operations, making it possible to trace why a QP is sleeping or waking.

## Dependencies and Integration Points

The header depends on `iowait.h`, `verbs.h`, `iowait_to_qp()`, and Linux tracepoint APIs. It is relevant to the TID RDMA send path because `hfi1_make_tid_rdma_pkt()` and `hfi1_schedule_tid_send()` set pending TID/IB iowait flags when tx requests or IO resources are unavailable.

## Risks and Test Signals

Risks are low but include tracing an iowait object before it has a valid owner QP or interpreting `flag` incorrectly if enum positions change. Test signals include paired set/clear events around resource starvation, TID send pending state, and later wakeup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_iowait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_misc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_misc.h

## Purpose

`trace_misc.h` defines miscellaneous HFI1 tracepoints for interrupt sources, RcvArray writes, and optional fault-injection diagnostics.

## Important Events

- `hfi1_interrupt` records the device, interrupt source name, and source number using the supplied interrupt-source table callback.
- `hfi1_csr_template` is a small CSR write template instantiated as `hfi1_write_rcvarray`, which records an MMIO address and value.
- Under `CONFIG_FAULT_INJECTION`, `hfi1_fault_opcode` records injected opcode faults by QP and opcode, and `hfi1_fault_packet` records packet receive error flags, context, lengths, eager index, and related packet metadata.

## Control Flow and State

The events are passive instrumentation. They snapshot interrupt, CSR, or fault-injection data when called. There is no persistent state in this header.

## Dependencies and Integration Points

This file depends on HFI1 device structures, interrupt-source tables, packet helpers, and common device trace macros. `hfi1_write_rcvarray` is especially useful with expected receive and TID RDMA code because `tid_rdma.c` programs and invalidates RcvArray entries while allocating or clearing TID flows.

## Risks and Test Signals

The main risk is calling tracepoints with invalid device or packet pointers during error paths. Test signals include interrupt trace output naming the correct source, RcvArray write traces matching expected receive programming, and fault-injection traces appearing only when the kernel option is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_mmu.h

## Purpose

`trace_mmu.h` defines tracepoints for the HFI1 MMU interval/rbtree tracking layer. These events expose registration, lookup, invalidation, eviction, and release of MMU range nodes.

## Important Events

`hfi1_mmu_rb_template` captures node address, length, and kref refcount. It instantiates `hfi1_mmu_rb_insert`, `hfi1_mmu_mem_invalidate`, `hfi1_mmu_rb_evict`, and `hfi1_mmu_release_node`. `hfi1_mmu_rb_search` records lookup address and length.

## Control Flow and State

The tracepoints observe MMU tracking operations and do not mutate state. Refcount is read with `kref_read()` to make ownership/lifetime visible in traces.

## Dependencies and Integration Points

The header depends on `struct mmu_rb_node`, krefs, and tracepoint APIs. It integrates with memory registration/invalidation code, which indirectly matters for RDMA and expected receive paths because stale or invalid memory mappings must not remain programmed in hardware.

## Risks and Test Signals

Risks are primarily diagnostic drift: if node lifetime or refcounting changes, trace output must still reflect meaningful state. Tests should exercise node insert/search/invalidate/evict/release and verify that refcounts and address ranges match expected memory-region lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rc.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rc.h

## Purpose

`trace_rc.h` defines tracepoints for reliable connection send, ACK, receive-error, completion, and ACK-processing state. It provides compact visibility into QP PSN and flag state around RC protocol transitions.

## Important Events

`hfi1_rc_template` captures device name, QP number, send flags, the event PSN, `s_psn`, `s_next_psn`, `s_sending_psn`, `s_sending_hpsn`, and `r_psn`. It instantiates `hfi1_sendcomplete`, `hfi1_ack`, `hfi1_rcv_error`, and `hfi1_rc_completion`.

`hfi1_rc_ack_template` captures device, QP, AETH, PSN, WQE opcode, WQE start PSN, and WQE last PSN. It instantiates `hfi1_rc_ack_do`.

## Control Flow and State

The events are emitted by RC send/completion/error/ACK paths. They snapshot QP state at protocol boundaries and do not mutate state.

## Dependencies and Integration Points

The header depends on `struct rvt_qp`, `struct rvt_swqe`, `dd_from_ibdev()`, and common trace macros. TID RDMA uses ordinary RC ACK/completion helpers in several places, so these tracepoints complement the TID-specific tracepoints when diagnosing mixed RC/TID behavior.

## Risks and Test Signals

The main risk is interpreting PSN snapshots without the matching TID or packet-header traces, especially when TID RDMA uses both verbs PSNs and KDETH flow PSNs. Test signals include monotonic RC PSN movement, expected ACK/completion events after TID READ responses and TID WRITE ACKs, and receive-error traces during injected PSN mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rx.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rx.h

## Purpose

`trace_rx.h` defines receive-path tracepoints for packet headers, receive interrupts, and MMU invalidation notifications. These events expose low-level receive metadata that helps correlate packet processing with context and memory events.

## Important Events

- `hfi1_rcvhdr` records device, RHF error flags, context, receive packet type, header length, total length, updated eager indicator, and eager tail index.
- `hfi1_receive_interrupt` records device, context number, slow-path status, and DMA receive-tail setting.
- `hfi1_mmu_invalidate` records context/subcontext, invalidation type string, and start/end address range.

The file also defines `show_tidtype()` for expected, eager, and invalid TID type names.

## Control Flow and State

These tracepoints are passive receive-path instrumentation. They snapshot packet/context fields when invoked. They do not own persistent state.

## Dependencies and Integration Points

The file depends on RHF decoding helpers, receive context structures, packet metadata, MMU invalidation call sites, and `show_packettype()` from `trace.h`. It is relevant for TID RDMA because KDETH/TID errors and FECN eager-delivery fallback are diagnosed by combining receive header traces with TID-specific and header-decoding traces.

## Risks and Test Signals

Risks include logging packet metadata after packet buffers have been advanced or using stale RHF fields. Test signals include receive interrupt traces per active context, rcvhdr traces with correct expected/eager/error/bypass type, and MMU invalidation traces aligned with memory deregistration or invalidation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_rx.h -->
