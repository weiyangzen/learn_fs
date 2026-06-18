## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/AbstractMetric.java

Purpose: Base immutable metric abstraction implementing `MetricsInfo` and requiring concrete metric value, type, and visitor dispatch.

Important APIs/types/functions: Constructor stores non-null `MetricsInfo`; `name`, `description`, and protected `info()` delegate to it. Subclasses implement `Number value()`, `MetricType type()`, and `visit(MetricsVisitor)`. Equality and hashing include info and value.

Control flow: Concrete implementations in `metrics2.impl` wrap numeric values, expose the right `MetricType`, and call the matching visitor method. No mutation is performed after construction.

State and persistence: In-memory final `MetricsInfo` only; no persistence or synchronization.

Dependencies/integration: Used by `MetricsRecord`, record builders, sink filtering, JMX cache generation, and string/JSON builders. Depends on Hadoop preconditions and relocated Guava `Objects`.

Risks/test signals: Equality ignores concrete subclass except via info/value, so tests should verify counter/gauge handling through `type` and visitor dispatch. Null info should fail fast.
