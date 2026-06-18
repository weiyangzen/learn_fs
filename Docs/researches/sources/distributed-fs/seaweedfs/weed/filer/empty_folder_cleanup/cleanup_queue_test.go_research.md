# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue_test.go

## Purpose
This file tests the `CleanupQueue` data structure used by empty-folder cleanup.

## Important APIs, Types, and Functions
Test functions cover `Add`, out-of-order add, duplicate older/newer events, `Remove`, `Pop`, `Peek`, `Contains`, `ShouldProcess`, `Clear`, `OldestAge`, ordering, and concurrent operations.

## Control Flow and State
The tests construct queues with controlled max sizes and ages, add synthetic folder paths with explicit times, and verify list order by popping. The concurrency test runs goroutines for add, remove, pop, and read methods to catch panics or map/list inconsistencies.

## State and Persistence Behavior
No persistence. The tests validate in-memory queue invariants: deduplication map and linked-list order stay synchronized.

## Dependencies and Integration Points
It depends only on Go's `testing` and `time` packages and the cleanup queue implementation.

## Risks and Edge Cases
- The concurrent test is a smoke test and does not assert a final deterministic state.
- Time-based tests use `time.Now`/`time.Since`, so very slow or skewed test environments could affect boundary assertions.

## Test Signals
These tests give strong signal for queue ordering and deduplication behavior. They do not directly test integration with `EmptyFolderCleaner`, which is covered separately.
