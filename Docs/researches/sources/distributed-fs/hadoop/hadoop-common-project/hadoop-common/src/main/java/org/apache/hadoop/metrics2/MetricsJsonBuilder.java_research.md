## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsJsonBuilder.java

Purpose: `MetricsRecordBuilder` implementation that accumulates tags and metrics in insertion order and serializes them as JSON.

Important APIs/types/functions: Constructor records a parent collector. `tuple` inserts into a `LinkedHashMap`. Overrides tag, add, context, counter, gauge, parent, and `toString`.

Control flow: Builder calls add entries to `innerMetrics`; `toString` uses a static Jackson `ObjectWriter`, returning a stack trace string if serialization fails.

State and persistence: Mutable map per builder instance; no synchronization or persistence. Duplicate keys overwrite prior entries.

Dependencies/integration: Uses Jackson, Commons Lang `ExceptionUtils`, SLF4J, and metrics model classes. Useful for JSON dumps, not the main sink pipeline.

Risks/test signals: `add(AbstractMetric)` stores `metric.toString()` rather than the raw number, so consumers must not assume every metric value is numeric JSON. Tests should cover duplicate key overwrite and serialization shape.
