# sources/distributed-fs/seaweedfs/weed/filer/empty_folder_cleanup/empty_folder_cleaner.go

## Purpose
This file implements asynchronous deletion of implicit empty folders in bucket paths. It listens to create/delete events, queues possibly empty parent folders, delays cleanup, verifies ownership and bucket policy, checks actual emptiness, preserves explicit directory markers, deletes empty metadata, and eagerly cascades cleanup to parent folders.

## Important APIs, Types, and Functions
- Constants define default count check limit, cache expiry, queue size/age, and processor sleep.
- `FilerOperations` abstracts the filer methods needed by the cleaner.
- `folderState` caches rough counts and last add/delete/check times.
- `bucketCleanupPolicyState` caches bucket policy lookup results.
- `EmptyFolderCleaner` holds filer ops, lock ring, host identity, caches, cleanup queue, configuration, enabled flag, and stop channel.
- Constructor and controls: `NewEmptyFolderCleaner`, `SetEnabled`, `IsEnabled`, `Stop`, `GetPendingCleanupCount`, and `GetCachedFolderCount`.
- Event and processing methods: `OnDeleteEvent`, `OnCreateEvent`, `cleanupProcessor`, `processCleanupQueue`, and `executeCleanup`.
- Helpers: `ownsFolder`, `countItems`, `deleteFolder`, `getBucketCleanupPolicy`, `autoRemoveEmptyFoldersEnabled`, `isUnderPath`, `isUnderBucketPath`, `cacheEvictionLoop`, and `evictStaleCacheEntries`.

## Control Flow and State
Construction starts background loops for cache eviction and queue processing. Delete events outside the bucket path or owned by another filer are ignored. Owned delete events decrement a rough count and enqueue the directory only if the rough count suggests it may be empty. Create events increment tracked counts and remove the directory from the queue. The processor periodically pops only items older than the queue delay, then `executeCleanup` rechecks enabled state, cached count, event ordering, ownership, bucket policy, actual item count, and explicit directory marker status before deleting. After deleting a folder, it removes cached state and recursively attempts the parent to avoid per-level delay.

## State and Persistence Behavior
Cleaner state is in-memory: rough count cache, bucket policy cache, and queue. Persistent effects are calls to `DeleteEntryMetaAndData` for empty implicit folder metadata. Bucket policy is read from bucket attributes using `s3_constants.ExtAllowEmptyFolders`; missing/empty/non-true values enable automatic cleanup, while `"true"` preserves empty folders.

## Dependencies and Integration Points
It integrates with SeaweedFS lock ring ownership, filer metadata APIs, bucket path extraction, S3 extended attributes, `filer_pb.ErrNotFound`, and glog. It is intended for multi-filer deployments where consistent hashing prevents duplicate cleaners from acting on the same folder.

## Risks and Edge Cases
- `Stop` closes `stopCh` unconditionally; calling it twice would panic.
- Recursive `executeCleanup` can walk many parent levels synchronously.
- Cached rough counts are approximate and rely on final `CountDirectoryEntries` for correctness.
- Policy cache can delay recognition of bucket attribute changes until expiry.
- `autoRemoveEmptyFoldersEnabled` has inverted semantics relative to `ExtAllowEmptyFolders`: `"true"` disables cleanup.
- The cleaner uses background goroutines immediately; tests often construct structs manually to avoid goroutines.
- Lock-ring ownership can change between queue and execution, so recheck is necessary and present.

## Test Signals
`empty_folder_cleaner_test.go` covers path filtering, bucket-depth filtering, policy interpretation, ownership across rings, create cancellation, delete deduplication, disabled cleaner behavior, directory deletion events, cached count updates, stop cleanup, cache eviction, queued-item eviction protection, queue order, aged-only processing, policy-disabled skip, and explicit directory marker preservation.
