# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/cleanup_queue.go

## Purpose
This file implements a thread-safe, deduplicated, time-ordered queue for folders that may need empty-folder cleanup.

## Important APIs, Types, and Functions
- `CleanupQueue` owns a mutex, a doubly linked list of `queueItem`, a map from folder path to list element, and max size/age thresholds.
- `queueItem` stores folder, triggering child name, and queue time.
- Public methods: `NewCleanupQueue`, `Add`, `Remove`, `ShouldProcess`, `Pop`, `PopOlderThan`, `Peek`, `Len`, `Contains`, `Clear`, and `OldestAge`.
- Internal helpers: `insertSorted` and `shouldProcessLocked`.

## Control Flow and State
`Add` deduplicates by folder. New folders are inserted in event-time order. Existing folders are updated only if the new event time is later, in which case the list element is removed and reinserted. Processing can be triggered by size or age, but the cleaner primarily uses `PopOlderThan` to avoid deleting folders before a delay has elapsed. All operations hold the queue mutex.

## State and Persistence Behavior
The queue is in-memory only. It tracks pending cleanup candidates and does not survive process restart.

## Dependencies and Integration Points
It is used by `EmptyFolderCleaner` to queue delete-event parent folders, cancel cleanup on create events, process aged items, and skip evicting cache entries still queued.

## Risks and Edge Cases
- Ordering is by event time, not enqueue wall-clock time; incorrect event timestamps can delay or accelerate cleanup.
- Duplicate older events are ignored, preserving newer trigger information.
- `ShouldProcess` uses `time.Since`, so tests and behavior depend on wall clock.
- The queue exposes `maxAge` as a field used directly by the cleaner, coupling internals across files in the same package.

## Test Signals
`cleanup_queue_test.go` covers add/update, out-of-order insert, duplicate older/newer events, remove, pop, peek, contains, size/age processing triggers, clear, oldest age, ordering, and concurrent access smoke testing.
