# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/schedule.go

## Purpose
This file provides the lifecycle worker's in-memory pending queue. It orders `Match` values by due time so the dispatcher can poll for ready actions and leave future work in place.

## Important APIs and functions
`Schedule` wraps a `scheduleHeap` with a mutex. `NewSchedule` constructs an empty schedule. `Add` pushes a match. `Len` returns pending count. `NextDue` exposes the earliest due time without popping. `Drain` pops every match whose `DueTime <= now` and returns them in due-time order. `scheduleHeap` implements `heap.Interface` with `Less` ordered by `Match.DueTime.Before`.

## Control flow and state behavior
All public methods take the mutex before reading or mutating the heap, making concurrent producer/consumer use safe at the data-structure level. The queue is ephemeral process memory; pending lifecycle work is not persisted here. Duplicate entries are intentionally allowed, because schedule-time dedup would need extra indexing while dispatcher identity CAS resolves stale duplicates safely.

## Dependencies and integration points
The schedule depends on the standard `container/heap`, `sync`, and `time` packages plus the local `Match` type. It is consumed by the lifecycle dispatch loop, which calls `Drain` on each tick and uses `NextDue`/`Len` for visibility or sleeping decisions.

## Risks and edge cases
Duplicates can grow heap size for hot keys if upstream routing over-emits. The heap ordering is only by due time; equal due times have no stable tie-break. Because state is in-memory, process restarts require bootstrap or event replay to restore pending work.

## Test signals
`schedule_test.go` verifies empty behavior, ordering, inclusive drain boundary, duplicate preservation, no-op drain before any item is due, heap invariants after partial drain and add-after-drain, ascending drain order, and concurrent add/drain race safety.
