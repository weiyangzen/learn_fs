# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metastore/rocks/RocksCheckpointed.java

## Purpose
`RocksCheckpointed` provides default `Checkpointed` implementations for classes backed by `RocksStore`. It standardizes exclusive locking around RocksDB checkpoint and restore operations.

## Important APIs and Types
- Extends `Checkpointed`.
- Requires `getRocksStore()`.
- Default async and stream `writeToCheckpoint` methods take `lockForCheckpoint`.
- Default async and stream restore methods take `lockForRewrite`.
- Wraps failures in `AlluxioRuntimeException` for async paths.

## Control Flow
Async checkpoint writes run on the supplied executor, create a subdirectory named by `getCheckpointName`, acquire checkpoint lock, and ask `RocksStore` to snapshot. Stream checkpoint writes acquire the same lock and stream compressed checkpoint data. Restores acquire rewrite locks because database contents are replaced.

## State and Persistence
No local state. It coordinates persistence of the underlying RocksDB directory/checkpoint stream.

## Dependencies and Integration Points
Implemented by `RocksInodeStore` and `RocksBlockMetaStore`. Depends on Alluxio checkpoint interfaces, `RocksStore`, executor services, and gRPC status/error typing for runtime exceptions.

## Risks and Edge Cases
- Async methods use `CompletableFuture.runAsync`; callers must observe future failures.
- Subdirectory names must match checkpoint names expected by restore.
- Long checkpoint/restore operations block or abort concurrent Rocks readers through `RocksStore` locks.

## Test Signals
Tests should verify lock type selection, subdirectory naming, async exception wrapping, stream checkpoint/restore delegation, and concurrent reader abort behavior through RocksStore fakes.
