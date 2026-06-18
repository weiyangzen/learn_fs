# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/CatchupFuture.java

## Purpose
`CatchupFuture` aggregates one or more journal catch-up threads for cancellation and termination waiting.

## Important APIs, Types, And Functions
`allOf` combines threads from multiple futures. `completed` creates an empty future. Constructors wrap one or more `AbstractCatchupThread`s. `cancel` forwards to each thread; `waitTermination` waits on each.

## Control Flow, State, Dependencies, Risks, And Tests
The state is a list of live or completed catch-up threads, with no persistence. Dependencies are `AbstractCatchupThread` and collection utilities. Risks include serial waiting where one hung thread blocks observation of later failures, duplicate threads if futures overlap, and cancellation ordering not waiting. Tests should cover empty futures, aggregation, cancel forwarding, wait forwarding, and duplicate/failed thread behavior.
