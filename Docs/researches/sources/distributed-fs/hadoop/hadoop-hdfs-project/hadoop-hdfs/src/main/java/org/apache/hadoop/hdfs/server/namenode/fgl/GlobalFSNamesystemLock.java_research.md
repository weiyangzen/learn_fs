# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/GlobalFSNamesystemLock.java

## Purpose

`GlobalFSNamesystemLock.java` implements `FSNLockManager` with a single traditional `FSNamesystemLock`, ignoring fine-grained lock modes. The source was read as a complete 150-line file.

## Important APIs, Types, and Functions

The class owns one `FSNamesystemLock` named `lock` and delegates every lock, unlock, metric, threshold, and testing hook method to it.

## Control Flow

All `RwLockMode` values acquire the same read or write lock. Unlock overloads pass operation names, suppression flags, or lock-report suppliers to the underlying lock. `hasReadLock` treats a current-thread write lock as satisfying read ownership.

## State and Persistence Behavior

State is the in-memory global read/write lock and its metrics. It protects persistent NameNode namespace state indirectly by serializing in-memory mutations before they are logged or saved.

## Dependencies and Integration Points

It integrates with `FSNamesystemLock`, `RwLockMode`, `MutableRatesWithAggregation`, and test replacement of the underlying `ReentrantReadWriteLock`.

## Risks and Edge Cases

Because all modes map to one lock, code tested only with this implementation can miss fine-grained ordering bugs. Conversely it provides simpler, conservative behavior for deployments not using fine-grained locking.

## Test Signals

Tests should verify delegation, read/write hold checks, queue and long-hold metrics, threshold changes, supplier reporting, interruptible acquisition, and `setLockForTests`/`getLockForTests`.
