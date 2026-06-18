# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/CompositeInodeLockList.java

Purpose: temporary extension of an existing `InodeLockList` without closing or mutating the base list. It lets code lock descendants relative to an already locked path and then release only the added locks.

Important APIs and types: wraps a base lock list and a new `SimpleInodeLockList`, storing the base inode count. Implements all `InodeLockList` methods except `lockRootEdge`, which is unsupported. `nextLockMode` forces added locks to write mode if the base currently ends in a write lock.

Control flow: the first edge lock verifies that it extends from the base list's last inode. Unlock and downgrade operations affect only the sub-list. `pushWriteLockedEdge` either delegates to the sub-list when the last write lock can be downgraded, or acquires additional write locks when the base write lock cannot be modified.

State and persistence behavior: lock state only, no persistence. Correct locking protects inode metadata mutations and reads elsewhere.

Dependencies and integration points: depends on `InodeLockList`, `SimpleInodeLockList`, `InodeLockManager`, `LockMode`, and inode tree traversal/locking code such as locked path descendant operations.

Risks: base lock list is not closed by `close`; callers must manage both lifetimes. Downgrade cannot affect base locks, so write scopes may remain wider than expected. Incorrect extension parent checks could allow inconsistent lock ordering.

Test signals: tests should cover extension from inode and edge, base write mode forcing, downgrade behavior, push write locked edge behavior, close releasing only sub-locks, and index/getLockedInodes composition.
