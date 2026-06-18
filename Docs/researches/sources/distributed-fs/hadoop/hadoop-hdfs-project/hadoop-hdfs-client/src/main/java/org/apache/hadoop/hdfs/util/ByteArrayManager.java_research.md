# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteArrayManager.java

Purpose: `ByteArrayManager` abstracts allocation/recycling of byte arrays with optional pooling and per-size allocation limits for HDFS client buffers.

Important APIs/types/functions: `leastPowerOfTwo(int)` rounds sizes and detects overflow. `Conf` configures count threshold, max arrays per length, and counter reset period. `newInstance(Conf)` returns unlimited allocation when config is null or pooled `Impl` otherwise. `Counter` and `CounterMap` track per-size allocation frequency with time resets. `FixedLengthManager` blocks allocation when `numAllocated >= maxAllocated`, recycles arrays into `freeQueue`, and notifies waiters on recycle. `ManagerMap` creates per-length managers after threshold. `Impl.newByteArray()` rounds to min 32/power-of-two, creates a manager only after threshold, and returns empty singleton for size zero. `release()` recycles into an existing manager if one exists.

Control flow: below threshold, allocations use new arrays. Once repeated allocations for a size exceed threshold, a `FixedLengthManager` starts limiting and recycling that rounded size. `allocate()` waits while at capacity; `release()` decreases allocated count and may enqueue the array.

State and persistence behavior: all state is in memory and synchronized at component granularity. Debug logging uses a thread-local `StringBuilder`.

Dependencies and integration points: depends on Hadoop `Time`, `Preconditions`, `HadoopIllegalArgumentException`, and SLF4J. Used by HDFS client code that wants bounded buffer allocation under high concurrency.

Risks and test signals: callers must release arrays to avoid blocked waiters. Releasing arrays not allocated by the manager can lower `numAllocated`, intentionally clamped to zero, which affects limit accounting. Power-of-two overflow throws. Tests should cover rounding, zero-length singleton, threshold transition, blocking/unblocking, recycle queue sizing, stale counter reset, and release of unmanaged arrays.
