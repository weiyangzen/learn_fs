# sources/cloud-native/containerd/internal/eventq/eventq.go

## Purpose
Implements a generic in-process event queue with fan-out subscribers and a short retention window for events sent before any subscriber exists.

## Important APIs, Types, And Functions
`EventQueue[T]` exposes `Send`, `Subscribe`, and `Shutdown`. `New` starts the dispatcher goroutine. `eventSubscription` wraps subscriber channel delivery and close signaling.

## Control Flow
The dispatcher receives events, publishes to active subscribers, queues events if none are active, drains queued events to a new subscriber, discards expired events via `discardFn`, and closes subscriber channels on shutdown.

## State And Persistence
State is in-memory: event channels, subscriber list, discard queue, and timers. No events persist beyond process lifetime.

## Dependencies And Integration Points
Uses Go channels, generics, `io.Closer`, and `time`. It can support runtime event notifications where late subscribers should receive recent events.

## Risks
`Shutdown` sends on then closes `shutdownC`; concurrent repeated shutdowns can panic. `Subscribe` sends on `subscriberC` without a shutdown select, so subscribing after shutdown may block. Subscriber channel buffer is fixed at 100 and slow subscribers can backpressure publishing.

## Test Signals
`eventq_test.go` covers single/multiple subscribers, missed events, late subscribers, time-based discard, and shutdown discard.
