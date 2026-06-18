# sources/distributed-fs/beegfs-go/watch/internal/subscribermgr/handler.go

## Purpose

This file implements the lifecycle manager for one subscriber. It connects with retry/backoff, starts bidirectional event and acknowledgement loops, advances the subscriber's ring-buffer cursor, handles reconnects, and disconnects on shutdown or stream errors.

## Important APIs, Types, And Functions

`Handler` wraps context/cancel, logger, `MultiCursorRingBuffer`, `HandlerConfig`, a `subscriber.Subscriber`, a mutex, and `lastSeqID`. `newHandler` adds a cursor for the subscriber ID and initializes state. `Handle` is the state machine. `connectLoop` applies exponential backoff with jitter. `receiveLoop` reads subscriber acknowledgements and calls `AckEvent`. `sendLoop` polls the event buffer and calls `Send`. `doDisconnect` and `Stop` handle cleanup and cancellation.

## Control Flow

`Handle` locks the handler for its lifetime, connects when disconnected, starts receive and send loops when connected, and disconnects when either loop exits or the handler context is canceled. On connect, it waits briefly for an initial acknowledgement so it can avoid resending events the subscriber already persisted. It then resets the send cursor to the ack cursor and streams events on a poll interval until no more events are available or send fails.

## State And Persistence

`lastSeqID` avoids duplicate sends after restart/reconnect even when the ring buffer is not yet repopulated enough for `AckEvent` to move the cursor. Durable progress is still subscriber-owned. The handler owns one cursor in the shared buffer for the subscriber ID; removal is done by the manager when a subscriber is deleted.

## Dependencies And Integration Points

It depends on `subscriber.Interface`, `types.MultiCursorRingBuffer`, generated `beewatch.Response` via the subscriber interface, and zap. It integrates tightly with `metadata.Manager` by consuming from the same event buffer that metadata pushes into.

## Risks And Test Signals

Polling adds delivery latency and CPU tradeoffs controlled by `PollFrequency`. The backoff clamp can produce values near `MaxReconnectBackOff - rand`, so zero or small config values should be validated elsewhere. Ack errors are logged once and tolerated during startup, which is pragmatic but can hide persistent subscriber bugs at debug level. Tests cover construction only; higher-value tests should simulate subscriber sends/acks, reconnects, duplicate suppression, and shutdown with unacknowledged events.
