## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsInfo.java

Purpose: Public metadata interface for metric, tag, and record identity.

Important APIs/types/functions: `name()` returns the stable programmatic name; `description()` returns human-readable context.

Control flow: No direct control flow; implementations are immutable value objects or enums.

State and persistence: Interface only. Interned implementations in `Interns` reduce duplicate metadata allocations.

Dependencies/integration: Used by every metric builder, tag, record, annotation factory, and registry. `MsInfo` is a built-in enum implementation for metrics-system fields.

Risks/test signals: Name stability affects JMX attribute names and sink schemas. Tests should verify names avoid illegal whitespace where registries enforce it.
