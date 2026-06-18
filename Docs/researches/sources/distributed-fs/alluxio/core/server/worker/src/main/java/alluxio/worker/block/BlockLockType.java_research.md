# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockType.java

Purpose: `BlockLockType` enumerates block lock modes for `BlockLockManager`.

Important API: enum values `READ(0)` and `WRITE(1)` plus `getValue`. Control flow is absent; callers choose the enum to acquire either a read lock or write lock on a block.

State and persistence are enum constants with integer values. Dependencies are only Java enum support and thread-safety annotation. Integration points are block store operations that call `BlockLockManager.acquireBlockLock` or `tryAcquireBlockLock`. Risks are low; the numeric values are not self-validating and should only be used where the local protocol expects them. No direct tests are in this subset.
