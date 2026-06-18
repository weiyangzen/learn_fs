# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInstrumentationLifecycle.java

## Purpose

Unit test for `S3AInstrumentation` lifecycle with Hadoop metrics registration through `WeakRefMetricsSource`, especially close and double-close behavior.

## Important APIs, Types, and Functions

The test uses `S3AInstrumentation`, `S3AInstrumentation.getMetricsSystem()`, `hasMetricSystem()`, `lookupMetric()`, `getMetricSourceName()`, `close()`, `getIOStatistics()`, Hadoop `MetricsSystem`, and `WeakRefMetricsSource`.

## Control Flow

It creates instrumentation for a sample S3A URI, verifies a metrics system is active and a counter metric can be looked up, checks the registered source is a weak reference pointing to the instrumentation instance, closes it, verifies IO statistics and metric lookup still work, forces a new metrics system on demand, then closes the instrumentation a second time and asserts the new metrics system is not closed.

## State, Dependencies, and Integration Points

State is global metrics-system state plus the instrumentation instance's metrics source registration. It integrates S3A instrumentation with Hadoop metrics2 weak-reference lifecycle semantics.

## Risks and Test Signals

Global metrics state makes the test sensitive to ordering and leftover metrics from other tests. It catches leaks, double-close side effects, and regressions where closed instrumentation cannot tolerate later metric updates.
