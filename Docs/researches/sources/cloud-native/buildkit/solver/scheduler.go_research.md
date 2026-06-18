# sources/cloud-native/buildkit/solver/scheduler.go

## Purpose
This file is the event scheduler for BuildKit solver edges. It owns the dispatch loop that unparks edges, routes pipe requests between dependent edges, handles asynchronous function requests, and merges equivalent edges when cache-key state proves they can share work.

## Important APIs and Types
`newScheduler` creates a `scheduler`, initializes wait queues and pipe maps, and starts `loop`. `scheduler.Stop` stops the loop. `dispatch` is the core edge-processing method. `signal` enqueues an edge for dispatch exactly once. `build` creates a completion request pipe and returns a cloned cached result. `newPipe`, `newRequestWithFunc`, and `pipeFactory` connect `edge.unpark` to input and function requests. `mergeTo` rewires pipes and secondary exporters from a source edge to a target edge.

## Control Flow
The scheduler loop waits on a stateful condition, pops a queued dispatcher from `next/last`, removes it from `waitq`, and calls `dispatch`. Dispatch receives outgoing pipe updates, records whether active outgoing requests remain, calls `e.unpark`, prunes completed incoming/outgoing pipes, then considers cache-key based merging. Merge is skipped if edges are dependencies of each other or if an ignore-cache edge would incorrectly merge into a non-ignore-cache target. On successful merge, incoming pipes are retargeted, outgoing pipes are moved and canceled, the target is signaled, and secondary exporter data is copied from the source.

## State and Persistence
State is in-memory scheduler state: wait queue membership, linked dispatch queue, incoming and outgoing pipe lists, and condition state. It does not persist data, but it controls result lifetime indirectly through active edges and pipes.

## Dependencies and Integration Points
It depends on solver `edge` internals, `solver/internal/pipe`, `util/cond`, `errdefs`, and scheduler debug hooks. `edgeFactory` bridges the scheduler to the shared active graph maintained by the solver.

## Risks
Deadlocks can arise if `edge.unpark` leaves only incoming or only outgoing pipes open; the scheduler detects this and marks the edge failed with an internal error. Merge correctness is delicate: dependency cycles, stale owners, ignore-cache semantics, and secondary exporter propagation all need to stay consistent with edge state.

## Test Signals
`scheduler_test.go` heavily exercises this behavior: active graph sharing, parallel builds, cancellations, slow cache, selectors, cache export, merged edge races/cycles, stale edge merge, load failures, and input request deadlock regressions.
