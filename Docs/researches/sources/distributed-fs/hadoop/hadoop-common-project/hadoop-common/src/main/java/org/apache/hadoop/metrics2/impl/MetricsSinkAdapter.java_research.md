## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSinkAdapter.java

Purpose: Runtime adapter that isolates sinks behind filtering, queueing, retry, latency, and dropped-update metrics.

Important APIs/types/functions: `putMetrics` enqueues periodic buffers, `putMetricsImmediate` enqueues a waitable buffer, `publishMetricsFromQueue` runs in a daemon `SubjectInheritingThread`, `consume` sends accepted records to the sink, and `snapshot` reports adapter stats.

Control flow: Periodic puts are accepted only when logical time matches sink period. Queue full increments dropped counters. The consumer thread drains all queued buffers, retries exceptions with backoff, clears queue after retry exhaustion, and suppresses repeated errors. Immediate puts wait on a semaphore until consumed or timeout.

State and persistence: Holds filters, queue, thread flags, retry parameters, and registry metrics (`latency`, `dropped`, `qsize`) in memory.

Dependencies/integration: Created by `MetricsSystemImpl` from config or explicit sink registration. Uses `SinkQueue`, sink plugin, Hadoop IO cleanup, time utilities, and mutable metrics.

Risks/test signals: Queue full, sink exceptions, immediate timeout, closeable cleanup, and retry backoff are high-risk. Tests should also cover source/context/record/metric filters and queue gauge refresh.
