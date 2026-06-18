<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java

## Purpose
`RwLock` defines the read/write locking abstraction used by FSNamesystem, with support for multiple lock modes.

## APIs and Types
It declares mode-aware read and write lock/unlock methods, interruptible acquisition, and lock-held checks. Default methods route legacy no-mode calls to `RwLockMode.GLOBAL` and default operation names to `"OTHER"`.

## Control Flow
Implementations provide actual locking semantics for `readLock`, `readLockInterruptibly`, `readUnlock`, `hasReadLock`, `writeLock`, `writeLockInterruptibly`, `writeUnlock`, and `hasWriteLock`. Interface defaults normalize simple calls into mode-aware calls.

## State and Persistence
No state in the interface. Implementations own lock state, metrics, and operation-name handling.

## Dependencies and Integration
It depends on `RwLockMode`. It is an FSNamesystem-facing contract and supports fine-grained locking modes such as global, filesystem, and block-manager locks.

## Risks
Default methods can hide mode selection mistakes if callers should use a non-global mode. Operation names are free-form strings, so metrics/logging consistency depends on callers. Implementations must preserve reentrancy/ownership semantics expected by existing FSNamesystem code.

## Test Signals
Implementation tests should verify default delegation, mode-specific acquisition/release, interruptible behavior, held-lock checks by current thread, write/read exclusion, and operation-name propagation to metrics/logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/RwLock.java -->
