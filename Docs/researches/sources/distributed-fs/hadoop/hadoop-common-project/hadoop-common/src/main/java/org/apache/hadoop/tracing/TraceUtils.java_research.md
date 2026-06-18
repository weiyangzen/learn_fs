# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/tracing/TraceUtils.java

Purpose: `TraceUtils` keeps old Hadoop tracing utility entry points while tracing is disabled/no-op in this source tree.

Important APIs and types: it defines `DEFAULT_HADOOP_TRACE_PREFIX` and static methods `wrapHadoopConf`, `createAndRegisterTracer`, `byteStringToSpanContext`, and `spanContextToByteString`.

Control flow: all methods currently return null and perform no registration, wrapping, serialization, or deserialization.

State and persistence behavior: no state is stored. No trace configuration or span context is persisted into protobuf bytes.

Dependencies and integration points: imports Hadoop `Configuration`, shaded protobuf `ByteString`, `TraceConfiguration`, `Tracer`, and `SpanContext`. Call sites retain compatibility but must handle nulls.

Risks: returning null from conversion and tracer creation is a sharp edge for callers that do not expect tracing to be removed. This differs from `Tracer.Builder.build`, which returns a no-op tracer.

Test signals: cover null-return compatibility, callers' null guards, and behavior of code paths that formerly expected serialized span contexts.
