# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/MoverMetrics.java

Purpose: metrics source for an HDFS mover instance scoped to one block pool.

Important APIs/types/functions: `create(Mover)` registers a `MoverMetrics` instance with `DefaultMetricsSystem`. `getName()` returns `Mover-<blockpoolID>`. Gauges/counters include `processingNamespace`, `blocksScheduled`, and `filesProcessed`. Metrics getters expose bytes moved, blocks moved, and blocks failed from `NameNodeConnector` counters. Package-private mutators update namespace-processing state and increment scheduled/processed counters.

Control flow: `Mover` constructs metrics, `Processor.processNamespace()` toggles processing gauge, file processing increments occur per processed file, and scheduling increments occur when a pending move is accepted.

State and persistence behavior: metrics are in-process mutable counters/gauges registered into Hadoop metrics. They are not persisted except through external metrics sinks.

Dependencies and integration points: uses Hadoop metrics annotations, `DefaultMetricsSystem`, and `NameNodeConnector` counters.

Risks: metric source naming depends on blockpool ID uniqueness. If a mover instance is created repeatedly for the same block pool without metrics-system cleanup, registration collisions are possible depending on metrics system behavior. It is package-private and tightly coupled to `Mover`.

Test signals: `TestMover.testMoverMetrics` validates metric registration/counters.
