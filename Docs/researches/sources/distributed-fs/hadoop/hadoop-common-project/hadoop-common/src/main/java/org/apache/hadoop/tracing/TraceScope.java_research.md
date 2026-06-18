# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceScope.java

Purpose: `TraceScope` is the closeable scope wrapper around a `Span`, preserved for try-with-resources tracing call sites.

Important APIs and types: constructor stores a `Span`. Methods include overloaded `addKVAnnotation`, `addTimelineAnnotation`, `span`, `getSpan`, `reattach`, `detach`, and `close`.

Control flow: annotation, attach, and detach methods are no-ops. `close` closes the wrapped span when non-null.

State and persistence behavior: stores one package-visible `Span` reference. No durable state is written.

Dependencies and integration points: used by `Tracer`, `NullTraceScope`, and code that scopes trace spans around operations.

Risks: a non-null span is closed on scope close, but no finish semantics are enforced beyond whatever `Span.close` does, currently no-op. Null spans are common via `NullTraceScope`.

Test signals: cover null and non-null span close behavior, getter aliases, and no-op annotations with string and number values.
