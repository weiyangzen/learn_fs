# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/RpcContext.java

## Purpose
`RpcContext` aggregates per-RPC resources used by file-system master operations: journal appends, block deletion registration, operation metadata, and cancellation trackers. It enforces close order after an RPC finishes.

## Important APIs, types, and functions
The class implements `Closeable` and `Supplier<JournalContext>`. It exposes singleton `NOOP`, `getJournalContext`, `journal`, `getBlockDeletionContext`, `getOperationContext`, `throwIfCancelled`, `getOpId`, `isCancelled`, `close`, and `get`. `closeQuietly` collects close failures and suppresses secondary exceptions.

## Control flow
Operations receive an `RpcContext`, append journal entries with `journal` or `getJournalContext`, and register block deletions through the block deletion context. On close, the journal context closes first, then block deletion closes. If either close throws, the context rethrows `UnavailableException` where possible or wraps in `RuntimeException`.

## State and persistence behavior
The journal context is the persistence channel for namespace mutations. The explicit close order is important: file-system journal state is flushed before block-master cleanup so a crash is more likely to leave orphaned blocks than inodes pointing to missing blocks.

## Dependencies and integration points
It integrates `BlockDeletionContext`, `JournalContext`, `OperationContext`, `CallTracker`, `OperationId`, and many master internals. `InodeSyncStream`, delete/create operations, active sync journaling, and tests use it directly.

## Risks
The class is not thread-safe. Sharing one context across concurrent metadata sync tasks can be safe only when the underlying journal/operation contexts support it or when `InodeSyncStream` wraps merge contexts appropriately. `throwIfCancelled` throws a generic `RuntimeException`, so callers must convert or handle it consistently. Close failures from both contexts are aggregated but can hide operation-level exceptions if close happens in a finally block without suppression handling.

## Test signals
`RpcContextTest` covers close order, exception propagation/suppression, cancellation trackers, operation ids, and supplier behavior. Integration tests around delete and metadata sync validate journal-before-block cleanup ordering.
