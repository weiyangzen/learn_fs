# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/NoopBlockDeletionContext.java

## Purpose
`NoopBlockDeletionContext` is a null-object implementation of `BlockDeletionContext` for operations that should not register block deletions.

## Important APIs, types, and functions
It exposes singleton `INSTANCE`. `registerBlockForDeletion(long)` and `close()` intentionally do nothing.

## Control flow
There is no branching. Callers can pass the singleton wherever a block deletion context is required but no block-master cleanup should be performed.

## State and persistence behavior
The class is stateless and causes no persistence side effects. It is used by `RpcContext.NOOP` and read-only or test operations.

## Dependencies and integration points
It implements `BlockDeletionContext` and integrates with `RpcContext` construction.

## Risks
Using this context in a path that actually deletes inodes with blocks can leave orphaned blocks. Its safety depends entirely on caller intent.

## Test signals
Tests should verify it is accepted by `RpcContext` and that operations using it do not call block deletion. Most coverage is indirect.
