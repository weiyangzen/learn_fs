# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_req.c

## Purpose

`rxe_req.c` implements the RXE requester state machine: consuming SQ WQEs, selecting packet opcodes, building packets, copying payloads, handling local operations, enforcing fences/atomic depth, and coordinating retries.

## Important APIs, Types, and Functions

Key functions are `rxe_requester()`, `rxe_sender()`, `rnr_nak_timer()`, `req_retry()`, `next_opcode_rc()`, `next_opcode_uc()`, `init_req_packet()`, `finish_packet()`, and WQE/PSN state update helpers.

## Control Flow

`rxe_sender()` runs requester then completer. The requester checks QP state, rewinds for retries, gets the next WQE, handles fences and RD atomic credits, executes local ops, selects an opcode, builds headers, copies inline or MR-backed payload, transmits through `rxe_xmit_packet()`, updates WQE state/PSNs, and arms RC retransmit timing.

## State and Persistence Behavior

State persists in `qp->req`, WQE DMA cursors, WQE first/last PSNs, WQE state/status, completer state, and RC timers. Wait flags represent fence, PSN window, RD atomic, RNR, retry, and skb backpressure conditions.

## Dependencies and Integration Points

The file depends on queue helpers, opcode tables, header initializers, MR copy/local MR-MW operations, AV lookup, network transmit, QP timers, and completer logic.

## Risks and Edge Cases

Retry reconstruction must restore DMA cursors and PSNs exactly. Fence and RD atomic credit handling must avoid deadlock or overcommit. UD oversized messages are silently completed successfully per spec. Inline and MR copy failures map to different WC statuses.

## Test Signals

Test RC/UC/UD/GSI sends, write/read/atomic/flush/atomic-write, inline and non-inline payloads, MTU segmentation, retransmit/RNR retry, local invalidate/register/bind, fences, max unacked PSNs, skb backpressure, and QP error/reset during sends.
