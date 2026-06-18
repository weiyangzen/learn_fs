# sources/distributed-fs/ceph-client/net/sctp/tsnmap.c

## Purpose
Maintains the receive-side Transmission Sequence Number map used to detect duplicates, track gaps, compute cumulative TSN ACK point, produce SACK gap-ack blocks, skip abandoned TSNs, and renege received TSNs under memory pressure.

## Important APIs, Types, And Functions
Exports `sctp_tsnmap_init`, `sctp_tsnmap_free`, `sctp_tsnmap_check`, `sctp_tsnmap_mark`, `sctp_tsnmap_skip`, `sctp_tsnmap_pending`, `sctp_tsnmap_renege`, and `sctp_tsnmap_num_gabs`. Internal helpers are `sctp_tsnmap_update`, `sctp_tsnmap_find_gap_ack`, iterator helpers, and `sctp_tsnmap_grow`.

## Control Flow
Initialization allocates a bitmap, sets `base_tsn`, cumulative ack to initial minus one, and clears duplicate count. Check rejects old or out-of-window TSNs and detects bitmap duplicates. Mark either fast-advances the no-gap case or grows the bitmap, sets the bit, updates `max_tsn_seen`, and shifts away contiguous received bits. Skip advances base and cumulative ack through a forwarded TSN and shifts or clears the bitmap. Gap ack generation iterates over set bit runs past the cumulative ack point. Renege clears a bit so SACK generation can report it missing again.

## State And Persistence
The map is an in-memory bitmap plus counters in `struct sctp_tsnmap`: `len`, `base_tsn`, `cumulative_tsn_ack_point`, `max_tsn_seen`, and duplicate count.

## Dependencies And Integration Points
Used by ULP event creation after receive memory admission, SACK generation, FORWARD-TSN/I-FORWARD-TSN handling, stream reset TSN reset paths, and reneging in `ulpqueue.c`.

## Risks
Risks include wrap-aware TSN comparison mistakes, bitmap length measured in bits but allocated in bytes, growth failure causing receive drops, gap-ack off-by-one relative to cumulative ack, and renege clearing invalid bits.

## Test Signals
Cover sequential receives, gap creation/fill, duplicate old/current TSNs, TSN wraparound comparisons, bitmap growth near `SCTP_TSN_MAP_SIZE`, skip beyond current map, SACK gap block limits, and renege/pending counts.
