# sources/distributed-fs/ipfs-kubo/core/corerepo/gc.go

## Purpose
Implements repository garbage collection orchestration, storage watermark checks, and result aggregation.

## Important APIs, Types, and Functions
Defines `ErrMaxStorageExceeded`, `GC`, `NewGC`, `BestEffortRoots`, `GarbageCollect`, `CollectResult`, `MultiError`, `GarbageCollectAsync`, `PeriodicGC`, `ConditionalGC`, and `(*GC).maybeGC`.

## Control Flow and State
`NewGC` reads repo config, initializes missing storage defaults in the repo config, parses storage max and watermark, and computes slack. GC roots are derived from MFS root. `GarbageCollect` and async variant call `gc.GC` over blockstore/datastore/pinner. `CollectResult` drains result channels, calls removal callbacks, and aggregates errors. Periodic/conditional GC compares storage usage plus offset to the GC watermark and runs GC when exceeded.

## Dependencies and Integration Points
Depends on Kubo core node, repo config/storage usage, Kubo `gc`, Boxo MFS, CIDs, humanize byte parsing, and logging. It interacts with add paths through blockstore GC locks and pin roots.

## Risks and Test Signals
Risks include mutating config defaults unexpectedly, best-effort root failures, multi-error construction assuming at least one error, GC running too often/late, and context cancellation while draining. Tests should cover watermark thresholds, config defaulting, result aggregation, and add-vs-GC concurrency; `coreunix/add_test.go` exercises live add safety.
