# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/SpanContext.java

Purpose: `SpanContext` is a no-op wrapper class retained to avoid exposing OpenTracing/OpenTelemetry context types directly through Hadoop APIs.

Important APIs and types: it implements `Closeable`, has a public constructor, and `close()` is a no-op.

Control flow: no runtime flow beyond no-op close.

State and persistence behavior: no fields, serialization, or propagation data.

Dependencies and integration points: accepted by `Tracer.newSpan` and `Tracer.newScope`, and referenced by `TraceUtils` conversion methods.

Risks: `TraceUtils` conversion methods currently return null, so this class does not carry distributed trace state. Callers must tolerate empty contexts.

Test signals: verify construction and close are harmless, and context-consuming APIs accept instances without producing real tracing effects.
