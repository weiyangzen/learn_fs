# sources/cloud-native/nydus/smoke/tests/chunk_dedup_test.go

## Purpose
This suite verifies runtime chunk deduplication across two independent mounts that share the same CAS database. It expects the second mount to issue fewer backend reads because metadata learned from the first mount can be reused.

## Important APIs, Types, And Functions
`ChunkDedupTestSuite` has `TestChunkDedup`, a dynamic generator with a single `iteration` value. It creates a temporary SQLite DB and passes it to `testRemoteWithDedup`. `testRemoteWithDedup` builds two separate texture layers and contexts, disables prefetch, points both contexts at the same `ChunkDedupDb`, mounts each with `tool.NewNydusdWithContext`, verifies file trees, fetches backend metrics, and compares read count and read amount.

## Control Flow
The first mount warms/populates the shared dedup DB while serving the synthetic file tree. The second mount repeats the same access pattern against a fresh workdir but the same DB. The final assertions compare `metrics.ReadCount` and `metrics.ReadAmountTotal`, requiring the first run to be greater than the second.

## State And Persistence
The shared DB path is created outside either Nydus workdir, then removed after the generator scope. Per-mount blob/cache/bootstrap data lives in each context workdir and is destroyed with deferred cleanup.

## Dependencies And Integration Points
The test depends on `nydusd` backend metrics from `/api/v1/metrics/backend`, `texture.PrepareLayerWithContext`, and consistent synthetic layer content. It integrates with runtime chunk dedup lookup/write paths through `ctx.Runtime.ChunkDedupDb`.

## Risks
The test is metric-sensitive: backend read counts may vary with prefetch, cache remnants, daemon implementation changes, or timing. It disables prefetch to reduce noise, but any non-determinism in verification order or cache sharing outside the DB can affect the comparison.

## Test Signals
Primary signals are no backend read errors for either mount and strictly lower read count/bytes for the second mount. These indicate dedup DB reuse rather than merely successful mounting.
