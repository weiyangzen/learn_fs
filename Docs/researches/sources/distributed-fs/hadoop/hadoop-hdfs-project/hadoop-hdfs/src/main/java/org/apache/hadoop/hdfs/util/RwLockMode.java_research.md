<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java

## Purpose
`RwLockMode` enumerates read/write lock domains for fine-grained locking.

## APIs and Types
The enum constants are `GLOBAL`, `FS`, and `BM`.

## Control Flow
There is no behavior. Callers pass modes to `RwLock` implementations to select the lock domain.

## State and Persistence
Enum constants are static JVM state only. No persistence.

## Dependencies and Integration
It integrates directly with `RwLock` and FSNamesystem fine-grained locking code. `GLOBAL` is the default used by `RwLock` compatibility methods, while `FS` and `BM` represent filesystem and block-manager scopes.

## Risks
Adding modes is source-compatible but can require implementation updates. Misusing a narrower mode where global coordination is required can introduce races.

## Test Signals
Tests should verify all `RwLock` implementations handle every enum constant and that default interface methods still route to `GLOBAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLockMode.java -->
