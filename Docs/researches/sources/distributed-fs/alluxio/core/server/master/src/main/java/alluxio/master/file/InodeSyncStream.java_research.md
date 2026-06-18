# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/InodeSyncStream.java

## Purpose
`InodeSyncStream` implements metadata synchronization between Alluxio inodes and mounted under file systems. It loads missing UFS metadata, updates inode attributes when UFS metadata changes, deletes Alluxio-only inodes when UFS entries disappear, recursively processes descendants, and maintains sync-path timestamps and metrics.

## Important APIs, types, and functions
The class exposes `sync()` returning `SyncStatus.OK`, `FAILED`, or `NOT_NEEDED`. Constructors accept a root `LockingScheme`, `DefaultFileSystemMaster`, sync cache, RPC context, descendant scope, common options, audit hooks, force/load flags, and absent-cache behavior. Core methods are `syncInternal`, `processSyncPath`, `syncInodeMetadata`, `syncExistingInodeMetadata`, `loadMetadataForPath`, `loadMetadata`, `loadFileMetadataInternal`, `loadDirectoryMetadata`, `loadMountPointDirectoryMetadata`, and `getMetadataSyncRpcContext`. `mergeCreateComplete` compacts file create/complete journal sequences.

## Control flow
`sync()` first checks `LockingScheme.shouldSync` and optionally acquires path-based metadata sync locks to deduplicate concurrent syncs. `syncInternal` records a sync start time, locks the root path, syncs it, then drains `mPendingPaths` through `mMetadataSyncService` up to configured concurrency. Existing inodes are compared with UFS fingerprints via `UfsSyncUtils.computeSyncPlan`; plans can update metadata, delete the inode Alluxio-only, load metadata, or queue children. Missing paths fetch `UfsStatus` and create file or directory metadata. Recursive loads prefetch child statuses, skip temporary files, and respect `DescendantType`.

## State and persistence behavior
The stream is per-sync-operation state: pending paths, submitted futures, status cache, sync counters, and journal context wrappers. Persistent effects go through `DefaultFileSystemMaster` internals and `RpcContext`: create directory/file, complete file, set attributes, delete internal, and set direct-children-loaded. It updates `UfsSyncPathCache` only on successful sync and may use `MetadataSyncMergeJournalContext` plus `FileSystemJournalEntryMerger` to flush merged inode journals asynchronously.

## Dependencies and integration points
It is tightly coupled to `DefaultFileSystemMaster`, `InodeTree`, `LockedInodePath`, `InodeLockManager`, `ReadOnlyInodeStore`, `MountTable`, UFS clients, `UfsStatusCache`, absent path cache, ACL objects, `UfsSyncUtils`, metrics, journal contexts, operation contexts, and configuration keys for traversal order, concurrency, sync interval, journaling, ACL, and prefetch. It backs explicit metadata sync RPCs, lazy path loading, active sync, and list/status flows.

## Risks
This is high-risk concurrency and persistence code. Callers must not hold conflicting inode write locks before `sync()`. Cancellation is cooperative and checked while waiting for UFS tasks and while draining jobs. Some child futures are cancelled after failure, so partial syncs can leave only some metadata refreshed. UFS status caching and ACL-dependent fingerprint construction must match UFS behavior. Journal merging must preserve replay equivalence. The code uses a shared `RpcContext` unless merge journaling creates wrapped contexts, so resource close and flush order matter. Configuration switches change traversal, load-only semantics, and failure reporting.

## Test signals
There are dedicated sync tests: metadata sync behavior, concurrent sync deduplication, flush-journal behavior, metrics, and journal context merge tests. Additional signals come from partial listing, metadata load, mount point, ACL, and UFS status cache tests. Strong coverage should include recursive UFS additions/deletions, changed mode/owner/group/fingerprint, missing UFS entries, persisted files under active persistence, cancellation, and both BFS/DFS traversal.
