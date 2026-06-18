# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FSNLockManager.java

## Purpose

`FSNLockManager.java` defines the abstraction used by `FSNamesystem` to acquire global or fine-grained NameNode locks by `RwLockMode`. The source was read as a complete 187-line file.

## Important APIs, Types, and Functions

The interface declares read/write lock and unlock methods, interruptible variants, overloads with operation names and lock-report suppliers, hold checks, read hold count, queue length, long-hold counters, metrics toggles, threshold getters/setters, and testing hooks for a `ReentrantReadWriteLock`.

## Control Flow

There is no implementation flow. `GlobalFSNamesystemLock` maps all modes to one lock, while `FineGrainedFSNamesystemLock` maps modes to FS, BM, or both locks.

## State and Persistence Behavior

The interface owns no state. Implementations own in-memory synchronization primitives and metrics; no persistent data is written directly.

## Dependencies and Integration Points

It depends on `RwLockMode`, `Supplier<String>`, `ReentrantReadWriteLock`, and `VisibleForTesting`. It is the contract that lets NameNode code use `RwLockMode.GLOBAL`, `FS`, and `BM` without binding to a concrete lock layout.

## Risks and Edge Cases

Implementations must agree on lock order and reporting semantics. Returning sentinel values for unsupported global aggregate metrics must be understood by metrics consumers.

## Test Signals

Tests should run the same lock-behavior suite against global and fine-grained implementations, covering reentrancy, interruptible acquisition, supplier reporting, metrics toggles, threshold propagation, hold checks, and test-lock hooks where supported.
