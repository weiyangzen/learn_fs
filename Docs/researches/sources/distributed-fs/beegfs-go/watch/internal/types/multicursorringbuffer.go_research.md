# sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer.go

## Purpose

This file implements BeeWatch's primary event buffer: a single-writer, multi-reader ring buffer with per-subscriber send and acknowledgement cursors. It is optimized to let metadata ingestion push events with minimal locking while multiple subscribers independently read and ack progress.

## Important APIs, Types, And Functions

`MultiCursorRingBuffer` stores event slots, `start`, `end`, cursor map, cursor-map lock, GC counter/frequency. `SubscriberCursor` stores `sendCursor`, `ackCursor`, mutex, and `ackError`. Public methods include `NewMultiCursorRingBuffer`, `AddCursor`, `RemoveCursor`, `AllEventsAcknowledged`, `Push`, `GetEvent`, `ResetSendCursor`, and `AckEvent`. Internal helpers `collectGarbage`, `getOldestAckCursor`, and `searchIndexOfSeqID` manage space reclamation and acknowledgement lookup.

## Control Flow

`Push` writes at `end`, advances it, and periodically or urgently calls `collectGarbage`. GC finds the oldest acknowledgement cursor and frees events before it; if the buffer is out of space and subscribers have not acknowledged the oldest event, it advances affected cursors and reports the dropped sequence ID. `GetEvent` reads the next event for one subscriber and advances its send cursor if non-nil. `AckEvent` validates the acknowledged sequence against sent events, handles exact next acknowledgements, calculated offsets, skipped/dropped sequence IDs, and a ring-aware binary search fallback.

## State And Persistence

All state is in memory. Cursor state determines what each subscriber can receive and when events can be garbage-collected. `ackError` excludes a subscriber from shutdown blocking when its ack cursor is invalid, usually during startup before the buffer has been repopulated.

## Dependencies And Integration Points

It depends on generated `beewatch.Event`. `metadata.Manager` is the single writer through `Push`; subscriber handlers call `AddCursor`, `GetEvent`, `AckEvent`, `ResetSendCursor`, `RemoveCursor`, and `AllEventsAcknowledged`.

## Risks And Test Signals

This is the most concurrency-sensitive BeeWatch type. It intentionally avoids buffer-wide locks on reads/pushes, so correctness depends on a single writer and cursor locking discipline. `collectGarbage` has a likely bug when dropping the oldest unacknowledged event: it clears the old start, advances `start`, then returns `b.buffer[b.start].SeqId`, which is the new oldest event, not the dropped event. Nil holes are noted as a TODO risk in `AckEvent`. Tests cover many wraparound, GC, ack, and binary-search cases but do not cover race detector concurrency or dropped sequence ID return accuracy.
