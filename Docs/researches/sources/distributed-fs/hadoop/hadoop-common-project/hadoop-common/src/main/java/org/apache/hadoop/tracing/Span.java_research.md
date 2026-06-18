# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/Span.java

Purpose: `Span` is a no-op compatibility wrapper preserving old Hadoop tracing call sites after HTrace removal.

Important APIs and types: methods include `addKVAnnotation`, `addTimelineAnnotation`, `getContext`, `finish`, and `close`. Annotation methods return `this`; context returns null; close/finish do nothing.

Control flow: all calls are local no-ops and never emit tracing data.

State and persistence behavior: no fields and no persistence.

Dependencies and integration points: implements `Closeable`; returned by `Tracer.newSpan`; used by `TraceScope`.

Risks: silent no-op behavior can hide assumptions in call sites that expect real trace propagation or non-null contexts. Because methods return self, fluent call chains still compile but record nothing.

Test signals: verify no exceptions from annotations/finish/close, fluent self return, and null context behavior.
