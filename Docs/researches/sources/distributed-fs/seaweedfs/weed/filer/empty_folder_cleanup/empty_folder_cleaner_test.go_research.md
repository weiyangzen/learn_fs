# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner_test.go

## Purpose
This file tests `EmptyFolderCleaner` helper logic, event handling, ownership, cache behavior, policy handling, queue processing, and deletion decisions.

## Important APIs, Types, and Functions
- `mockFilerOps` implements `FilerOperations` with configurable function fields.
- Tests cover `isUnderPath`, `isUnderBucketPath`, `autoRemoveEmptyFoldersEnabled`, `ownsFolder`, create/delete event handling, disabled behavior, cached counts, stop, cache eviction, FIFO/time ordering, aged processing, bucket-policy skip, and directory-marker preservation.

## Control Flow and State
Tests often construct `EmptyFolderCleaner` structs directly with a lock ring, host, maps, cleanup queue, and stop channel. This avoids background goroutines unless testing constructor-level behavior is needed. Mock filer functions record deletions or provide counts/attrs/marker status so tests can drive `executeCleanup` branches.

## State and Persistence Behavior
No external persistence. Tests verify that in-memory caches and queues are updated and that persistent deletion would be requested only for eligible implicit empty folders.

## Dependencies and Integration Points
Tests depend on `lock_manager.LockRing`, `pb.ServerAddress`, S3 constants, and `util.FullPath`. They validate integration assumptions around consistent-hash ownership and bucket cleanup policy attributes.

## Risks and Edge Cases
- Some tests call `Stop` on manually constructed cleaners; they are valid because `stopCh` is initialized, but double stop remains untested.
- Ownership tests may skip one branch if a non-owned folder cannot be found in the sample.
- There is limited coverage for errors from `CountDirectoryEntries`, `DeleteEntryMetaAndData`, `GetEntryAttributes`, and `IsDirectoryKeyObject`.

## Test Signals
The tests provide good signal for race-prevention behavior: create cancels cleanup, only aged items are processed, cache eviction skips queued folders, explicit directory markers are preserved, and policy `"true"` disables auto-removal.
