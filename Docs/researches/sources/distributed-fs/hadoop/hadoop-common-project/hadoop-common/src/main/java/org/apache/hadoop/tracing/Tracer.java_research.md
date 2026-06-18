# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Tracer.java

Purpose: `Tracer` is Hadoop's no-op tracer facade retained after HTrace removal so existing tracing call sites keep compiling.

Important APIs and types: constructor stores a name and `NullTraceScope`. Static methods include `curThreadTracer` and `getCurrentSpan`; instance methods include `newScope`, `newSpan`, `activateSpan`, `close`, and `getName`. Nested `Builder` accepts a name, optional `TraceConfiguration`, and builds a singleton no-op tracer.

Control flow: `newScope` and `activateSpan` return the shared null scope; `newSpan` returns a new no-op `Span`; `getCurrentSpan` and `curThreadTracer` return null in the outer static API. Builder caches one static `Tracer` for all names after the first build.

State and persistence behavior: instance state is name and null scope. Builder has static singleton state. No trace spans are exported or persisted.

Dependencies and integration points: used throughout Hadoop where trace scopes are created around IO/RPC operations. Constant `SPAN_RECEIVER_CLASSES_KEY` preserves config-key compatibility.

Risks: outer `globalTracer` is a separate static field initialized null while `Builder.globalTracer` may hold the singleton, so `curThreadTracer()` still returns null even after builder construction. Later builder names are ignored after the first build.

Test signals: cover builder singleton behavior, name retention for first build, null current tracer/span, null-scope return values, no-op close, and compatibility with try-with-resources scopes.
