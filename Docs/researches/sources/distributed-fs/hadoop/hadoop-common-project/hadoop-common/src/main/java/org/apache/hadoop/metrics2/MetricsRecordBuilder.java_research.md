## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsRecordBuilder.java

Purpose: Fluent abstract builder for constructing one metrics record.

Important APIs/types/functions: Abstract methods add tags, existing metrics, context, counters, and gauges for int, long, float, and double values. `parent()` returns the collector; `endRecord()` returns `parent()`.

Control flow: Source code calls builder methods during `getMetrics`; concrete builders create immutable metric objects, text, or JSON.

State and persistence: Abstract only; mutable state is in implementation builders.

Dependencies/integration: Common API used by mutable metrics, annotations-generated sources, metrics system self-source, and custom source implementations.

Risks/test signals: Fluent chaining relies on every override returning `this`. Tests should cover all primitive overloads and parent/end chaining.
