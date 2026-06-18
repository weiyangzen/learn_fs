# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_comp.c

## Purpose
`rxe_comp.c` implements the requester-side completer state machine for RXE RC traffic. It processes ACK/NAK/read/atomic responses, completes send WQEs, manages retry/RNR timers, flushes queues on error/reset, and posts send CQEs.

## Important APIs, types, and functions
External entry points are `retransmit_timer()`, `rxe_comp_queue_pkt()`, and `rxe_completer()`. Important helpers include `get_wqe()`, `check_psn()`, `check_ack()`, `do_read()`, `do_atomic()`, `make_send_cqe()`, `do_complete()`, `complete_ack()`, `complete_wqe()`, `flush_send_queue()`, `free_pkt()`, and `reset_retry_timer()`. The `enum comp_state` names the state-machine stages.

## Control flow
Incoming response packets are queued on `qp->resp_pkts` and schedule the QP send task. `rxe_completer()` first handles invalid, ERR, or RESET QPs by draining response packets and flushing send WQEs. Otherwise it consumes an ACK packet, finds the oldest send WQE, validates PSN ordering, checks opcode/ACK/NAK semantics, copies read or atomic response data into local memory, advances completion PSNs, and posts CQEs when signaled or on error. Timeout and NAK paths trigger retry state by setting requester flags, decrementing retry counters, arming RNR timers, or transitioning the QP to error.

## State and persistence
State is in `qp->comp`, `qp->req`, send queue WQE states, response skb queue, retry timers, CQ queues, and hardware-style stats counters. Packet SKBs hold QP and device references until `free_pkt()` drops them. CQEs persist in user or kernel completion queues until polled.

## Dependencies and integration points
The completer depends on RXE queues, tasks, CQ posting, MR copy helpers, packet header helpers, timers, QP state locking, requester flags, and counters from `rxe_hw_counters.h`. It works in tandem with `rxe_req.c`, `rxe_resp.c`, and `rxe_task.c`.

## Risks
The retry/RNR state machine is high risk: spurious retransmit timer expirations are expected, and fields like `started_retry`, `timeout_retry`, `need_retry`, and `again` coordinate with requester scheduling. There is a source TODO about protection from QP destruction around `mod_timer(&qp->rnr_nak_timer)`. CQ full handling during flush stops notifications for remaining WQEs. Error handling must always generate completions required by the IB spec.

## Test signals
Run RC send/write/read/atomic/flush tests with ACKs, duplicate ACKs, out-of-order PSNs, RNR NAKs, sequence NAKs, remote invalid/access/op errors, retry exhaustion, RNR retry exhaustion, SQ drain, CQ overflow, QP ERR/RESET flushing, and packet loss with retransmit timers.
