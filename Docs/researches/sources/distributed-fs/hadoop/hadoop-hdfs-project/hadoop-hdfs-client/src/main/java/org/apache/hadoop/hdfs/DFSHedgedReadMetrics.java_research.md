# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/DFSHedgedReadMetrics.java

## Purpose
`DFSHedgedReadMetrics` is a small private metrics holder for HDFS client hedged reads. It tracks how often a hedged read is launched, how often a hedged request wins, and how often the hedged-read executor rejects work and runs it in the caller thread.

## Important APIs, Types, and Functions
The class contains three public `LongAdder` fields: `hedgedReadOps`, `hedgedReadOpsWin`, and `hedgedReadOpsInCurThread`. It exposes increment methods `incHedgedReadOps`, `incHedgedReadOpsInCurThread`, and `incHedgedReadWins`, plus getters returning `long` snapshots.

## Control Flow
`DFSClient` owns one static instance and exposes it through `getHedgedReadMetrics()`. `DFSInputStream.hedgedFetchBlockByteRange` increments `hedgedReadOps` when the first positional read exceeds the hedged-read threshold and a parallel attempt is launched. It increments `hedgedReadOpsWin` when one hedged future completes and the remaining futures are canceled. `DFSClient` increments `hedgedReadOpsInCurThread` from the hedged-read thread pool rejection handler when executor saturation causes caller-runs fallback.

## State and Persistence
All counters are in-memory process metrics. `LongAdder` makes concurrent increments cheap and thread-safe, but the counters are not persisted and are shared through the static `DFSClient` metric instance. Tests can reset the public adders directly.

## Dependencies and Integration Points
The main integration points are `DFSClient.initThreadsNumForHedgedReads`, `DFSInputStream.hedgedFetchBlockByteRange`, `DistributedFileSystem.getHedgedReadMetrics`, and tests in `TestPread`. The class intentionally avoids Hadoop metrics-system dependencies and is directly accessible to client-side consumers such as HBase.

## Risks
Because fields are public, external code and tests can reset or mutate counters at any time. Since the `DFSClient` instance is static, metrics combine all clients in the JVM and do not distinguish files, clusters, users, or nameservices. `LongAdder.longValue()` is a weakly consistent snapshot under concurrent updates, which is acceptable for metrics but not for exact accounting.

## Test Signals
`TestPread` resets the adders and verifies hedged-read launches, wins, and caller-thread fallback under delayed reads and constrained pools. Good regression tests should assert counter changes only around controlled hedged-read scenarios and should avoid assuming global counters start at zero unless they reset them first.
