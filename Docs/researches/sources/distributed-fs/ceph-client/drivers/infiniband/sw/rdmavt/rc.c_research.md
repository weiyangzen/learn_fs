# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/rc.c

## Purpose
`rc.c` contains small but critical Reliable Connection helpers shared by rdmavt providers: AETH credit encoding/decoding and send SGE rewind. It supports RC flow control and retransmission recovery.

## Important APIs, types, and functions
`rvt_compute_aeth()` builds an Acknowledge Extended Transport Header value using `qp->r_msn` and receive queue credit information. `rvt_get_credit()` consumes AETH credits on the requester side, updating `qp->s_lsn`, unlimited-credit state, and wait flags. `rvt_restart_sge()` resets an SGE state to the beginning of a WQE and skips a requested byte length. The file uses a 31-entry credit table and `IB_AETH_*` bit definitions.

## Control flow
Responder ACK generation calls `rvt_compute_aeth()`. For SRQ-backed QPs, credit is marked invalid because SRQs do not advertise per-QP credits. For per-QP receive queues, it reads cached `kwq->count`, and if empty computes credits from sanitized head/tail ring indices. It then binary-searches the credit table to choose the largest encoded credit not exceeding the available RWQE count.

Requester ACK handling calls `rvt_get_credit()` with `s_lock` held. Invalid credit enables unlimited sending and wakes send processing when waiting on SSN credit. Valid credit extends `s_lsn` only if it advances beyond the previous value. `rvt_restart_sge()` is used by retry paths to rebuild the current SGE cursor from a WQE.

## State and persistence
State is entirely in the QP: `r_msn`, receive-queue counts, user or kernel ring indices, `s_lsn`, `s_flags`, and SGE cursor fields. The helper deliberately tolerates fuzzy concurrent reads of head/tail because subsequent ACKs correct credit approximation.

## Dependencies and integration points
The file depends on `rdmavt_qp.h`, `ib_hdrs.h`, RDMA UAPI atomic accessors, and provider send scheduling through `rdi->driver_f.schedule_send()`. It is used by RC responder/requester code in provider drivers and by rdmavt retry logic.

## Risks
Credit encoding mistakes can deadlock senders or overrun receive queues. User-mapped queue indices must remain sanitized before credit calculations. `rvt_get_credit()` assumes `s_lock` is held; callers that violate this can race wait flags and send scheduling.

## Test signals
RC tests should cover SRQ vs non-SRQ AETH generation, empty and partially filled receive queues, corrupt user head/tail values, invalid/unlimited credits, credit wrap via MSN masking, and retry paths that call `rvt_restart_sge()` at packet boundaries.
