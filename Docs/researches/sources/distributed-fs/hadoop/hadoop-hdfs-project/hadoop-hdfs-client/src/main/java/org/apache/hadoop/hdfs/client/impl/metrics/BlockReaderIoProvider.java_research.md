# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/metrics/BlockReaderIoProvider.java

## Purpose
`BlockReaderIoProvider` wraps short-circuit local block `FileChannel` reads with optional sampled latency recording.

## Important APIs, types, and functions
The constructor accepts nullable `ShortCircuitConf`, `BlockReaderLocalMetrics`, and `Timer`; it enables sampling only when configuration exists and short-circuit metrics are enabled. `read(FileChannel, ByteBuffer, long)` performs the actual positional channel read and, for sampled calls, measures elapsed monotonic time and calls `addLatency`. `addLatency` records latency and logs one warning per provider if a sampled read exceeds 1000 ms.

## Control flow
Sampling compares a random integer in `[0, Integer.MAX_VALUE)` against a precomputed range derived from the configured sampling percentage. Unsampled reads call `FileChannel.read` directly. Sampled reads measure before and after the read and update rolling metrics.

## State and persistence behavior
State includes the metrics object, enabled flag, sample threshold, timer, and a boolean suppressing repeated slow-read warnings. Metrics are exported through Hadoop metrics, but this class itself persists nothing.

## Dependencies and integration points
It depends on `DfsClientConf.ShortCircuitConf`, `BlockReaderLocalMetrics`, `Timer`, `FileChannel`, `ByteBuffer`, and `ThreadLocalRandom`. It is used by the newer `BlockReaderLocal` short-circuit implementation, not the legacy reader in this subset.

## Risks and test signals
Tests should cover disabled metrics with null config, 0/100 sampling behavior, latency recording, warning suppression after the first slow read, exception propagation from `FileChannel.read`, and deterministic timer injection. The range computation intentionally scales by sampling percentage; extreme values are normalized upstream in `ShortCircuitConf`.
