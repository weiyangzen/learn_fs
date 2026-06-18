# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/rc.h

## Purpose
`rc.h` is the small shared header for HFI1 RC helper routines. It shortens RC opcode macro usage, exposes selected ACK/completion helpers implemented in `rc.c`, and provides inline utilities for ACK queue maintenance, deferred ACK scheduling, SGE restart, and ACK-entry MR release.

## Important APIs, Types, and Functions
- `OP(x)` aliases `IB_OPCODE_RC_##x` for dense RC state-machine code.
- `update_ack_queue()` advances `s_tail_ack_queue` and `s_acked_ack_queue` past a completed ACK entry and resets `s_ack_state` to `ACKNOWLEDGE`.
- `rc_defered_ack()` puts a QP on the receive context `qp_wait_list`, sets `RVT_R_RSP_NAK`, and takes a QP reference so a later context drain can send the deferred ACK/NAK.
- `restart_sge()` converts a restart PSN into a byte offset relative to a SWQE and calls `rvt_restart_sge()`.
- `release_rdma_sge_mr()` drops the MR reference held by an ACK queue RDMA SGE and clears the pointer.
- `find_prev_entry()`, `do_rc_ack()`, and `do_rc_completion()` are exported from `rc.c` for internal HFI1 RC/TID RDMA use.

## Control Flow
The inline helpers are invoked by `rc.c` retry, receive-error, and ACK-response paths. `restart_sge()` is used when a requester has to restart in the middle of a SEND/RDMA operation or when an RDMA READ response is being copied after a retry. `rc_defered_ack()` is used by receive paths that want to delay NAK/ACK emission until the receive queue is drained. `update_ack_queue()` is used when an ACK queue entry can be skipped or reclaimed. `release_rdma_sge_mr()` is called before overwriting or retiring ACK entries that may own MR references.

## State and Persistence Behavior
The helpers mutate only QP runtime state: ACK queue indices, `s_ack_state`, `rspwait` list membership, `r_flags`, QP references, and MR references. There is no durable persistence. Correctness depends on callers holding the locks documented in `rc.c` and on the receive context wait list eventually dropping the QP reference with `rvt_put_qp()`.

## Dependencies and Integration Points
The header depends on RDMA VT QP structures, HFI1 receive context structures, Linux list handling, and RC opcode definitions from the RDMA headers. It is included by `rc.c` and indirectly supports TID RDMA code that needs RC ACK/completion helpers.

## Risks and Edge Cases
`update_ack_queue()` relies on `rvt_size_atomic()` wrap rules matching ACK queue allocation. `rc_defered_ack()` has to avoid double-enqueue by checking `list_empty(&qp->rspwait)`. `restart_sge()` assumes PSN deltas multiplied by PMTU correctly reflect byte offsets for the target work request. `release_rdma_sge_mr()` must be called on every overwrite/retire path to avoid MR reference leaks, but not while data is still needed for a response resend.

## Test Signals
Test signals come from RC retry and duplicate tests rather than this header directly: ACK queue wraparound, deferred NAK emission, RDMA READ resend from a middle PSN, and QP teardown with outstanding ACK entries should show no leaks, list corruption, or incorrect completions.
