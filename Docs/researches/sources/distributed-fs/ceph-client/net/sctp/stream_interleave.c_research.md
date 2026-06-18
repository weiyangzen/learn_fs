# sources/distributed-fs/ceph-client/net/sctp/stream_interleave.c

## Purpose
Implements SCTP message interleaving support for I-DATA and I-FORWARD-TSN while preserving the legacy DATA/FORWARD-TSN operations table. It provides the `struct sctp_stream_interleave` callbacks used by transmit numbering, receive validation, ULP event reassembly/order delivery, PR-SCTP skipping, reneging, and partial-delivery aborts.

## Important APIs, Types, And Functions
The exported entry point is `sctp_stream_interleave_init`. Important internal callbacks include `sctp_make_idatafrag_empty`, `sctp_chunk_assign_mid`, `sctp_validate_data`, `sctp_validate_idata`, `sctp_ulpevent_idata`, `sctp_generate_iftsn`, `sctp_validate_iftsn`, `sctp_report_iftsn`, and `sctp_handle_iftsn`. Key state is in `struct sctp_stream_in` (`mid`, `mid_uo`, `fsn`, `fsn_uo`, partial-delivery flags), `struct sctp_ulpq` (`reasm`, `reasm_uo`, `lobby`), and skip records.

## Control Flow
Transmit fragments receive MID and FSN values across every chunk in a datamsg, with unordered messages using the unordered MID counter. Receive validation rejects DATA or I-DATA with already skipped ordered sequence numbers. Ordered I-DATA is sorted by stream/MID/FSN in `reasm`, reassembled when a complete sequence or partial-delivery threshold is reached, then held in `lobby` until the next expected MID. Unordered I-DATA uses `reasm_uo` and separate partial-delivery state. I-FORWARD-TSN generation coalesces abandoned chunks into up to ten skip entries and queues a control chunk. I-FORWARD-TSN receive advances the TSN map, flushes fragments up to the forwarded TSN, aborts partial delivery when required, and skips ordered MID dependencies to release lobby data.

## State And Persistence
All state is volatile per association/stream. The selected interleave ops pointer switches between legacy DATA and I-DATA behavior based on peer `intl_capable`. Receive queues own skb-backed ULP events until delivery or flush.

## Dependencies And Integration Points
Relies on `ulpqueue.c` for common ULP queueing and reassembled skb construction, `ulpevent.c` for receive events and partial-delivery notifications, `tsnmap.c` for cumulative TSN advancement, outqueue abandoned lists for PR-SCTP, and socket receive queues for ULP delivery.

## Risks
The main risks are ordering bugs in stream/MID/FSN sorted queues, partial-delivery state not being cleared on skips, incorrect unordered MID handling, I-FORWARD-TSN skip coalescing truncation, skb queue ownership mistakes, and inconsistent behavior between legacy DATA and I-DATA paths.

## Test Signals
Cover fragmented ordered and unordered I-DATA, partial delivery with and without EOR, interleaved streams, skipped ordered MIDs via I-FORWARD-TSN, reneging under receive memory pressure, duplicate or stale MID validation, and fallback to legacy callbacks when `intl_capable` is false.
