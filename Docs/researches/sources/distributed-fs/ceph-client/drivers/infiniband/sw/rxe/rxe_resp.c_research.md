# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_resp.c

## Purpose

`rxe_resp.c` implements the RXE responder state machine for received requests, including validation, execution, completion, ACK/NAK/read responses, duplicate replay, and error handling.

## Important APIs, Types, and Functions

Main entry points are `rxe_resp_queue_pkt()` and `rxe_receiver()`. Important stages include `check_psn()`, `check_op_seq()`, `check_op_valid()`, `check_resource()`, `rxe_resp_check_length()`, `check_rkey()`, `execute()`, `read_reply()`, `atomic_reply()`, `atomic_write_reply()`, `process_flush()`, `do_complete()`, `acknowledge()`, `duplicate_request()`, and `cleanup()`.

## Control Flow

The responder loops through explicit states: fetch packet, validate PSN/opcode/access/resource/length/rkey, execute send/write/read/atomic/flush/invalidate behavior, post completions, send RC ACK/NAK or read responses, cleanup packet/MR references, or transition to QP error. RDMA read, atomic, atomic write, and flush resources support duplicate request replay.

## State and Persistence Behavior

Responder state persists in `qp->resp`: expected PSN, MSN, ACK PSN, opcode, flags, current WQE, held MR/rkey/VA/resid, SRQ WQE copy, responder resource ring, and current replay resource. Packets stay queued on `qp->req_pkts` until cleanup.

## Dependencies and Integration Points

It depends on packet/header accessors, queues, MR/MW lookup and copy, ODP operations, CQ posting, network transmit, QP state management, SRQ events, and RDMA WC/event semantics.

## Risks and Edge Cases

PSN wrap, duplicate replay, RKEY/MW handling, zero-length operations, flush range vs MR semantics, atomic-write length/padding checks, SRQ malformed WQEs, and error class mapping across RC/UC/UD/SRQ are all high-risk. CQ overflow forces QP error.

## Test Signals

Test all responder operations, segmentation, zero-length read/write, duplicate replay, PSN/RNR NAKs, invalid rkey/access/range, immediate/invalidate completions, SRQ limit events, CQ overflow, ODP atomics, persistent flush, and QP reset/error drains.
