# sources/cloud-native/buildkit/solver/progress.go

## Purpose
This file exposes build progress from a `Job` as client-facing `SolveStatus` messages. It translates internal progress records into vertex updates, status bars, logs, and warnings while preserving ordering and adding final cancellation/completion updates for active vertices.

## Important APIs
`(*Job).Status(ctx, ch)` is the public streaming loop. It reads from `j.pr.Reader(ctx)` and writes `*client.SolveStatus` until EOF, error, or context cancellation. `vertexStream` tracks the last known `client.Vertex` by digest and whether a vertex was observed as cached. Its methods are `append`, `markCached`, and `encore`.

## Control Flow
`Status` reads batches from the progress reader. Each item is switched by `p.Sys` type: `client.Vertex` is passed through `vertexStream.append`; `progress.Status` becomes a `client.VertexStatus`; `client.VertexLog` and `client.VertexWarning` inherit the vertex digest and timestamp from progress metadata when missing. Before sending a status batch, vertices are sorted by start time, and status/log entries by timestamp. On EOF, the deferred block emits `vertexStream.encore()` updates and closes the channel.

## State and Persistence
State is in-memory only. `vertexStream.cache` stores mutable vertex copies, and `wasCached` records cached subgraphs. `append` also marks incomplete input vertices as cached when a downstream vertex starts and the input has not completed, producing deterministic client-side cached events for skipped vertices.

## Dependencies and Integration Points
It integrates with `client.SolveStatus`, `util/progress`, BuildKit logging, and digest metadata stored on progress records. The output channel is consumed by BuildKit clients and frontends that render solve progress.

## Risks
Progress entries without `vertex` metadata are skipped with warnings, so producer bugs can silently reduce UI detail. Type assertions on metadata assume a `digest.Digest`; malformed metadata can panic. `encore` marks active uncached vertices as canceled when the stream ends without explicit completion, which is useful for cleanup but can make abrupt stream termination look like vertex cancellation.

## Test Signals
No direct tests are in this subset. Scheduler and solver tests indirectly rely on jobs completing and being discardable, but progress rendering details are not directly asserted here.
