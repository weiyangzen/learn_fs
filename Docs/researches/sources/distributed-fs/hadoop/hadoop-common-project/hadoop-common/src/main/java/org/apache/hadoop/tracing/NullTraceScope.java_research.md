# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/NullTraceScope.java

Purpose: `NullTraceScope` is the singleton no-op trace scope returned when tracing APIs are retained but no real tracer is active.

Important APIs and types: it extends `TraceScope`, exposes `INSTANCE`, and calls the parent constructor with null span.

Control flow: no additional flow beyond `TraceScope` methods. Closing the null scope is safe because the parent checks for a null span before closing.

State and persistence behavior: singleton object with inherited null `span`; no persistence.

Dependencies and integration points: returned by `Tracer.newScope` and `Tracer.activateSpan` in this no-op tracing layer.

Risks: callers expecting non-null spans from `span()` or `getSpan()` must handle null. The public constructor permits extra null scopes, though the singleton is intended.

Test signals: verify singleton reuse, close no-op behavior, and null span exposure.
