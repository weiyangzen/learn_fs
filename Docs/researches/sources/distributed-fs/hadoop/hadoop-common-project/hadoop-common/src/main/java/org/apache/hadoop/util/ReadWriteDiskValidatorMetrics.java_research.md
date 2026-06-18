# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidatorMetrics.java

## Purpose
`ReadWriteDiskValidatorMetrics` registers and updates metrics for each directory checked by `ReadWriteDiskValidator`, including failure count, last failure time, and read/write latency quantiles.

## Important APIs, Types, And Functions
Important members are annotated `MutableCounterInt failureCount`, `MutableGaugeLong lastFailureTime`, `MetricsRegistry`, quantile intervals of one hour, one day, and ten days, `DIR_METRICS`, `getMetric`, `addWriteFileLatency`, `addReadFileLatency`, `sourceName`, and `diskCheckFailed`.

## Control Flow
`getMetric` synchronizes on the class, checks the directory-name cache, constructs metrics if absent, registers them with `DefaultMetricsSystem.instance()` using `sourceName(dirName)`, stores the result, and returns it. Latency methods add values to every configured quantile. `diskCheckFailed` increments the failure counter and sets last failure time to `System.nanoTime()`.

## State And Persistence
State is in-memory metrics objects cached by raw directory string. Metrics are exported through Hadoop metrics2 but not persisted by this class.

## Dependencies And Integration Points
It depends on metrics2 annotations and mutable metric types, `DefaultMetricsSystem`, `Interns.info`, and `ReadWriteDiskValidator`.

## Risks
Cache keys are unnormalized directory strings, so aliases can register duplicate sources. Source names include directory text and may contain characters problematic for sinks. `lastFailureTime` uses monotonic nano time, not wall-clock time. Cached metrics are never removed.

## Test Signals
Tests should assert per-directory caching, registration source names, quantile array setup, latency propagation to all quantiles, failure counter/gauge updates, and behavior when metrics system is absent.
