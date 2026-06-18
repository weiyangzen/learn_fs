## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MutableMetricsFactory.java

Purpose: Factory that maps `@Metric` annotated fields and methods to concrete mutable metric instances.

Important APIs/types/functions: `newForField` handles counter, gauge, rate, rates, aggregated rates, stat, rolling average, and quantile field types. `newForMethod` creates custom or `MethodMetric` wrappers. `getInfo` helpers derive names/descriptions from annotations, fields, methods, and classes.

Control flow: Field processing creates or registers the appropriate metric, throwing `MetricsException` for unsupported types. Method processing creates a metric and registers it by derived info.

State and persistence: Stateless factory; extension hooks allow subclasses to return custom metrics.

Dependencies/integration: Used by `MetricsSourceBuilder` with `DefaultMetricsFactory`.

Risks/test signals: Unsupported types, annotation `always`, sample/value names, interval, and get-prefix stripping should all be tested.
