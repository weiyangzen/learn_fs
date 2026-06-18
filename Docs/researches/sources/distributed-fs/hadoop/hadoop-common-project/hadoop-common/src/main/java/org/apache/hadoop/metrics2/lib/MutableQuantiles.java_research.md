## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableQuantiles.java

Purpose: Mutable metric that estimates selected quantiles over a rolling interval using online sampling.

Important APIs/types/functions: Defines default quantiles, constructor builds metric infos and schedules rollover, `add(long)` inserts values, `snapshot` emits previous count and quantile gauges, `stop` cancels the scheduled task, and testing setters expose estimator internals.

Control flow: A static daemon scheduler runs `RolloverSample` every interval. Rollover snapshots estimator values into `previousSnapshot`, clears the estimator, and marks changed. `snapshot` emits the previous rolled values, using zero when no snapshot exists.

State and persistence: Holds metric infos, interval, estimator, previous count/snapshot, and scheduled future in memory. Static scheduler is shared across instances.

Dependencies/integration: Created by registry and annotation factory; uses Hadoop quantile utilities and Guava thread factory.

Risks/test signals: Background task lifecycle and static scheduler can leak across tests. Tests should cover interval validation at registry level, rollover, no-data snapshot, quantile names, and `stop`.
