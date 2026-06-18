# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule_test.go

## Purpose
This file tests the lifecycle `Schedule` heap contract. It ensures due-time ordering and mutex-protected concurrent access behave as the dispatcher expects.

## Important APIs and helpers
`mkMatch` creates small `Match` values with an `ActionKey`, `DueTime`, and `ObjectKey`. The tests call `NewSchedule`, `Add`, `Len`, `NextDue`, and `Drain` directly.

## Control flow and state behavior under test
The tests cover an empty schedule returning length zero, no next due time, and nil drain output. They insert matches out of order and assert `NextDue` returns the minimum and `Drain` returns due matches in ascending due-time order. Boundary behavior is pinned as inclusive: an item due exactly at `now` drains. Duplicate matches with the same object key and due time are retained and drained separately. Partial drains leave future entries in the heap, and adding a new earlier entry after a drain correctly updates `NextDue`.

## Dependencies and integration points
The tests use the local router package and `s3lifecycle.ActionKey` only to satisfy the `Match` shape. They implicitly validate `container/heap` usage through public schedule operations rather than inspecting internals.

## Risks and gaps
The concurrent test only asserts no deadlock or data race under race-enabled runs; without `go test -race`, it mainly exercises completion. It does not test process restart recovery because `Schedule` has no persistence layer.

## Test signals
The suite is a clear regression guard for dispatcher timing semantics: no early dispatch, no missed remaining minimum after partial drains, no deduplication, and thread-safe add/drain interactions.
