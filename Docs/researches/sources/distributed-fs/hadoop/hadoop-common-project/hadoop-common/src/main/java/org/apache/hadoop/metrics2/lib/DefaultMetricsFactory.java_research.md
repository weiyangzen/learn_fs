## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/DefaultMetricsFactory.java

Purpose: Provides a default `MutableMetricsFactory` singleton for annotation-based source construction.

Important APIs/types/functions: Static `getAnnotatedMetricsFactory` or similar accessor returns the singleton factory.

Control flow: Lazy or static initialization supplies the factory to `MetricsAnnotations.newSourceBuilder`.

State and persistence: Process-local singleton factory; no persistence.

Dependencies/integration: Bridges public annotation helper APIs to `MutableMetricsFactory`.

Risks/test signals: Factory replacement or singleton initialization changes could affect all annotated sources. Tests should verify stable default factory and custom extension points if present.
