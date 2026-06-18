## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/annotation/Metrics.java

Purpose: Runtime type annotation that marks a class as a metrics source and supplies source metadata.

Important APIs/types/functions: Attributes include `name`, `about`, and `context`, with defaults allowing class-name based metadata.

Control flow: `MetricsSourceBuilder.initRegistry` reads this annotation, builds source `MetricsInfo`, creates or reuses a `MetricsRegistry`, and tags it with the context.

State and persistence: Runtime annotation metadata only.

Dependencies/integration: Used by metrics system self-source and application metric source classes.

Risks/test signals: Missing annotation is acceptable only if explicit `@Metric` fields/methods can use a default registry. Tests should verify registry reuse and context tag emission.
