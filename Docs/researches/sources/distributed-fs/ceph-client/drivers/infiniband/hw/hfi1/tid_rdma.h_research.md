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
