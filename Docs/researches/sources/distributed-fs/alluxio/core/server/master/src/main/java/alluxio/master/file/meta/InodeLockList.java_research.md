# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeLockList.java

Purpose: interface describing a locked inode path as an ordered list of inode and edge locks. It formalizes lock ordering, downgrade, extension, and release behavior for inode tree concurrency control.

Important APIs and types: methods lock root edge, inode, and child edge; unlock last inode or edge; downgrade all locks or last edge; push a write-locked edge forward; inspect lock mode, locked inodes, indexed inode, inode count, whether the list ends in an inode, emptiness, and the associated `InodeLockManager`; and close all locks.

Control flow: implementations build paths with read locks followed by write locks. `pushWriteLockedEdge` supports traversal patterns that hold a write edge only at the frontier while downgrading prior locks to read. Composite implementations can extend existing lock lists.

State and persistence behavior: in-memory lock state only, but it protects all persistent inode metadata operations. Correct use prevents concurrent create/delete/update races.

Dependencies and integration points: depends on `LockMode`, `Inode`, `InodeView`, and `InodeLockManager`. Used by locked inode paths, inode tree traversal, metadata sync, create/delete/rename, and mount handling.

Risks: annotated not thread-safe; each lock list should be owned by one thread. Implementations must maintain strict lock ordering to avoid deadlocks. Callers must always close lists to release locks.

Test signals: tests should cover root edge locking, inode/edge order, downgrade semantics, push-write behavior, composite behavior, close idempotence if promised by implementation, and deadlock-sensitive traversal patterns.
