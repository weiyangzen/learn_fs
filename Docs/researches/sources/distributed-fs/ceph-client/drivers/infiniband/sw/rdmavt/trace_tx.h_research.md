# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/trace_tx.h

## Purpose
`trace_tx.h` declares send-queue trace events for rdmavt post-send and send-completion paths.

## Important APIs, types, and functions
`rvt_post_one_wr` records WQE pointer, WR ID, send flags, QPN, QP type, PSN/lPSN, SSN, length, opcode, queue size/availability/head/last, PID, and SGE counts. `rvt_qp_send_completion` records WQE pointer, WR ID, QPN/QP type, length, completed index, SSN, opcode, and send flags. `show_wr_opcode()` maps common `IB_WR_*` opcodes to names.

## Control flow
`qp.c` emits `rvt_post_one_wr` after validating and filling a send WQE but before advancing the head. It emits `rvt_qp_send_completion` while completing a WQE and updating send queue cursors.

## State and persistence
Events snapshot send queue state. They can expose kernel pointers and user WR IDs through tracing but do not mutate queues.

## Dependencies and integration points
It depends on RDMA core work request enums, `rdmavt_qp.h`, and tracepoint infrastructure. It is a key diagnostic companion for provider send engines and CQ completion traces.

## Risks
Opcode maps must track RDMA core additions. Tracepoints should remain inside regions where the WQE and QP are stable. Since `rvt_post_one_wr` emits before `s_head` advances, trace consumers must interpret `head` as the pre-advance slot.

## Test signals
Enable TX events while posting SEND, RDMA, atomic, local invalidate, and fast-reg WRs. Verify PSN ranges, queue availability, reserve usage, completion index advancement, and matching CQ completion records.
