# sources/distributed-fs/ceph-client/include/net/sctp/tsnmap.h

## Purpose
This header defines the TSN map used by SCTP receive paths to track cumulative acknowledgments, out-of-order data, gaps, duplicates, and pending data for SACK generation.

## Important APIs, Types, And Functions
`struct sctp_tsnmap` stores the bitmap, base TSN, cumulative TSN ACK point, max TSN seen, length, pending data count, and duplicate TSN list. APIs initialize/free maps, check/mark/skip TSNs, compute gap blocks, refresh pending counts, mark duplicates, and renege received TSNs. Inline getters expose cumulative TSN, max seen TSN, duplicate count/list, and gap status.

## Control Flow
When DATA arrives, receive code checks validity, marks the TSN, advances cumulative ack when possible, records duplicates, and later converts gaps/duplicates into SACK fields. FWD-TSN and reneging paths skip or unmark ranges.

## State And Persistence
TSN maps persist inside `sctp_association::peer.tsn_map`. Duplicate reports are reset when `sctp_tsnmap_get_dups()` hands the array to SACK construction.

## Dependencies And Integration Points
It depends on SCTP constants and gap ack UAPI structures. It integrates with association receive state, SACK generation, ULP queue reneging, and PR-SCTP/FWD-TSN handling.

## Risks And Test Signals
Risks include sequence wrap errors, gap-block overflow, duplicate suppression, pending-data drift, and reneging inconsistency. Test signals are out-of-order delivery, duplicate DATA, large TSN gaps near configured limits, SACK gap block generation, FWD-TSN skip, and receive-buffer pressure reneging.
