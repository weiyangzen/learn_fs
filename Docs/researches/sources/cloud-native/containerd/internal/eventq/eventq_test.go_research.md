# sources/cloud-native/containerd/internal/eventq/eventq_test.go

## Purpose
Tests event queue delivery, replay, discard, and shutdown behavior.

## Important APIs, Types, And Functions
Tests create `EventQueue[int]` instances and use a helper `collector` goroutine that subscribes, records events until channel close, and closes its subscription.

## Control Flow
Scenarios send events before and after subscription, create multiple subscribers, sleep past discard deadlines, call `Shutdown`, and compare collected/discarded slices.

## State And Persistence
All state is in-memory test channels and slices.

## Dependencies And Integration Points
Uses `testing`, `time`, and `testify/assert`.

## Risks
Timing-based discard tests can be flaky on heavily loaded machines. Tests do not cover concurrent `Shutdown`, subscribe-after-shutdown, or slow subscriber backpressure.

## Test Signals
Good behavioral signal for normal delivery semantics and the pre-subscriber retention queue.
