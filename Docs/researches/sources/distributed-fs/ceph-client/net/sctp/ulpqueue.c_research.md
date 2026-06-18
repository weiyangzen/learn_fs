# sources/distributed-fs/ceph-client/net/sctp/ulpqueue.c

## Purpose
Implements the legacy SCTP upper-layer protocol queue for DATA chunks: receive event creation, TSN-based fragment reassembly, SSN ordering, socket receive/lobby delivery, partial delivery, reneging, FORWARD-TSN skipping, and queue flushing.

## Important APIs, Types, And Functions
Exports `sctp_ulpq_init`, `sctp_ulpq_flush`, `sctp_ulpq_free`, `sctp_ulpq_tail_data`, `sctp_clear_pd`, `sctp_ulpq_tail_event`, `sctp_make_reassembled_event`, `sctp_ulpq_reasm_flushtsn`, `sctp_ulpq_skip`, `sctp_ulpq_renege_list`, `sctp_ulpq_partial_delivery`, `sctp_ulpq_renege`, and `sctp_ulpq_abort_pd`. Key queues are `reasm`, `reasm_uo`, `lobby`, socket `sk_receive_queue`, and socket `pd_lobby`.

## Control Flow
Incoming DATA becomes an ULP event, then fragmented messages are sorted by TSN in `reasm` until complete or partial-delivery thresholds are met. Complete messages are ordered by stream/SSN in `lobby` unless unordered. `sctp_ulpq_tail_event` chooses socket receive queue or partial-delivery lobby depending on socket/association PD state and fragment-interleave setting, then signals `sk_data_ready`. Partial delivery retrieves the first contiguous fragment run when allowed and sets association/socket PD mode. Renege frees received-but-undelivered events above cumulative TSN, clears TSN map bits, and retries chunk admission. FORWARD-TSN flushes stale fragments and skips SSNs to release newly ordered lobby data.

## State And Persistence
State is volatile in `struct sctp_ulpq`, socket `pd_mode`, and skb queues. Receive-window and TSN map updates are coupled to event ownership.

## Dependencies And Integration Points
Works with `ulpevent.c` for event allocation/free/accounting, `tsnmap.c` for cumulative TSN and renege behavior, stream SSN helpers, socket receive queues, and stream-interleave callbacks that reuse reassembly helpers.

## Risks
Risks include skb frag_list manipulation during reassembly, partial-delivery deadlocks when lobbies are not drained, reneging below cumulative ack, wrong queue selection under fragment interleave, and ordering bugs after SSN skip.

## Test Signals
Test fragmented complete and partial messages, unordered delivery, receive shutdown filtering, simultaneous associations in partial delivery, FORWARD-TSN skip/reap, memory-pressure reneging, cloned skb reassembly, and aborting partial delivery with notification enabled/disabled.
