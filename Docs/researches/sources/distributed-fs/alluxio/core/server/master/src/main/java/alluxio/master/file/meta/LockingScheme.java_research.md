# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/LockingScheme.java

## Purpose
`LockingScheme` bundles a target path, the caller's desired inode-tree lock pattern, and the metadata-sync decision for that path. It lets file master RPC code compute whether a read or metadata update must be upgraded to structural locking because UFS sync may delete or create namespace entries.

## Important APIs, Types, and Functions
Constructors accept either an explicit boolean sync decision or RPC common options plus `UfsSyncPathCache` and `DescendantType`. `getDesiredPattern()` returns the caller-requested pattern, `getPattern()` returns `WRITE_EDGE` when sync is required or the desired pattern otherwise, `getPath()` returns the target URI, and `shouldSync()` exposes the `SyncCheck`.

## Control Flow, State, and Persistence
The class is immutable and has no persistence. The option-based constructor chooses a sync interval from client options if present or server configuration `USER_FILE_METADATA_SYNC_INTERVAL` otherwise, then asks `pathCache.shouldSyncPath()`. `getPattern()` is the key control-flow decision: sync requires write-edge locking because syncing can remove an inode deleted in UFS.

## Dependencies and Integration Points
`InodeTree.lockInodePath(LockingScheme, ...)` consumes the scheme. The class integrates with RPC common options, `UfsSyncPathCache`, `DescendantType`, and `SyncCheck`, and is typically created by `DefaultFileSystemMaster` before path locking and metadata sync.

## Risks
Using the boolean constructor with `shouldSync=true` bypasses path-cache deduplication and loses last-sync-time information; the source comment explicitly discourages it when the option-based constructor is available. A sync decision upgrades locking to `WRITE_EDGE`, which can reduce concurrency for otherwise read-only operations.

## Test Signals
Tests should verify default sync interval fallback, client sync interval override, descendant type forwarding to `UfsSyncPathCache`, `getPattern()` upgrade on sync, and no upgrade when `SyncCheck` says sync is unnecessary.
