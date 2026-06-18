# sources/distributed-fs/juicefs/pkg/meta/context_cancellation_test.go

## Purpose

This file is a focused regression suite for metadata context cancellation. It verifies that long-running or transactional metadata paths notice canceled `Context` values and return interruption/cancellation errors instead of continuing work indefinitely.

## Important Tests And Helpers

`createSummaryTestTree` builds a configurable tree of directories and files under a parent inode using `Mkdir` and `Create`. It is used to make tree-summary traversal large enough to invoke progress callbacks repeatedly.

`TestGetTreeSummaryCanceledByProgressCallback` creates an in-memory KV metadata engine, initializes it, populates 50 directories with 20 files each, and calls `GetTreeSummary` with a progress callback. After ten progress updates the callback cancels the context; the expected result is `syscall.EINTR`.

`TestKVTxnReturnsEINTRWhenContextAlreadyCanceled` creates a `memkv` engine, cancels a context before calling `kvMeta.txn`, and expects `syscall.EINTR` without running useful transaction work. `TestBadgerKVTxnReturnsEINTRWhenContextAlreadyCanceled` repeats the same signal against a badger-backed TKV URL in a temp directory.

`TestCleanupTrashBeforeReturnsEINTRWhenContextAlreadyCanceled` initializes a KV engine and calls `CleanupTrashBefore` with an already-canceled context. It accepts `EINTR` or `0` because an empty-trash fast path may complete before observing cancellation.

`TestCleanupDelayedSlicesReturnsCanceledWhenContextCanceled` injects 128 delayed-slice keys through a transaction, cancels the context, then calls `doCleanupDelayedSlices`; the expected Go error wraps or equals `context.Canceled`.

`TestRemoveEmptyDirReturnsEINTRWhenCanceled` creates an empty directory, cancels a context, and verifies recursive `Remove` returns `EINTR`.

## Control Flow

Each test constructs an isolated metadata engine, resets it, initializes the standard test format, creates only the state needed for that cancellation path, then cancels a `NewContext` before or during the target operation. Assertions use either syscall errno values (`EINTR`) for public metadata APIs or `errors.Is(err, context.Canceled)` for lower-level cleanup internals.

## State And Persistence Behavior

The tests use volatile `memkv` stores for most cases and a temporary badger store for the TKV transaction case. They persist enough metadata state to exercise traversal, trash cleanup, delayed-slice cleanup, and remove logic, but all stores are test-local. The delayed-slice test writes raw delayed slice keys with `km.delSliceKey`, so it is coupled to KV persistence layout.

## Dependencies And Integration Points

The file depends on `newKVMeta`, `NewClient`, `kvMeta`, `kvTxn`, `TreeSummary`, `RootInode`, `testConfig`, `testFormat`, and public `Meta` operations. It integrates with Go `context`, `errors`, `filepath`, `syscall`, and `time`. It provides direct regression coverage for cancellation checks in KV transactions, cleanup workers, tree traversal, and recursive removal.

## Risks And Test Signals

These tests are strongest for KV-family engines; Redis and SQL cancellation behavior is not directly exercised here. Some paths accept fast-path success when there is no work, so they signal responsiveness without requiring every empty operation to fail. Failures indicate operations may ignore cancellation and block unmounts, CLI interrupts, or maintenance jobs.
