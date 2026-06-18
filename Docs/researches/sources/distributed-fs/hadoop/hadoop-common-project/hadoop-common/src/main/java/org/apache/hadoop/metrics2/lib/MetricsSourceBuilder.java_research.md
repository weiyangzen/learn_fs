## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/MetricsSourceBuilder.java

Purpose: Reflection-based builder that turns annotated objects into `MetricsSource` instances and initializes annotated mutable fields.

Important APIs/types/functions: Constructor scans inherited fields and methods. `build()` returns an existing `MetricsSource` or a generated source that snapshots the registry. `info()` returns source metadata.

Control flow: `initRegistry` reuses an existing `MetricsRegistry` field or creates one from `@Metrics`; field annotations initialize null mutable fields; method annotations create `MethodMetric` entries. Hybrid annotated `MetricsSource` objects require a registry.

State and persistence: Holds source object, factory, registry, source info, and flags for annotations/registry presence.

Dependencies/integration: Used by `MetricsAnnotations` and `MetricsSystemImpl.register`.

Risks/test signals: Reflection access, inherited members, existing non-null fields, hybrid validation, and missing annotations should be tested.
