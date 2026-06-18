# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsAbsentPathCache.java

## Purpose
`UfsAbsentPathCache` is the file-master abstraction for remembering paths or ancestors known to be absent in the under file system. It lets metadata operations avoid repeated UFS existence checks when a path has recently been proven absent.

## Important APIs, types, and functions
The interface defines `processAsync(AlluxioURI, List<Inode>)`, `addSinglePath(AlluxioURI)`, `processExisting(AlluxioURI)`, and `isAbsentSince(AlluxioURI, long)`. Constants `ALWAYS = -1` and `NEVER = Long.MAX_VALUE` express validity thresholds. The nested `Factory.create(MountTable, Clock)` returns `NoopUfsAbsentPathCache` when `MASTER_UFS_PATH_CACHE_THREADS <= 0`, otherwise `AsyncUfsAbsentPathCache`.

## Control flow
Implementations decide the actual traversal and mutation behavior. The contract states that async processing sequentially walks path components against UFS, existing-path processing removes or adjusts absence state, and `isAbsentSince` checks the path and its ancestors against the supplied timestamp.

## State and persistence behavior
The interface itself has no persisted state. Implementations maintain cache entries in memory, and factory selection is entirely configuration driven. State is safe to lose on master restart because UFS absence can be rediscovered.

## Dependencies and integration points
It integrates with `MountTable`, `Inode` prefix information, `AlluxioURI`, and the UFS path cache thread configuration. `DefaultFileSystemMaster` and inode sync paths use it when resolving paths against UFS.

## Risks
Behavior depends heavily on implementation details outside this file. Disabling via thread count silently switches to a no-op cache, so tests and production diagnostics must account for that. Stale absent entries can hide newly-created UFS paths until invalidated or considered too old by the `absentSince` threshold.

## Test signals
Factory tests should validate disabled and enabled selection. Implementation tests should cover ancestor absence, existing-path invalidation, mount boundary behavior, async ordering, and `ALWAYS`/`NEVER` threshold semantics.
