## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableInverseQuantiles.java

Purpose: Specialized quantile metric for inverse/rate-style values where lower percentiles may be more meaningful than upper latency percentiles.

Important APIs/types/functions: Extends `MutableQuantiles` and overrides quantile definitions and naming as needed.

Control flow: Uses the same scheduled rollover and snapshot mechanics as `MutableQuantiles`, but with inverse quantile targets.

State and persistence: Maintains estimator, previous snapshot/count, interval, and scheduled task through the parent class.

Dependencies/integration: Created by `MetricsRegistry.newInverseQuantiles`.

Risks/test signals: Tests should verify inverse quantile set, generated metric names/descriptions, rollover, and `stop` task cancellation.
