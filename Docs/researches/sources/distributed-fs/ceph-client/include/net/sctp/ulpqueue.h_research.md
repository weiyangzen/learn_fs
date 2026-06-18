# sources/distributed-fs/ceph-client/include/net/sctp/ulpqueue.h

## Purpose
This header defines the SCTP upper-layer protocol queue, which reassembles, orders, partially delivers, reneges, and forwards data/events from SCTP core to sockets.

## Important APIs, Types, And Functions
`struct sctp_ulpq` tracks partial-delivery mode, owning association, ordered reassembly queue, unordered reassembly queue, and lobby queue. APIs initialize, flush, free, append DATA chunks, append event skb lists, renege data, perform or abort partial delivery, clear socket partial-delivery state, skip SSNs, flush reassembly by TSN, and renege queued lists.

## Control Flow
Inbound DATA chunks enter `sctp_ulpq_tail_data()`, where reassembly and ordering decide whether to produce ULP events or hold chunks. Memory pressure can call reneging helpers. Partial delivery moves data up before full message completion when thresholds require it.

## State And Persistence
ULP queue state persists per association in `sctp_association::ulpq`. Queues hold skb-backed events/chunks until delivered, reneged, or flushed.

## Dependencies And Integration Points
It integrates with SCTP association state, stream interleaving, TSN map reneging, socket receive queues, and ULP events.

## Risks And Test Signals
Risks include ordered/unordered reassembly bugs, partial delivery deadlock, SSN skip mistakes, memory pressure losing accounting, and event ordering regressions. Test signals include fragmented ordered and unordered messages, partial delivery thresholds, receive-buffer pressure, stream reset skip, and FWD-TSN flush behavior.
