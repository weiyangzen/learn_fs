# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestTopMetrics.java

Purpose: verifies that the NameNode top-user metrics source publishes expected records and counters for operation totals and per-user operation counts.

Important APIs and types: `TopConf`, `TopMetrics`, `TOPMETRICS_METRICS_SOURCE_NAME`, `MetricsAsserts.getMetrics`, `MetricsCollector`, `MetricsRecordBuilder`, `Interns.info`, and Mockito `verify`.

Control flow: the test constructs `TopMetrics` with default reporting windows from `TopConf`, reports the user `test` performing `listStatus` three times, retrieves metrics, and verifies the collector receives records for the 60s, 300s, and 1500s windows. It then verifies each window emits `op=listStatus.TotalCount`, wildcard `op=*.TotalCount`, and `op=listStatus.user=test.count` counters with value 3.

State and persistence behavior: all state is in-memory rolling-window top metrics. There is no filesystem namespace or persistent state.

Dependencies and integration points: integrates top metrics aggregation with Hadoop metrics2 collection naming conventions and interned metric metadata.

Risks and test signals: risks include missing reporting windows, broken wildcard totals, incorrect per-user counter naming, or metrics source record naming changes. Mockito verification of three records and three counter emissions per metric is the main signal.
