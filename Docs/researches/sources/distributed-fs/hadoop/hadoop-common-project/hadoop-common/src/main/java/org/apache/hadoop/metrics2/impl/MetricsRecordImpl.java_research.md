## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsRecordImpl.java

Purpose: Concrete immutable metrics record implementation.

Important APIs/types/functions: Constructor stores `MetricsInfo`, timestamp, tags, and metrics. Implements `timestamp`, `tags`, `metrics`, and string rendering.

Control flow: Built by `MetricsRecordBuilderImpl.getRecord` after filtering.

State and persistence: Holds record snapshot lists in memory; no persistence. Lists are expected to be unmodifiable from builder.

Dependencies/integration: Consumed by buffers, sink adapters, JMX source adapters, and filters.

Risks/test signals: Snapshot immutability and context tag resolution are critical. Tests should cover toString, iteration, empty metrics, and context extraction.
