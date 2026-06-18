# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFineGrainedFSNamesystemLock.java

## Purpose

`TestFineGrainedFSNamesystemLock` stress-tests `FineGrainedFSNamesystemLock` read/write and interruptible read/write methods for `GLOBAL`, `FS`, and `BM` lock modes under heavy multithreaded use.

## Important APIs, Types, and Functions

The test creates `FineGrainedFSNamesystemLock`, uses `RwLockMode`, `FSNLockManager.writeLock/readLock/writeLockInterruptibly/readLockInterruptibly` and matching unlock methods, `HadoopExecutors.newFixedThreadPool`, `AtomicLong` counters, and many `Callable<Boolean>` tasks.

## Control Flow

`testMultipleThreadsUsingLocks` creates 1000 callables spread across twelve operation categories: normal and interruptible read/write locks for each mode. Each task loops a random 2000-3000 times. Write helpers increment and later decrement a per-mode counter while holding the lock; read helpers only inspect. After invoking all tasks and waiting on futures, the test asserts all counters returned to zero.

## State and Persistence Behavior

Only in-memory lock state and atomic counters are mutated. There is no filesystem persistence.

## Dependencies and Integration Points

This directly tests the lock manager abstraction used by the NameNode fine-grained lock model. Unlock calls include operation names, covering instrumentation-aware unlock signatures.

## Risks and Edge Cases

The test uses Java `assert` statements for final counter checks, so assertions must be enabled to enforce them. Interruptible lock helpers ignore interrupts but carefully retry the decrement if the increment succeeded. The randomized loop count makes runtime variable.

## Test Signals

Signals are completion of all futures within 240 seconds and final `globalCount`, `fsCount`, and `bmCount` equal to zero, showing balanced lock/unlock behavior under concurrency.
