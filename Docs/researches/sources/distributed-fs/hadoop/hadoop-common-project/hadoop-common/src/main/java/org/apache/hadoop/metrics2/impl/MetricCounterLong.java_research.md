## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricCounterLong.java

Purpose: Immutable long counter metric implementation.

Important APIs/types/functions: Stores long value, returns `Long`, reports `MetricType.COUNTER`, and dispatches to the long counter visitor overload.

Control flow: Built by `MetricsRecordBuilderImpl.addCounter(MetricsInfo,long)`.

State and persistence: Final value and metadata only.

Dependencies/integration: Used for long mutable counters, stats sample counts, and system dropped-publish counters.

Risks/test signals: Visitor overload selection and large long values should be covered.
