## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsAnnotations.java

Purpose: Static helper entry points for creating metrics sources from annotations.

Important APIs/types/functions: Provides `newSourceBuilder(Object)`, `makeSource(Object)`, and related helpers that use `DefaultMetricsFactory`.

Control flow: Callers pass a source object; helpers construct a `MetricsSourceBuilder` and either return the builder or generated `MetricsSource`.

State and persistence: Stateless utility class.

Dependencies/integration: Used by `MetricsSystemImpl.register` and self-source registration.

Risks/test signals: Tests should cover plain `MetricsSource` objects, annotated POJOs, invalid annotated classes, and hybrid source/annotation rules.
