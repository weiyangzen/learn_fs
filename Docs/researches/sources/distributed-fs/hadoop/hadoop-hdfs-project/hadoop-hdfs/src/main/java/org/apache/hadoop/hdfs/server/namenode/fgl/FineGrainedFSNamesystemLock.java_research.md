# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/fgl/FineGrainedFSNamesystemLock.java

## Purpose

`FineGrainedFSNamesystemLock.java` implements `FSNLockManager` by splitting the NameNode lock into a namespace/tree lock (`FS`) and a block-manager/data-node lock (`BM`). The source was read as a complete 285-line file.

## Important APIs, Types, and Functions

The class owns two `FSNamesystemLock` instances, `fsLock` and `bmLock`. It implements all `FSNLockManager` methods, dispatching on `RwLockMode.GLOBAL`, `FS`, or `BM`.

## Control Flow

For global lock mode, acquisition always takes FS then BM, and unlock releases BM then FS. Single-mode operations take only the selected lock. Interruptible global acquisition releases the already-held FS lock if interrupted while acquiring BM. Hold checks require both locks for global write/read and one lock for single modes. Metrics and threshold setters propagate to both locks, while getters return FS values. Queue length and long-hold counters return `-1` for global because there is no single aggregate queue.

## State and Persistence Behavior

State is in-memory lock state and lock metrics. No metadata is persisted, but correctness protects all NameNode namespace and block state mutations.

## Dependencies and Integration Points

It integrates with `FSNamesystemLock`, `RwLockMode`, and `MutableRatesWithAggregation`. NameNode code relies on its lock ordering to avoid deadlocks when operations need both namespace and block-manager state.

## Risks and Edge Cases

The FS-before-BM order is the key invariant. Any caller or future lock path that takes BM then FS can deadlock. The global read hold count returns only FS count for content-summary use, which is not a full aggregate. Test lock replacement is unsupported and throws.

## Test Signals

Tests should cover global and single-mode locking, interrupt during second-lock acquisition, unlock order, hold checks while write-locked, read hold counts, metrics propagation to both locks, unsupported test hooks, and concurrency scenarios that would reveal order inversion.
