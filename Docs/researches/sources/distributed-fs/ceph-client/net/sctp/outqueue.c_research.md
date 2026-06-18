# sources/distributed-fs/ceph-client/net/sctp/outqueue.c

## Purpose
`outqueue.c` implements association-level outbound queueing, retransmission, SACK processing, congestion interactions, and PR-SCTP abandonment/forward-TSN generation. It is the bridge between state-machine/user chunks and packet assembly in `output.c`.

## Important APIs, Types, And Functions
Primary APIs are `sctp_outq_init()`, `sctp_outq_teardown()`, `sctp_outq_free()`, `sctp_outq_tail()`, `sctp_outq_uncork()`, `sctp_retransmit_mark()`, `sctp_retransmit()`, `sctp_outq_sack()`, `sctp_outq_is_empty()`, `sctp_prsctp_prune()`, and `sctp_generate_fwdtsn()`. Important helpers include `sctp_outq_head_data()`, `sctp_outq_tail_data()`, `sctp_outq_dequeue_data()`, `sctp_insert_list()`, `__sctp_outq_flush_rtx()`, `sctp_outq_flush_ctrl()`, `sctp_outq_flush_rtx()`, `sctp_outq_flush_data()`, `sctp_outq_flush_transports()`, `sctp_check_transmitted()`, `sctp_mark_missing()`, and `sctp_acked()`.

## Control Flow
DATA chunks are queued through the stream scheduler and `out_chunk_list`; control chunks are queued separately and counted as outbound control. Unless corked, `sctp_outq_tail()` immediately flushes. Flush sends control first, respecting SCTP bundling rules that INIT, INIT ACK, and SHUTDOWN COMPLETE are singleton packets. Response chunks may force one-packet behavior; ASCONF source-address restrictions can stop DATA flushing until address reconfiguration completes.

Retransmission starts with `sctp_retransmit()`, which adjusts counters and congestion state based on reason (T3 timeout, fast retransmit, PMTUD, T1), moves eligible transmitted chunks to the sorted retransmit queue with `sctp_retransmit_mark()`, possibly generates FWD-TSN, and flushes for timeout-style retransmits. `__sctp_outq_flush_rtx()` sends at most one packet for timeout/fast retransmit and moves retransmitted chunks back to the chosen transport's transmitted list.

SACK processing in `sctp_outq_sack()` validates cumulative TSN progress, updates CACC state, runs retransmit and per-transport transmitted queues through `sctp_check_transmitted()`, advances `ctsn_ack_point`, marks missing chunks for fast retransmit, recomputes unacknowledged DATA, frees cumulatively acked chunks, updates rwnd, and generates PR-SCTP FWD-TSN when abandoned chunks advance `adv_peer_ack_point`.

## State And Persistence
The outqueue persists association send state in memory: unsent DATA, control chunks, retransmit queue, sacked queue, abandoned queue, outstanding bytes, cork/fast retransmit flags, per-transport transmitted lists, flight sizes, T3 timers, cwnd/ssthresh, rwnd, TSN missing reports, PR-SCTP removable counters, and stream scheduler queues. No disk persistence exists.

## Dependencies And Integration Points
It integrates with `output.c` packet assembly, transport congestion helpers, stream scheduler ops, PR-SCTP policies, SCTP timers, state-machine chunk constructors, trace events, association peer path management, and SACK/FWD-TSN wire formats.

## Risks
Accounting is the hardest risk: bytes must move exactly once between unsent, outstanding, retransmit, sacked, and abandoned states. Reneged SACKs, ASCONF-deleted transports, migrated DATA, zero-window probing, and PR-SCTP abandonment all create edge cases. Fast retransmit marking depends on gap-block interpretation and CACC skip rules; errors can cause spurious retransmits or data stalls. Freeing chunks during teardown must notify send-failure paths without touching already freed stream scheduler state.

## Test Signals
Use tests for normal DATA/SACK progression, gap ACK fast retransmit after three missing reports, reneged gap ACKs, T3 timeout retransmission, PMTU retransmission, COOKIE-ECHO bundling limits, zero-window probe SACKs, PR-SCTP priority pruning of sent/unsent data, FWD-TSN generation, ASCONF source restrictions, stream-closed requeueing, cork/uncork, multi-homed path switch/CACC behavior, and teardown with chunks in every queue.
