# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeIterationResult.java

Purpose: pairs an `Inode` with the `LockedInodePath` used to reach it during inode tree iteration.

Important APIs and types: constructor stores inode and locked path. `getInode`, `getLockedPath`, and `toString` expose the pair.

Control flow: `DefaultSyncProcess.SyncProcessState.getNextInode` returns iteration results from a `SkippableInodeIterator`. Sync logic compares the result's locked path URI with current UFS item and may traverse, delete, update, or skip children.

State and persistence behavior: value object only. The locked path manages live locks protecting persistent metadata operations.

Dependencies and integration points: depends on `Inode` and `LockedInodePath`. Integrates with inode iteration, lock management, and metadata sync diffing.

Risks: consumers must close or manage the underlying locked path according to iterator semantics; this wrapper does not own lifecycle beyond holding the reference. `toString` only includes the path, not inode id.

Test signals: tests should cover getter behavior and integration with skippable inode iteration and lock lifecycle.
