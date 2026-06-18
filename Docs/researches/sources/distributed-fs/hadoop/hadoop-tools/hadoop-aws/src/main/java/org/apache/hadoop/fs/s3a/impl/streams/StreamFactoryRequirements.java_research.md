<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java

Purpose: immutable description of resources and filesystem behavior required by a stream factory. It lets the filesystem size shared pools and configure vectored IO based on the selected stream type.

Important APIs/types/functions: constructor accepts shared thread count, per-stream thread count, mutable `VectoredIOContext`, and varargs `Requirements`. It calls `vectoredIOContext.build()` to freeze the vector context. Accessors include `sharedThreads()`, `streamThreads()`, `requiresFuturePool()`, `vectoredIOContext()`, and `requires(Requirements)`. Requirement flags are `ExpectUnauditedGetRequests` and `RequiresFuturePool`.

Control flow: a factory computes requirements after configuration initialization. The S3A filesystem reads these values before serving streams and adjusts background pools/auditing/vector behavior.

State/persistence: contains final in-memory values only. No persistence. The enum set is built from varargs and then treated as read-only by callers.

Dependencies/integration: depends on `VectoredIOContext` and is returned by `ObjectInputStreamFactory.factoryRequirements()`.

Risks/test signals: incorrect thread counts can underprovision or oversubscribe stream workloads; vector context immutability depends on `build()`. Tests should assert vararg flags, no-flag behavior, vector configuration propagation, and `toString()` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamFactoryRequirements.java -->
